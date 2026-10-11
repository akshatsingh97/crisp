A crash after a few hours usually means a memory leak, so find what keeps growing and fix it. Raising the heap limit only delays the crash.

1. Confirm the leak. Log `process.memoryUsage().heapUsed` every minute. If it climbs and never drops after garbage collection (GC, the automatic memory cleanup), you have a leak.
2. Buy time. Run `node --max-old-space-size=4096 app.js` (the value is in MB). Keep the value below the memory of the host or container. Also restart the service on a schedule until you fix the leak.
3. Capture evidence before the crash. Run `node --heapsnapshot-near-heap-limit=3 app.js`. Node will write `.heapsnapshot` files as it nears the limit. This needs Node 14 or newer.
4. Compare snapshots. Open two snapshots in Chrome DevTools, under Memory, and use the Comparison view. Sort by size delta to find the object type that grows.
5. Trace the retainers. Select a growing object and read the Retainers panel. It shows which reference keeps the object alive.
6. Fix the cause and re-test. Watch `heapUsed` for several hours under realistic load.

Common causes:
- Caches or Maps with no size limit or expiry. Use an LRU cache (evicts the least recently used entries) with a maximum size.
- Event listeners added on every request and never removed.
- Timers (`setInterval`) that are never cleared.
- Global arrays or objects that collect request data.
- Closures that hold large objects, such as request or response objects.
- Unbounded queues when a downstream service is slow.

If heap size looks stable but the process still dies, check total memory with `process.memoryUsage().rss`. Buffers and native addons use memory outside the V8 heap (the JavaScript memory area). Also check for a container memory limit, which causes a different error.

If you share the Node version, your framework, and a heap snapshot summary, I can help narrow down the cause.
