Your service most likely has a memory leak, which means objects stay referenced and the garbage collector (GC, the automatic memory cleaner) cannot free them. Find the leak with heap snapshots. Raising the limit only delays the crash.

1. Confirm the trend. Log `process.memoryUsage().heapUsed` every minute. If it rises and never drops after GC, you have a leak.
2. Start the service with `node --heapsnapshot-signal=SIGUSR2 app.js`. Node will write a heap snapshot (a file of all live objects) each time it gets that signal.
3. Take a snapshot soon after start. Run `kill -USR2 <pid>`. Take a second one after memory has grown, and a third later.
4. Open the snapshots in Chrome DevTools, Memory tab. Select the latest snapshot and choose the "Comparison" view against the first one.
5. Sort by "Size Delta". Look for object types that grow in every snapshot. Open "Retainers" to see what holds them.
6. Fix the code that holds the references, then redeploy and watch the memory trend again.

Common causes:
- Unbounded caches or maps that never evict entries
- Event listeners added on every request and never removed
- Timers or intervals that are never cleared
- Global arrays or objects that collect data
- Closures that capture large objects
- Unclosed streams, sockets, or database connections

Temporary mitigations while you debug:
- Raise the heap limit, for example `node --max-old-space-size=4096 app.js`. This only buys time.
- Let a process manager such as PM2, systemd, or Kubernetes restart the service on a memory threshold.
- In production, take snapshots on one instance only. A snapshot pauses the process and can use as much memory as the heap itself, so it can trigger the crash early.

If you share your Node version, framework, and what the service does, I can narrow down the likely causes. I can also help read the snapshot output.
