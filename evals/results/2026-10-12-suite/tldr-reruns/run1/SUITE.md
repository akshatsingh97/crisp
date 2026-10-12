# Crisp evaluation suite, 2026-10-12

- Claude Code: 2.1.296 (Claude Code)
- Runs per content scenario: 2
- Isolated HOME: yes
- Suites: tldr
- Baseline: Claude Code with no plugin. Pairwise verdicts come from a blind judge that sees each pair in both orders. A pair counts as a win or a loss only if both orders agree.

## Gates

| Gate | Check | Target | crisp-1.2.0 |
|---|---|---|---|
| G1 | No net loss of critical information | <= 0 | skipped |
| G2 | Few critical items cut at all | <= 0.1 | skipped |
| G3 | Useful information is not net-cut | <= 1.25 | skipped |
| G4 | Not less useful than no plugin (preference) | >= 0 | skipped |
| G5 | Must-cover fact coverage | >= -2 | skipped |
| G6 | Accuracy holds | >= -0.3 | skipped |
| G7 | Readability score | >= 85 | skipped |
| G8 | Sentences over the limit | <= 0.5 | skipped |
| G9 | Not longer than no plugin | <= 1.1 | skipped |
| G10 | Requests for depth get full answers | >= 0.85 | skipped |
| G11 | Code in answers still compiles | >= 1 | skipped |
| G12 | Never mentions Crisp or its rules | <= 0 | PASS (0) |
| G13 | Strict level keeps content | >= -5 | skipped |
| G14 | Strict level is at least as readable as lite | >= -3 | skipped |
| G15 | On-demand mode does not load Crisp for ordinary questions | <= 0 | skipped |
| G16 | TL;DR format (one sentence, at most three bullets) | >= 1 | PASS (1) |
| G17 | TL;DR keeps the critical caveat | >= 1 | PASS (1) |
| G18 | Clarify keeps the source facts | >= 0.95 | skipped |
| G19 | Clarify adds no new facts | <= 0 | skipped |
| G20 | Clarify starts with a bottom line | >= 1 | skipped |
| G21 | Check cites only real rule IDs | <= 0 | skipped |
| G22 | Creative writing keeps its voice | >= 1 | skipped |

## crisp-1.2.0: 3 passed, 0 failed or incomplete


## Limits

- The judge is a Claude model that judges Claude text. Family bias is possible.
- Each run samples the model, so numbers move between runs. Small differences are noise.
- The readability gates use Crisp's own checker. The content gates do not.
