# Recommended Learning Loop

## Decision matrix

Each direction scored 1–5 (5 = best) against the seven required criteria.
Scores reflect the current repo state (deterministic core, static hosting, one
developer, two live experiments / eight scenarios, no mandatory auth).

| Criterion | A · Decision Trainer | B · Chart Sandbox | C · Case Rounds |
| --- | :---: | :---: | :---: |
| Learning value (trains the target decision) | 5 | 4 | 4 |
| Fit with existing scientific core | 5 | 3 | 3 |
| Usability for non-technical students | 5 | 4 | 3 |
| Usefulness in Bea's classes | 4 | 5 | 5 |
| Implementation cost (5 = cheapest) | 5 | 3 | 1 |
| Maintainability by one developer | 5 | 3 | 2 |
| Feasibility on free hosting (5 = static-friendly) | 5 | 4 | 2 |
| **Total (max 35)** | **34** | **26** | **20** |

**Why A fits the core best:** the truth it needs — which rule fired, at which
run, whether it was a false alarm — is _already_ in the exported payload
(`rule_results`, `summary`). A needs no engine change and no client-side rule
re-implementation, so it cannot drift from the audited Python. B scores lower on
core-fit and maintainability precisely because it must re-evaluate rules
client-side to respond to sliders, creating a second implementation to keep in
sync.

## Selected direction

**A — Guided Decision Trainer**, with **B — Chart Sandbox** as the immediate next
release once A proves the loop. A delivers the highest-leverage missing behavior
(commit a decision before the reveal) at the lowest cost and risk, entirely on
the existing static host with no auth.

## The loop (one scenario)

```
PRESENT   Show one Levey-Jennings chart. No trigger colors, no rule table,
          no explanation. Just the data and the control limits.
              │
PREDICT   Student commits a decision:
          • Accept the run  OR  Reject the run
          • If Reject: pick the rule (1_2s / 1_3s / 2_2s) and click the
            first offending point on the chart.
              │  (decision is locked before anything is revealed)
REVEAL    Engine truth appears: correct decision, the rule(s) that actually
          fired, and the first-trigger run — now colored on the same chart.
              │
EXPLAIN   Short "why", tied to this student's answer:
          • Correct → one-line confirmation of the pattern.
          • Wrong in a known way → the matching misconception note
            (e.g. rejected a normal run on a lone 2s excursion → false alarm).
              │
TRANSFER  Advance to the next scenario, chosen to vary one thing (severity,
          start run, or error type) so the skill generalizes.
```

## Why this loop, grounded in the code

- **It closes the one gap the audit found:** `ScenarioViewer.tsx` reveals
  everything at once. Inserting a locked decision before reveal is the smallest
  change that converts browsing into practice.
- **The answer key already exists.** No new science; the loop reads
  `rule_results` and `summary` that the engine already emits and validates.
- **It stays anonymous and static.** Progress can live in `localStorage` exactly
  like flashcards do today — no login for the first activity.
- **It is honest about the engine.** The rule picker offers only the three rules
  the core evaluates. The `10x`/`R-4s` rules the content mentions are explicitly
  out of scope until the core is extended (a P1 item, `CONTENT_MODEL_GAPS.md`).

## Observable success for the first release

A student who completes one 5-scenario set can, on a **new** scenario they have
not seen: state accept/reject, name the governing rule, and point to the first
break — measured by their in-app decision accuracy trending up across the set,
not by cards completed.

## Deliberately excluded from the loop

Timers, points, streaks, leaderboards, accounts, new rules, real-time
multiplayer, and any server round-trip. Those are B/C-tier or anti-features for
the first release.
