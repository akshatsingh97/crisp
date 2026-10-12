Reconciliation is how React decides which parts of the screen to change when state changes. Fiber is the data structure and scheduler that lets React do that work in small, pausable pieces. Together, they let React keep a UI responsive while it computes a new UI tree.

## 1. The problem React solves

You describe the UI as a function of state. After each state change, you return a new tree of **elements**. Elements are plain objects such as `{ type: 'div', props: {...}, key }`.

React must make the real UI (the DOM, or a native view tree) match that new description. Rebuilding the whole real tree on every change is too slow. So React compares the new element tree with the previous one and applies only the differences.

This comparison is **reconciliation**. A generic tree diff costs O(n³). React uses two heuristics to make it O(n):

1. Two elements of different types produce different trees.
2. A `key` prop tells React which child elements are stable across renders.

## 2. Reconciliation rules

React compares trees level by level, starting at the root.

**Different type at the same position.** React unmounts the old subtree and mounts a new one. All state in the old subtree is lost. Changing `<div>` to `<span>`, or `<A />` to `<B />`, triggers this.

**Same type at the same position.**
- For a host element, React keeps the DOM node and updates only the changed props.
- For a component, React keeps the instance and its state. It calls the component again with the new props, then reconciles whatever it returns.

**Lists of children.** React walks the old and new child lists together. The algorithm in `reconcileChildrenArray` has these steps:

1. Walk both lists in order while the keys match. Reuse each matching fiber.
2. Stop at the first key mismatch.
3. If the new list ran out, delete the remaining old fibers.
4. If the old list ran out, create fibers for the remaining new elements.
5. Otherwise, put the remaining old fibers in a map by key (or by index when there is no key).
6. Walk the rest of the new list and look up each element in the map. Reuse the fiber if found, and create one if not.
7. Track `lastPlacedIndex`. If a reused fiber's old index is lower than it, mark the fiber as moved. Otherwise, raise `lastPlacedIndex` to that index.
8. Delete every fiber left in the map.

Step 7 means that moving an item to the front is cheap, and moving an item to the end can cost more moves than you expect.

**Consequences you can observe:**
- State belongs to a **position in the tree**, not to a component definition.
- Defining a component inside another component creates a new type on each render. React then remounts it every time.
- Using the array index as a key breaks state when the list reorders. The state stays at the index, and the data moves away from it.
- Changing a `key` on purpose resets a component. This is a common way to clear state.

## 3. Why Fiber exists

Before React 16, the "stack reconciler" used plain recursion. React walked the whole tree in one call stack. It could not stop halfway. A large update blocked the main thread, so input and animation froze.

The goals of the rewrite were:
- Split rendering into small units of work.
- Pause work, resume it, or throw it away.
- Give different updates different priorities.
- Return control to the browser often.

Recursion uses the JavaScript call stack, and you cannot pause that stack. So React built its own stack as a data structure on the heap. That structure is the **fiber tree**.

## 4. What a fiber is

A fiber is a JavaScript object. It is both a unit of work and the record of a component instance. Its main fields are:

| Field | Purpose |
|---|---|
| `tag`, `type`, `key` | What the fiber represents (function component, class, host element, and so on) |
| `stateNode` | The DOM node or class instance |
| `return`, `child`, `sibling`, `index` | Links that form the tree |
| `pendingProps`, `memoizedProps` | Props before and after this render |
| `memoizedState` | State. For function components, this is the head of the hooks list |
| `updateQueue` | Pending state updates and effects |
| `lanes`, `childLanes` | Priority bits for work on this fiber and in its subtree |
| `flags`, `subtreeFlags` | Side effects to apply in the commit phase |
| `alternate` | The matching fiber in the other tree |

The tree is a linked list, not an array of children. Each fiber points to its first `child`, its next `sibling`, and its parent (`return`). This layout lets React walk the tree with a loop and stop between any two fibers. Walking resumes from a pointer to one fiber.

## 5. Two trees: current and work-in-progress

React keeps two fiber trees:

- **current**: the tree that matches what is on the screen.
- **workInProgress**: the tree that React is building for the next screen.

Each fiber in one tree links to its twin through `alternate`. React reuses these twin objects between renders, so it does not allocate a full new tree each time. This pattern is **double buffering**.

When rendering finishes and React commits, it changes one pointer. `root.current` now points to the finished tree. The old current tree becomes the spare for the next render.

If React abandons a render, it discards the work-in-progress tree. The current tree stays valid and on screen.

## 6. The two phases

### Render phase (can pause)

The render phase computes what changed. It does not touch the DOM. It runs this loop:

```js
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
}
```

`performUnitOfWork` handles one fiber. It has two steps.

**`beginWork(fiber)` goes down the tree.**
- It decides whether the fiber needs work. If the props, context, and lanes show no work, React **bails out**. It then reuses the existing child fibers, or skips the whole subtree when `childLanes` shows no pending work.
- Otherwise, it runs the component. For a function component, React calls your function with hooks. For a class, it calls `render`.
- It then reconciles the returned elements against the old child fibers (section 2). This creates or updates child fibers and sets `flags` such as `Placement`, `Update`, and `ChildDeletion`.
- It returns the first child. React continues with that child.

**`completeWork(fiber)` goes back up the tree.** React reaches it when a fiber has no child.
- For a new host element, it creates the DOM node in memory. The node is not yet in the document.
- For an existing host element, it prepares the prop changes.
- It merges the `flags` of the children into the parent's `subtreeFlags`.
- It then moves to the sibling. If there is none, it moves up to the parent and completes that fiber.

The result is a depth-first walk: begin, begin, begin, complete, move sideways, begin, complete, move up.

Because React can stop and restart this phase, **render functions must be pure**. React may call a component several times before one result commits. Strict Mode calls components twice in development to expose impure code.

### Commit phase (cannot pause)

The commit phase applies the result. It runs in one synchronous pass, so users never see a half-updated screen. React uses `subtreeFlags` to skip subtrees with no effects. It has these sub-steps:

1. **Before mutation.** React calls `getSnapshotBeforeUpdate`.
2. **Mutation.** React inserts, moves, updates, and removes DOM nodes. It runs cleanups for deleted components and `useLayoutEffect` cleanups. It detaches old refs.
3. **Pointer swap.** `root.current` now points to the finished tree.
4. **Layout.** React runs `componentDidMount`, `componentDidUpdate`, and `useLayoutEffect`. It attaches refs. The DOM is already updated, so you can measure it here.
5. **Passive effects.** `useEffect` callbacks run after the browser can paint. If the render came from a discrete event such as a click, React flushes them sooner.

The swap happens between steps 2 and 4. That order is why `componentWillUnmount` sees the old tree and `componentDidMount` sees the new one.

## 7. Scheduling and priorities

Splitting work is not enough. React also decides what to work on and when to yield.

**Lanes.** Each update gets a lane. A lane is a bit in a bitmask, which makes it cheap to combine and compare. Examples, from most to least urgent:
- Sync (discrete events such as clicks)
- Input continuous (hover, scroll, drag)
- Default (most updates)
- Transition (updates inside `startTransition` or `useDeferredValue`)
- Idle and offscreen

**Scheduling a render.** When you call `setState`:
1. React creates an update object, with a lane based on the current context. It adds the update to the fiber's queue.
2. It marks `lanes` on that fiber and `childLanes` on every ancestor up to the root. This is how `beginWork` knows to descend, and where it can skip.
3. It schedules a task for the root at the highest-priority pending lane.

**Time slicing.** React runs on a `Scheduler` package that uses `MessageChannel` to run tasks. In concurrent mode, `shouldYield` returns true after about 5 ms. React then stops, lets the browser handle input and paint, and resumes in a new task.

**Interruption.** Suppose a transition is rendering and a click arrives. React stops the transition and throws away its work-in-progress tree. It renders the click first and commits it. Then it restarts the transition, based on the new state.

**Rebasing.** A lower-priority update may skip while a higher-priority one commits. React keeps the skipped update in the queue. On the next render, it applies the updates again in their original order on top of the new base state. This keeps the final state consistent no matter which update ran first.

**Starvation.** Low-priority work that waits too long gets an expiration time. After that time, React treats it as urgent.

Concurrent features rely on this design:
- `startTransition` marks an update as interruptible.
- `useDeferredValue` renders a stale value first, then a fresh one at lower priority.
- Suspense can pause a render while data loads and show a fallback.
- Automatic batching merges updates from the same event into one render.

Concurrent rendering is on only when you opt in through an API such as `createRoot` with a transition. A plain `setState` in a click handler still renders as sync work.

## 8. How hooks fit in

For a function component, `fiber.memoizedState` is the head of a linked list. Each hook (`useState`, `useMemo`, and the others) owns one node in the list.

When the component renders, React sets the current dispatcher to the mount version or the update version. Each hook call then takes the next node in the list. It has no name to look up. Order is the only key.

This is why the **Rules of Hooks** exist. If you call hooks in a different order between renders, each call reads the wrong node.

`useEffect` adds an effect object to `updateQueue`. It also sets a flag on the fiber. React compares dependency arrays in the render phase and runs the effects in the commit phase.

## 9. Other pieces built on fibers

- **Context.** A provider stores its value on its fiber. On change, React walks the subtree to find consumers and marks their lanes.
- **Error boundaries.** When a component throws during render, React unwinds to the nearest boundary fiber. It re-renders from there with the error state.
- **Suspense.** A component can throw a promise. React unwinds to the nearest Suspense boundary and shows the fallback. When the promise settles, React retries the render.
- **Offscreen (`Activity`).** A subtree can be hidden but keep its state. React can render it at low priority.

## 10. Practical results

- Rendering a component is not the same as changing the DOM. A component can render and produce no DOM change.
- A parent render re-renders all its children by default. `React.memo`, `useMemo`, and stable props let `beginWork` bail out. The React Compiler can add this memoization for you.
- Keys control identity. Use stable IDs.
- Keep render pure and put side effects in event handlers or effects.
- Do heavy work as a transition so urgent input stays fast.
- Fiber does not make React faster in total. It makes React more responsive, because it can choose what to do first.

## Where to read more

The source files to start with are `ReactFiberWorkLoop.js`, `ReactFiberBeginWork.js`, `ReactFiberCompleteWork.js`, `ReactChildFiber.js`, `ReactFiberHooks.js`, and `ReactFiberLane.js` in the React repository. Function names and details change between versions. The model in this answer holds for React 18 and later.
