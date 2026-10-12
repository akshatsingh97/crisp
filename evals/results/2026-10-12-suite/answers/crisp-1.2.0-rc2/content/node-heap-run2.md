Your service most likely has a memory leak, so find it with heap snapshots. Raising the heap limit only delays the crash.

## Confirm it is a leak

1. Log `process.memoryUsage()` every minute. Watch `heapUsed`, `rss`, and `external`.
2. If `heapUsed` climbs steadily and never drops after garbage collection, you have a leak.
3. If `rss` grows but `heapUsed` stays flat, the leak is outside the JS heap. Check Buffers, native addons, or streams that are never closed.
4. If memory is stable but simply near the limit, raise the limit instead.

## Stopgaps

- Raise the limit with `node --max-old-space-size=4096 app.js`. The value is in MB. It must stay below the container or host memory limit.
- Restart automatically before the crash. With pm2, use `pm2 start app.js --max-memory-restart 1500M`. Kubernetes or systemd restarts also work.

## Find the leak

1. Start the service with `node --heapsnapshot-signal=SIGUSR2 app.js`.
2. After startup, run `kill -USR2 <pid>` to write a snapshot.
3. Wait 30 to 60 minutes under real traffic. Take a second snapshot, then a third.
4. Open the files in Chrome DevTools, Memory tab, using Load.
5. Select the last snapshot and choose the Comparison view against the first.
6. Sort by size delta or retained size. Look for object types that keep growing, such as arrays, Maps, strings, or closures.
7. Open the retainers panel on a suspect object. It shows what holds the object in memory.

Alternative: `node --heapsnapshot-near-heap-limit=3 app.js` writes snapshots automatically just before the crash.

Warning: taking a snapshot pauses the process. It also needs memory roughly equal to the heap size. Do this on staging or on one instance behind the load balancer, not on all production instances.

## Common causes

- Caches, Maps, or arrays that grow without a size limit or expiry
- Event listeners added on every request and never removed
- Timers or intervals that are never cleared
- Closures that keep large objects alive
- Request or session data stored in module-level variables
- Unbounded queues, or a producer faster than its consumer
- Connection pools or streams that are never closed

## Other tools

- `clinic heapprofiler` shows which code paths allocate memory.
- `node --inspect` with DevTools allows live heap profiling and allocation timelines.

If you share the comparison output or your heap growth pattern, I can help narrow down the cause.
