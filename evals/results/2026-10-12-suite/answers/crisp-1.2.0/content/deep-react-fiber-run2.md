React reconciliation is the process that compares the new element tree from a render with the current tree. Fiber is the data structure and scheduler design that lets React do that work in small, pausable units. This description follows React 18 and 19. Internal names and details change between versions.

## 1. The problem Fiber solves

Before React 16, the "stack reconciler" walked the tree with plain recursion. It used the JavaScript call stack to track its position. React could not pause that walk, because the stack is not something it can save or resume.

A large update therefore blocked the main thread until it finished. Input handling, animations, and painting all stalled.

Fiber (shipped in React 16) rewrote the reconciler. It stores the position and state of the walk in heap objects instead of the call stack. That change gives React four abilities:

- Pause work and resume it later.
- Abort work and discard it.
- Give different updates different priorities.
- Reuse work that already finished.

## 2. Elements versus fibers

A React element is a plain, immutable object that describes what to render. JSX produces elements: `{ type: 'div', props: {...}, key: null }`. Elements are cheap and React creates them on every render.

A fiber is a mutable object that React keeps between renders. It represents one instance of a component or DOM node. A fiber is both a unit of work and a node in the tree.

The key fields of a fiber are:

```js
{
  tag,            // FunctionComponent, HostComponent, ClassComponent, ...
  type,           // the function, class, or 'div' string
  key,
  stateNode,      // DOM node, class instance, or FiberRoot

  return,         // parent fiber
  child,          // first child
  sibling,        // next sibling
  index,          // position among siblings

  pendingProps,   // props for this render
  memoizedProps,  // props from the last completed render
  memoizedState,  // state (for hooks: a linked list of hook objects)
  updateQueue,    // queued updates, callbacks, effects

  flags,          // what must happen to this fiber at commit
  subtreeFlags,   // union of flags in the descendants
  lanes,          // priorities of pending work on this fiber
  childLanes,     // priorities of pending work below this fiber

  alternate       // the same fiber in the other tree
}
```

The tree uses `child`, `sibling`, and `return` pointers. It does not use a children array. This makes the tree a linked structure.

A loop can walk a linked structure without recursion. It goes to the child first, then the sibling, then back up through `return`. That loop can stop after any single fiber and continue later.

## 3. Two trees and double buffering

React keeps two fiber trees. The current tree matches what is on screen. The work-in-progress tree is the one React builds during a render.

Each fiber points to its twin through `alternate`. React creates the twin lazily and then reuses it on later renders. This avoids allocating a new tree each time.

When a render finishes and commits, React switches one pointer: `root.current = finishedWork`. The work-in-progress tree becomes current. The old current tree becomes the spare for the next render.

This design is what makes abort safe. If React abandons a render, the current tree is untouched and the screen stays consistent.

## 4. Triggering an update

An update starts in one of these ways:

- `setState` or a `useReducer` dispatch.
- A `root.render()` call.
- A context value change.
- A `useSyncExternalStore` change.

The flow for a state update has five steps:

1. React creates an update object and assigns it a lane (a priority, see section 9).
2. React appends the update to the fiber's queue.
3. React walks up the `return` pointers. It marks `childLanes` on every ancestor. This leaves a trail that tells the render which subtrees have work.
4. React schedules a render task for the root at the highest pending priority.
5. The render starts at the root and follows the trail down.

## 5. The render phase

The render phase builds the work-in-progress tree. It calls your components. It does not touch the DOM. This phase can pause, restart, or be thrown away.

The core loop is small:

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

The synchronous version of the loop is the same without the `shouldYield()` check.

### beginWork (going down)

`beginWork` runs on each fiber as the walk descends. It does three things.

First, it checks for a bailout. If the old and new props are the same object, no context changed, and the fiber has no pending lanes, React skips the component. It then checks `childLanes`. If no descendant has work, React skips the whole subtree. If a descendant has work, React clones the child fibers and continues down.

Second, if there is no bailout, React does work based on `tag`:

- A function component runs through `renderWithHooks`, which calls your function and returns its elements.
- A class component runs its lifecycle logic and `render()`.
- A host component such as `div` only needs its children reconciled.

Third, React reconciles the returned elements against the existing child fibers. That produces the new child fibers. `beginWork` returns the first child so the loop continues downward.

### completeWork (going up)

When a fiber has no child, React calls `completeWork` on it. Then it moves to the sibling. If there is no sibling, it moves up to the parent and completes the parent.

For host components, `completeWork` does the following:

- On mount, it creates the DOM node in memory and appends the already-built child DOM nodes to it. The node is not yet attached to the page.
- On update, it diffs the old and new props and records the changes on the fiber.

For every fiber, `completeWork` also bubbles flags upward. A parent's `subtreeFlags` becomes the union of its children's `flags` and `subtreeFlags`. This lets the commit phase skip subtrees that have nothing to do.

Because completion moves bottom-up, children always complete before parents. A parent can therefore assemble a fully built DOM subtree before it attaches to the page.

## 6. Reconciliation: the diffing rules

A full tree diff costs O(n³). React uses two assumptions to get O(n):

1. Elements of different types produce different trees.
2. A `key` prop can identify which children are stable across renders.

### Same position, different type

If the element type at a position changes, React does not try to match the children. It marks the old fiber for deletion and creates a new fiber. The old subtree unmounts and loses all state. The new subtree mounts from scratch.

Changing `<div>` to `<span>` is one example. Changing `<A />` to `<B />` is another. Defining a component inside another component's body is a common bug. The inner component is a new function on every render, so it has a new type every time, and React remounts it each time.

### Same position, same type

React reuses the fiber and its state. It updates `pendingProps`. For host components, it later patches only the changed attributes. For components, it re-renders them and recurses into their output.

### A single child

`reconcileSingleElement` walks the existing children. If it finds one with a matching `key` and `type`, it reuses that fiber and deletes the siblings. If the key matches but the type differs, it deletes all of them and creates a new fiber.

### Arrays of children

`reconcileChildrenArray` handles lists in up to three stages.

1. Walk the old fibers and the new array together by index. Stop at the first position where the keys differ. Matching entries are reused in place.
2. If the new array ran out, delete the remaining old fibers. If the old fibers ran out, create fibers for the remaining new elements.
3. If both still have entries, put the remaining old fibers in a map. The map key is the element key, or the index if there is no key. Then walk the remaining new elements and look each one up in the map. A match is reused. A miss creates a new fiber. Anything left in the map is deleted.

In stage 3, React tracks `lastPlacedIndex`. This is the highest old index it has seen so far. If a reused fiber's old index is lower than `lastPlacedIndex`, the fiber must move, so React flags it `Placement`. Otherwise, the fiber stays and React updates `lastPlacedIndex`.

This means moving an item earlier in the list is cheap. Moving an item later can cause more moves than needed.

### Why keys matter

Keys must be stable and unique among siblings. Do not use array indexes as keys when the list can reorder, insert, or delete. State then attaches to the position, not the item. For example, the text in an input will jump to the wrong row.

A key can also reset state on purpose. Changing the key of a component forces React to unmount and remount it.

### Other element kinds

- Text nodes reconcile as text fibers.
- Fragments without keys are unwrapped, and their children join the parent's list.
- Portals produce a fiber that targets a different DOM container but stays in the same React tree.

## 7. Bailouts and why children re-render

When a component re-renders, all its children re-render by default. React does not compare their props unless you ask.

React compares element identity, not deep equality. If a child element object is the exact same reference as last time, the props are `===` equal and React can bail out. That is why this pattern avoids re-renders:

```jsx
function Parent({ children }) {
  const [n, setN] = useState(0);
  return <div onClick={() => setN(n + 1)}>{n}{children}</div>;
}
```

`children` is created by the grandparent and does not change when `Parent` updates. `React.memo` adds a shallow comparison of props. `useMemo` and `useCallback` help keep references stable so those comparisons succeed.

A bailout is not a promise that nothing runs. React can still enter a component once more before it decides to bail out, in the case of state that equals the previous state. It will not commit any changes.

## 8. Hooks inside fibers

Hooks store their data on the fiber. `fiber.memoizedState` points to a linked list of hook objects. Each hook object has its own `memoizedState`, an update `queue`, and a `next` pointer.

Hooks have no names or keys. React matches them by call order. On each render, React walks the list in step with your hook calls. This is the reason for the Rules of Hooks: no hooks in conditions or loops.

React swaps the hook implementation depending on the situation. During mount, `useState` allocates a new hook object. During update, it reads the existing one and applies the queued updates. Outside a render, hooks throw an error.

`useEffect` and `useLayoutEffect` push effect objects onto the fiber's `updateQueue`. The fiber gets a flag so the commit phase knows to run them.

## 9. Lanes and priorities

Early Fiber used expiration times. Current React uses lanes. A lane is one bit in a 31-bit integer. A set of lanes is a bitmask.

Some lanes, from highest priority to lowest, are:

- `SyncLane` for discrete events such as clicks and key presses.
- `InputContinuousLane` for continuous events such as scroll and drag.
- `DefaultLane` for most other updates, such as a `setState` in a timeout or a network callback.
- Transition lanes for updates wrapped in `startTransition`.
- `IdleLane` for work that can wait.
- `OffscreenLane` for hidden content.

Bitmasks make set operations cheap. React can ask "does this fiber have work in the lanes I am rendering?" with one `&` operation.

When React renders, it picks a set of lanes for that pass. Any update whose lane is outside that set is skipped. It stays in the queue.

When an update is skipped but later updates are included, React must keep the order consistent. It uses rebasing. The skipped update and all later ones stay in the queue. React recomputes state from the skipped point later. Your reducer logic must therefore be pure, because it can run more than once for the same update.

A higher-priority update can interrupt a lower-priority render. React throws away the work-in-progress tree and starts again from the root with the urgent lane. The low-priority work resumes afterward.

## 10. Scheduling and time slicing

React uses a separate package called Scheduler. It runs tasks from a priority queue. It yields to the browser using `MessageChannel`, because that task runs sooner than `setTimeout`.

The `shouldYield()` check in the work loop returns true when the current time slice ends. The slice is about 5 ms. When it returns true, the loop exits between fibers. React asks the Scheduler to continue later, and the browser can handle input and paint.

Time slicing does not apply to every update. In React 18 and later, only non-blocking lanes use the concurrent loop. Those are transitions and similar work. Sync and default-lane updates render with the synchronous loop to completion. The exact lane rules differ between versions, so check the source for the version you use.

`startTransition` and `useDeferredValue` are the main tools that put work in the interruptible lanes. An urgent update, such as typing, can then interrupt a large transition render.

## 11. The commit phase

After the render phase completes, React has a finished work-in-progress tree. The commit phase applies it. This phase is synchronous and cannot be interrupted. The user must never see a half-applied tree.

The phase has three sub-steps, then a deferred step.

1. Before mutation. React calls `getSnapshotBeforeUpdate` on class components. It reads from the DOM before any change happens.
2. Mutation. React walks the fibers using `flags` and `subtreeFlags`. It performs insertions, moves, updates, and deletions on the real DOM. It runs `componentWillUnmount` and cleanup functions for deleted fibers. It runs `useLayoutEffect` cleanups. It detaches refs.
3. Layout. React first sets `root.current = finishedWork`. The order matters. During `componentWillUnmount` the old tree is still current. In layout effects the new tree is current. Then React runs `componentDidMount`, `componentDidUpdate`, `useLayoutEffect` bodies, and attaches refs. These run after the DOM is changed and before the browser paints.
4. Passive effects. React runs `useEffect` cleanups and bodies after paint, scheduled as a separate task. If the render came from a discrete event such as a click, React flushes them synchronously at the end of the commit. React also flushes any pending passive effects before it starts the next render.

Layout effects block paint. Use them only when you must measure or mutate the DOM before the user sees it. Use `useEffect` for everything else.

## 12. Suspense and error handling

Suspense uses the same machinery. When a component reads data that is not ready, it throws a promise. In current React, `use` and framework data layers do this for you.

React catches the throw during the render phase. It unwinds the fiber stack to the nearest Suspense boundary. It renders the fallback. When the promise resolves, React retries the render of the suspended subtree.

For a transition, React avoids replacing already visible content with a fallback. It keeps the old UI until the new one is ready.

Error boundaries work the same way, with one difference. A thrown error unwinds to the nearest error boundary. That boundary re-renders with its error state.

## 13. What this means in practice

- Render must be pure. React can call a component more than once, pause it, or discard its result. Strict Mode in development deliberately renders twice to expose side effects.
- Do not mutate state or props. Reference checks drive bailouts, so mutation hides changes.
- Put side effects in event handlers or effects, never in the render body.
- Use stable, unique keys for list items.
- Do not define components inside other components.
- Keep state as low in the tree as possible. A state change re-renders that component and its subtree.
- For slow renders, first reduce the work. Then use `memo`, `useMemo`, or transitions. Measure with the React DevTools Profiler before you optimize.

## 14. Mental model summary

A state change creates an update with a lane and marks a path from the root to the changed fiber. The scheduler starts a render for the highest pending lane. The work loop walks the fibers, calls components, and reconciles each returned element list against the old child fibers. Each completed fiber records flags. When the whole tree is done, React applies the flags to the DOM in one synchronous commit and swaps the current pointer. Effects run after that.

Fiber's main idea is that each step of this process is a data object and a loop iteration, not a stack frame. That is what allows pausing, prioritizing, and discarding work.

If you want to read the source, start with `ReactFiberWorkLoop.js`, `ReactFiberBeginWork.js`, `ReactFiberCompleteWork.js`, `ReactChildFiber.js`, `ReactFiberHooks.js`, and `ReactFiberCommitWork.js` in the `react-reconciler` package.
