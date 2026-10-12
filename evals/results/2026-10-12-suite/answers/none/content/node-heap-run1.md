Answer first, short sentences, plain words.

**Find out whether it is a leak or a limit that is too low. Then fix the cause.**

**1. Check the heap trend.** Log `process.memoryUsage().heapUsed` every minute.
- If it climbs and never drops, you have a leak.
- If it rises and falls but peaks near the limit, the heap limit is too low for your load.

**2. Raise the limit while you investigate.** This buys time. It does not fix a leak.
```
node --max-old-space-size=4096 app.js
```
In a container, keep this value below the container memory limit. If it is above, the OS kills the process (OOM kill).

**3. Take heap snapshots.**
1. Start with `node --heapsnapshot-signal=SIGUSR2 app.js`.
2. Send `kill -USR2 <pid>` early, then again after the memory has grown.
3. Open both files in Chrome DevTools, under Memory. Choose "Comparison" view.
4. Sort by "Size Delta". The objects that grow the most point to the leak.

You can also run `node --inspect` and connect DevTools to the live process. Do not do this on a public port.

**4. Check the common causes.**
- Caches or Maps with no size limit or expiry. Use an LRU cache with a maximum size.
- Event listeners added on each request and never removed. Node warns about this with `MaxListenersExceededWarning`.
- Timers or intervals that are never cleared.
- Global arrays or objects that collect request data.
- Closures that keep large objects alive.
- Unbounded queues, or streams with no backpressure, when the producer is faster than the consumer.
- Per-request data attached to long-lived objects, such as a database connection or a metrics label with many unique values.

**5. Contain the crash while you fix it.**
- Run under a process manager (PM2, systemd, or Kubernetes) so the service restarts.
- Use `--heapsnapshot-near-heap-limit=3` to write a snapshot just before the crash. This gives you evidence from production.

Which Node version do you use, and does the service run in a container? With those two facts and the heap trend, I can narrow down the cause.
