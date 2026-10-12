Reconciliation is the algorithm that compares the previous UI description with the next one and finds the smallest set of changes. Fiber is the data structure and execution model that runs that algorithm in small, pausable, prioritized units. This answer follows the React 18 and 19 source. Internal names change between versions, so treat function and lane names as approximate.

## Vocabulary

- Element: a plain, immutable object that JSX produces, shaped like `{ type, props, key, ref }`. It describes what to render. It does nothing itself.
- Component: a function or class that takes props and returns elements.
- Fiber: a mutable JavaScript object. React creates one per component instance, host node, or special node such as Fragment or Suspense. It stores props, state, links to other fibers, and pending work.
- Host node: a node in the target platform, such as a DOM element.
- Reconciler: the shared core in the `react-reconciler` package. A renderer such as `react-dom` or `react-native` supplies platform functions like `createInstance`, `appendChild`, and `commitUpdate`.

## Why Fiber exists

Before React 16, React used a stack reconciler. It called itself recursively down the tree. The JavaScript call stack cannot pause, so a large update blocked the main thread until it finished. At 60 Hz, the browser has about 16 ms per frame. A long render dropped frames and delayed input.

Fiber reimplements the stack as a linked list of heap objects. React now controls the "stack" itself. This gives React these abilities:

- Pause work and resume it later.
- Abandon work that is no longer needed.
- Give each update a priority.
- Reuse work done earlier.
- Return arrays and fragments from components.
- Support error boundaries and Suspense.

Fiber shipped in React 16 in 2017. React 18 made concurrent rendering available through opt-in APIs such as `startTransition`.

## The fiber node

A simplified fiber looks like this:

```js
{
  // identity
  tag, key, elementType, type, stateNode,
  // tree links
  return,   // parent
  child,    // first child
  sibling,  // next sibling
  index,    // position among siblings
  // data
  pendingProps, memoizedProps, memoizedState, updateQueue,
  // work tracking
  lanes, childLanes,
  flags, subtreeFlags, deletions,
  // double buffering
  alternate,
  ref, dependencies, mode
}
```

- `tag` says what kind of fiber it is: function component, class, host component, Suspense, and so on.
- `stateNode` holds the class instance or DOM node.
- `return`, `child`, and `sibling` form a singly linked tree. Every fiber has at most one `child` pointer. Siblings chain through `sibling`.
- `pendingProps` are the new props for this render. `memoizedProps` are the props from the last completed render.
- For function components, `memoizedState` points to the head of the hooks linked list. For class components, it holds the state object.
- `lanes` marks pending work on this fiber. `childLanes` marks pending work anywhere below it.
- `flags` record the side effects this fiber needs at commit, such as Placement, Update, or Ref. `subtreeFlags` summarize the flags of all descendants.
- `alternate` points to the twin fiber in the other tree.

## Two trees

React keeps two fiber trees:

- The current tree represents what is on screen now.
- The workInProgress tree is the draft React builds during a render.

Each current fiber links to its workInProgress twin through `alternate`. React reuses these two objects across renders instead of allocating new ones. This is double buffering. The function `createWorkInProgress` clones or recycles the twin.

The root object, called FiberRoot, holds a `current` pointer to the top fiber. During render, React never touches the current tree or the DOM. If React must interrupt a render, it discards the draft and starts again. Only the commit phase swaps the pointer: `root.current = finishedWork`.

## Phase 1: the render phase

The render phase builds the workInProgress tree and decides what changed. It has no visible side effects. In concurrent mode, React can pause, restart, or throw it away. Because of this, render code must be pure.

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

One "unit of work" is one fiber. React checks `shouldYield()` between fibers. That check is where it can hand control back to the browser.

### Traversal order

The traversal is depth-first without recursion:

1. `beginWork` runs on a fiber and returns its first child.
2. React moves to that child and repeats until it reaches a fiber with no children.
3. `completeWork` runs on that leaf.
4. If the fiber has a sibling, React moves to the sibling and starts `beginWork` there.
5. If not, React moves up through `return` and runs `completeWork` on the parent.

For `<A><B/><C/></A>`, the order is: begin A, begin B, complete B, begin C, complete C, complete A. The loop state is only a pointer to the current fiber. That is why React can stop and resume at any fiber boundary.

### beginWork

`beginWork` runs top-down. It does the following:

1. It checks for a bailout. If props are identical by reference, no context changed, and no update is scheduled on this fiber, it tries to skip the work.
2. Otherwise it switches on `tag`.
3. For a function component, it calls `renderWithHooks`, which runs your function and gets new elements.
4. For a class, it runs lifecycle methods such as `getDerivedStateFromProps` and `render`.
5. For a host component, it reads `props.children`.
6. It then calls `reconcileChildren` to diff the returned elements against the existing child fibers.

### completeWork

`completeWork` runs bottom-up. For a new host component, it creates the DOM node in memory and attaches the already-built child nodes. It does not attach it to the page. For an existing host component, it compares old and new props and flags an Update if anything changed.

It also bubbles information upward. A parent's `subtreeFlags` and `childLanes` combine those of its children. This summary lets later steps skip subtrees that have no work.

## The diffing algorithm

A fully general tree diff costs O(n³). React uses two heuristics to get O(n):

1. Elements of different types produce different trees. React does not try to match them.
2. A `key` prop identifies which children are stable across renders.

### Rules at one position

- If the type differs, React unmounts the old subtree and mounts a new one. All state in the old subtree is lost.
- If the type is the same and it is a host element, React keeps the DOM node and updates only the changed attributes.
- If the type is the same and it is a component, React keeps the fiber, updates props, and re-renders it. State persists.

Position in the tree is part of identity. The same component at the same position keeps its state. A component that moves to a new position remounts.

### Single child

For one returned element, React compares key and type with the existing child. If both match, it reuses the fiber and deletes any extra siblings. If not, it marks the old child for deletion and creates a new fiber.

### Arrays of children

`reconcileChildrenArray` makes up to two passes:

1. Walk the old fibers and new elements in lockstep. If keys match, reuse the fiber. Stop at the first key mismatch.
2. If the new list ends first, delete the remaining old fibers.
3. If the old list ends first, create fibers for the remaining new elements.
4. Otherwise, put the remaining old fibers in a Map keyed by `key` (or index when there is no key).
5. Walk the remaining new elements. Look each one up in the Map. Reuse the match, or create a new fiber.
6. Delete any old fibers left in the Map.

To decide moves, React tracks `lastPlacedIndex`. For each reused fiber, it reads the fiber's old index. If the old index is below `lastPlacedIndex`, the fiber must move, so React flags Placement. Otherwise React raises `lastPlacedIndex` to that old index.

This has a known quirk. Moving the first item to the end is cheap, because only that item moves. Moving the last item to the front is expensive, because every other item has a lower old index and gets flagged to move.

### Key pitfalls

- Index keys break when the list reorders, inserts, or deletes. State and DOM values (such as input text) stick to the position, not the data.
- Missing keys cause a dev warning. React falls back to index.
- A random key such as `Math.random()` forces a remount on every render.
- Changing a key on purpose is a valid way to reset a component's state.
- A component defined inside another component's body gets a new function identity each render. React sees a new type and remounts it every time. Define components at module level.

## Hooks and state storage

For a function component, `fiber.memoizedState` is the head of a linked list of hook objects. Each call to a hook in your function uses the next node in order. That is the technical reason for the rules of hooks: React matches hooks to nodes by call order, not by name.

A hook node holds `memoizedState`, `baseState`, `baseQueue`, `queue`, and `next`. React switches dispatchers between mount and update. On mount, `useState` creates the node. On update, it reads the existing node.

When you call `setState`, React does this:

1. It creates an update object and assigns it a lane (see below).
2. It adds the update to the hook's queue, which is a circular list.
3. It marks the fiber's `lanes` and walks up the `return` chain, marking each ancestor's `childLanes`.
4. It schedules a render on the root.

An eager-state check exists. If the fiber has no pending work and the new state equals the old by `Object.is`, React can skip scheduling. Sometimes React still renders the component once more and then bails out before committing.

## Lanes: priorities

A lane is one bit in a 31-bit bitmask. A set of lanes is a bitwise OR of lanes. Examples include SyncLane, InputContinuousLane, DefaultLane, several TransitionLanes, RetryLanes, and IdleLane.

The lane for an update comes from context. A click handler yields a discrete-event priority, which maps to SyncLane. A plain update outside any event gets DefaultLane. An update inside `startTransition` gets a transition lane.

On each render, React picks the highest-priority pending lanes with `getNextLanes`. It processes only updates that include those lanes. This has several consequences:

- Urgent updates such as typing can interrupt a running transition render. React discards the draft and restarts with the urgent lane.
- Lower-priority updates that were skipped stay in the queue.
- Starvation protection assigns each pending lane an expiration time. When a lane expires, React treats it as urgent, so it cannot wait forever.
- Entanglement links lanes that must commit together, such as related transition updates.

### Update rebasing

State must be correct even when updates apply out of order. Suppose a low-priority update A is skipped and a high-priority update B applies. React keeps the state from before A as a base. It then replays A and B in their original order on the next render. The final state equals what a sequential application would produce. The intermediate screen can show B without A.

### Batching

Since React 18, all updates in the same tick batch into one render, including those in promises, timeouts, and native handlers. Use `flushSync` to force a synchronous flush when you must read the DOM right after an update.

## The Scheduler

The `scheduler` package is separate from the reconciler. It keeps a priority queue (a min-heap) of tasks and runs them in macrotasks. In browsers it uses `MessageChannel` to get a new task quickly. It falls back to `setImmediate` or `setTimeout` elsewhere.

Time slicing works as follows. The Scheduler gives the work loop a slice of about 5 ms. `shouldYield()` returns true when that time is up. React then stops after the current fiber, returns control to the browser for input and paint, and schedules a continuation.

Not all renders time-slice. In React 18, blocking lanes such as SyncLane and DefaultLane render without yielding. Transitions, retries, and idle work use `workLoopConcurrent` and can yield. Synchronous work is flushed in a microtask at the end of the event. I am less sure of the exact lane groupings in React 19, so check the source if this matters to you.

## Phase 2: the commit phase

The commit phase applies the finished tree to the host. It is synchronous and cannot be interrupted. This avoids showing half-applied UI. React walks the tree using `flags` and `subtreeFlags`, and skips any subtree whose `subtreeFlags` are empty. (React 16 and 17 used a linked effect list instead. React 18 replaced it with flag traversal.)

The commit has these steps:

1. Before mutation: call `getSnapshotBeforeUpdate`. Schedule passive effects.
2. Mutation: apply the flags.
   - Placement inserts or moves DOM nodes.
   - Update applies prop changes to host nodes.
   - ChildDeletion unmounts the subtree. This runs class `componentWillUnmount`, layout effect cleanups, detaches refs, and removes DOM nodes.
3. Pointer swap: set `root.current = finishedWork`. The workInProgress tree is now current.
4. Layout: run `componentDidMount`, `componentDidUpdate`, and `useLayoutEffect`. Attach refs. These run synchronously before the browser paints. State updates scheduled here flush synchronously before paint.
5. Passive effects: run `useEffect` callbacks after paint. First React runs all cleanups, then all new effect functions. If the render came from a discrete event such as a click, React flushes these effects synchronously at the end of the commit.

The swap sits between mutation and layout on purpose. `componentWillUnmount` sees the old tree. `componentDidMount` and layout effects see the new one.

## Bailouts

A bailout is how React avoids re-rendering. In `beginWork`, React compares `oldProps` and `newProps` by reference. If they match, no context changed, and the fiber has no pending lanes, it bails out. It then checks `childLanes`:

- If no descendant has pending work, React returns `null` and skips the whole subtree.
- If descendants have pending work, React clones the child fibers and continues down.

This explains the default behavior. When a parent re-renders, JSX creates new props objects for every child. References differ, so every child re-renders too. Three tools change that:

- `React.memo` wraps a component with a shallow props comparison.
- `useMemo` and `useCallback` keep references stable so memo comparisons succeed.
- Context is separate. When a provider's value changes, React walks the subtree, finds consumers, and marks their lanes. Memoized components in between do not block that.

The React Compiler, available since React 19, inserts this memoization automatically at build time.

## Suspense and error handling

A component suspends by throwing a promise, which `use` and Suspense-aware libraries do internally. The reconciler catches it in `throwException`. It finds the nearest Suspense boundary and marks it to show its fallback. It attaches a callback to the promise that schedules a retry lane when the promise resolves.

In a transition, React avoids hiding content that is already visible. It keeps the old UI on screen and reports the transition as pending. A new fallback shows only for boundaries that are not yet revealed.

Error boundaries use the same mechanism. A thrown error unwinds to the nearest class with `getDerivedStateFromError` or `componentDidCatch`. React re-renders that boundary with its error state. After an error during a concurrent render, React first retries the render synchronously.

Hidden subtrees (the Offscreen mechanism, exposed as `<Activity>` in newer versions) can keep their fiber state while not displayed.

## Related behaviors

- Strict Mode in development calls component functions twice and double-mounts effects. This exposes impure render code and missing cleanups. It is a direct result of render being repeatable.
- External mutable stores can change while a concurrent render is paused. Different components can then read different values, which is called tearing. `useSyncExternalStore` prevents this. It checks consistency before commit and falls back to a synchronous render.

## End-to-end example

A user clicks a button that calls `setCount(c => c + 1)`:

1. The click is a discrete event, so the update gets SyncLane.
2. React enqueues the update on the hook and marks lanes on the fiber and `childLanes` on every ancestor.
3. React schedules a sync render on the root and flushes it in a microtask.
4. The work loop starts at the root and calls `beginWork` down the path. Fibers with no matching lanes and equal props bail out.
5. On the counter's fiber, React runs the function, applies the queued update, and gets new elements.
6. `reconcileChildren` diffs those elements against the old child fibers and flags changes.
7. `completeWork` runs on the way back up and bubbles flags and lanes.
8. Commit applies the Update flag to the DOM text node, swaps `root.current`, and runs layout effects.
9. The browser paints. Then passive effects run.

## Practical consequences

- Keep render pure. Do not mutate, read refs for output, or start side effects during render. React can run it many times or discard it.
- Use stable, data-derived keys. Avoid index keys on reorderable lists.
- Define components at module scope, never inside other components.
- Keep state close to where it is used. A state change re-renders its owner and, by default, that owner's children.
- Wrap slow, non-urgent updates in `startTransition` or use `useDeferredValue`. This lets urgent input interrupt them.
- Use the React DevTools Profiler to confirm which fibers render and why. Fix measured problems before adding `memo` everywhere.

React 19 added Actions, `use`, ref as a prop, and the compiler. These sit on top of the same fiber and lane model described here.
