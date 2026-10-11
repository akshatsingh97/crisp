Your service most likely has a memory leak, so find what grows over time with heap snapshots. Raising the heap limit only delays the crash.

1. Confirm the growth. Log `process.memoryUsage()` (heapUsed and rss) every minute. If heapUsed climbs and never drops after garbage collection (GC, automatic memory cleanup), you have a leak.
2. Add a short-term fix. Run `node --max-old-space-size=4096 app.js` (value in MB) and set a restart policy, such as PM2 or Kubernetes. Keep the limit below the container memory limit.
3. Capture snapshots. Start with `node --inspect app.js` and open `chrome://inspect`. Take one snapshot after warm-up and another after some hours of load.
4. Compare the snapshots. In Chrome DevTools, select the second snapshot and choose the Comparison view. Sort by "Size Delta". Open the largest growing objects and read their retainers (what holds them in memory).
5. Take a snapshot in production without a debugger. Start with `--heapsnapshot-signal=SIGUSR2`, then run `kill -USR2 <pid>`. Snapshots can pause the process and use memory about equal to the heap, so do this on one instance.
6. Fix the cause and redeploy. Check that heapUsed now stays flat.

Common causes:
- Unbounded caches or Maps with no size limit or expiry
- Event listeners added on each request and never removed
- Timers or intervals that are never cleared
- Global arrays or objects that collect request data
- Closures that keep large objects alive
- Unclosed streams, database connections, or sockets

If you cannot reproduce the leak locally, replay production-like traffic against a test instance. Tools such as `clinic heapprofiler` or `autocannon` can help.

If you share the heap snapshot findings or your main dependencies, I can help narrow down the cause.
