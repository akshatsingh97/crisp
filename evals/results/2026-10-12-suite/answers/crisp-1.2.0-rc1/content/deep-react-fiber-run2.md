React reconciliation is the algorithm that compares the previous element tree with the next one to find the smallest set of changes. Fiber is the data structure and scheduling design that lets React run that algorithm in small, pausable, prioritized pieces. This explanation describes React 18 and 19. Internal names and details change between versions, but the model stays the same.

## 1. The problem Fiber solved

Before React 16, the "stack reconciler" walked the tree with plain recursion. It used the JavaScript call stack to remember where it was. A recursive walk cannot stop in the middle and resume later. A large update therefore blocked the main thread until it finished, and input and animation stalled.

Fiber replaced the call stack with a heap-allocated linked structure. React now controls the "stack frames" itself. It can pause, resume, abandon, or reorder work. That one change enables time slicing, priorities, Suspense, and transitions.

## 2. Elements, components, and instances

Three terms matter here.

- An element is a plain object like `{ type: 'div', props: {...}, key }`. JSX produces elements. They are cheap and immutable.
- A component is a function or class that returns elements.
- A fiber is the long-lived internal record for one component instance or one host node. Host node means a DOM element, in the browser.

Elements describe what the UI must look like now. Fibers hold what React knows about what is on screen. Reconciliation compares the new elements against the existing fibers.

## 3. The diffing heuristics

A general tree diff costs O(n³). React uses two assumptions to reach O(n).

1. Two elements of different types produce different trees. React destroys the old subtree and builds a new one.
2. Keys hint which children are stable across renders.

Rule 1 has a direct effect. If the type at a position changes from `<div>` to `<span>`, or from `<A>` to `<B>`, all descendants unmount. Their state is lost. If the type stays the same, React keeps the fiber and updates its props.

React also compares position. State belongs to a position in the tree, not to a variable name. The same component type at the same position keeps its state.

## 4. Keys

Keys matter when a parent has multiple children. Without keys, React matches children by index. Inserting an item at the front makes every following index shift. React then updates every child instead of inserting one.

With stable keys, React matches children by identity. It can move existing fibers instead of recreating them. Use ids from your data. Do not use random values, because a new key each render forces a remount. Index keys are safe only for static lists that never reorder.

A key also works as a reset button. Changing the key of a component forces React to unmount it and mount a fresh instance.

## 5. Anatomy of a fiber

A fiber is a JavaScript object. These fields carry the core meaning.

- `tag`: the kind of fiber, such as function component, class component, host component, or Suspense boundary.
- `type` and `key`: the identity used for matching.
- `stateNode`: the DOM node for host fibers, or the instance for class components.
- `return`, `child`, `sibling`: pointers to the parent, first child, and next sibling. They form a tree as a linked list.
- `pendingProps` and `memoizedProps`: the incoming props and the props used in the last render.
- `memoizedState`: for function components, the head of the hooks linked list.
- `updateQueue`: pending updates, such as class setState calls or effect lists.
- `flags` and `subtreeFlags`: bitmasks that record side effects needed on this fiber and below it.
- `lanes` and `childLanes`: bitmasks that record pending update priorities on this fiber and below it.
- `alternate`: the paired fiber in the other tree. See the next section.

## 6. Two trees and double buffering

React keeps two fiber trees. The current tree matches what is on screen. The work-in-progress tree is the draft that React builds during a render.

Each fiber in one tree points to its twin through `alternate`. React reuses these twins instead of allocating new objects each render. The function `createWorkInProgress` takes a current fiber, reuses its alternate if one exists, and copies over fresh props.

When the draft is complete and committed, React flips one pointer: `root.current` now refers to the draft. The old current tree becomes the spare for the next render. This is double buffering, the same technique graphics code uses.

## 7. The render phase

The render phase builds the work-in-progress tree. It must be pure. React can run it multiple times, pause it, or throw it away. StrictMode in development calls components twice to expose impure code.

The loop is simple:

```js
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
}
```

Each call to `performUnitOfWork` processes one fiber. The traversal is depth-first and has two halves.

1. `beginWork(fiber)` runs on the way down. It renders the component, reconciles its children, and returns the first child.
2. If a fiber has no child, React calls `completeWork` on it. This runs on the way up.
3. After completing a fiber, React moves to its sibling. If no sibling exists, it completes the parent and continues.

Because the position lives in a variable (`workInProgress`) and not on the call stack, React can stop between any two fibers. In concurrent mode, `shouldYield` returns true after about 5 ms. React then returns control to the browser and resumes later.

### What beginWork does

For each fiber, `beginWork` first decides whether it can skip work. This is the bailout check. It can skip when all of these hold:

- The old and new props are the same object (`===`).
- No context this fiber reads has changed.
- No update with a matching lane is pending on this fiber.

If the fiber itself has no work, React checks `childLanes`. If no descendant has pending work either, it skips the whole subtree and reuses it. If a descendant does have work, React clones the child fibers and keeps walking. This is why `React.memo` helps. It makes the props comparison shallow instead of reference-based.

If the fiber cannot bail out, React runs the component. Function components execute with hooks. Class components call `render`. The result is a set of new elements, which go to child reconciliation.

### What completeWork does

For host components, `completeWork` creates the DOM node on first mount. It appends all child DOM nodes to it, off screen. It then sets the initial properties.

On update, it compares old and new props and marks the fiber with an Update flag if anything changed. Finally it bubbles up flags and lanes. Each fiber merges its children's `flags` into its own `subtreeFlags`, and does the same for `childLanes`. The commit phase uses these to skip clean subtrees quickly.

## 8. Child reconciliation in detail

After a component returns elements, React matches them against the existing child fibers. The behavior depends on the shape of the result.

For a single child, React compares key and type with the existing child. On a match, it reuses the fiber and updates its props. On a mismatch, it marks the old fiber for deletion and creates a new one.

For an array of children, React runs a two-pass algorithm.

1. Walk the old fibers and the new elements in parallel by position. Stop at the first pair whose keys differ.
2. If the new list ended, mark all remaining old fibers for deletion. If the old list ended, create fibers for all remaining new elements.
3. Otherwise, put the remaining old fibers in a map keyed by `key` (or by index when no key exists).
4. Walk the remaining new elements. Look up each one in the map. Reuse the fiber if found, and create one if not.
5. Track `lastPlacedIndex`, the highest old index seen so far. If a reused fiber had an old index below that value, mark it for Placement, which means a move. Otherwise raise `lastPlacedIndex`.
6. Delete every fiber left in the map.

This design has one known weakness. Moving the last item to the front marks every other item as moved. Moving the first item to the back costs only one move. React does not compute a minimal edit script. It trades optimality for speed and simplicity.

## 9. Side effects as flags

React does not run DOM changes during render. It records them as bit flags on fibers: Placement, Update, ChildDeletion, Ref, Snapshot, Passive, Layout, and others. Deletions are stored in a `deletions` array on the parent.

Older versions kept a linked "effect list". Modern versions use `subtreeFlags` instead. The commit phase walks the tree and skips any subtree whose `subtreeFlags` is empty.

## 10. The commit phase

The commit phase applies the draft to the host. It is synchronous and cannot be interrupted. Users must never see a half-applied tree.

It has three sub-phases, in this order.

1. Before mutation: React calls `getSnapshotBeforeUpdate` on class components. It reads layout information here, before the DOM changes.
2. Mutation: React performs placements, updates, and deletions. It runs cleanups for layout effects and `useInsertionEffect`, calls `componentWillUnmount`, and detaches refs.
3. Layout: React runs `componentDidMount`, `componentDidUpdate`, `useLayoutEffect` callbacks, and attaches refs.

Between steps 2 and 3, React sets `root.current` to the finished tree. During `componentWillUnmount`, `current` still points to the old tree. During layout effects, it points to the new tree.

Passive effects (`useEffect`) run after commit. Usually they run after the browser paints. If the render came from a discrete event such as a click, React flushes them synchronously at the end of commit. React always flushes pending passive effects before it starts the next render.

## 11. Hooks and state storage

Each function component fiber stores its hooks as a singly linked list in `memoizedState`. Each node holds that hook's state, queue, and a pointer to the next hook. On every render, React walks this list in order.

This is why the Rules of Hooks exist. Hooks have no names. Their identity is their call order. A conditional hook shifts the list and attaches state to the wrong hook.

React swaps the hooks implementation (the "dispatcher") depending on context. On mount it uses allocating versions. On update it uses versions that read from the existing list. Calling a hook outside a component finds no valid dispatcher, which produces the familiar error.

When you call a state setter, React does the following.

1. It creates an update object and picks a lane for it based on the current event priority.
2. It appends the update to the hook's queue.
3. It marks the fiber and its ancestors with the lane, using `lanes` and `childLanes`.
4. It schedules a render for the root.

There is one shortcut. If the fiber has no pending work, React computes the next state eagerly. If the result equals the current state under `Object.is`, React skips the render entirely.

## 12. Lanes and scheduling

Fiber attaches a priority to every update. Modern React represents priorities as lanes, bits in a 31-bit integer. A lane set is a bitmask, so React can combine, test, and subtract priorities with fast bit operations.

The main lanes, from highest to lowest priority, are:

- SyncLane: discrete events such as clicks and key presses.
- InputContinuousLane: continuous events such as drag and scroll.
- DefaultLane: updates outside any special context, such as a `setTimeout` callback.
- TransitionLanes: updates wrapped in `startTransition`.
- IdleLane and Offscreen lanes: low-value background work.

The root tracks `pendingLanes`. When React schedules a render, `getNextLanes` picks the highest-priority group to work on. Sync work runs in a microtask. Other work goes through the `scheduler` package, which uses `MessageChannel` to yield to the browser between slices.

### Interruption and restart

Suppose a transition render is in progress and a click arrives. The click has a higher-priority lane. React abandons the draft tree by resetting `workInProgress` to the root. It renders the urgent update first and commits it. Later, it restarts the transition from scratch.

Restarting from scratch is safe because render is pure and nothing touched the DOM. It does mean that the render phase may repeat work. Rendering the transition twice is the cost of keeping input responsive.

### Update queues and rebasing

A low-priority render skips high-priority updates it does not own. A high-priority render skips low-priority ones. If React skipped an update, it keeps it in the queue and rebases later updates on top. Updates are applied in insertion order within the lanes being processed. The final state therefore matches what sequential processing would give, even though intermediate renders showed different states.

### Starvation

Low-priority work could wait forever under constant urgent updates. React assigns each lane an expiration time. When a lane expires, React treats it as urgent and renders it without time slicing.

## 13. Concurrent features built on Fiber

- Time slicing: the render loop yields every few milliseconds.
- Transitions: `startTransition` marks updates as low priority. The old UI stays visible while the new tree renders in the background. `isPending` reports that state.
- `useDeferredValue`: React first renders with the old value at urgent priority. It then renders again with the new value at low priority.
- Suspense: a component that is not ready throws a promise (or calls `use` on one). React catches it and finds the nearest Suspense boundary. It renders the fallback there. When the promise settles, React retries the suspended subtree.
- Offscreen and Activity: React can keep a hidden subtree's fibers and state alive while it skips or lowers the priority of rendering it.

Concurrent rendering has one cost. External mutable stores can change between slices and show inconsistent values ("tearing"). `useSyncExternalStore` solves this by forcing a synchronous, consistent render for such stores.

## 14. Context propagation

When a context provider's value changes, React walks the provider's subtree. It looks for fibers that read that context and marks them with the update lane. It also marks their ancestors' `childLanes`. This lets those consumers re-render even when a `React.memo` parent blocks normal prop-driven updates.

## 15. Practical consequences

- Define components at module level. A component defined inside another component gets a new type on every render. React sees a different type and remounts the subtree each time.
- Keep component types and positions stable if you want to keep state. Switch to a new key if you want to reset it.
- Use stable, unique keys for lists.
- Keep render pure. Fiber depends on that to pause, restart, and double-render safely.
- Use `memo`, `useMemo`, and `useCallback` to preserve reference equality when profiling shows a cost. They help the bailout check in `beginWork`. The React Compiler can automate much of this.
- Move state down or lift content up. Rendering is top-down, so state closer to where it is used limits the subtree that React must check.
- Use transitions for expensive, non-urgent updates. They let urgent input interrupt the work.

## 16. The full flow in one view

1. An event or call to a state setter creates an update with a lane.
2. React marks the fiber path to the root and schedules the root.
3. The render phase builds the work-in-progress tree. It runs `beginWork` down and `completeWork` up, one fiber at a time, and can yield between fibers.
4. Child reconciliation reuses, moves, creates, or deletes fibers and records flags.
5. The commit phase runs before-mutation, mutation, and layout steps synchronously, and flips `root.current`.
6. Passive effects run after paint, or at the end of commit for discrete events.

If you want, I can go deeper on one part. The hooks implementation, the Suspense unwinding logic, and the lane selection code are the three areas with the most detail left.
