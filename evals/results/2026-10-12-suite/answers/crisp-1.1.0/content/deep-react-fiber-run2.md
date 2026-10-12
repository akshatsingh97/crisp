React reconciliation is the diff that decides which UI changes to apply after a render. Fiber is the data structure and work loop that runs this diff in small, pausable units. Internal names below match React 18 and 19. File and function names can change between versions.

## 1. Why Fiber exists

Before React 16, the reconciler was recursive and used the JavaScript call stack. Once it started on a tree, it had to finish. A large update blocked the main thread, so frames dropped and input lagged.

Fiber replaces the call stack with a linked data structure that React controls. This gives React four abilities:

- Pause work and resume it later.
- Abort work that is no longer needed.
- Reuse work done earlier.
- Assign a priority to each update.

## 2. Elements, fibers, and instances

These three things are easy to confuse.

- An element is a plain object: `{ type, props, key, ref }`. It describes what you want. It is cheap, immutable, and recreated on every render.
- A fiber is React's internal work unit. There is one per component instance or DOM node. It lives across renders and is mutable.
- An instance is the real thing, such as a DOM node or class instance. The fiber holds it in `stateNode`.

JSX produces elements. The reconciler turns elements into fibers.

## 3. Anatomy of a fiber

A fiber is a JavaScript object. These are the fields that matter most:

- `tag`: the kind of node, such as FunctionComponent, ClassComponent, HostComponent, HostRoot, Fragment, or Suspense.
- `type` and `key`: identity, used by the diff.
- `stateNode`: the DOM node or class instance.
- `return`, `child`, `sibling`, `index`: the tree links.
- `pendingProps` and `memoizedProps`: the new props and the props used in the last render.
- `memoizedState`: the state of the last render. For function components, this is the head of the hooks list.
- `updateQueue`: queued state updates and the effects list.
- `flags` and `subtreeFlags`: bit flags for side effects on this fiber and below it.
- `lanes` and `childLanes`: bit flags for pending work on this fiber and below it.
- `alternate`: the twin fiber, explained in the next section.

The tree is not a normal tree with child arrays. `child` points to the first child only. Each child points to the next with `sibling`, and back to the parent with `return`.

This layout lets React walk the tree with a loop instead of recursion. The walk goes down through `child`, then across through `sibling`, then up through `return`. A loop can stop at any point and continue later. A recursive call cannot.

## 4. Two trees and double buffering

React keeps two fiber trees:

- The current tree matches what is on screen.
- The work-in-progress tree is the one React builds during a render.

Each fiber has an `alternate` that points to its twin in the other tree. React reuses the twin object instead of allocating a new one. Only the first render of a node allocates.

When a render finishes and commits, React sets `root.current` to the work-in-progress tree. That tree becomes current, and the old current tree becomes the spare for the next render. Because the current tree is never edited during render, React can throw away a half-built tree safely.

## 5. The render phase

The render phase builds the work-in-progress tree. It has no visible effects. It can pause, restart, or be discarded.

The core loop looks like this:

```js
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
}

function performUnitOfWork(fiber) {
  const next = beginWork(fiber.alternate, fiber, renderLanes);
  fiber.memoizedProps = fiber.pendingProps;
  if (next === null) completeUnitOfWork(fiber);
  else workInProgress = next;
}
```

Each fiber gets two visits: `beginWork` on the way down, and `completeWork` on the way up.

### beginWork (going down)

`beginWork` decides what to do with one fiber. It follows these steps:

1. Check for a bailout. If props, context, and pending lanes are unchanged, React can skip this fiber (see section 9).
2. Switch on `tag`. For a function component, React runs your function with hooks. That call returns new child elements.
3. Call `reconcileChildren`. This diffs the new elements against the old child fibers.
4. Return the first child fiber. The loop then continues from that child.

`reconcileChildren` creates or reuses child fibers and marks them with flags. The main flags are `Placement` (insert or move), `Update` (props changed), and `ChildDeletion`.

### completeWork (going up)

When a fiber has no more children to visit, React completes it:

1. For a new host node, React creates the DOM element in memory and appends the already-built child DOM nodes. Nothing is attached to the page yet.
2. For an updated host node, React compares old and new props and records the changes. It sets the `Update` flag if any exist.
3. React merges the flags of all children into the parent's `subtreeFlags`.
4. React moves to the sibling, or back up to the parent.

The `subtreeFlags` merge matters later. It lets the commit phase skip whole subtrees that have no side effects.

## 6. The diffing rules

A general tree diff costs O(n³). React uses two assumptions to get O(n):

1. Elements of different types produce different trees.
2. A `key` gives a stable identity to children across renders.

React also only compares siblings at the same level. It never searches the whole tree for a moved node.

### Same position, different type

If the type changes, React destroys the old subtree and builds a new one. All state below that point is lost. This happens when `<div>` becomes `<span>`, or when `<A />` becomes `<B />`.

### Same position, same type

React keeps the fiber and updates its props. A DOM node gets only the attributes that changed. A component rerenders with the new props and keeps its state.

State therefore belongs to a position in the tree, not to an element. Two `<Counter />` calls in different positions have separate state. Moving one to another position resets it.

### Single child

React compares `key` first, then `type`. If both match, it reuses the fiber. If not, it deletes the old fiber and creates a new one.

### Lists of children

React uses a two-pass algorithm:

1. Walk the old and new lists together while keys match. Reuse each fiber. Stop at the first mismatch.
2. If the new list ended, delete the remaining old fibers. If the old list ended, create fibers for the remaining new elements.
3. Otherwise, put the remaining old fibers in a map keyed by `key` (or by index when there is no key).
4. Scan the remaining new elements. Look each one up in the map and reuse the fiber if found.
5. Track `lastPlacedIndex`. If a reused fiber had an old index below this value, it moved, so React marks it `Placement`.
6. Delete every fiber left in the map.

This design has a known quirk. Moving the last item to the front costs many moves. Moving the first item to the end costs one.

### Practical rules for keys

- Use stable, unique keys from your data, such as an ID.
- Do not use the array index if the list can reorder, insert, or delete. Fibers will match the wrong items and carry the wrong state.
- Do not use `Math.random()`. A new key every render forces a remount every render.
- Change a `key` on purpose when you want to reset a component's state.
- Do not define a component inside another component. The inner type is a new function each render, so React remounts it every time.

## 7. Hooks and state storage

For a function component, `fiber.memoizedState` points to a linked list of hook objects. Each hook object has its own `memoizedState`, a `queue` of updates, and a `next` pointer.

React matches hooks to list entries by call order. This is the reason hooks must run in the same order every render. A hook inside a condition shifts the list, and every later hook reads the wrong entry.

Calling `setState` does this:

1. React picks a lane for the update (section 8).
2. React adds the update to the hook's queue.
3. React marks the fiber and its ancestors with that lane.
4. React schedules a render on the root.

During the next render, `useState` replays the queue. It applies updates whose lane is part of the current render. It skips the others and keeps them for later. This is called rebasing, and it keeps the final state correct even when updates apply out of order.

There is an eager shortcut. If the queue is empty and the new state equals the current state, React can skip scheduling.

## 8. Lanes and scheduling

A lane is a bit in a 31-bit mask. Each bit marks a priority level. Common lanes, from most to least urgent:

- `SyncLane`: discrete events, such as a click or key press.
- `InputContinuousLane`: continuous events, such as drag or scroll.
- `DefaultLane`: updates outside of events, such as a `setTimeout` callback.
- `TransitionLanes`: updates inside `startTransition`.
- `RetryLanes`: Suspense retries.
- `IdleLane` and `OffscreenLane`: low-value background work.

Bitmasks make set operations cheap. Merging lanes is `a | b`. Testing overlap is `a & b`.

Every fiber has `lanes` for its own pending work and `childLanes` for work below it. During a render, if a fiber's `childLanes` do not overlap the render lanes, React skips the whole subtree. It clones the child fibers instead of visiting them.

The root chooses which lanes to render with `getNextLanes`. It then asks the Scheduler to run the work.

### The Scheduler and time slicing

The Scheduler is a separate package. It runs tasks with `MessageChannel` and gives each slice about 5 ms. The exact slice length is an internal detail and can change.

`shouldYield()` returns true when the slice ends. The work loop exits. The browser can paint and handle input. The Scheduler then queues the next slice.

Sync-lane renders do not yield. They run to completion. Concurrent renders, such as transitions, do yield.

### Interruption

Suppose a transition render is in progress and the user types. A new sync update arrives. React drops the work-in-progress tree and restarts from the root with the urgent lane. This is `prepareFreshStack`. The transition update stays in its queue and renders later.

This is safe only because render is pure. React may run your component body more than once and throw the result away. StrictMode double-invokes components in development to expose impure code.

## 9. Bailouts: skipping work

A re-render does not always mean a DOM update. React skips work in several ways:

- If a fiber has no pending lanes and its props are the same object, React bails out. It reuses the existing child fibers.
- If `childLanes` are empty, React skips the subtree entirely.
- `React.memo` adds a shallow props comparison before rendering.
- If a parent passes the same element object, such as `props.children`, that child does not rerender. Lifting content into `children` is a known way to limit rerenders.
- On a context change, React walks the subtree and marks only the consumers of that context.

Without these, a parent render would rerender all descendants. React rerenders children by default, because it cannot know if they depend on changed values. The React Compiler automates much of the memoization that you would otherwise write by hand.

## 10. The commit phase

The commit phase applies the result to the host. It is synchronous and cannot be interrupted. It uses `flags` and `subtreeFlags` to visit only fibers with work to do.

It has these steps:

1. Before mutation. React calls `getSnapshotBeforeUpdate` and schedules the passive effects.
2. Mutation. React applies the DOM changes: inserts, moves, attribute updates, and deletions. It runs `useLayoutEffect` cleanups, detaches refs, and runs unmount logic for deleted nodes.
3. Tree swap. React sets `root.current = finishedWork`. This happens after mutation and before layout. Unmount code sees the old tree and mount code sees the new one.
4. Layout. React runs `componentDidMount`, `componentDidUpdate`, and `useLayoutEffect`. It attaches refs. DOM reads here see the final layout, and a state update here forces a synchronous rerender before paint.
5. Passive effects. `useEffect` runs after paint in most cases. If the render came from a discrete event such as a click, React flushes passive effects at the end of the commit. React also flushes pending passive effects before the next render starts.

## 11. Suspense and transitions

When a component reads an unresolved promise, such as with `use`, React stops rendering that component. It unwinds to the nearest Suspense boundary and renders the fallback.

Transitions change this behavior. If a transition would hide content that is already visible, React keeps the old UI on screen. It renders the new tree in the background and commits it when ready. When the data resolves, React schedules a retry on a retry lane.

## 12. Reconciler versus renderer

The reconciler does not know about the DOM. It is the `react-reconciler` package. Each renderer, such as `react-dom` or React Native, supplies a host config with functions like `createInstance`, `appendChild`, `commitUpdate`, and `removeChild`.

The reconciler decides what changed. The renderer applies it. This split is why one algorithm drives the web, native, and custom targets.

## 13. What this means for your code

- Keep render pure. React will call it more than once and discard results.
- Put side effects in event handlers or effects, never in the render body.
- Use stable keys. They control identity and therefore state.
- Remember that state follows tree position and type.
- Do not nest component definitions.
- Use transitions for slow, non-urgent updates so urgent input stays responsive.
- Measure before you memoize. A rerender that produces no DOM change is often cheap.
