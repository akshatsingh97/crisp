# Crisp evaluation suite, 2026-10-12

- Claude Code: 2.1.296 (Claude Code)
- Runs per content scenario: 2
- Isolated HOME: yes
- Suites: content, strict, on_demand, tldr, clarify, check, creative
- Baseline: Claude Code with no plugin. Pairwise verdicts come from a blind judge that sees each pair in both orders. A pair counts as a win or a loss only if both orders agree.

## Gates

| Gate | Check | Target | crisp-1.1.0 | crisp-1.2.0 |
|---|---|---|---|---|
| G1 | No net loss of critical information | <= 0 | **FAIL** (0.12) | PASS (-0.1) |
| G2 | Few critical items cut at all | <= 0.1 | **FAIL** (0.18) | PASS (0.1) |
| G3 | Useful information is not net-cut | <= 1.25 | **FAIL** (2.48) | PASS (0.6) |
| G4 | Not less useful than no plugin (preference) | >= 0 | **FAIL** (-0.74) | PASS (0.61) |
| G5 | Must-cover fact coverage | >= -2 | PASS (1.4) | PASS (1.9) |
| G6 | Accuracy holds | >= -0.3 | PASS (0.03) | PASS (-0.06) |
| G7 | Readability score | >= 85 | PASS (96.4) | PASS (93.5) |
| G8 | Sentences over the limit | <= 0.5 | PASS (0.42) | **FAIL** (0.56) |
| G9 | Not longer than no plugin | <= 1.1 | PASS (0.83) | **FAIL** (1.14) |
| G10 | Requests for depth get full answers | >= 0.85 | **FAIL** (0.77) | PASS (0.98) |
| G11 | Code in answers still compiles | >= 1 | PASS (1) | PASS (1) |
| G12 | Never mentions Crisp or its rules | <= 0 | **INCOMPLETE** (0) | **INCOMPLETE** (0) |
| G13 | Strict level keeps content | >= -5 | PASS (91.7) | PASS (91.7) |
| G14 | Strict level is at least as readable as lite | >= -3 | PASS (-1.2) | PASS (3.2) |
| G15 | On-demand mode does not load Crisp for ordinary questions | <= 0 | PASS (0) | PASS (0) |
| G16 | TL;DR format (one sentence, at most three bullets) | >= 1 | **FAIL** (0.5) | **FAIL** (0.5) |
| G17 | TL;DR keeps the critical caveat | >= 1 | PASS (1) | PASS (1) |
| G18 | Clarify keeps the source facts | >= 0.95 | PASS (1) | PASS (1) |
| G19 | Clarify adds no new facts | <= 0 | **FAIL** (2) | **FAIL** (1) |
| G20 | Clarify starts with a bottom line | >= 1 | PASS (1) | PASS (1) |
| G21 | Check cites only real rule IDs | <= 0 | PASS (0) | PASS (0) |
| G22 | Creative writing keeps its voice | >= 1 | **INCOMPLETE** (1) | **INCOMPLETE** (1) |

## crisp-1.1.0: 13 passed, 9 failed or incomplete

- Incomplete data in: creative (1 failed model calls). Rerun with --resume to fill the gaps.

- Pairwise vs no plugin: 1 wins, 30 losses, 5 ties (of 36).
- Per pair: critical items cut 0.18, added 0.06. Useful items cut 3.86, added 1.56.
- Length vs no plugin: 0.83x. Readability score: 96.4.

| Category | Pairs | Wins | Losses | Critical cut | Useful cut | Useful added |
|---|---|---|---|---|---|---|
| alternatives | 4 | 0 | 4 | 0 | 13.5 | 4 |
| code | 2 | 0 | 2 | 0 | 6.5 | 2 |
| debug | 4 | 0 | 4 | 1.5 | 14.5 | 5 |
| decision | 6 | 0 | 3 | 2 | 16.5 | 11 |
| depth | 2 | 0 | 2 | 0.5 | 22.5 | 9.5 |
| doc | 10 | 0 | 8 | 0.5 | 38 | 13.5 |
| safety | 8 | 1 | 7 | 2 | 27.5 | 11 |

Critical items that this version cut (as listed by the judge):

- charge-retry-run1: Stripe stores and replays the first result including errors: after a card decline, same key returns same decline, so use a new key only for a new customer attempt
- charge-retry-run1: Stripe stores and replays the first result, including errors. A retry with the same key after a card decline returns the same decline, so a new key is needed when the customer starts a new attempt
- node-heap-run1: In containers, keep --max-old-space-size below the container memory limit or the OS OOM-kills the process
- node-heap-run1: In a container, keep --max-old-space-size below the container memory limit, or the OS OOM-kills the process
- node-heap-run1: --heapsnapshot-near-heap-limit=3 writes a snapshot just before the crash, giving production evidence
- pg-index-run1: Set statement_timeout = 0 for the session, since a default statement_timeout can kill the long build and leave an INVALID index
- runbook-disk-run1: Do not run VACUUM FULL on a nearly full disk because it needs extra space
- deep-react-fiber-run2: Caveat: time slicing works between fibers, not inside one slow function; a slow render cannot be split
- docker-prune-run1: Docker Desktop (Mac/Windows) virtual disk may not shrink; use Clean/Purge data or reduce the disk image size
- queue-choice-run1: Set Redis maxmemory-policy noeviction (in addition to AOF) or Redis can drop queued jobs when memory is full
- queue-choice-run1: Both options are at-least-once delivery, so every job must be idempotent
- queue-choice-run1: Set maxmemory-policy noeviction in Redis, otherwise queued jobs can be dropped when memory is full
- queue-choice-run1: Both options deliver at-least-once, so jobs must be idempotent / safe to run twice

## crisp-1.2.0: 16 passed, 6 failed or incomplete

- Incomplete data in: creative (1 failed model calls). Rerun with --resume to fill the gaps.

- Pairwise vs no plugin: 23 wins, 5 losses, 8 ties (of 36).
- Per pair: critical items cut 0.1, added 0.19. Useful items cut 2.18, added 3.62.
- Length vs no plugin: 1.14x. Readability score: 93.5.

| Category | Pairs | Wins | Losses | Critical cut | Useful cut | Useful added |
|---|---|---|---|---|---|---|
| alternatives | 4 | 3 | 0 | 0 | 6.5 | 15.5 |
| code | 2 | 1 | 0 | 0 | 4.5 | 9 |
| debug | 4 | 3 | 1 | 0 | 7 | 11.5 |
| decision | 6 | 5 | 0 | 1 | 8.5 | 21 |
| depth | 2 | 1 | 1 | 2.5 | 11.5 | 16 |
| doc | 10 | 4 | 3 | 0 | 26.5 | 26 |
| safety | 8 | 6 | 0 | 0 | 14 | 31.5 |

Critical items that this version cut (as listed by the judge):

- deep-react-fiber-run2: Warning that array index keys cause state (typed text, focus, checkbox) to attach to wrong rows after reorder/insert/filter
- deep-react-fiber-run2: By default, when a component re-renders all its children re-render because a new element means new props reference; re-render is not a DOM update, and a wasted render doesn't touch the DOM
- deep-react-fiber-run2: Practical caveats: time slicing works only between fibers so a slow single render can't be split; a large commit still blocks; don't add useMemo everywhere, profile first; moving a component resets its state; effects belong in useEffect
- deep-react-fiber-run2: Warning: index keys cause stale state (typed text, focus, checkbox) on wrong row after reorder/insert/filter
- deep-react-fiber-run2: Limitations: time slicing works between fibers so a slow single render function still blocks; large synchronous commit still blocks
- queue-choice-run1: Both options deliver at-least-once, so every job must be idempotent regardless of backend
- queue-choice-run1: Both options deliver at-least-once, so write every job to be idempotent/safe to run twice

## Limits

- The judge is a Claude model that judges Claude text. Family bias is possible.
- Each run samples the model, so numbers move between runs. Small differences are noise.
- The readability gates use Crisp's own checker. The content gates do not.
