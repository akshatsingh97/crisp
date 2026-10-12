A heap that grows until the crash means a memory leak, and you must find what holds the objects. Raising the heap limit only delays the crash.

**Quick stopgap**

Raise the V8 heap limit (the memory pool for JavaScript objects). The default depends on your Node version and system memory.

```bash
node --max-old-space-size=4096 server.js
```

In containers, keep this value below the container memory limit. If it is higher, the OOM killer will end the process first.

**Confirm it is a leak**

1. Log `process.memoryUsage()` every minute. Watch `heapUsed` and `rss`.
2. If `heapUsed` climbs steadily and never drops after garbage collection, you have a leak.
3. If `rss` grows but `heapUsed` stays flat, the leak is outside the heap. Check Buffers, native addons, and streams.

```js
setInterval(() => {
  const m = process.memoryUsage();
  console.log(Math.round(m.heapUsed / 1048576) + ' MB heap, ' + Math.round(m.rss / 1048576) + ' MB rss');
}, 60000);
```

**Find the leak**

1. Start the service with `node --inspect server.js`.
2. Open `chrome://inspect` in Chrome and click your process.
3. In the Memory tab, take a heap snapshot after startup.
4. Apply normal load for some time. Take a second snapshot.
5. Select the second snapshot and choose the "Comparison" view. Sort by "Size Delta".
6. Look for object types that keep growing, such as arrays, Maps, strings, or closures.
7. Open the "Retainers" panel for those objects. It shows what keeps them alive.

Snapshots pause the process and use extra memory. In production, take them on one instance, not the whole fleet.

If you cannot attach a debugger, start with `--heapsnapshot-signal=SIGUSR2`. Then run `kill -USR2 <pid>` to write a snapshot file. You can also use `--heapsnapshot-near-heap-limit=3` (Node 16 and later) to capture snapshots just before a crash.

**Common causes**

- Unbounded caches or Maps with no eviction. Use an LRU cache with a size limit.
- Event listeners added on every request and never removed. Look for the `MaxListenersExceededWarning`.
- Global arrays or objects that collect request data.
- Timers or intervals that are never cleared and hold closures.
- Unresolved promises, or streams that are never consumed or closed.
- Per-request data stored in module-level variables.
- Large logging or metrics label sets, such as a user ID used as a metric label.

**If snapshots do not show the cause**

- Run `node --trace-gc server.js` to see whether garbage collection is running and reclaiming memory.
- Try `clinic heapprofiler` or `clinic doctor` for a guided view.
- Use the heap profiler in `--inspect` to see which functions allocate the most.

**Safety net**

Run the service under a process manager or orchestrator that restarts it on a crash. Set a memory-based alert so you can act before the crash. Treat restarts as a temporary measure only.

If you share your Node version, framework, and a heap snapshot comparison, I can help narrow it down.
