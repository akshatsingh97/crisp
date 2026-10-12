React reconciliation compares the previous element tree with the new one to decide what changes. Fiber is the data structure and work loop that runs this comparison in small, interruptible, prioritized units.

This describes React 18 and 19. Internal names and details change between versions, so treat them as a mental model, not a public API.

## The three trees

- Elements are plain objects from JSX, like `{type, props, key}`. They are cheap, immutable, and recreated on every render.
- Fibers are React's internal mutable work nodes. There is one per component instance or host node. They persist across renders and hold state.
- The host tree is the real output, such as DOM nodes or native views.

The flow is: your components return elements, the reconciler matches them to fibers, and the commit step mutates the host tree.

## Why Fiber replaced the stack reconciler

Before React 16, reconciliation was a recursive function on the JavaScript call stack. It could not pause once started. A large update blocked the main thread, so input lagged and animations dropped frames.

Fiber turns the recursion into a loop over a linked list of heap objects. React can stop after any unit of work, yield to the browser, then resume or discard the work.

This design enabled these goals:

- Pause, resume, and abort rendering.
- Assign priorities to updates.
- Reuse work from earlier renders.
- Return arrays and fragments from components.
- Support error boundaries and Suspense.

## The fiber node

Each fiber is a plain object. These are the main fields:

- `tag`: the kind of node, such as function component, class component, host component, or fragment.
- `type` and `key`: the identity used to match fibers across renders.
- `stateNode`: the DOM node or class instance.
- `return`, `child`, `sibling`, `index`: the parent, first child, next sibling, and position. These form the tree as a linked list.
- `pendingProps`, `memoizedProps`, `memoizedState`: new props, props from the last render, and state. For function components, `memoizedState` is the head of the hook list.
- `updateQueue`: queued state updates and effects.
- `flags` and `subtreeFlags`: the side effects needed, such as Placement, Update, ChildDeletion, Ref, and Passive.
- `lanes` and `childLanes`: pending update priorities on this fiber and on its descendants.
- `alternate`: the matching fiber in the other tree.

Traversal needs no recursion. Go to the child. If there is none, go to the sibling. If there is none, go to the parent's sibling.

## Double buffering

React keeps two fiber trees. The current tree matches what is on screen. The work-in-progress tree is the one React builds.

Each fiber points to its twin through `alternate`. React reuses the twin and copies new props onto it instead of allocating a new fiber.

When the work finishes and commits, React sets `root.current` to the new tree. The old tree becomes the scratch space for the next render. React can drop a half-built work-in-progress tree at any time without touching the screen.

## The render phase

An update starts when `setState` or a similar call marks lanes on the fiber and on every ancestor up to the root. React then schedules work on that root.

The work loop looks like this:

```js
// sync version
while (workInProgress !== null) performUnitOfWork(workInProgress);

// concurrent version
while (workInProgress !== null && !shouldYield()) performUnitOfWork(workInProgress);
```

Each unit has two halves, `beginWork` on the way down and `completeWork` on the way up.

`beginWork(current, workInProgress, lanes)` does this:

1. If a current fiber exists, the props are identical, context did not change, and no update is pending here, React tries a bailout. A bailout means reusing the existing result without re-rendering. If `childLanes` is also empty, React skips the whole subtree. Otherwise it clones the child fibers and continues.
2. If there is no bailout, React runs work based on `tag`. It calls the function component with hooks, or calls the class `render`.
3. It runs `reconcileChildren` to compare the returned elements with the current child fibers. It creates, reuses, or marks fibers for deletion.
4. It returns the first child as the next unit of work.

`completeWork` runs when a fiber has no child to descend into:

- For a host component on mount, it creates the DOM node and appends the already-built child nodes. The node is not yet in the document.
- For a host component on update, it works out which props changed and sets the Update flag.
- It bubbles flags and lanes up into `subtreeFlags` and `childLanes`.
- It moves to the sibling, or back to the parent if there is no sibling.

The render phase must be pure. React can call it more than once, abandon it, or restart it. StrictMode in development double-invokes it on purpose to expose impurity. Never mutate the DOM or external state during render.

## The diffing rules

A general tree diff costs O(n³). React uses two heuristics to get O(n):

1. Elements of different types produce different trees. If the type at a position changes, React unmounts the old subtree, loses its state, and builds a new one.
2. The `key` prop tells React which children are stable across renders.

For same-type elements, React keeps the fiber and updates props. A host element has its attributes and styles diffed. A component re-renders with its state intact.

### Child reconciliation

`reconcileChildFibers` handles the result by shape:

- Single element: React walks the old children to find a match on key and type. It reuses the match and deletes the other old children. If nothing matches, it deletes them all and creates a new fiber.
- Text: React reuses or creates a text fiber.
- Array or iterable: React runs `reconcileChildrenArray`, which has two passes.

Pass one walks the old and new lists together in order. It updates in place while keys match. A missing key matches by index. It stops at the first mismatch.

Then React checks two cases:

- If the new list ended, React deletes the remaining old fibers.
- If the old list ended, React creates fibers for the remaining new children.

Pass two handles the rest. React puts the remaining old fibers in a map by key, or by index if no key exists. For each remaining new child, it looks up the map, then reuses or creates a fiber. It tracks `lastPlacedIndex`. If a reused fiber had an old index below `lastPlacedIndex`, React marks it for Placement, which means a move. Otherwise it raises `lastPlacedIndex`. Unused map entries are deleted.

One consequence: moving an item later in the list is cheap, but moving the last item to the front moves every other item.

### Keys

Keys must be stable and unique among siblings. Index keys break when you reorder, insert, or delete. State then attaches to the wrong item. Changing a key on purpose forces a remount, which is a clean way to reset state.

State also depends on position. The same component type at the same place keeps its state. This code remounts `Child` on every parent render:

```jsx
function Parent() {
  const Child = () => <input />; // new function identity each render
  return <Child />;
}
```

Define components at module level to avoid this.

## State and hooks

A function component stores its hooks as a linked list in `memoizedState`. Hooks match by call order, which is the reason for the rules of hooks. Conditional hooks shift the list and corrupt state.

On mount, React uses a dispatcher that creates hook objects. On update, it uses a dispatcher that reads the existing list.

`setState` creates an update object with a lane and adds it to the hook's queue. During render, React processes only updates that belong to the lanes being rendered. It skips the rest and rebases them for later. If the queue is empty, React can compute the next state early. It then bails out with no render when `Object.is` finds the value unchanged.

## The commit phase

The commit phase is synchronous and cannot be interrupted. It starts when the work-in-progress tree is complete. React uses `subtreeFlags` to skip subtrees with no effects. It runs these steps:

1. Before mutation: `getSnapshotBeforeUpdate` runs.
2. Mutation: React inserts, updates, and deletes DOM nodes. It detaches refs and runs layout effect cleanups and `componentWillUnmount`. Insertion needs the next host sibling, so React searches for it.
3. React sets `root.current` to the finished tree. This happens after mutation and before layout, so lifecycle methods see the right tree.
4. Layout: `useLayoutEffect`, `componentDidMount`, and `componentDidUpdate` run. Refs attach. These run before the browser paints, so you can measure the DOM and re-render without flicker.
5. Passive effects: `useEffect` callbacks run later, after paint, through the scheduler. React flushes them before the next render starts. After a discrete event like a click, React 18 flushes them synchronously.

## Priorities: lanes and the scheduler

A lane is one bit in a 31-bit mask that labels a priority. Bitmasks let React group lanes and test membership cheaply. The main lanes are:

- SyncLane: discrete events like clicks and key presses.
- InputContinuousLane: hover, scroll, and drag.
- DefaultLane: updates from timers and network callbacks.
- TransitionLanes: updates inside `startTransition`.
- IdleLane and Offscreen lanes: lowest priority.

`getNextLanes` picks the highest priority pending lanes on the root. Lanes that wait too long expire and get promoted, which prevents starvation.

Sync lanes render without yielding and flush in a microtask. Other lanes render through the Scheduler package. It uses `MessageChannel` to run work in slices of about 5 ms and yield to the browser between slices. This is time slicing.

In React 18, only non-blocking lanes such as transitions are time-sliced. Default updates render without yielding. I am less sure of this detail than of the rest, so check it against your React version.

If a higher-priority update arrives mid-render, React discards the work-in-progress tree with `prepareFreshStack` and starts over at the higher priority. The interrupted update runs later. This is why render must be pure.

Related features build on lanes:

- Automatic batching: React 18 groups all updates in one tick into a single render per lane.
- `startTransition` and `useDeferredValue`: React keeps showing the old UI while it builds the new one in the background. Typing can interrupt that background render.

## Suspense and errors

When a component suspends, it throws a promise, or calls `use()` in React 19. React unwinds to the nearest Suspense boundary and shows its fallback. During a transition, React keeps the old UI instead of showing the fallback. When the promise settles, React retries the render.

Errors unwind the same way. `unwindWork` walks up to the nearest error boundary, which renders its fallback.

## Bailouts and memoization

By default, a parent re-render re-renders all its children. Each render creates new props objects, so React sees changed props. React does not compare props unless you opt in:

- `React.memo` compares props shallowly with `Object.is`.
- `PureComponent` and `shouldComponentUpdate` do the same for classes.
- `useMemo` and `useCallback` keep references stable so `memo` works.
- The React Compiler in React 19 adds this memoization automatically.

Context changes work differently. React walks the subtree and marks every consumer of the changed context for update. Intermediate components can bail out, but consumers still re-render.

Element identity also gives a free bailout. If a parent passes the same `children` element object as before, the child fiber sees identical `pendingProps` and skips the render. Moving state down into a smaller component, or passing content as `children`, uses this.

## Practical rules from the model

1. Use stable, unique keys. Never use the index for lists that reorder.
2. Never define components inside other components.
3. Keep render pure. Put side effects in event handlers or effects.
4. Use `key` to reset state on purpose.
5. Use `startTransition` for slow, non-urgent updates.
6. Profile with the React DevTools Profiler before you add memoization.
