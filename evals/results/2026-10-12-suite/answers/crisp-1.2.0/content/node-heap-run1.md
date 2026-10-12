Your service most likely has a memory leak, so find what grows over time and fix it. A bigger heap only delays the crash. The heap is the memory V8 uses for JavaScript objects.

Short-term mitigation:
1. Raise the limit: `node --max-old-space-size=4096 app.js`. The value is in MB. Keep it below the memory of the container or host.
2. Let PM2 or Kubernetes restart the process after a crash. This hides the leak and does not fix it.

Confirm the leak:
1. Log `process.memoryUsage().heapUsed` every minute.
2. If the value climbs steadily and does not drop after garbage collection, you have a leak.

Find the leak:
1. Start the service with `node --inspect app.js`. Open `chrome://inspect` in Chrome and connect.
2. In the Memory tab, take a heap snapshot.
3. Send realistic traffic for several minutes.
4. Take a second snapshot. Select it and switch to the Comparison view.
5. Sort by size delta. The object types that grow the most point to the leak.
6. Open the retainers list for those objects. It shows which reference keeps them alive.

Production options:
- Start with `--heapsnapshot-signal=SIGUSR2`. Then run `kill -USR2 <pid>` to write a `.heapsnapshot` file. Do this on one instance only. Writing a snapshot pauses the process and needs extra memory.
- Use `--heapsnapshot-near-heap-limit=3` to write snapshots just before the crash. Writing near the limit is slow and can fail on its own. Check that your Node version supports the flag.
- If you cannot attach a debugger, run `node --heap-prof app.js` in staging. It writes a sampling profile that shows where allocations happen.

Common causes:
- In-memory caches or Maps with no size limit. Use an LRU cache with a maximum size and a TTL (time to live).
- Event listeners added per request and never removed. Watch for `MaxListenersExceededWarning` in your logs.
- Global arrays or objects that collect data for each request.
- `setInterval` timers that are never cleared.
- Closures that hold large objects, such as request or response objects.
- Streams, database connections, or promises that never close or resolve.
- Metrics with high-cardinality labels, such as a user ID or URL in a label.

After the fix, run the service under load again and watch `heapUsed`. It must level off and stay flat.
