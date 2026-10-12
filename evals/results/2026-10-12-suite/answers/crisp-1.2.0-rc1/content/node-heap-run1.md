A crash after a few hours usually means a memory leak, so you must find what grows over time and fix it. Raising the heap limit only delays the crash.

**Quick stopgap**

1. Raise the limit: `node --max-old-space-size=4096 app.js`. The value is in MB. Keep it below the memory of the host or container.
2. In containers, check that the limit is not lower than the heap size. If it is, the OS kills the process (OOMKilled) before Node reports an error.

**Confirm it is a leak**

1. Log `process.memoryUsage()` every minute. Watch `heapUsed` and `rss`.
2. If `heapUsed` climbs steadily and never drops after garbage collection, you have a leak.
3. If `rss` grows but `heapUsed` stays flat, the leak is outside the heap. Look at Buffers, native addons, or streams.

**Find the leak**

1. Start the service with `node --inspect app.js`. Open `chrome://inspect` in Chrome and connect.
2. Open the Memory tab. Take a heap snapshot, run load for a few minutes, then take a second snapshot.
3. Select the second snapshot and choose "Objects allocated between Snapshot 1 and 2". Sort by retained size.
4. Open the retainers list of the largest objects. It shows which reference keeps them alive.

**Production option**

1. Start with `node --heapsnapshot-signal=SIGUSR2 app.js`.
2. Send `kill -USR2 <pid>` when memory is high. Node writes a `.heapsnapshot` file. Load it in Chrome DevTools.
3. Note that writing a snapshot pauses the process and needs free memory about the size of the heap. On a nearly full heap, it can crash the service. Take snapshots early, not at the limit.
4. You can also use `--heapsnapshot-near-heap-limit=3` to write snapshots automatically before a crash.

**Common causes**

- Unbounded caches or Maps. Add a size limit or TTL, or use an LRU cache.
- Event listeners added on each request and never removed. Node warns "MaxListenersExceededWarning" when this happens.
- Global arrays or objects that collect request data, logs, or metrics.
- Timers (`setInterval`) that hold references to large objects and are never cleared.
- Closures that capture large objects.
- Unresolved promises or queues that grow faster than they drain.
- Metric labels with unbounded values, such as user IDs in Prometheus labels.

**Tell me more**

If you share your Node version, framework, and a snapshot summary or the `memoryUsage` trend, I can narrow down the cause. I can also review code if you point me to the service.
