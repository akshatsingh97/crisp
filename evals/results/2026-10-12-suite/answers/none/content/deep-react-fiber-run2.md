# React reconciliation and Fiber

Reconciliation is how React compares the new UI description with the previous one and finds the smallest set of changes. Fiber is the data structure and work loop that does this in small units that React can pause, drop, and prioritize. This explanation follows React 18 and 19. Internal function and field names are real, but they change between versions.

## 1. The problem

React lets you write `UI = f(state)`. After each state change, you return a whole new description of the UI. React must turn that into as few DOM operations as possible.

A general tree diff costs O(n³). React gets O(n) with two heuristics:

1. Elements of different types produce different trees. React does not try to match them.
2. Keys tell React which children in a list are the same across renders.

Both heuristics can be wrong for unusual cases. In practice they hold almost always, and the speed gain is large.

## 2. Elements, components, and fibers

These four things are easy to confuse.

| Thing | What it is | Lifetime |
|---|---|---|
| Element | A plain object: `{type, props, key, ref}`. JSX produces it. | One render |
| Component | A function or class that returns elements | Your code |
| Instance | The mounted, stateful occurrence of a component | Mount to unmount |
| Fiber | React's internal object for one instance, DOM node, or other unit of work | Mount to unmount, reused between renders |

Elements are cheap and thrown away on every render. Fibers persist. A fiber holds state, hooks, and links to its neighbors. It is the "instance" that function components do not have.

## 3. The diffing rules

React compares a new element with the existing fiber at the same position.

**Same type** (same string tag, or same component reference). React keeps the fiber and its state. It updates the props. For a DOM element, it changes only the attributes that differ. Then it recurses into the children.

**Different type.** React destroys the old subtree and builds a new one. All state below that point is lost. Effects clean up, and DOM nodes are removed.

This is why defining a component inside another component's body causes trouble. The inner function has a new identity on each render. React sees a new type every time and remounts the subtree.

```jsx
function Parent() {
  const Child = () => <input />;   // new type each render: remounts, loses focus and state
  return <Child />;
}
```

**Position matters.** If no key exists, React matches children by index. State belongs to a position in the tree, not to the JSX you wrote. This is why you can reset a component's state by changing its `key`.

## 4. Why React needed Fiber

Before React 16, the "stack reconciler" worked by plain recursion. It walked the tree using the JavaScript call stack.

- You cannot pause a recursive call stack in the middle and resume it later.
- A large update blocked the main thread until it finished. Typing, animations, and scrolling froze.
- React had no way to say "this update matters more than that one".

Fiber (shipped in React 16, 2017) reimplemented the reconciler. The recursion became a loop over heap-allocated objects. Because the position in the traversal is stored in plain objects, React can stop at any fiber and continue later, or throw the work away.

The goals were:

- Split work into units.
- Pause, abort, and restart work.
- Assign priorities to updates.
- Reuse earlier work.
- Return multiple children from a component, and support error boundaries.

## 5. Anatomy of a fiber

A fiber is a JavaScript object. The main fields are below.

```
Identity
  tag            What kind of fiber: FunctionComponent, HostComponent, HostRoot, ...
  key, type      From the element. Used for matching.
  stateNode      The DOM node (host fibers), class instance, or the root object

Tree links (a linked list, not a children array)
  return         Parent fiber
  child          First child
  sibling        Next sibling
  index          Position among siblings

Data
  pendingProps   Props for the render in progress
  memoizedProps  Props from the last completed render
  memoizedState  State from the last render. For function components: the hooks list.
  updateQueue    Pending state updates, or the effect list for function components

Work tracking
  lanes          Priority bits of pending work on this fiber
  childLanes     Priority bits of pending work somewhere below
  flags          What to do at commit: Placement, Update, ChildDeletion, Ref, Passive, ...
  subtreeFlags   Union of the flags of all descendants
  deletions      Child fibers to remove

Double buffering
  alternate      The other version of this fiber (current vs work-in-progress)
```

The parent holds only the `child` pointer to its first child. Siblings chain through `sibling`. Each child points back with `return`. This layout lets React walk the whole tree with a loop and no recursion.

## 6. Two trees

React keeps two fiber trees.

- The current tree matches what is on screen.
- The work-in-progress tree is being built for the next screen.

Each fiber's `alternate` points to its twin in the other tree. React reuses these twins and allocates a new fiber only when none exists. Creating a work-in-progress fiber is `createWorkInProgress`.

A special `FiberRoot` object holds a `current` pointer. It points at the root fiber of the current tree. When the commit finishes, React sets `root.current` to the work-in-progress tree. That single pointer swap is what "publishes" the new UI in React's own bookkeeping.

The benefit: while React works, it never touches the current tree. If it must abandon the render, nothing is half-updated.

## 7. The render phase

The render phase calls your components and decides what changed. It performs no DOM mutation. It can be paused, restarted, or discarded.

### The work loop

```js
function workLoopConcurrent() {
  while (workInProgress !== null && !shouldYield()) {
    performUnitOfWork(workInProgress);
  }
}
```

The synchronous version has no `shouldYield()` check. The unit of work is one fiber. After each fiber, a concurrent render asks whether it has used up its time slice, about 5 ms. If yes, it returns control to the browser and schedules itself to continue.

### One unit of work

`performUnitOfWork(fiber)` does two things.

1. `beginWork(fiber)` runs on the way down. It processes this fiber and returns its first child.
2. If there is no child, `completeUnitOfWork` runs on the way up. It calls `completeWork` on this fiber, then moves to the sibling. If no sibling exists, it moves to `return` (the parent) and completes that.

For this tree:

```
App
├─ Header
└─ Main
   ├─ List
   └─ Footer
```

the order is:

```
begin App → begin Header → complete Header →
begin Main → begin List → complete List →
begin Footer → complete Footer → complete Main → complete App
```

This is depth-first, in a loop, with the position stored in `workInProgress`.

### beginWork

`beginWork` decides what to do with a fiber, using its `tag`:

- **Function component.** It calls `renderWithHooks`. That runs your function with the right hooks dispatcher and returns new children elements.
- **Class component.** It processes the update queue, calls lifecycle methods, and calls `render()`.
- **Host component** (`div`, `span`). It has no code to run. It only reconciles children from `props.children`.
- **Special types.** Context providers, Suspense, memo, Fragment, and others each have their own branch.

Then it calls `reconcileChildren`. This is where the diffing rules from section 3 run. It compares the new child elements with the old child fibers and produces the work-in-progress child fibers. It marks them with flags such as `Placement` (insert or move) or `ChildDeletion`.

### completeWork

On the way up, `completeWork` finishes a fiber.

- For a new host component, it creates the DOM node (`createInstance`), appends the already-built child DOM nodes to it, and sets initial properties. The node is not yet in the document. This builds the DOM subtree off-screen.
- For an updated host component, it compares old and new props and sets an `Update` flag if anything changed.
- It bubbles `flags` into `subtreeFlags` and `lanes` into `childLanes`, so a parent knows whether anything below it needs work.

Early React 16 and 17 kept a linked "effect list" of fibers with side effects. React 18 replaced it with `subtreeFlags`. The commit phase now walks the tree and skips subtrees whose flags are empty.

## 8. Child reconciliation in detail

`reconcileChildFibers` has different paths for the shape of the new children.

**A single element.** React looks at the existing first child. If key and type match, it reuses the fiber with new props and deletes any extra old siblings. If not, it deletes the old children and creates a new fiber.

**An array of children.** React runs a two-pass algorithm.

1. Pass one walks old fibers and new elements together, in order. It stops at the first pair whose keys differ. Matching pairs are updated in place.
2. If new elements remain after an old list ends, React creates fibers for them. If old fibers remain after the new list ends, React deletes them.
3. If both lists have items left, React builds a map of the remaining old fibers by key (or index when there is no key). It then walks the remaining new elements and looks each up in the map. Found items are reused. Missing items are created. Whatever stays in the map at the end is deleted.

**Moves use `lastPlacedIndex`.** React remembers the highest old index it has seen so far. When a reused fiber has an old index lower than that, it must move, so React flags it `Placement`. If its old index is equal or higher, it stays and the marker advances.

Examples with keys A, B, C, D:

| Change | Result |
|---|---|
| `[A,B,C,D]` to `[B,C,D,A]` | Only A moves. |
| `[A,B,C,D]` to `[D,A,B,C]` | A, B, and C move. D stays. |

Moving an item toward the front is the expensive case. React does not detect the shorter move of D alone.

### Why keys matter

- Keys must be stable and unique among siblings.
- Do not use the array index as a key when the list can be reordered, inserted into, or filtered. After a reorder, the index points to a different item. React then keeps the old state (typed text, focus, checkbox state) on the wrong row.
- Do not use `Math.random()`. A new key on every render forces a remount of every item.

## 9. Bailouts: skipping work

Most of React's speed comes from not doing work. In `beginWork`, React compares the current and pending state of the fiber.

If all of these are true, the fiber **bails out**:

- `oldProps === newProps` (reference equality, so a new object each render defeats it)
- No legacy context change
- No pending update on this fiber (`lanes` has no matching bits)

Then there are two cases:

1. **`childLanes` has no matching work.** React skips the entire subtree. It reuses the current children and does not walk below. This is the fast path.
2. **`childLanes` has matching work.** React clones the child fibers and continues down only to reach them. This one fiber does not re-render.

`React.memo`, `PureComponent`, and `shouldComponentUpdate` add extra checks. `memo` compares props shallowly and bails out if they are equal.

Two key facts follow from this:

- By default, when a component re-renders, all its children re-render. A new element object means new props by reference. Bailout needs the same props reference. This is why `memo`, `useMemo`, and `useCallback` exist.
- Re-rendering is not the same as DOM updating. A "wasted" render calls your function and compares output. It does not touch the DOM unless something actually changed.

When a state setter is called with the same value (checked with `Object.is`), React may skip scheduling work. In some cases it still renders the component once more before it bails out.

React Compiler, available in newer versions, adds this memoization automatically at build time.

## 10. Hooks live on the fiber

For a function component, `fiber.memoizedState` is the head of a singly linked list. Each hook call creates or reads one node in that list.

```
fiber.memoizedState → [useState] → [useEffect] → [useMemo] → null
```

On each render, React walks this list in call order. The nth hook call gets the nth node. React stores no hook names. It relies on order only.

This explains the Rules of Hooks:

- Do not call hooks in conditions or loops. A skipped call shifts every later hook onto the wrong node.
- Call hooks only from components and custom hooks, so there is a current fiber to attach to.

Each `useState` node holds a queue of pending updates. `setState` does not change state at once. It does these steps:

1. Pick a lane (priority) for the update from the current context.
2. Append an update object to the hook's queue.
3. Mark `lanes` on this fiber and its alternate. Walk up `return` pointers and mark `childLanes` on every ancestor, up to the root.
4. Schedule a render on the root.

On the next render, `useState` processes the queue and computes the new state. The ancestor marks from step 3 are how React finds the dirty fiber without searching the whole tree.

## 11. The commit phase

After the render phase finishes, React has a complete work-in-progress tree. The commit phase applies it. **It is synchronous and cannot be interrupted.** A half-applied DOM would show an inconsistent screen.

The commit has these sub-phases:

1. **Before mutation.** React calls `getSnapshotBeforeUpdate` on class components. It reads layout information such as scroll position before the DOM changes.
2. **Mutation.** React walks the tree and applies flags.
   - It inserts, moves, and removes DOM nodes (`Placement`, `ChildDeletion`).
   - It applies property updates (`Update`).
   - It runs `useLayoutEffect` cleanups, detaches refs, and calls `componentWillUnmount` for deleted subtrees.
3. **The pointer swap.** After mutation and before layout, React sets `root.current = finishedWork`. The new tree becomes current. This order means `componentWillUnmount` and cleanups see the old tree, while `componentDidMount`, `componentDidUpdate`, and layout effects see the new one.
4. **Layout.** React runs `useLayoutEffect` bodies, `componentDidMount` and `componentDidUpdate`, and attaches refs. The DOM is updated, but the browser has not painted yet. Reading layout here and setting state forces a synchronous re-render before paint.
5. **Passive effects.** `useEffect` callbacks run later, after the browser paints. React schedules them as a separate task. If the render came from a discrete event such as a click, React flushes them synchronously at the end of the commit instead. Before React runs a new effect, it runs the previous effect's cleanup. Before any new render starts, it flushes pending passive effects.

In short, `useLayoutEffect` blocks paint and `useEffect` does not.

## 12. Scheduling: lanes and priorities

### Lanes

Each update gets a **lane**. A lane is one bit in a 31-bit integer. A set of lanes is a bitmask, so React can test, merge, and subtract priorities with fast bit operations.

Examples of lanes, from highest to lowest priority:

| Lane | Typical source |
|---|---|
| `SyncLane` | Discrete events such as click, keydown |
| `InputContinuousLane` | Continuous events such as scroll, mousemove |
| `DefaultLane` | Updates outside of events, such as a timer or a fetch callback |
| `TransitionLanes` (a group) | Updates inside `startTransition` |
| `RetryLanes` | Retrying a Suspense boundary |
| `IdleLane`, `OffscreenLane` | Hidden or background work |

The lane is chosen in `requestUpdateLane`, based on the current event priority and whether the code runs inside a transition.

### Choosing what to render

`ensureRootIsScheduled` looks at all pending lanes on the root and picks the highest-priority group (`getNextLanes`). It renders only the updates in that group. Work in other lanes stays pending.

- `SyncLane` work runs in a microtask, without yielding.
- Other work goes to the **Scheduler**, a separate package. It uses a `MessageChannel` to create a macro-task, so the browser can handle input and paint between slices. This is time slicing.
- Entangled lanes render together when they must stay consistent, for example updates in the same transition.

### Starvation

A low-priority update could wait forever behind a stream of high-priority ones. React gives every pending lane an expiration time. Once a lane is overdue, React treats it as urgent and renders it without yielding.

### Interruption in practice

Suppose a transition render is in progress and the user types. The typing update has a higher priority.

1. React stops the transition render at the next fiber boundary.
2. It **discards the work-in-progress tree** and starts again from the root. The current tree was never touched, so the screen is consistent.
3. It renders and commits the typing update.
4. It later restarts the transition render with the new state.

So React does not pause and resume a render in the middle of one tree. It either finishes the render or abandons it. This is the reason render functions must be pure. They can run many times, or run and be thrown away.

### Rebasing updates

Updates with different priorities can sit in the same hook queue. Suppose update 1 is low priority, update 2 is high priority, and update 3 is low priority. A render at the high priority skips 1, applies 2, and shows a result. React keeps update 1 as the start of a "base queue" and keeps 2 and 3 after it. When the low-priority render runs, it applies 1, 2, and 3 in the original order. The final state is the same as if everything ran in order. Only the intermediate screens differ.

## 13. Features that Fiber makes possible

- **Automatic batching (React 18).** Several `setState` calls in one event, timeout, or promise create updates in the same lane. They share one render.
- **`startTransition` and `useTransition`.** They mark updates as low priority. The old UI stays interactive while the new UI renders in the background.
- **`useDeferredValue`.** It returns an older value first, then schedules a low-priority render with the new value.
- **Suspense.** A component that is not ready throws a promise. React unwinds to the nearest Suspense boundary, shows the fallback, and retries when the promise settles. The retry uses `RetryLanes`. React 19's `use(promise)` works the same way. In a transition, React keeps the old UI on screen instead of showing the fallback.
- **Error boundaries.** If a render throws, React unwinds (`unwindWork`) to the nearest boundary and renders its fallback.
- **Offscreen and Activity.** They hide a subtree and keep its state, and give it a low priority.
- **`useSyncExternalStore`.** An external store can change in the middle of a time-sliced render. That would show two different values of the same data on one screen, which is called tearing. This hook forces a synchronous re-render when it detects the change.
- **Server Components and hydration.** Hydration also uses fibers. React can hydrate parts of a page in priority order, for example the part the user clicks first.

## 14. One update, end to end

The user clicks a button. The handler calls `setCount(c => c + 1)`.

1. The click has discrete event priority, so the update gets `SyncLane`.
2. `dispatchSetState` creates an update object and puts it in the hook's queue.
3. `scheduleUpdateOnFiber` marks `lanes` on the component's fiber and its alternate. It marks `childLanes` on every ancestor up to the root.
4. `ensureRootIsScheduled` queues a synchronous render in a microtask.
5. The render phase starts at the root. It clones the root fiber into a work-in-progress fiber. `beginWork` goes down. Ancestors with no own work and with `childLanes` set clone themselves and continue. Siblings with no matching lanes bail out.
6. At the target component, `renderWithHooks` runs your function. `useState` applies the queue and returns the new count.
7. `reconcileChildren` compares the new elements with the old child fibers. A text node changes, so the host fiber gets an `Update` flag.
8. `completeWork` runs on the way up and bubbles the flags into `subtreeFlags`.
9. The commit phase mutates the one text node. It swaps `root.current`. It runs layout effects, then passive effects.
10. The browser paints.

## 15. Practical consequences

- Render must be pure. Do not mutate outside values, start requests, or subscribe in render. React can call render more than once, and StrictMode does this on purpose in development to expose problems.
- Effects belong in `useEffect` or `useLayoutEffect`. The commit phase is the only place where side effects are safe.
- Keep keys stable. A key is the identity of a component, and a changed key means a remount.
- Do not define components inside components.
- State lives at a position in the tree. Moving a component to a different position or parent resets its state.
- Re-rendering is cheap, and DOM work is not. Optimize with the profiler first, then use `memo`, stable props, and moving state down. Do not add `useMemo` everywhere.
- Use transitions for slow, non-urgent updates such as filtering a big list. Use `useDeferredValue` when you receive the value from outside.
- Heavy work in a single component still blocks. Time slicing works between fibers, not inside one function. A slow render function cannot be split.
- Commit is synchronous. Thousands of DOM changes in one commit still block the main thread.

## Source files to read

If you want to check this in the code, start in the React repository under `packages/react-reconciler/src`:

- `ReactFiber.js`: fiber creation and `createWorkInProgress`
- `ReactFiberWorkLoop.js`: work loop, scheduling, and the commit entry point
- `ReactFiberBeginWork.js` and `ReactFiberCompleteWork.js`
- `ReactChildFiber.js`: the child diffing algorithm
- `ReactFiberHooks.js`: hooks and update queues
- `ReactFiberLane.js`: lane definitions
- `ReactFiberCommitWork.js`: the commit sub-phases

The file names and exact function names change often, so use them as a map and not as a fixed API.
