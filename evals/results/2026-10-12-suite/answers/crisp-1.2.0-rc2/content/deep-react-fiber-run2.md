React reconciliation compares the element tree from your latest render with the tree React already has, then computes the smallest set of changes to apply. Fiber is the data structure and execution model that makes this work pausable, resumable, and prioritizable. Internal names below match React 18 and 19. They can change between versions, but the concepts are stable.

## 1. Vocabulary

- Element: a plain object that describes UI, such as `{type: 'div', props, key}`. JSX produces elements.
- Component instance: the persistent state React keeps for one mounted component.
- Fiber: a JavaScript object that represents one component instance or DOM node. It also acts as a unit of work.
- Reconciliation: the algorithm that diffs new elements against existing fibers.
- Renderer: the code that applies changes to a host environment. React DOM, React Native, and others are renderers.
- Virtual DOM: an informal name for the element tree plus the fiber tree. React has no separate "virtual DOM" object.

## 2. Why Fiber exists

Before React 16, the "stack reconciler" walked the tree with plain recursion. It used the JavaScript call stack.

- The recursion could not stop halfway. A large update blocked the main thread until it finished.
- Input, animation, and painting stalled during that time.
- React could not give urgent updates priority over slow ones.
- React could not reuse partial work or throw it away.

Fiber, shipped in React 16, reimplements the call stack in heap memory. Each fiber acts as one virtual stack frame. React controls the frames, so it can:

1. Pause work and resume it later.
2. Assign priorities to different updates.
3. Abort work and restart it.
4. Reuse work done earlier.
5. Yield to the browser between units of work.

## 3. The fiber data structure

A fiber is a mutable object. These are the important fields.

```js
{
  // identity
  tag,            // FunctionComponent, ClassComponent, HostComponent, HostRoot, Fragment, Suspense...
  key,
  elementType,    // the type from the element
  type,           // resolved type (differs for lazy or memo wrappers)
  stateNode,      // DOM node, class instance, or FiberRoot

  // tree links (a singly linked list structure, not an array of children)
  return,         // parent
  child,          // first child
  sibling,        // next sibling
  index,          // position among siblings

  // data
  pendingProps,   // new props for this render
  memoizedProps,  // props used in the last completed render
  memoizedState,  // state (for hooks: head of the hook linked list)
  updateQueue,    // queued state updates, or effect list for function components
  dependencies,   // contexts this fiber reads

  // work tracking
  flags,          // bitmask: Placement, Update, Deletion, Ref, Passive, Snapshot...
  subtreeFlags,   // OR of all descendant flags
  deletions,      // children to remove
  lanes,          // pending work priority on this fiber
  childLanes,     // pending work priority in the subtree
  alternate,      // the twin fiber, see next section
}
```

The `child`, `sibling`, and `return` pointers let React walk the tree without recursion. React can stop at any fiber and later continue from that fiber, because the traversal state is just a pointer: the "current work in progress" fiber.

## 4. Two trees and double buffering

React keeps two fiber trees.

- The current tree: matches what is on screen now.
- The work-in-progress tree: the draft React builds during a render.

Each fiber has an `alternate` pointer to its twin in the other tree. When React starts rendering a fiber, it calls `createWorkInProgress`. That function reuses the alternate object if one exists and allocates a new one if not. React then copies the fields it needs.

When the render finishes and commits, React flips a pointer: `root.current = finishedWork`. The draft becomes current. The old current tree becomes the spare for the next render.

This pattern has three effects:

- Aborting a render costs nothing. React discards the draft and the screen stays consistent.
- Allocation stays low, because React recycles fiber objects.
- Render never mutates the current tree's visible output. Only the commit phase touches the host environment.

## 5. The two phases

Every update has a render phase and a commit phase.

Render phase (also called reconcile phase):
- Calls your components and computes the new tree.
- Is pure by contract. It must have no side effects.
- Is interruptible in concurrent mode.
- React can run it multiple times for one commit, or throw the result away.

Commit phase:
- Applies the result to the host (DOM mutations), runs lifecycle methods and effects.
- Is synchronous and never interrupted.
- Must be synchronous so users never see a half-updated screen.

This split explains why render functions must be pure. React may call them twice, pause them, or discard them. In Strict Mode development builds, React deliberately double-invokes render to expose impurities.

## 6. The render phase in detail

### 6.1 Triggering

A render starts from an update: `setState`, a `useReducer` dispatch, a root `render`, a context change, or a Suspense retry. The update is placed on the fiber's update queue with a lane (priority). React then marks that fiber and all its ancestors. It sets `lanes` on the source fiber and `childLanes` on each ancestor. This marking lets the render find the changed fiber quickly. React then schedules a task for the root.

### 6.2 The work loop

The core loop is small.

```js
function workLoopSync() {
  while (workInProgress !== null) performUnitOfWork(workInProgress);
}
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) performUnitOfWork(workInProgress);
}
```

`shouldYield` returns true when the current time slice is used up. The Scheduler package uses a slice of about 5 ms. If the loop exits early, React yields to the browser. It then continues from the same `workInProgress` pointer in a new task. The Scheduler schedules tasks with `MessageChannel`, so the browser can handle input and paint between slices.

### 6.3 One unit of work

```js
function performUnitOfWork(unit) {
  const next = beginWork(unit.alternate, unit, renderLanes);
  unit.memoizedProps = unit.pendingProps;
  if (next === null) completeUnitOfWork(unit);
  else workInProgress = next;
}
```

The traversal is depth-first:

1. `beginWork` runs on a fiber as React goes down. It returns the first child, or null for a leaf.
2. At a leaf, `completeWork` runs. React then moves to the sibling. If no sibling exists, it moves to the parent and completes it.
3. This repeats until the root completes.

Think of `beginWork` as "enter the function" and `completeWork` as "return from the function".

### 6.4 beginWork

`beginWork` does the following for each fiber:

1. Compare old and new props. If props are identical (same reference), no context changed, and no pending update targets this fiber, take the bailout path (section 9).
2. Otherwise, switch on `tag`:
   - Function component: call `renderWithHooks`, which runs your function and returns new elements.
   - Class component: process the update queue, call `getDerivedStateFromProps`, then `render`.
   - Host component (like `div`): read children from props.
   - Fragment, Suspense, Context provider, memo, forwardRef, and others each have their own handler.
3. Call `reconcileChildren` with the returned elements. This is the diff (section 7). It creates or updates child fibers and sets `workInProgress.child`.

### 6.5 completeWork

On the way up, `completeWork` does the following:

- For new host components, it creates the DOM node in memory with `createInstance` and appends the child DOM nodes. The node is not yet attached to the document.
- For updated host components, it computes a diff of props and marks the fiber with the `Update` flag.
- It bubbles `flags` and `lanes` from children into `subtreeFlags` and `childLanes`.

Bubbling lets the commit phase skip whole subtrees that have no work.

## 7. Reconciliation: the diffing algorithm

A general tree diff costs O(n³). React instead uses two heuristics to run in O(n):

1. Elements of different types produce different trees. React does not try to match them.
2. A `key` prop identifies which children are stable across renders.

### 7.1 Type comparison

At the same position, React compares the old fiber's `type` with the new element's `type`.

- Same type: React keeps the fiber. It updates props and, for host nodes, reuses the DOM node. Component state persists.
- Different type: React unmounts the old subtree and mounts a new one. All state in the old subtree is lost, and effects clean up.

Types compare by identity. For host elements, the type is a string like `'div'`. For components, it is the function or class reference. A component defined inside another component gets a new identity on every render. React therefore treats it as a new type and remounts it every time. Define components at module level to avoid this bug.

### 7.2 Single child

`reconcileSingleElement` loops over existing children:

1. If a child has the same key and the same type, reuse it, delete its remaining siblings, and return it.
2. If the key matches but the type differs, delete all remaining children. No other child can match, because keys are unique.
3. If the key does not match, delete that child and keep looking.
4. If nothing matched, create a new fiber.

### 7.3 Arrays of children

`reconcileChildrenArray` handles lists. It makes up to two passes.

Pass 1 walks the old fibers and the new elements together, by position.
- For each pair, it checks whether the keys match. Elements without a key use the index as the implicit key.
- If the keys match, it reuses or updates the fiber.
- At the first key mismatch, pass 1 stops.

After pass 1:
- If the new list is exhausted, React deletes the remaining old fibers.
- If the old list is exhausted, React creates fibers for the remaining new elements. This is the common append case.
- Otherwise, React runs pass 2.

Pass 2 handles reordering:
1. Build a `Map` of the remaining old fibers, keyed by `key` (or by `index` when there is no key).
2. Walk the remaining new elements. For each, look up the map. If found, reuse that fiber and remove it from the map. If not found, create a fiber.
3. Track `lastPlacedIndex`, the highest old index seen so far among reused fibers.
   - If a reused fiber's old index is less than `lastPlacedIndex`, it must move. React sets the `Placement` flag.
   - Otherwise, the fiber stays, and `lastPlacedIndex` becomes its old index.
4. Delete every fiber left in the map. They have no match in the new list.

The algorithm only moves items "forward". Take the list `[A, B, C]` that becomes `[C, A, B]`. C has old index 2, so `lastPlacedIndex` is 2. A and B have lower old indexes, so React moves both of them. One move of C would suffice, but React makes two. This is a known limitation, and it rarely matters in practice.

### 7.4 Why keys matter

- Stable keys let React match items across reorders, insertions, and removals. State and DOM nodes follow the item.
- Index keys break when the list reorders or when items insert at the front. The fiber at index 0 now receives a different item's props. Local state (for example, text in an input) stays at index 0 and appears to belong to the wrong item.
- Random keys, such as `Math.random()`, force a remount on every render. This destroys state and wastes work.
- Changing a key on purpose is a valid way to reset a component's state.

### 7.5 What reconciliation does not do

Reconciliation does not decide whether your component function runs. That depends on bailouts (section 9). It also does not apply changes. It only marks fibers with flags such as `Placement`, `Update`, and `ChildDeletion`. The commit phase reads those flags.

## 8. Hooks and fibers

For a function component, the fiber stores hook state in `memoizedState` as a linked list. Each node holds one hook's data: current state, a queue of pending updates, and a `next` pointer.

- Each call to `useState` or `useEffect` takes the next node in the list.
- React identifies hooks by call order only, not by name. This is why hooks must not run conditionally or in loops.
- React swaps the active "dispatcher" object. On mount, `useState` allocates a new node. On update, it reads the existing node from the current fiber and clones it into the work-in-progress fiber.
- `setState` does not change state immediately. It adds an update object to the hook's queue and schedules a render. During the next render, React processes the queue to compute the new state.

If React discards a render, the work-in-progress hook list is thrown away. Your committed state stays intact.

## 9. Bailouts: skipping work

Bailouts are how React avoids re-rendering the whole tree. In `beginWork`, a fiber can skip its own render if both are true:

- `oldProps === newProps` by reference, and no context it reads has changed.
- No update with a matching lane is pending on this fiber.

When a fiber bails out, React checks `childLanes`:
- If the subtree has no pending work in the current lanes, React skips the whole subtree and returns null. This is why marking ancestors with `childLanes` matters.
- If descendants have pending work, React clones the child fibers and continues down. The bailed-out fiber itself does not re-render.

Consequences:

- When a parent re-renders, it creates new element objects for its children. Their `props` objects are new references, so the children re-render by default, even if the values are equal.
- `React.memo` changes the check to a shallow comparison of props. If all props are `Object.is`-equal, the component bails out.
- Passing the same element reference down (for example, via `children` from a stable parent) also bails out, because the props reference does not change.
- `useMemo` and `useCallback` keep props stable so that `memo` works.
- Context works differently. When a provider's value changes, React walks the provider's subtree and marks every consumer fiber for update. Intermediate components do not re-render unless their props changed. This is why `memo` does not block context updates.
- The React Compiler can add this memoization automatically at build time.

## 10. The commit phase in detail

After the render phase completes, React has a finished work-in-progress tree with flags on it. Commit has these steps:

1. Before mutation: React reads the DOM before changes. It calls `getSnapshotBeforeUpdate` on class components.
2. Mutation: React applies the changes.
   - Insert, move, and remove DOM nodes (`Placement`, `ChildDeletion`).
   - Update DOM properties (`Update`).
   - Run cleanup functions of `useLayoutEffect` and detach refs for changed fibers.
   - For deletions, call `componentWillUnmount` and run effect cleanups.
3. Tree swap: React sets `root.current = finishedWork`. The new tree is now current. This happens after mutation and before layout, so `componentWillUnmount` sees the old tree and `componentDidMount` sees the new one.
4. Layout: React runs `componentDidMount`, `componentDidUpdate`, and `useLayoutEffect` callbacks. It also attaches refs. These run synchronously, so reading layout here forces the browser to calculate it before paint.
5. Passive effects: React runs `useEffect` callbacks after the browser paints. If the render came from a discrete event such as a click, React flushes passive effects synchronously at the end of commit. This keeps results consistent with what the user just did.

Effects run in a defined order: children before parents, and all cleanups before any new setups in the same flush.

The commit phase uses `subtreeFlags` to prune. If a subtree has no flags, React skips it entirely.

## 11. Lanes and priority

Fiber tracks priority with lanes. A lane is one bit in a 31-bit integer, and a set of lanes is a bitmask.

Common lanes, from most to least urgent:

- `SyncLane`: discrete events like clicks and key presses, and `flushSync`.
- `InputContinuousLane`: continuous events like drag and scroll.
- `DefaultLane`: updates from timers, network callbacks, and other non-event sources.
- `TransitionLanes`: updates wrapped in `startTransition`. There are several, so independent transitions do not entangle.
- `RetryLanes`: Suspense retries.
- `IdleLane` and `OffscreenLane`: work that can wait.

How lanes drive scheduling:

1. When an update happens, `requestUpdateLane` picks a lane from the current context. Examples are the event type, whether code is inside a transition, and whether it is in a Suspense retry.
2. The root records the lane in `pendingLanes`.
3. `getNextLanes` chooses the highest-priority lanes to render. Urgent lanes render synchronously. Transition lanes use `workLoopConcurrent` and yield.
4. During render, `beginWork` and update queue processing skip updates whose lane is not in the current render lanes.

Interruption works like this:

- If a higher-priority update arrives during a transition render, React abandons the work-in-progress tree. It calls `prepareFreshStack` and starts over with the urgent lane.
- After the urgent commit, React renders the lower-priority lane again.
- Update queues preserve ordering. If an urgent update skipped over a lower-priority update, React keeps a base state and "rebases". The final state is as if all updates ran in the order they were issued.

Starvation protection: each pending lane has an expiration time. Once a lane expires, React treats it as urgent and renders it without yielding.

## 12. Concurrent features built on Fiber

- `startTransition` and `useTransition`: mark updates as non-urgent. The old UI stays interactive while the new tree renders in the background.
- `useDeferredValue`: renders first with the old value at urgent priority, then re-renders with the new value at low priority.
- Suspense: when a component throws a promise (or calls `use` on a pending one), React unwinds the stack to the nearest Suspense boundary. It shows the fallback and schedules a retry on a retry lane when the promise settles. In a transition, React usually keeps the old UI instead of showing the fallback.
- `useSyncExternalStore`: external stores can change mid-render. Because concurrent render yields, different components could read different values ("tearing"). This hook detects the change and forces a synchronous re-render.
- Offscreen and Activity: keep a subtree mounted but hidden, with its state preserved, and render it at low priority.

## 13. The renderer boundary

The `react-reconciler` package contains the fiber algorithm. A renderer supplies a "host config": a set of functions the reconciler calls.

- `createInstance`, `createTextInstance`
- `appendInitialChild`, `appendChild`, `insertBefore`, `removeChild`
- `prepareUpdate` and `commitUpdate`
- `finalizeInitialChildren`, `shouldSetTextContent`

React DOM implements these with DOM APIs. React Native implements them with native views. Custom renderers (for canvas, 3D, terminals) implement their own.

## 14. Practical consequences

1. Keep render pure. React can call it multiple times and discard results.
2. Use stable, unique keys from your data. Do not use indexes for lists that reorder, insert, or delete.
3. Define components at module scope. Never define them inside another component's body.
4. Changing an element's type or key at a position resets all state below it.
5. Re-render cost depends on props identity. Stabilize props with `memo`, `useMemo`, and `useCallback`, or use the React Compiler.
6. Put side effects in event handlers or effects, never in render.
7. Use `useLayoutEffect` only for measurement that must happen before paint. It blocks the paint.
8. Mark slow, non-urgent updates with `startTransition` so urgent input stays responsive.
9. If a list is long, reconciliation still visits every item. Use virtualization to reduce the number of fibers.

## 15. How to see this yourself

- React DevTools Profiler shows which fibers rendered and why.
- The "Highlight updates" option shows commits visually.
- Read `ReactFiberBeginWork`, `ReactFiberCompleteWork`, `ReactChildFiber`, `ReactFiberWorkLoop`, and `ReactFiberLane` in the React repository. File names and function names shift between versions, so check the version you use.

## 16. Whole flow, end to end

1. An event calls `setState`. React enqueues the update with a lane and marks the fiber and its ancestors.
2. The Scheduler runs a task for the root at that priority.
3. React builds a work-in-progress tree. `beginWork` goes down, calls components, and reconciles children. `completeWork` goes up, builds DOM nodes, and bubbles flags.
4. If a time slice ends or a higher-priority update arrives, React yields or restarts.
5. When the tree completes, commit runs synchronously: before-mutation, mutation, tree swap, layout.
6. After paint (or immediately for discrete events), passive effects run.
7. The finished tree is now current. The old tree becomes the spare for the next render.
