# Debugging a Node.js "heap out of memory" crash

A crash after a few hours usually means a **memory leak**, where the heap grows steadily until it hits the limit. Raising the limit only delays the crash. The steps below are in the order I'd do them.

## 1. Confirm it's a leak

Log memory over time:

```js
setInterval(() => {
  const m = process.memoryUsage();
  console.log(`heapUsed=${(m.heapUsed/1e6)|0}MB rss=${(m.rss/1e6)|0}MB`);
}, 60_000);
```

- **Sawtooth pattern** (rises, then drops after GC): healthy.
- **Staircase that never comes back down:** leak.
- **High `rss` but flat `heapUsed`:** native memory, such as Buffers, native addons, or streams. Heap snapshots won't show this.

## 2. Buy time (a stopgap)

```bash
node --max-old-space-size=4096 app.js
```

In containers, keep this below the container memory limit, or the OOM killer will end the process first.

## 3. Capture heap snapshots

Don't wait for the crash. Take snapshots while the leak is growing:

```bash
node --heapsnapshot-signal=SIGUSR2 app.js
kill -USR2 <pid>   # run at hour 0, then again an hour or two later
```

Or write one on the way out:

```bash
node --heapsnapshot-near-heap-limit=2 app.js
```

## 4. Compare the snapshots

1. Open Chrome DevTools, go to **Memory**, and click **Load**.
2. Load the later snapshot and choose the **Comparison** view against the earlier one.
3. Sort by **Size Delta** or **# Delta**.
4. Click a growing object and read its **Retainers** panel. It shows what is holding the object in memory.

## 5. Common culprits

| Cause | Typical fix |
|---|---|
| Unbounded caches or Maps (`cache[key] = ...` with no eviction) | Use an LRU with a max size and TTL |
| Event listeners added per request and never removed | `removeListener`, or `once`. Watch for `MaxListenersExceededWarning`. |
| Global arrays or objects that only grow (logs, metrics, request history) | Cap or flush them |
| Timers or intervals never cleared | `clearInterval` on cleanup |
| Closures that capture large objects | Don't hold references longer than needed |
| Unresolved promises piling up, or unbounded queues | Add backpressure and timeouts |
| Per-request metric labels (e.g. user ID in Prometheus labels) | Use low-cardinality labels |
| Streams not consumed or destroyed | Use `pipeline()` and handle errors |

## 6. Tooling

- **`clinic doctor` / `clinic heapprofiler`** gives guided diagnosis.
- **`node --inspect`** lets you attach DevTools to a running process. Be careful doing this in production.
- **APM tools** (Datadog, New Relic, etc.) can track heap over time and across deploys.

## 7. Verify the fix

Run a load test and watch `heapUsed` stay flat across several GC cycles.

---

If you share your Node version, framework, how you deploy (container or bare metal), and the memory graph, I can narrow it down. If the code is in this directory, I can also search it for the usual leak patterns.
