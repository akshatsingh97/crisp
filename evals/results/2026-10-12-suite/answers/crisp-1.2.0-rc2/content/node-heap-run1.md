A crash after a few hours usually means a memory leak, so find what grows over time instead of only raising the limit.

1. Confirm the leak. Log `process.memoryUsage().heapUsed` every minute, or watch it in your metrics tool. If the value climbs and does not drop after garbage collection (GC), you have a leak.

2. Add a temporary fix to buy time. Raise the heap limit and restart the service on a schedule:
   ```
   node --max-old-space-size=4096 app.js
   ```
   The value is in MB. The default depends on the Node version and system memory. In a container, keep the limit below the container memory limit. Otherwise the kernel kills the process (OOMKilled) before Node can report an error. A bigger heap only delays the crash if there is a leak.

3. Capture heap snapshots. Start Node with `--heapsnapshot-signal=SIGUSR2`. Then run `kill -USR2 <pid>` at start, after one hour, and after two hours. Each signal writes a `.heapsnapshot` file.
   - A snapshot pauses the process and can need memory about twice the heap size. Do this on one instance, not all of production.
   - Alternatively, run `node --inspect` and connect Chrome DevTools at `chrome://inspect`.

4. Compare the snapshots. Open them in Chrome DevTools, Memory tab. Select the later snapshot and choose "Comparison" view. Sort by "Size Delta". Look for object types that keep growing. Open "Retainers" to see what holds them.

5. Check the common causes:
   - Unbounded caches or Maps with no size limit or expiry
   - Event listeners added on every request or reconnect and never removed
   - Global arrays or objects that collect data, such as logs or request history
   - Timers (`setInterval`) that are never cleared and hold references in closures
   - Large request or response bodies kept in memory instead of streamed
   - Unclosed resources such as database connections, sockets, or streams
   - Libraries with known leaks, so check their issue trackers

6. Fix the cause, then run the service again and confirm that `heapUsed` stays flat.

If the heap looks stable but the process still dies, check non-heap memory. `process.memoryUsage().rss` and `external` include Buffers and native addons. These do not appear in heap snapshots. If a snapshot is hard to read, tools such as `clinic.js` (`clinic heapprofiler`) or `memlab` can point to the leak faster.

If you share the snapshot comparison, the Node version, or the main libraries you use, I can narrow down the cause.
