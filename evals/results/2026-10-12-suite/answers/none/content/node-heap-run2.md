Find what is growing in memory, then fix that. Raising the heap limit only delays the crash.

**1. Confirm it is a leak.** Memory that rises steadily and never falls after garbage collection means a leak. Log `process.memoryUsage().heapUsed` every minute, or watch it in your monitoring tool. If it rises with traffic and falls when traffic stops, you need more headroom, not a leak fix.

**2. Take heap snapshots.**
1. Start the service with `node --inspect app.js`, or send `SIGUSR2` after you start it with `--heapsnapshot-signal=SIGUSR2`.
2. Take one snapshot early and one after memory has grown, for example 30 minutes later.
3. Open both in Chrome DevTools (Memory tab). Select the second snapshot and set the view to "Objects allocated between Snapshot 1 and Snapshot 2".
4. Sort by retained size. Open the biggest groups and read the "Retainers" panel to see what holds them.

On a production host, use `heapdump` or `v8.writeHeapSnapshot()`. A snapshot pauses the process and needs about twice the heap size in free memory, so do it on one instance only.

**3. Check the usual causes.**
- Caches or maps with no size limit or expiry. Use `lru-cache` with a `max`.
- Event listeners added on every request and never removed.
- Timers or intervals that are never cleared.
- Global arrays or objects that collect data, such as request logs or metrics labels with unbounded values.
- Closures that keep large objects, such as request or response objects.
- Unresolved promises or growing queues, where producers are faster than consumers.

**4. Add a temporary safety net.** Raise the limit with `node --max-old-space-size=4096 app.js` (value in MB). Keep it below the memory limit of your container or host. Also restart the process automatically with a process manager or Kubernetes. This keeps the service up while you look for the leak.

**5. Verify the fix.** Run a load test and watch `heapUsed` for several hours. It should rise and fall in a stable band.

If you share your Node version, your framework, and a heap snapshot summary, I can help you read it. If the code is in this directory, I can search it for the patterns above.
