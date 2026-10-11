A crash after a few hours usually means a memory leak. Raising the heap limit only delays the crash, so the real work is finding what's growing.

## 1. Confirm it's a leak

Log memory over time:

```js
setInterval(() => {
  const m = process.memoryUsage();
  console.log(`heapUsed=${(m.heapUsed/1e6)|0}MB rss=${(m.rss/1e6)|0}MB external=${(m.external/1e6)|0}MB`);
}, 60_000);
```

- **`heapUsed` climbs steadily and never drops after GC:** a JS-level leak. Go to step 3.
- **`rss` climbs but `heapUsed` is flat:** the leak is in Buffers or native addons (`external`, `arrayBuffers`).
- **Memory spikes and then crashes:** a single huge allocation, such as loading a big file or query result into memory.

## 2. Stopgap (not a fix)

```bash
node --max-old-space-size=4096 app.js
```

In containers, set it to about 75% of the memory limit. Newer Node versions respect cgroup limits, but check yours.

## 3. Find the leak

**Option A: heap snapshots (most reliable)**
```bash
node --inspect app.js
```
Open `chrome://inspect`, then the Memory tab. Take a snapshot after startup, put the service under load, then take a second and a third. Select the later snapshot and use the **Comparison** view to see which object types keep growing. Check **Retainers** to see what holds them.

**Option B: automatic snapshot near the limit**
```bash
node --heapsnapshot-near-heap-limit=3 app.js
```
This writes snapshots just before the crash, which suits production. Load them in DevTools.

**Option C: on-demand snapshot in production**
```bash
node --heapsnapshot-signal=SIGUSR2 app.js
kill -USR2 <pid>
```

Snapshots pause the process and need roughly 2x the heap in memory, so use a staging box or a single instance if you can.

## 4. Usual suspects

| Cause | What to look for |
|---|---|
| Unbounded caches or maps | Module-level `Map`, `Set`, or object keyed by user, request, or session ID with no eviction. Use an LRU such as `lru-cache` with a max size and TTL. |
| Event listener leaks | Adding `.on()` per request without `.off()`. A `MaxListenersExceededWarning` is a strong hint. |
| Timers and intervals | `setInterval` never cleared, or closures capturing large objects. |
| Closures holding references | Request or response objects captured in long-lived callbacks. |
| Unresolved promises | Promises that never settle, so their closures stay alive. |
| Unbounded queues | Producers faster than consumers, such as a job queue, log buffer, or stream without backpressure. |
| Global arrays | Request logs, metrics, or audit trails pushed to forever. |
| Metrics labels | Prometheus or similar labels with high cardinality, such as user IDs or URLs. |
| DB or HTTP clients | Creating a new client or connection pool per request. |
| Large payloads | Reading entire files or result sets instead of streaming. |

## 5. Verify the fix

Run the service under realistic load and watch whether `heapUsed` forms a sawtooth pattern (rises, GC drops it back to a stable baseline). A staircase that keeps rising means it's still leaking.

If you can share your Node version, a heap snapshot comparison (the top growing constructors), or your framework and the code that handles requests, I can help narrow it down. If you point me at the code in this directory, I can also scan it for the patterns above.
