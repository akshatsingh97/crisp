A heap out of memory crash after a few hours almost always means a memory leak (memory that your code keeps but never uses again), so find what grows over time instead of only raising the limit. First, confirm the leak. Log `process.memoryUsage().heapUsed` every minute, or watch it in your monitoring tool. If the number climbs steadily and never drops after garbage collection, you have a leak.

To buy time while you investigate, raise the heap limit with `node --max-old-space-size=4096 app.js`. This only delays the crash, so do not treat it as the fix.

Next, take heap snapshots (saved copies of everything in memory). Start the service with `node --inspect app.js`, open `chrome://inspect` in Chrome, and attach to the process. Take one snapshot soon after startup and another after memory has grown. In the second snapshot, choose the "Comparison" view against the first one. Sort by "Size Delta" and look for object types that keep growing. The "Retainers" panel then shows what holds each object in memory.

If you cannot attach a debugger in production, you can write a snapshot from inside the process. Add this code, then send the signal `kill -USR2 <pid>` at two different times and compare the files in Chrome DevTools.

```js
const v8 = require('v8');
process.on('SIGUSR2', () => {
  console.log('Wrote', v8.writeHeapSnapshot());
});
```

You can also make Node write a snapshot just before it crashes, with `node --heapsnapshot-near-heap-limit=1 app.js`. Snapshots pause the process and need memory of their own, so run them on one instance and not on all of them.

These are the most common causes in Node services:

An in-memory cache or a plain object or `Map` that gets new keys on every request and never removes old ones. Add a size limit or expiry, for example with the `lru-cache` package.

Event listeners that your code adds on each request or connection and never removes. A warning that says `MaxListenersExceededWarning` in your logs points to this.

Timers or intervals that are never cleared, and closures (functions that remember their surrounding variables) that keep large objects alive.

Global arrays or maps that collect data such as logs, metrics, or request history.

Unclosed resources such as database connections, streams, or sockets.

Once you find the cause, fix it, deploy, and watch `heapUsed` for several hours. A healthy service shows a saw-tooth pattern that returns to about the same low point after each garbage collection. If you share a snapshot comparison or your framework and main dependencies, I can help read the result.
