A heap out of memory crash after a few hours almost always means a memory leak (memory that your code keeps but never uses again), so your job is to find which objects pile up over time. First, confirm the pattern. Watch `process.memoryUsage().heapUsed` or your monitoring graph. If the line climbs steadily and never falls back after garbage collection (the automatic cleanup of unused memory), you have a leak. If it jumps once and crashes, you have one large allocation instead.

To find the leak, take heap snapshots (saved copies of everything in memory) at two points in time and compare them. Start the service with the inspector on, or write snapshots on a signal:

```
node --heapsnapshot-signal=SIGUSR2 server.js
kill -USR2 <pid>
```

Send the signal once after the service warms up, again an hour later, and open both `.heapsnapshot` files in Chrome DevTools under the Memory tab. Select the second snapshot and choose the Comparison view. Sort by size delta, and the object types that grew the most will point to the leak. Then open the Retainers panel for those objects to see which variable holds them.

The most common causes are these. A cache or Map that grows without a limit, such as one keyed by user ID or request ID. Event listeners added on each request but never removed. Timers or intervals that are never cleared. Global arrays that collect logs or results. Closures that hold large request objects. Unbounded queues when a downstream service is slow. If you use a cache, give it a maximum size, for example with the `lru-cache` package.

While you investigate, you can buy time in two ways. You can raise the limit with `node --max-old-space-size=4096 server.js`, where the number is megabytes. This delays the crash but does not fix the leak. You can also restart the process on a schedule or when memory passes a threshold, using your process manager or your container memory limit. If you run in Docker or Kubernetes, make sure that the Node limit is lower than the container limit, or the container may be killed first with no Node error.

If you share your Node version, your framework, and what the heap snapshot comparison shows, I can help you narrow down the exact cause.
