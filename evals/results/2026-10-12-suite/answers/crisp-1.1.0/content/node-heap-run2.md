A crash after a few hours usually means a memory leak: objects stay referenced, so the garbage collector (GC, the automatic memory cleaner) cannot free them. Find the leak with heap snapshots, then fix the code. Raising the limit only delays the crash.

Steps:

1. Confirm the leak. Log `process.memoryUsage().heapUsed` every minute. If it climbs and never drops after GC, you have a leak.
2. Enable a heap snapshot trigger. Start the service with `node --heapsnapshot-signal=SIGUSR2 app.js`.
3. Take a snapshot when the service starts. Send `kill -USR2 <pid>`.
4. Take a second snapshot after memory has grown, for example 30 to 60 minutes later.
5. Open both `.heapsnapshot` files in Chrome DevTools, Memory tab. Select the second snapshot and choose the "Comparison" view.
6. Sort by "Size Delta". The constructors that grow the most point to the leak. Open "Retainers" to see what holds them.
7. Fix the cause, deploy, and watch `heapUsed` again.

Common causes:

- Unbounded caches or Maps. Add a size limit or TTL (time to live), or use an LRU cache (evicts least recently used entries).
- Event listeners added on every request and never removed.
- Timers (`setInterval`) that are never cleared.
- Global arrays or objects that collect data per request.
- Closures that capture large objects.
- Unbounded queues when a downstream service is slow.

Temporary mitigation while you debug:

- Raise the limit with `node --max-old-space-size=4096 app.js` (value in MB). Keep it below the memory of the host or container. If it is too high, the OS will kill the process (OOM kill) instead.
- Restart the service on a schedule or when memory passes a threshold. Use your process manager or orchestrator for this.

Risk: a heap snapshot pauses the process and needs memory about equal to the heap size. On a large heap, take it on one instance, not in a busy production node. Also note that the snapshot can contain sensitive data such as tokens and user data, so handle the file with care.

If you share the Node version, how you deploy (container or VM), and the top growing constructors from the comparison, I can help narrow it down.
