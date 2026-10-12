A memory leak most likely causes the crash, so find what grows over time with heap snapshots, then fix the retention. Raising the heap limit only delays the crash.

## Quick mitigation

1. Raise the heap limit to buy time: `node --max-old-space-size=4096 app.js`. The value is in MB. Keep it below the memory limit of the container or host.
2. Restart the service on a schedule or on a memory threshold. Use PM2 `max_memory_restart` or a Kubernetes memory limit. This hides the leak and does not fix it.

## Find the leak

1. Confirm the trend. Log `process.memoryUsage()` every minute, or watch RSS in your monitoring. Heap used that climbs and never drops after garbage collection (GC, automatic memory cleanup) confirms a leak.
2. Start the service with `node --inspect app.js`. Open `chrome://inspect` in Chrome and attach.
3. Open the Memory tab. Take a heap snapshot after startup. Apply normal load for 10 to 30 minutes. Take a second snapshot.
4. Select the second snapshot and choose "Comparison" against the first. Sort by "Size Delta". Look for object types that grow without limit.
5. Click a growing object and read its "Retainers" panel. This shows what holds the object in memory.

## Production without a debugger

- Write a snapshot on demand with `v8.writeHeapSnapshot()`. For example, call it from a signal handler or an admin route that you protect.
- Start Node with `--heapsnapshot-near-heap-limit=3`. Node will write snapshots when memory nears the limit.
- Add `--heapsnapshot-signal=SIGUSR2` to write a snapshot when the process receives that signal.
- Warning: writing a snapshot pauses the process and can need memory up to about twice the heap size. Do it on one instance, not the whole fleet.
- Snapshots contain your data, such as tokens and user records. Store them securely.

## Common causes

- Caches or maps with no size limit or expiry. Use an LRU cache (least recently used eviction) with a maximum size.
- Event listeners added on each request and never removed. Node warns `MaxListenersExceededWarning` in this case, so check your logs.
- Global arrays or objects that collect request data, logs, or metrics.
- Closures that keep large objects alive, often inside timers or callbacks.
- `setInterval` timers never cleared.
- Unresolved promises or unbounded queues. Work arrives faster than the service can process it.
- Per-request labels in metrics libraries, such as user IDs. These create unlimited time series.
- Large result sets loaded into memory. Use streams or pagination instead.

## If the snapshots show no clear leak

- Your workload may simply need more memory. Check for large payloads, big JSON parsing, or large buffers. Raise the limit and add streaming where you can.
- If RSS grows but heap used stays flat, the leak is outside the V8 heap. Check Buffers, native addons, and `process.memoryUsage().external` and `arrayBuffers`.
- If the heap snapshot tool is hard to use, try `clinic heapprofiler` or `node --heap-prof`. These show which code allocates the most memory.

## Verify the fix

Run the same load test again. Heap used after GC must stay flat over several hours. You can force GC in a test by starting Node with `--expose-gc` and calling `global.gc()`.

If you share your Node version, framework, and a heap snapshot comparison summary, I can help narrow down the cause.
