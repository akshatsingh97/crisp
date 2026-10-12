React reconciliation is the process that compares the last rendered tree with a new one and finds the minimum changes for the host (the DOM). Fiber is the data structure and work loop that runs this process in small, pausable units. Details below follow React 18 and 19. Internal names can change between versions.

## 1. The problem Fiber solves

Before React 16, the "stack reconciler" used plain recursion. It walked the whole tree in one uninterrupted call stack.

- A large update blocked the main thread. Typing, animation, and scrolling froze until it finished.
- The JavaScript call stack cannot be paused and resumed later. It also cannot be thrown away halfway.
- React could not give urgent work (a keystroke) priority over slow work (a big list render).

Fiber replaced the call stack with a heap-allocated linked structure. React now controls the "stack" itself. It can pause, resume, reprioritize, or abandon work.

## 2. Elements, components, and fibers

Three different things share similar names.

- Element: a plain object that describes UI, such as `{ type: 'div', props, key }`. JSX creates elements. They are cheap and immutable.
- Component instance: the logical thing that holds state across renders. For function components, this state lives in hooks.
- Fiber: an internal mutable object, one per component instance or host node. It holds the work to do and the results of past work.

A fiber is both a unit of work and a node in the tree. React creates fibers from elements during render and reuses them across renders.

## 3. What a fiber contains

Simplified, a fiber has these fields.

```js
{
  // identity
  tag,            // FunctionComponent, HostComponent, ClassComponent, Suspense, ...
  key,
  elementType,
  type,           // the function, class, or 'div'
  stateNode,      // DOM node or class instance

  // tree links
  return,         // parent
  child,          // first child
  sibling,        // next sibling
  index,          // position among siblings

  // data
  pendingProps,   // new props for this render
  memoizedProps,  // props used in the last render
  memoizedState,  // state from last render (hooks list for function components)
  updateQueue,    // queued updates, effects, callbacks

  // work tracking
  flags,          // side effects this fiber needs (Placement, Update, Deletion, ...)
  subtreeFlags,   // union of flags in the subtree
  lanes,          // priority of pending work on this fiber
  childLanes,     // priority of pending work below this fiber

  alternate       // the other version of this fiber
}
```

The tree uses `child`, `sibling`, and `return` pointers. It does not use arrays of children. This makes the tree a singly linked structure that React can walk iteratively without recursion.

## 4. Two trees: current and work-in-progress

React keeps two fiber trees.

- The current tree matches what is on screen now.
- The work-in-progress tree is the draft React builds during a render.

Each fiber points to its twin through `alternate`. This technique is called double buffering.

1. React starts a render by cloning or reusing the alternate fibers. It calls `createWorkInProgress(current, pendingProps)`.
2. It builds the work-in-progress tree and does all the diffing there.
3. When it finishes and commits, the root pointer `FiberRoot.current` flips to the new tree. The old tree becomes the spare for the next render.

This is why React can abandon a render safely. The current tree is never touched until commit. Reusing the two objects also avoids allocating new fibers on every update.

## 5. The reconciliation algorithm

A full tree diff is O(n³). React instead uses a heuristic O(n) algorithm based on two assumptions.

1. Elements of different types produce different trees.
2. A `key` prop tells React which children are stable across renders.

### Comparing a single element

For one fiber and its new element, React compares `type` (and `key`).

- Same type and key: reuse the fiber. Keep its state and DOM node. Update props and recurse into children.
- Different type: destroy the old subtree and mount a new one. All state below is lost. React unmounts the old DOM node and creates a new one.

This is why defining a component inside another component breaks state. The inner function gets a new identity on every render, so React sees a new type each time.

```jsx
function Parent() {
  const Child = () => <input />;   // new type every render: remounts, loses state
  return <Child />;
}
```

### Comparing children

The function `reconcileChildFibers` has branches by the shape of the new children: a single element, text, an array, or an iterable.

For arrays, `reconcileChildrenArray` runs these passes.

1. First pass: walk old fibers and new children together by index. Stop at the first pair whose keys differ. Reuse any fiber with a matching key and type.
2. If new children run out: mark the remaining old fibers for deletion.
3. If old fibers run out: create fibers for the remaining new children and mark them for placement.
4. Otherwise: put the remaining old fibers in a map keyed by `key` (or by index if no key). Then walk the remaining new children. Look up each one in the map. Reuse the match, or create a new fiber.
5. Track `lastPlacedIndex`. If a reused fiber's old index is lower than `lastPlacedIndex`, it must move, so React flags it with `Placement`. Otherwise it stays in place.
6. Delete any old fibers left in the map.

React only moves nodes forward. Moving the last item to the front is therefore expensive, because every other item gets flagged to move. Moving the first item to the end is cheap.

### Why keys matter

- Stable, unique keys let React match items across reorders, insertions, and deletions. State stays with the right item.
- Using the array index as key works for static lists. It breaks for lists that reorder or insert at the front. Input values and component state attach to the wrong item.
- If you omit keys, React falls back to index and warns in development.
- A changed key forces a remount. You can use this on purpose to reset a component's state: `<Form key={userId} />`.

## 6. The render phase

The render phase is pure computation. It builds the work-in-progress tree and records what must change. It does not touch the DOM. It can be paused, restarted, or discarded.

### The work loop

```js
function workLoopSync() {
  while (workInProgress !== null) performUnitOfWork(workInProgress);
}
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) performUnitOfWork(workInProgress);
}
```

`performUnitOfWork` processes one fiber.

```js
function performUnitOfWork(unitOfWork) {
  const next = beginWork(current, unitOfWork, renderLanes);
  unitOfWork.memoizedProps = unitOfWork.pendingProps;
  if (next === null) completeUnitOfWork(unitOfWork);
  else workInProgress = next;
}
```

The traversal is depth-first.

1. `beginWork` runs going down. It returns the first child, or null at a leaf.
2. At a leaf, `completeWork` runs. Then React moves to the sibling and does `beginWork` on it.
3. When there are no more siblings, React goes up through `return` and runs `completeWork` on the parent.

Each fiber gets `beginWork` on the way down and `completeWork` on the way up.

### beginWork

`beginWork` decides what to do for a fiber based on its `tag`.

- Function component: call `renderWithHooks`. This runs your function, processes hooks, and returns children elements.
- Class component: call lifecycle methods like `getDerivedStateFromProps` and `render`.
- Host component (`div`): no user code to run. It only reconciles its children.
- Context provider, Suspense, memo, and others have their own handlers.

After getting new children, it calls `reconcileChildren`. That is the diff described above.

### Bailouts

Before doing work, `beginWork` checks if it can skip the fiber.

- If `oldProps === newProps` (same reference), no context change, and no pending update lanes, React can bail out.
- If the subtree also has no pending work (`childLanes` has no matching lanes), React skips the whole subtree. It returns null and reuses the child fibers.
- If only the subtree has work, React clones the children and continues below without re-rendering this component.

This is why a parent re-render re-renders all children by default. New JSX creates new props objects, so the reference check fails. `React.memo` adds a shallow props comparison to restore the bailout. The React Compiler can add this memoization automatically.

### completeWork

On the way up, `completeWork` finishes each fiber.

- For host components on mount, it creates the DOM node, appends child DOM nodes, and sets initial properties. The nodes are not attached to the document yet.
- On update, it compares old and new props, and stores a list of changed properties in `updateQueue`. It flags the fiber with `Update`.
- It bubbles flags up. `bubbleProperties` merges the children's `flags` and `lanes` into the parent's `subtreeFlags` and `childLanes`.

The commit phase later uses `subtreeFlags` to skip subtrees with no effects.

## 7. Hooks on fibers

Hooks work because each function component fiber stores a linked list in `memoizedState`. Each node in the list is one hook, in call order.

- On mount, `useState` creates a hook object and appends it to the list.
- On update, React reads the next node in the list. It uses call order to match each call to its slot.

This is the reason for the Rules of Hooks. Calling hooks conditionally changes the order. The slots then no longer match, and state attaches to the wrong hook.

Key hook internals:

- `useState` and `useReducer` store a queue of pending updates. On render, React applies the queue to the base state. Updates with lower priority than the current render stay in the queue and are applied later.
- `useEffect` pushes an effect object onto `updateQueue`. It also sets a flag (`Passive`) on the fiber. The effect runs after commit.
- `useMemo` and `useCallback` store `[value, deps]` and compare deps with `Object.is`.
- `useRef` stores a stable `{ current }` object.

The dispatcher (the object that implements the hooks) switches between mount, update, and invalid-context versions during a render. Calling a hook outside a render hits the invalid version and throws.

## 8. How an update starts

When you call `setState`:

1. `dispatchSetState` creates an update object and picks a lane for it based on the current priority (event type, transition, and so on).
2. It may compute the new state eagerly. If the queue is empty and the new state equals the old, React skips scheduling. This is the eager bailout.
3. It appends the update to the hook's queue.
4. `markUpdateLaneFromFiberToRoot` walks up the `return` pointers. It sets `lanes` on the fiber and `childLanes` on each ancestor, up to the root.
5. `ensureRootIsScheduled` schedules a render for that root through the Scheduler.

The marks on ancestors are what let `beginWork` find the one changed component without re-rendering the whole tree. It follows `childLanes` down and bails out on everything else.

## 9. Lanes: priority and batching

React 18 replaced the older expiration-time model with lanes. A lane is one bit in a 31-bit integer. A set of lanes is a bitmask.

Main lanes, from most to least urgent:

- `SyncLane`: discrete events like clicks and key presses.
- `InputContinuousLane`: scroll, drag, mouse move.
- `DefaultLane`: updates from timers, network callbacks, and similar.
- `TransitionLanes`: updates wrapped in `startTransition` or from `useDeferredValue`. There are several, so separate transitions can stay separate.
- `IdleLane`, and `OffscreenLane` for hidden content.

Bitmasks make several operations cheap: merging lanes, checking overlap, and picking the highest priority bit.

Batching follows from this design. All updates in the same lane within one event become one render. React 18 batches automatically, even in promises and timeouts.

Two behaviors to know:

- Urgent updates can interrupt a transition render. React throws away the in-progress tree, renders the urgent update, and then restarts the transition from the fresh state.
- Updates are rebased. If a low-priority update is skipped, later updates that depend on it stay queued. When the low-priority one finally renders, React replays them in order. The final state is the same as if everything had run in order.

Lanes that wait too long get promoted so they cannot starve. React tracks this with expiration times per lane.

## 10. Time slicing and the Scheduler

The `scheduler` package decides when to run React's work. Concurrent rendering uses it. Sync lanes do not.

- Scheduler uses `MessageChannel` (fallback `setTimeout`) to yield to the browser between tasks.
- `shouldYield()` returns true after a frame budget, about 5 ms by default.
- When it returns true, `workLoopConcurrent` exits. The work-in-progress pointer stays where it stopped. The Scheduler continues the render in the next task.
- Between slices, the browser can handle input and paint.

If the render finishes without being interrupted, React moves to commit. If a higher-priority update arrives, React can restart from the root with a fresh work-in-progress tree.

Concurrent rendering is only on when you use `createRoot` and a concurrent feature such as transitions, `useDeferredValue`, or Suspense. Plain `setState` in `createRoot` still renders synchronously in many cases, such as discrete events.

Because render can run more than once before a commit, render functions must be pure. Strict Mode double-invokes them in development to expose violations.

## 11. The commit phase

The commit phase applies the result to the host. It is synchronous and cannot be interrupted. It walks the finished tree and uses `flags` and `subtreeFlags` to visit only fibers with work.

Commit has three main sub-phases, then passive effects.

1. Before mutation: read the DOM before changes. Class `getSnapshotBeforeUpdate` runs here.
2. Mutation: apply changes. Insert, move, and delete DOM nodes. Update DOM properties. Detach refs. Run layout effect cleanups (`useLayoutEffect` cleanup) and `componentWillUnmount` for deleted fibers.
3. Switch the root: `root.current = finishedWork`. This happens after mutation and before layout, so layout code sees the new tree as current.
4. Layout: run `useLayoutEffect` bodies, `componentDidMount` and `componentDidUpdate`, and attach refs. The DOM is updated here but not yet painted.
5. Passive effects: `useEffect` cleanups and bodies run later, after paint. React schedules them separately. If the render came from a discrete event like a click, React flushes them synchronously before the next render.

Consequences:

- `useLayoutEffect` can read layout and trigger a synchronous re-render before the browser paints. It blocks painting, so keep it short.
- `useEffect` does not block paint. Use it by default.
- All cleanups for a commit run before any new effect bodies run.

After commit, React checks for remaining work in `root.pendingLanes` and schedules another render if needed.

## 12. Suspense and error boundaries

Both work through the same fiber walk.

Suspense:
- A component that is not ready throws a promise (or calls `use(promise)` on a pending one). React catches it in the work loop.
- It unwinds to the nearest `Suspense` boundary fiber. That fiber renders the fallback.
- When the promise resolves, React schedules a retry lane on the boundary and re-renders.
- With transitions, React can keep showing the old UI instead of the fallback. This avoids hiding already-visible content.

Error boundaries:
- Errors during render are caught in the work loop. `throwException` marks the nearest class boundary fiber with `ShouldCapture`.
- The unwind phase (`unwindWork`) finds it. The boundary re-renders with its error state and shows the fallback UI.
- There are no function component error boundaries. React requires `getDerivedStateFromError` or `componentDidCatch`, which only classes have.

## 13. Context

Context propagation uses the fiber tree too.

- When a provider's value changes, `propagateContextChange` walks the provider's subtree.
- It finds fibers that read that context through their `dependencies` list. It marks them with the update lane.
- It also sets `childLanes` on their ancestors, so `beginWork` can reach them.
- This works even if an intermediate `memo` component would otherwise bail out.

Every consumer re-renders when the context value changes, even if it uses only part of the value. This is why large context objects cause wide re-renders. Splitting contexts or using selectors in a library reduces the cost.

## 14. Putting it together: one update, end to end

1. A click calls `setCount(c => c + 1)`.
2. React creates an update on the hook queue. The lane is `SyncLane`, because the event is discrete.
3. It marks the fiber and all ancestors with lanes. It schedules a render on the root.
4. Render phase: `workInProgress` starts at the root. `beginWork` follows `childLanes` down. Fibers with no work bail out and reuse their children.
5. At the changed component, React runs your function, applies the queue, and gets new JSX. It reconciles children against the old fibers.
6. `completeWork` runs on the way up. It records DOM prop diffs and bubbles flags.
7. Commit phase: React applies the placements, updates, and deletions. It swaps `root.current`. It runs layout effects.
8. The browser paints.
9. Passive effects run.

## 15. Practical consequences

- Render is not commit. A component can render many times without any DOM change. Never put side effects in render.
- Re-rendering a component does not mean the DOM changes. React diffs first and only touches nodes that differ.
- Component identity is position plus type plus key. Moving a component to a different place in the tree, or changing its type, resets its state.
- Do not define components inside other components.
- Use stable keys. Never use index for dynamic lists.
- Pass stable references (`useMemo`, `useCallback`, or the React Compiler) to memoized children. Otherwise the bailout fails.
- Wrap slow, non-urgent updates in `startTransition` so urgent input stays responsive.
- Keep `useLayoutEffect` rare. It delays paint.

## 16. Where to read the source

- `packages/react-reconciler/src/ReactFiber.js`: fiber creation and `createWorkInProgress`.
- `ReactFiberBeginWork.js` and `ReactFiberCompleteWork.js`: the down and up passes.
- `ReactChildFiber.js`: the child diff, including `reconcileChildrenArray`.
- `ReactFiberWorkLoop.js`: the work loop, `performUnitOfWork`, and root scheduling.
- `ReactFiberHooks.js`: hooks and dispatchers.
- `ReactFiberLane.js`: lane definitions and helpers.
- `ReactFiberCommitWork.js`: commit sub-phases.
- `packages/scheduler`: the cooperative scheduler.

File names and layout move between releases. Check the version you use. If you need exact behavior for an edge case, read the source for that version, because the details above are simplified.
