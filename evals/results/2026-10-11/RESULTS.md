# Crisp benchmark, 2026-10-11

- Scenarios: 12 (8 questions, 4 document tasks)
- Runs per scenario: 2
- Claude Code: 2.1.296 (Claude Code)
- Isolated HOME: yes
- Judge: a separate `claude -p` run with no plugins. It does not see the condition name.

## Summary

| Measure | none | crisp | simple-english |
|---|---|---|---|
| Fact coverage (judge, %) | 93 | 97 | 96 |
| Accuracy (judge, 1-10) | 8.5 | 8.4 | 8.5 |
| Clarity (judge, 1-10) | 9.0 | 8.8 | 8.6 |
| Scan speed (judge, 1-10) | 8.9 | 8.5 | 7.3 |
| Crisp checker score (/100) | 74 | 96 | 88 |
| Words per answer | 224 | 192 | 213 |
| Longest sentence (words) | 20.9 | 18.7 | 24.8 |
| Sentences over the limit (per answer) | 1.0 | 0.2 | 2.2 |

## Fact coverage per scenario (covered / total)

| Scenario | Type | none | crisp | simple-english |
|---|---|---|---|---|
| charge-retry | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| react-race | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| force-push | reply | 3/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| jwt-storage | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| node-heap | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| pg-index | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| docker-latest | reply | 3/4 / 4/4 | 4/4 / 4/4 | 3/4 / 3/4 |
| cors | reply | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |
| readme-install | doc | 4/5 / 4/5 | 4/5 / 4/5 | 5/5 / 4/5 |
| runbook-disk | doc | 5/5 / 5/5 | 5/5 / 5/5 | 5/5 / 5/5 |
| error-413 | doc | 2/4 / 3/4 | 4/4 / 3/4 | 3/4 / 4/4 |
| release-notes | doc | 4/4 / 4/4 | 4/4 / 4/4 | 4/4 / 4/4 |

## Errors the judge found

- none / charge-retry: "Don't retry card declines (4xx errors)" is imprecise: 4xx covers more than declines, and 409 and 429 are 4xx errors that the answer itself says to retry.
- none / charge-retry: "Retry only on network errors, 5xx responses, and rate limits" does not match its 409 conflict advice. The 409 retry is a separate case, so the list reads as inconsistent.
- none / charge-retry: Idempotency keys with an attempt number ("order ID plus an attempt number") are risky as written. If the attempt number increments on each retry, the key changes and the protection is lost. This contradicts the "reuse on every retry" point.
- none / charge-retry: "Stripe returns an error" when parameters differ is correct, but the answer leaves out that the error is returned even if the first request failed. This is minor.
- none / charge-retry: The answer says that reusing a key with different parameters returns an error that is 'safe' but 'shows the key is being reused when it shouldn't be'. That is slightly confusing, because a key reused with different parameters is often a bug. The answer is not clearly wrong, though.
- none / charge-retry: The answer says 'Keys are kept for at least 24 hours'. Stripe documents that keys can be removed after they are at least 24 hours old. 'At least' is acceptable, but a reader may take it as a guaranteed retention period.
- none / charge-retry: The answer says 'SDK retries: the official Stripe libraries can add idempotency keys automatically when you configure retries'. That is broadly correct, but it depends on the library and version. The answer does not say so.
- crisp / charge-retry: "Do not retry 4xx card errors with the same key, because Stripe returns the saved result" is misleading: Stripe saves and replays the result of the first request, including 4xx errors, so retrying with the same key just returns the same error. The point should be that a corrected request needs a new key, not that retrying is dangerous.
- crisp / charge-retry: "Retry only on network errors, timeouts, and 5xx responses" is too narrow. Stripe also saves 5xx results, so a same-key retry replays the saved 500. Stripe's guidance is that retrying with the same key is safe in any case where the outcome is unknown.
- crisp / charge-retry: "Stripe keeps keys for at least 24 hours" is slightly off. Stripe says keys can be removed once they are at least 24 hours old, so 'at least' reads as a guarantee of longer retention.
- crisp / charge-retry: The claim that `maxNetworkRetries` 'sets a key automatically' is only partly right. The library generates a key for its own retries of POST requests, but the answer doesn't say this applies per call and isn't reused across separate calls. It also says 'You must set one yourself' without noting that this is a client-library detail that differs by SDK.
- crisp / charge-retry: The claim that 'Recent SDKs add idempotency keys for their own retries' is broadly accurate for Stripe's official libraries, but the answer does not say which SDKs or versions. This is vague rather than wrong.
- crisp / charge-retry: The answer says to store the key before the first call. It does not say to store the key with the order. This is a minor gap and does not mislead.
- crisp / charge-retry: The answer treats the create-charge API as the current Stripe recommendation. Stripe now steers new integrations toward PaymentIntents. This is a minor omission and does not make any statement false.
- simple-english / charge-retry: Stripe's "create-charge API" (Charges) is legacy; the answer doesn't mention PaymentIntents, which Stripe recommends. The advice still applies, though.
- simple-english / charge-retry: "Stripe keeps keys for at least 24 hours" is slightly off. Stripe says keys can be removed after they are at least 24 hours old, so it is a minimum, not a guarantee of how long they are kept. This is a minor point.
- simple-english / charge-retry: Using an order ID or cart ID as the key is not always safe. If the first attempt is declined and the customer retries the same order with a new card, the same key returns the cached decline. The answer does not say so.
- simple-english / charge-retry: Saying Stripe's libraries "attach a key automatically" is mostly right for stripe-node's network retries, but the answer doesn't say this is library-specific.
- simple-english / charge-retry: The example key `order_8841_attempt_1` contains "attempt_1", which suggests a per-attempt key. That conflicts with the advice to reuse one key across all retries and could mislead readers into incrementing the attempt number.
- simple-english / charge-retry: The answer says a PaymentIntent retry "cannot create a second payment". That is only true if you reuse the same PaymentIntent object. Creating a new PaymentIntent on each retry can still double-charge unless you also use an idempotency key.
- simple-english / charge-retry: The answer says an order or cart ID protects against a double-click on the pay button. That is only true if the same key is reused for the same request parameters. Stripe also warns that keys can be pruned after 24 hours, and the answer states this only as a minimum.
- none / react-race: The Fix 2 snippet doesn't guard setError or loading state, and it doesn't reset the previous user's data. Related details mention these points, so this is a minor gap rather than an error.
- none / react-race: Fact 4 is only implied: both code samples include [userId] in the dependency array, and the text says the effect fires each time userId changes. The answer never states it as a requirement.
- none / react-race: Minor: the Strict Mode bullet says React 'mounts, unmounts and remounts effects' and calls the double fetch intentional. That is accurate for development, but it can read as if it explains the user's bug.
- none / react-race: Minor: the Fix 2 snippet leaves out setLoading and setError(null) resets, and it doesn't define setError. This is a small omission.
- crisp / react-race: The first AbortController example calls setUser and setError without showing they exist, and it does not check res.ok. This is minor.
- crisp / react-race: The answer implies `userId` is in the dependency array by showing `[userId]` in the examples. It never says this needs to be there, so fact 4 is covered only implicitly.
- crisp / react-race: The claim that 'React does not cancel the old effect's async work' is accurate. The explanation of why the stale data appears is slightly informal.
- crisp / react-race: The first example's .then(setUser) path in the AbortController snippet is fine, but the answer's claim that the cleanup 'does not cancel the old request unless you write that code' is true; no error. Minor: the AbortController snippet references setError without defining it, and a late non-abort response can still be handled after abort only if the body parse resolves, which is a negligible edge case.
- simple-english / react-race: Slightly misleading: "React does not cancel the old request when the effect runs again" is fine, but "If you use only one, the flag is the more important part" is a mild oversimplification (abort alone also prevents the late setState because the promise rejects with AbortError).
- simple-english / react-race: The dependency-array point is framed as causing 'stale data for a different reason' without explaining that a missing userId would prevent refetching entirely; it is brief but not wrong.
- simple-english / react-race: Both snippets show [userId] in the dependency array, but the answer never explains that userId must be listed there. Fact 4 is only implied by the code.
- simple-english / react-race: The AbortController example has a minor gap. It calls setUser(data) and setError(err) without defining them. This is normal for a snippet and is not misleading.
- crisp / force-push: Step 2 `git log HEAD..origin/<branch>` lists remote commits not in local HEAD, which after a rebase may include your own pre-rebase commits (rewritten with different hashes). The 'list is empty' check is therefore unreliable. A better check is `git range-diff` or inspecting the author of those commits. The 'or you know those commits are in your rebase' clause only partly covers this.
- crisp / force-push: The claim that force pushing 'updates' a PR and that 'existing review comments can lose their position' is broadly true but is stated loosely. Comments are usually marked outdated rather than lost.
- simple-english / force-push: Slightly misleading: `--force-with-lease` only protects against changes since your last fetch; if a background fetch updated the remote-tracking ref, the lease can still overwrite unseen work. The answer says it refuses if the remote changed since your last fetch, which is roughly right but overstates the protection.
- simple-english / force-push: Minor: saying 'you must rewrite the remote history' is slightly overstated, since rebasing is not always required, and 'push to a shared branch such as main' implies the main branch is the only concern.
- none / jwt-storage: Calling localStorage 'often acceptable' and a 'reasonable compromise' understates the risk, since a strong CSP does not remove XSS exposure.
- none / jwt-storage: The claim that an attacker can use a stolen token 'from anywhere' is true for bearer tokens, but the answer doesn't say that token binding or short lifetimes limit this.
- none / jwt-storage: The in-memory access token is presented as a safe fix, but XSS can still call the refresh endpoint to get a new token. The answer only says this about cookies.
- none / jwt-storage: The claim 'It isn't vulnerable to CSRF' is accurate but could mislead if read as the app being safe overall. The answer does not point out that an XSS attacker can still act as the user from inside the page with an in-memory token, so the recommended pattern is only partly protective.
- none / jwt-storage: Saying 'SameSite covers most of it' is slightly overconfident. SameSite=Lax does not protect against same-site attacks, and some older browsers do not support it.
- crisp / jwt-storage: Slightly misleading ending: says a cookie 'only prevents token theft', but a stolen token and injected-script requests are different risks. The statement is mostly correct though it may understate that XSS still allows full account abuse.
- crisp / jwt-storage: Calling SameSite=Lax/Strict plus an optional CSRF token sufficient is a simplification. Lax still allows some top-level GET requests, and same-site subdomain attacks are not covered.
- crisp / jwt-storage: Step 1 of the preferred setup says to send the access token in a cookie, then step 3 adds a refresh token cookie. The sequence is slightly muddled but not wrong.
- crisp / jwt-storage: The opening line says localStorage is acceptable only if you accept the risk, which is fine. 'Never store a long-lived refresh token there' is stated as absolute, but it is a common best practice, not a strict rule.
- simple-english / jwt-storage: Describing the refresh-token cookie as restoring the session is fine, but the answer never says that the refresh endpoint needs its own CSRF protection, since it relies on a cookie.
- simple-english / jwt-storage: SameSite=Lax is described as blocking 'most CSRF'. That is broadly right but slightly overstated, because Lax still allows top-level GET navigations.
- none / node-heap: `--heapsnapshot-signal=SIGUSR2` is correct, but the claim that snapshots need 'roughly 2x the heap in memory' is an approximation presented as fact.
- none / node-heap: 'Newer Node versions respect cgroup limits' is vague. Node's default heap sizing is only partly cgroup-aware, and the answer does not say which versions, so the reader may wrongly assume the default is safe in containers.
- none / node-heap: 'Memory spikes and then crashes: a single huge allocation' is oversimplified, because a spike can also come from a burst of concurrent requests.
- none / node-heap: `--heapsnapshot-near-heap-limit=2` is not strictly 'on the way out'. It writes snapshots as the heap nears its limit, which can itself use a lot of memory and slow or crash the process.
- none / node-heap: The `kill -USR2` step is under-explained. It does not say the snapshot signal handler blocks the process while the file is written, which matters in production.
- none / node-heap: The Chrome DevTools Comparison view gives the best results when you load the earlier snapshot first. The answer does not say which to load first.
- crisp / node-heap: Calling the --heapsnapshot-signal=SIGUSR2 approach 'without a debugger' is accurate, but the answer never mentions that the flag must be set at startup, so the process has to be restarted before a snapshot can be taken. It does say 'Start with', so this is only a minor gap.
- crisp / node-heap: The advice to 'Keep the limit below the container memory limit' is correct but gives no margin. Native memory, buffers and the stack also count toward the container limit, so the heap limit should sit well below it.
- crisp / node-heap: 'Take one snapshot after warm-up and another after some hours of load' is vague. Snapshots taken closer together, such as 10–30 minutes apart under steady load, are often enough, and waiting hours risks the crash happening first.
- simple-english / node-heap: Slight imprecision: "If it jumps once and crashes, you have one large allocation instead" is oversimplified, because a sudden spike can have other causes.
- simple-english / node-heap: The advice to set the Node limit lower than the container limit is correct, but it is not precise. The answer does not say that --max-old-space-size covers only the old-generation heap, so total process memory is higher.
- simple-english / node-heap: The answer is written as dense paragraphs with no headings or numbered steps, so the reader cannot scan quickly. This hurts scan, not accuracy.
- simple-english / node-heap: The "--heapsnapshot-near-heap-limit=1" flag is described as writing a snapshot "just before it crashes". That is roughly right. But snapshotting near the limit can itself run out of memory and fail, and the answer doesn't say so.
- simple-english / node-heap: The SIGUSR2 handler writes snapshots from inside the process. The answer says to run it "on one instance" because snapshots pause the process. It doesn't say that writeHeapSnapshot blocks the event loop and needs roughly twice the heap in extra memory, so this can crash a process that is already near its limit.
- simple-english / node-heap: The answer says heapUsed "never drops after garbage collection" confirms a leak. A steadily rising heapUsed can also come from lazy garbage collection or legitimate load growth. Checking it after forced GC, or using the post-GC low points, would be more accurate.
- simple-english / node-heap: The 4096 MB example for --max-old-space-size is given with no mention that it should fit the container or host memory limit. Otherwise the process may be OOM-killed, so the crash is not avoided.
- none / pg-index: Says CREATE INDEX CONCURRENTLY does 'two table scans' and implies it is simply slower; fine, but 'Bloat on a busy table' claim is vague and not a well-established concern.
- none / pg-index: Says 'CONCURRENTLY isn't supported on the parent' for partitioned tables and to 'build on each partition, then attach'; this is roughly right (use CREATE INDEX ON ONLY parent, then concurrent per-partition, then ATTACH) but the omitted ON ONLY step is misleading.
- none / pg-index: Setting statement_timeout = 0 is advised as protection from a 'global timeout'; fine, but lock_timeout of 5s may cause the build to fail and leave an invalid index, which is not warned about.
- none / pg-index: Index size estimate of '10–30% of table size' is a loose guess presented as typical.
- none / pg-index: Claims CREATE INDEX CONCURRENTLY is 'not supported on the parent' of a partitioned table as a reason for a different approach; this is true (must build on partitions then attach), but the answer gives no guidance, leaving it vague.
- none / pg-index: States concurrent builds take 'roughly 2–3x' the time of a plain build; this is a loose rule of thumb, not a documented figure, and can vary a lot.
- none / pg-index: Says a long-running transaction 'blocks the finish' and that cancelling leaves invalid index; mostly correct, but a uniqueness violation or deadlock failing is only one cause, and the phrasing 'Don't leave invalid indexes around, because they still add write overhead' is correct but omits that an invalid unique index still enforces uniqueness checks on inserts.
- crisp / pg-index: Says concurrent build 'scans the table twice' and implies it is mainly slower; fine, but 'Duplicate values in a UNIQUE index cause this failure' is correct only for unique indexes and is presented without that qualification being prominent.
- crisp / pg-index: Says the build 'takes brief locks at the start and end' and that lock_timeout prevents blocking; actually CONCURRENTLY takes a SHARE UPDATE EXCLUSIVE lock for the whole build (blocks other DDL/vacuum), so 'brief locks' is slightly misleading.
- crisp / pg-index: Says 'Long transactions stall the build: waits for every older open transaction'; true, but advice to 'end idle-in-transaction sessions' is risky production guidance without caution.
- crisp / pg-index: Step 2 is slightly misleading: CONCURRENTLY waits for transactions that could hold older snapshots, including ones that start before each phase. It does not only wait for old ones at the start. The advice to end or wait out old ones is still reasonable.
- crisp / pg-index: Step 3 rationale is loose. lock_timeout makes the build fail instead of queuing behind a conflicting lock. The answer implies a stall-avoidance effect but does not say the build may fail and need a retry, and that failure can leave an INVALID index.
- crisp / pg-index: 'Scans the table twice' is correct. But 'sorting can use temporary files' and the disk-space note omit that a failed build wastes that space. This is minor.
- crisp / pg-index: The partitioned-table note is correct in substance. It omits that the parent index stays invalid until all partition indexes are attached. This is minor.
- simple-english / pg-index: Partitioned tables: CREATE INDEX CONCURRENTLY is not supported on a partitioned parent, which is right. The advice to build on each partition and then create the index on the parent is incomplete: it should be CREATE INDEX ON ONLY parent, followed by ALTER INDEX ... ATTACH PARTITION. A plain CREATE INDEX on the parent would build non-concurrently and lock partitions.
- simple-english / pg-index: The line 'a single long-running transaction can stall it' is correct. But 'end or wait for them' is risky advice for production because it could mean killing application transactions.
- simple-english / pg-index: The temp-space figure of 20 to 40 percent of the table size is given as a rule of thumb with no basis. Index size depends on the column, so this is imprecise.
- simple-english / pg-index: SET lock_timeout = '5s' is in the example without explanation. It can make the concurrent build fail at its brief lock steps and leave an invalid index, and the answer never says so.
- simple-english / pg-index: The unique-index remark is only partly right: a duplicate causes the failure, and the invalid index remains. The answer does not say whether 'check for duplicates first' applies to a non-unique index.
- simple-english / pg-index: The build "waits for older transactions to finish" and "scans the table twice" are correct, but the claim that an invalid index "slows down every write" is true only for the index maintenance. It is fine in practice, though slightly imprecise.
- simple-english / pg-index: The pg_index query casts the index name with ::regclass, which is fine, but it does not check the schema. This is a minor omission.
- simple-english / pg-index: Setting statement_timeout to 0 is advised without noting that lock_timeout may still matter. This is a minor omission.
- none / docker-latest: The offer to scan Dockerfiles with the remark that none were seen in the working directory is irrelevant to the question, though harmless.
- none / docker-latest: The answer does not say that pinning needs regular rebuilds to pick up security patches. Pinning an old digest without rebuilding can leave known CVEs in place. This is an omission, not a false statement.
- crisp / docker-latest: The claim that registries and tools treat :latest as mutable so cached layers can be stale is vague and partly misleading: mutability is a property of the tag itself, and stale caches are mainly a local-build issue.
- crisp / docker-latest: The 'Risk' section says to update the pin on a regular schedule, which implies rebuilding but never says to rebuild images regularly to pick up patches (including patches within the same pinned tag).
- simple-english / docker-latest: "A digest never changes, so the build always uses the same bytes" is slightly overstated: the tag-plus-digest form is fine, but the answer does not mention that the digest must be updated to receive patches, and a registry can remove old digests.
- simple-english / docker-latest: "you must not" is stronger than the usual guidance (it is a strong recommendation, not a hard rule), though not seriously misleading.
- simple-english / docker-latest: The answer says a pinned image "does not receive security patches by itself", but it does not say to rebuild regularly to pick up patches in the same tag, which can leave readers thinking updates only come through version bumps.
- none / cors: Minor: the Spring Boot @CrossOrigin snippet is shown without noting that it does not cover Spring Security setups, which need separate CORS configuration.
- none / cors: Minor: the answer says the `no-cors` mode 'doesn't fix anything', which is slightly overstated, since it does let a request be sent. Its main point, that the response is unreadable, is correct.
- none / cors: The nginx snippet is shown without any mention that preflight OPTIONS handling needs additional config (return 204 plus Allow-Methods/Headers), so it will not fully work for preflighted requests.
- none / cors: Redirect point is vague: a redirect can fail a preflight, but a simple cross-origin redirect does not itself cause this error.
- none / cors: Spring `@CrossOrigin` and the Django note omit the credentials caveat, which is a minor omission rather than an error.
- crisp / cors: The raw headers example omits Access-Control-Allow-Credentials and doesn't mention that the server must echo the request origin if multiple origins are allowed, but this is minor.
- crisp / cors: Minor: the "Do not use * in production for private APIs" advice is fine, but the answer doesn't note that FastAPI's allow_headers=["*"] combined with credentials is not allowed with wildcard origins; not stated incorrectly though.
- simple-english / cors: Says a preflight is triggered by 'a method other than GET or POST'. In fact HEAD is also a simple method, and the main triggers are PUT, DELETE and PATCH.
- simple-english / cors: Says preflight is triggered by 'a custom header such as Authorization'. This is fine, but the answer leaves out that the preflight must also include Access-Control-Allow-Origin. It does list that header, so this is a minor point only.
- simple-english / cors: Says the server must answer the preflight with status 200 or 204. Any 2xx status works, so this is slightly too narrow but not wrong in practice.
- simple-english / cors: Saying a preflight must be answered with status 200 or 204 is slightly oversimplified, but it is not wrong. Any 2xx works.
- simple-english / cors: The advice to use `origin: "*"` for a public API with no cookies is correct, but it is brief and does not warn about other risks.
- crisp / readme-install: The sentence "logtail follows `app.log` and keeps reading as the file changes" states an assumption about `--follow` as fact. The answer then admits the assumption is unverified, which contradicts the confident claim.
- crisp / readme-install: The closing note about `--follow` and `tail -f` is meta-commentary addressed to the user. It does not belong in README text.
- crisp / readme-install: The `node --version` check only verifies the Node.js version. It does not confirm that logtail itself is installed or working.
- simple-english / readme-install: The `--follow` description (keeps running and shows new lines) is an assumption, though the answer flags it as such.
- simple-english / readme-install: Fact 5 is only covered weakly: the `node --version` check verifies Node, not that logtail works, and no expected output or `logtail --version` check is given.
- simple-english / readme-install: The parenthetical definition of an environment variable is fine, but `export` is bash-specific and the section does not say how to set it in other shells such as Windows.
- simple-english / readme-install: The `node --version` check only confirms the Node version. It does not confirm that logtail itself is installed or working.
- none / runbook-disk: Fact 4 is partly met: the 'never delete pg_wal by hand' rule is at the top, before every cleanup step, so it works as a warning. But section 2 says to `rm` rotated logs with no caution about the pg_wal rule, which is fine for logs.
- none / runbook-disk: Step 2.2 says to force rotation with pg_rotate_logfile() and 'then handle the old file'. This is vague, and it only works if logging_collector is on. If logs go through syslog or logrotate, it does nothing.
- none / runbook-disk: Step 3 table says to run CHECKPOINT as a fix for long transactions or write bursts. A checkpoint does not release WAL held by a long transaction, a slot or an archive failure. It is only useful after the cause is removed.
- none / runbook-disk: Dropping a replication slot is shown as a fix, with only 'confirm with the owner first'. It can break a replica or logical consumer, and it may force a rebuild.
- none / runbook-disk: The `replay_lag` column in pg_stat_replication exists only on PG 10 and later. The pg_stat_archiver query is correct on all versions.
- none / runbook-disk: There is no explicit step to re-run df to confirm usage is under 90%. The text only says 'check again after a checkpoint'. The escalation threshold of 95% is stated, but a verification step is missing.
- none / runbook-disk: The 'du -sh /var/lib/postgresql/*/main/...' paths assume a Debian-style layout (version/main), which may not match this host, though the glob is reasonable.
- none / runbook-disk: A manual CHECKPOINT does not by itself make Postgres recycle WAL held by archiving failures or replication slots. It only helps after the cause is fixed, which the text does say, but it is placed under 'Settings' and is slightly misleading.
- none / runbook-disk: Truncating the active log with ': > current.log' is fine, but the 'remove oldest logs' advice does not warn to check that logs aren't needed for an investigation.
- none / runbook-disk: The 'Rule: never delete or move' warning sits at the top, before triage. The cleanup steps follow it, so this is fine, but 'move' goes beyond the user's 'delete' requirement. This is harmless.
- crisp / runbook-disk: Dropping a replication slot is presented as a way to free WAL, and 'Wait for the next checkpoint' is slightly imprecise: WAL removal happens at checkpoints but the slot's WAL may need several checkpoints. It is minor.
- crisp / runbook-disk: 'If the WAL disk fills completely, Postgres can stop and refuse to start' assumes pg_wal is on a separate disk, but the runbook never says so. The data directory path may also differ.
- crisp / runbook-disk: The warning is not placed immediately before the cleanup steps. A one-line version sits at the top, with the full warning right after it, so the order is acceptable but not perfect.
- crisp / runbook-disk: Case A step 3 offers deleting old logs, which is fine. The runbook does not give a command to confirm that rotation or compression freed space, although Case B step 5 does.
- crisp / runbook-disk: Dropping a replication slot is described as a routine fix; it can break a standby or consumer permanently, though the answer does say to confirm with the slot owner first.
- crisp / runbook-disk: "PostgreSQL will remove old WAL itself" and "Wait for the next checkpoint" are oversimplified. WAL removal also depends on archiving status, wal_keep_size and slot state, and the answer gives no way to force it.
- crisp / runbook-disk: The log section says to delete or compress old logs but gives no command for it. It also does not warn against removing logs that other processes may still need, such as audit or compliance logs.
- crisp / runbook-disk: The du command uses -x with several paths and may not show which filesystem a path belongs to. The df and du steps assume the three paths are on the same filesystem, but the data, WAL and logs may be on separate mounts.
- simple-english / runbook-disk: Step 9: CHECKPOINT does not reliably free WAL when a replication slot or archiving is the cause; it only helps after the cause is fixed. The step is placed after both fixes, but a failing archive_command also needs the archiver to catch up, not just a CHECKPOINT.
- simple-english / runbook-disk: Step 4: The find command only matches *.gz files older than 7 days. Active or uncompressed old logs are not covered, and the answer does not tell the reader to compress logs first.
- simple-english / runbook-disk: Step 10: pg_class query lists tables from the current database only and includes indexes and toast tables. It does not say which database to connect to.
- simple-english / runbook-disk: Step 7: Dropping a replication slot is irreversible and may force a replica rebuild. The step only says to confirm with the owner.
- simple-english / runbook-disk: The warning says Postgres can 'lose data' if pg_wal files are deleted. This is roughly right, but the cause is not explained.
- simple-english / runbook-disk: Step 5 says 'Go to step 6', which is redundant because step 6 is the next step. Steps 6–9 apply only to pg_wal, but the numbering does not show the branches.
- simple-english / runbook-disk: The pg_class query in step 6 is not limited to tables (it includes indexes, TOAST tables and other relations), and it does not filter by database or schema. It is also run in whichever database the user is connected to, so it may not show the biggest tables overall.
- simple-english / runbook-disk: Step 2 deletes compressed logs older than 14 days with `find -delete`. That is a reasonable default, but it is not fitted to the situation, and it is irreversible if the logs are needed for an investigation. The runbook does not say to check this first.
- simple-english / runbook-disk: The runbook mentions the replication slot and archiving checks but does not mention other common causes of a WAL backlog, such as a long-running transaction or a standby that is lagging. This is an omission, not an error.
- simple-english / runbook-disk: The warning about pg_wal is in the opening paragraph, before the steps. It is correct, but step 4 tells the reader to drop a replication slot, which is a risky action. It does not warn that a dropped slot may break the standby that uses it, though it does say to ask the owner first.
- crisp / error-413: Fact 4 is only partly met: the rewritten user-facing message omits ERR_UPLOAD_413 and the answer only advises keeping it in logs or a Details section.
- crisp / error-413: Suggesting that users split a large file into parts may be impractical or wrong for some file types. It also assumes the app supports multi-part sharing.
- crisp / error-413: Fact 1 is only implied. The headline says the file is too large to upload but never says the upload failed.
- simple-english / error-413: The suggested message omits ERR_UPLOAD_413; the answer only suggests keeping it in logs or small text, so the rewrite itself does not keep the code.
- none / release-notes: The `client.on('error')` example uses a `client` variable the user never mentioned, and the 'set the retry option explicitly to 3' advice refers to an option the user never named. The answer flags both as invented, but they are still unverified.
- none / release-notes: The statement that calling `init()` without `apiKey` 'will now fail' is a plausible inference but is not stated in the request, so it is slightly speculative.
- none / release-notes: The 'Before' example shows `init()` with no arguments, which may not match real usage.
- none / release-notes: The 'Before (2.x)' snippet uses `sdk.init()` and the answer says init() 'will now fail' without apiKey; the failure mode is assumed, not stated in the request.
- none / release-notes: The retries advice ('set the retry option explicitly to `3`') refers to an option whose name the answer admits it does not know, and gives no snippet.
- none / release-notes: The claim that the memory leak fix 'improv[es] stability for long-running connections' goes beyond the facts given.
- none / release-notes: The `sdk.on('error', ...)` handler and `sdk.init({ apiKey: ... })` snippets use invented API shapes. The closing note discloses this, but the snippets themselves are not marked as placeholders.
- none / release-notes: The checklist calls the `on('error')` handler optional. The request does not say whether it is optional.
- crisp / release-notes: The `retries` option name is an assumption, though the answer flags it as one.
- crisp / release-notes: The 'Changes' section implies the retry default is the only change. It doesn't mention that more retries can mean longer waits before a failure surfaces.
- crisp / release-notes: The `on('error')` example calls `on` as a bare global function. It doesn't show it as a method on the SDK client, so it may mislead readers.
- crisp / release-notes: 'Long-running apps will now use less memory' is a mild extrapolation beyond the stated fix.
- crisp / release-notes: The breaking change is not the first section; a summary sentence comes before it, though it also mentions apiKey first.
- crisp / release-notes: "Requests that fail will now retry up to two more times" is an inference; the default goes from 3 to 5 retries, which is two more than before. This is correct but slightly loose wording.
- crisp / release-notes: "Long-running apps that reconnect often will now use stable memory" overstates the fix. The input only says a leak was fixed, not that memory is stable.
- crisp / release-notes: "If you do not pass it, init() will not work" is vague. It does not say whether init() throws, returns an error, or fails silently.
- crisp / release-notes: The example for on('error') is shown as a bare on() call, with an assumption note on handler arguments. This is flagged honestly but adds uncertainty.
- simple-english / release-notes: States that calling init() without apiKey 'fails' — plausible but not given in the request.
- simple-english / release-notes: Says 'The websocket reconnect code leaked memory' without noting it affected earlier versions; minor wording imprecision.
- simple-english / release-notes: The retries sentence tells readers to 'set the number of retries to 3 in your configuration' without naming the option, so it is not actionable until the user edits it (the answer flags this at the end).
- simple-english / release-notes: Intro says 'one new default', and the 'If you want the old behavior, set the number of retries to 3' line gives no option name, so readers can't act on it.
- simple-english / release-notes: 'Memory use no longer grows each time the connection reconnects' is an assumed cause, which the answer itself admits it did not know.
- simple-english / release-notes: 'A call to init() without apiKey is no longer valid' does not say what happens (error or not), so the upgrade impact is vague.

## Limits

- The judge is a Claude model that judges Claude text. Family bias is possible.
- Small samples move between runs. Run with `--runs 3` before you trust a difference of a few points.
- The checker measures Crisp's own rules, so it favors Crisp. The judge scores do not use the checker.
