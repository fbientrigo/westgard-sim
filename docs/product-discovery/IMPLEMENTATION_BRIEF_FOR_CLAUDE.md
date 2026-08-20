# Implementation Brief — Decision Trainer (P0)

For the implementing agent. This brief is bounded on purpose. Build the loop, not
a platform.

## Selected direction

**Guided Decision Trainer**: the student commits an Accept/Reject decision (and,
if Reject, a rule + first-break point clicked on the chart) **before** the
deterministic engine result is revealed and explained. Direction B (Chart
Sandbox) is the next release, not this one.

## Exact scope

**In scope (P0):**
- A new "decision set" runner over the **eight already-exported scenarios**.
- Present → Predict → Reveal → Explain → Summary flow, anonymous, static, local progress.
- Additive content fields (`decision_key`, plain-language labels, one or two `sets`) and additive Zod contract fields.
- Home reworked to one primary action.

**Out of scope (P0):**
- Any backend, auth, or Supabase dependency for the trainer.
- New Westgard rules (`10x`, `R-4s`) — see `CONTENT_MODEL_GAPS.md` §1 (P1).
- Client-side rule evaluation / sliders (that is Direction B).
- Scores, timers, streaks, leaderboards, accounts, real-time, teacher tooling.
- New simulation scenarios or a third hosting target.

## User stories

- As a first-time student, I see one clear "start", so I know what to do.
- As a student, I judge a chart (accept/reject) **before** seeing the answer, so I actually practice deciding.
- As a student who chooses reject, I name the rule and click where it first breaks, so my reasoning is explicit.
- As a student, after I commit I see whether I was right and a short why, so I learn from the gap.
- As a student who made a common mistake, I get a note about that specific mistake, not a generic explanation.
- As a returning student, my place in a set is remembered locally, so I can continue without logging in.
- As Bea, I can point the class at one URL and one activity that runs on phones without installs or accounts.

## Acceptance criteria

1. In `present`, the chart shows data + control limits only — **no** trigger colors, rule table, or educational text in the DOM.
2. The decision cannot be revealed until the student confirms Accept, or Reject + a selected rule + a clicked point.
3. The rule selector offers exactly `1_2s`, `1_3s`, `2_2s` (plain-language labels), and nothing else.
4. Reveal compares the student's decision to values derived from the existing `rule_results`/`summary`; a correct/incorrect banner is shown.
5. Explain text is answer-specific: a matching `misconception` note appears when the student's error matches one; otherwise a confirmation/rationale line.
6. On the last scenario, a summary shows `X/N` and names one handled/one missed pattern.
7. Progress per set persists in `localStorage` and survives reload with no login.
8. No network call to Supabase or any API is required to complete a full set.
9. All existing Python (101) and frontend (17) tests still pass; new logic (decision-derivation, contract parsing) has unit tests; a golden test asserts derived answer keys match the engine output for all eight scenarios.
10. Contract changes are **additive**; existing scenario payloads still parse.

## Required screens and states

| Screen | States |
| --- | --- |
| Home ⭑ | loading, error(retry), empty, ready |
| Set runner ⭑ | present, predict, reveal, explain; plus loading, error, empty per scenario |
| Set summary ⭑ | ready (X/N + pattern feedback) |
| Scenario viewer (reference) | unchanged; relabeled "Explorar" |
| Flashcards | unchanged; relabeled "Repaso" |

## Interactions

- Accept/Reject as two clear buttons.
- Reject expands: rule selector + "tap the first offending point" directly on the LJ chart (reuse `LeveyJenningsChart` point geometry; add a selectable/clickable point layer gated to predict state).
- Confirm locks the decision (no edit after lock).
- Reveal recolors the true first-trigger point(s) on the **same** chart (the trigger plumbing already exists via `triggerTooltip.ts`).
- Next / Repeat / Home navigation only. No other controls.

## Accessibility expectations

- Semantic headings and landmark structure consistent with current app.
- Every decision control reachable and operable by keyboard; the "click the point" interaction must have a keyboard-accessible equivalent (e.g. a run-number selector) so it is not mouse-only.
- Visible focus states; correct/incorrect conveyed by **text + icon**, never color alone (the chart already uses red for triggers — pair it with a label).
- Chart has a text alternative summarizing the series decision (accept/reject + rule) after reveal.
- Contrast meets WCAG AA for text and essential graphics.

## Mobile expectations

- The full loop works on a phone in portrait: chart legible, decision buttons thumb-reachable, tap-the-point usable at touch target size (or fall back to the run-number selector on small screens).
- No horizontal page scroll; chart scrolls within its own container if needed.
- Bea's class use assumes students on phones with no install.

## Data requirements

- Reads the existing exported payload (`series`, `control_limits`, `rule_results`, `summary`) — unchanged shape.
- Adds (additive, see `CONTENT_MODEL_GAPS.md`): derived `decision_key` per scenario (correct_decision, governing_rule, first_break_run) computed at export from engine truth; authored Spanish `rationale` + `misconceptions`; plain-language scenario label; one or two `sets` referencing existing scenarios.
- Extend Zod contracts additively; keep contract tests green.
- Local progress store mirrors the flashcard `progressRepository` pattern (local mode only for P0).

## Elements to preserve

- The deterministic simulation core and export contract (do not touch `qc_lab_simulator/` logic for P0).
- Zod runtime validation and existing tests.
- The Recharts LJ chart and its trigger metadata.
- Static, no-backend hosting.

## Elements to remove or demote

- Demote the all-at-once Scenario viewer from default first contact to an explicit "Explorar/reference" mode.
- Demote Flashcards from a co-equal home entry to "Repaso".
- Stop rendering engine internals to students: `Semilla` (seed), raw `parameters` keys, `scenario_type` labels.
- Do **not** make Supabase/auth part of the trainer path.
- Flag (do not silently keep) the dual GitHub Pages + Vercel hosting — pick one as the student URL (see `OPEN_TEACHER_DECISIONS.md`).

## Prioritized backlog

**P0 — the loop (this brief):**
- Home with one primary action.
- Decision set runner (present/predict/reveal/explain) over existing 8 scenarios.
- On-chart decision interaction + keyboard-accessible equivalent.
- Derived answer keys (golden-tested against engine) + additive contracts.
- Spanish `rationale`/`misconception` for the 8 scenarios; one starter `set`.
- Local progress + set summary.
- Suppress engine-internal terminology in student UI.

**P1 — depth and honesty:**
- Extend core with `10x` and `R-4s` rules (pure functions + tests), then add them to the picker and fix content claims.
- Direction B: Chart Sandbox with TS rule port (golden-vector matched to Python) and parameter sliders.
- Confidence check ("how sure?") before reveal for calibration.
- Author 1–2 additional decision sets varying severity/start-run.
- Consolidate to a single production host.

**Later:**
- Direction C: anonymous classroom Case Rounds (teacher link, aggregated votes, discussion checkpoint) on Supabase — only after A is validated.
- Spaced retrieval across sessions; mastery signal.
- Bea self-serve publishing (reduce the Streamlit/PowerShell authoring cliff).
