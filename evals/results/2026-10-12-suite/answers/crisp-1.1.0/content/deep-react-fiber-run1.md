React reconciliation is the process that compares the previous element tree with the new one and finds the minimum changes needed. Fiber is the data structure and work loop that runs this comparison in small units that React can pause, resume, or discard. This explanation follows the React 18 and 19 source. Internal names and details change between versions.

## The problem Fiber solved

Before React 16, the reconciler was recursive and used the JavaScript call stack. Once an update started, it ran to the end. A large tree could block the main thread for tens of milliseconds, which caused dropped frames and delayed input.

Fiber replaced the call stack with heap-allocated objects that React walks with a loop. React controls the loop, so it can stop between units of work and let the browser paint or handle input.

Fiber gave React four abilities:
- Pause work and resume it later.
- Assign priorities to different updates.
- Reuse or discard work that is already done.
- Return to the parent and move to the next sibling without recursion.

## Elements, components, and fibers

A React element is a plain object that describes what to render. JSX like `<Button color="red" />` compiles to a call that returns `{ type: Button, props: { color: "red" }, key: null }`. Elements are cheap and React creates them on every render.

A component is a function or class that returns elements. A fiber is the internal object that represents one component instance or one DOM node in the tree. Fibers live across renders. Elements do not.

## The two heuristics behind diffing

A general tree diff costs O(n³). React instead uses two assumptions to reach O(n):

1. Two elements of different types produce different trees. React destroys the old subtree and builds a new one.
2. A `key` prop tells React which children are stable across renders among siblings.

React compares only nodes at the same position in the tree. It never searches for a moved subtree elsewhere.

## What a fiber contains

A fiber is a JavaScript object. These are the most important fields:

- `tag`: the kind of fiber, such as function component, class component, host component, or Suspense boundary.
- `type` and `key`: the identity used by the diff.
- `stateNode`: the DOM node, class instance, or root object.
- `return`, `child`, `sibling`: pointers that form the tree as a linked list. `return` points to the parent.
- `pendingProps` and `memoizedProps`: the new props and the props used in the last render.
- `memoizedState`: for function components, the head of the linked list of hooks.
- `updateQueue`: queued state updates and effects.
- `lanes` and `childLanes`: bitmasks that mark pending work on this fiber and in its subtree.
- `flags` and `subtreeFlags`: bitmasks that mark side effects needed at commit time, such as `Placement` or `Update`.
- `alternate`: a pointer to the matching fiber in the other tree.

The `child`, `sibling`, and `return` pointers allow a depth-first walk with a simple loop and no recursion.

## Two trees: current and work-in-progress

React keeps two fiber trees. The current tree matches what is on screen. The work-in-progress tree is the one React builds during a render.

Each fiber in one tree points to its twin in the other through `alternate`. React reuses these twin objects between renders to avoid allocating new memory. This technique is called double buffering.

When a render finishes and commits, React sets `root.current` to the work-in-progress tree. That tree becomes the current tree. The old current tree becomes the spare for the next render.

## The render phase

The render phase is pure computation. It does not touch the DOM. It can be paused, restarted, or thrown away.

The core loop looks like this:

```js
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
}
```

`shouldYield()` returns true when the time slice is used up. The slice is about 5 ms. The legacy synchronous mode uses the same loop without the `shouldYield` check.

Each `performUnitOfWork` call does the following:

1. Call `beginWork(current, workInProgress)`. It processes the fiber and returns its first child, or null if there is none.
2. If a child comes back, that child becomes the next unit of work.
3. If the result is null, call `completeUnitOfWork`. It runs `completeWork` on this fiber.
4. After completion, move to the sibling if one exists. Otherwise go up to `return` and complete the parent.

So the walk goes down with `beginWork` and back up with `completeWork`. Every fiber gets both calls.

### beginWork

`beginWork` first decides whether it can skip the fiber. A bailout happens when all of these are true:
- The old and new props are the same object by reference.
- No context that this fiber reads has changed.
- The fiber has no pending update in its own lanes.

If the fiber itself has no work, React checks `childLanes`. If no descendant has work, React skips the whole subtree and returns null. If a descendant has work, React clones the child fibers and continues down.

If the fiber does have work, React acts by `tag`. For a function component, it calls the function with a hooks dispatcher active. For a class component, it calls `render` and the lifecycle methods. For a host component like `div`, it only reconciles the children.

The component then returns new elements, and `reconcileChildren` compares them with the old child fibers.

### The child diff

`reconcileChildFibers` handles three cases.

For a single child, React compares `key` and `type`. If both match, it reuses the existing fiber and gives it the new props. If not, it marks the old fiber for deletion and creates a new fiber.

For arrays, React uses a two-pass algorithm:

1. Walk the old fibers and new elements together in order. Continue while the keys match. Reuse each fiber. Stop at the first mismatch.
2. If the new list ends, mark all remaining old fibers for deletion.
3. If the old list ends, create fibers for all remaining new elements.
4. Otherwise, put the remaining old fibers in a map by key. If an element has no key, React uses the index.
5. Walk the remaining new elements and look each one up in the map. Reuse the match and remove it from the map. Create a fiber if none exists.
6. Delete every fiber left in the map.

Step 5 also detects moves. React tracks `lastPlacedIndex`, the highest old index it has seen so far. If a reused fiber has an old index lower than that value, it must move, so React sets the `Placement` flag. Otherwise it stays in place.

This is why stable keys matter. With index keys, inserting an item at the start makes every following item look changed. With stable keys, only the new item is created.

### completeWork

On the way up, `completeWork` does the following:
- For a new host fiber, it creates the DOM node, appends the already-built child nodes, and sets the initial props. The node is not yet attached to the document.
- For an existing host fiber, it compares old and new props and records the changes in `updateQueue`, with an `Update` flag.
- It merges the `flags` and `subtreeFlags` of children into the parent's `subtreeFlags`.

The `subtreeFlags` merge lets the commit phase skip whole subtrees that have no effects.

## Hooks and state storage

For a function component, `memoizedState` on the fiber holds a linked list of hook objects. Each hook object stores its value and a queue of pending updates.

React matches hooks to their data by call order. This is the reason for the rule that hooks must not run inside conditions or loops. A changed order would pair a hook with the wrong stored data.

React swaps the hooks dispatcher before calling the component. On mount, `useState` creates a new hook object. On update, it reads the next object in the existing list.

Calling `setState` does not change state at once. It adds an update to the hook's queue and schedules a render at some lane. During the next render, React processes the queue in order and computes the new state.

## Lanes and scheduling

Each update receives a lane. A lane is one bit in a 31-bit mask. Lower bits have higher priority. The main lanes are:

- `SyncLane`: discrete events like clicks and key presses.
- `InputContinuousLane`: continuous events like drag and scroll.
- `DefaultLane`: updates outside any event, such as from a timeout or a network response.
- Transition lanes: updates wrapped in `startTransition`.
- `IdleLane` and `OffscreenLane`: low-priority and hidden work.

A bitmask lets React combine lanes, test for overlap, and mark them on fibers with fast bit operations.

The root picks the highest-priority lanes with pending work and renders only those. Updates in other lanes stay in the queue. When React skips an update for priority reasons, it keeps the later updates in the queue and rebases them. The final state is then the same as if all updates ran in order, even though the intermediate renders differ.

A higher-priority update can arrive during a low-priority render. React then discards the work-in-progress tree and starts again from the root with the urgent lane. The discarded work leaves no trace, because the render phase did not touch the DOM or the current tree.

To prevent starvation, React marks lanes as expired after a timeout. It then renders them synchronously without yielding.

The separate `scheduler` package wraps the browser `MessageChannel`. It runs React's work in macro-tasks and gives control back to the browser between them.

## The commit phase

The commit phase is synchronous. It cannot be interrupted, because it changes the DOM and the user must never see a half-applied result. It has three sub-phases:

1. Before mutation: React calls `getSnapshotBeforeUpdate` on class components.
2. Mutation: React walks the effect flags. It inserts, moves, updates, and deletes DOM nodes. It runs cleanup functions of `useLayoutEffect` and detaches refs of removed or changed nodes. On deletion, it calls `componentWillUnmount`.
3. Layout: React has already set `root.current = finishedWork` between steps 2 and 3. It now calls `componentDidMount`, `componentDidUpdate`, and `useLayoutEffect` callbacks, and attaches refs.

Because the tree swap happens before the layout step, layout effects see the new tree. In the mutation step, the old tree is still current. That is why `componentWillUnmount` sees the old tree.

Passive effects, which are `useEffect` callbacks, run after the commit. Normally React schedules them after the browser paints. If the render came from a discrete event like a click, React flushes them at the end of the commit, before the next render can start.

## Suspense and transitions

Suspense works through the render phase. When a component reads data that is not ready, it throws a promise or calls `use`. React catches this at the nearest `Suspense` boundary and shows the fallback. When the promise resolves, React retries the render.

Transitions change this behavior. When an update inside `startTransition` suspends, React keeps the old UI on screen and works on the new tree in the background. It commits only when the new tree is ready. This is possible because the work-in-progress tree is separate from the current tree.

## Consequences for your code

- Render must be pure. React can call a component several times, or discard the result. Strict Mode calls components twice in development to expose impurity.
- A new component type means a remount. If you define a component inside another component, it gets a new type on each render. The inner tree loses its state every time.
- Changing `key` on purpose resets a component. This is a clean way to reset state.
- Parent re-renders do not skip children by default. A child skips only when React sees the same element object, or when `memo` shallow-compares equal props.
- Use stable, unique keys in lists. Avoid array indexes if the list can reorder, insert, or delete.
- Side effects belong in event handlers or effects, not in the render body.

## Summary of the full flow

1. An event or timer calls `setState`. React adds the update to a queue and assigns it a lane.
2. React marks the fiber and its ancestors with that lane up to the root, then schedules a render.
3. The render phase builds the work-in-progress tree, one fiber at a time, with `beginWork` and `completeWork`. It can yield or restart.
4. Diffing happens inside `beginWork` through `reconcileChildren`. Results are stored as flags on fibers.
5. The commit phase applies the flags to the DOM in one synchronous pass and swaps the current tree.
6. Layout effects run during the commit. Passive effects run right after, usually after paint.

To go deeper, read `ReactFiberWorkLoop`, `ReactFiberBeginWork`, `ReactChildFiber`, and `ReactFiberLane` in the React repository.
