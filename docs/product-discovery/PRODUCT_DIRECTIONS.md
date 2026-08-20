# Product Directions

Three substantially different directions. Direction B is the required
interactive-graphical-reasoning option (manipulation happens _on the chart_,
not in a quiz beside it). All three preserve the deterministic scientific core.

---

## The learning problem they must serve

The smallest meaningful Westgard outcomes (see `RECOMMENDED_LEARNING_LOOP.md` for full list). A student can:

- read a Levey-Jennings chart and **decide accept or reject** a run;
- **name the rule** that forces the decision (from the three the engine actually evaluates: `1_2s`, `1_3s`, `2_2s`);
- point to **where** the run first breaks;
- distinguish **systematic** (bias, drift) from **random** (imprecision) error;
- **explain why**, and transfer the call to a slightly different case.

Content consumption and card completion are **not** outcomes.

---

## Direction A — Guided Decision Trainer (predict → commit → reveal)

**Central learning loop:** Student sees one LJ chart with no answers shown. They commit a decision (Accept / Reject), and if Reject, pick the rule and click the first offending point. Only then does the deterministic engine result appear, comparing their call to the truth, with a short "why" and a targeted note if they made a known mistake.

**Five-minute activity:** A 5-scenario "shift" set from the existing dataset. Each: judge → reveal → one-line rationale → next. Ends with "4/5 correct — you reliably catch sudden bias; drift is where you slipped."

**Pedagogical value:** Directly trains the target skill (decision under uncertainty) and creates the prediction-before-explanation gap that makes the later explanation stick. Reuses `false_alarm` truth to teach that a single 2s excursion in `normal` is _not_ a rejection.

**Repo changes:** New "decision" mode of the scenario page that hides `rule_results` until submit; a small answer-key derivation from the existing payload (truth is already in `rule_results` + `summary`); structured `correct_decision` + `rationale` + `misconception` fields added to content (see `CONTENT_MODEL_GAPS.md`). No engine change. No backend.

**Complexity:** Low–Medium. Mostly frontend state + a content-field addition.

**Risks:** If reveal copy stays generic, it degrades into "flashcards with a picture." Mitigated by requiring the interaction to be _on the chart_ and feedback to be misconception-specific.

**Do NOT build:** scoring leaderboards, timers, accounts, new rules.

**In class:** Bea projects a scenario, students commit on their phones/laptops anonymously, then she reveals and discusses. Works as a warm-up or an exit ticket.

---

## Direction B — Chart Sandbox (direct manipulation) _[required graphical-reasoning direction]_

**Central learning loop:** Student manipulates the _cause_ and watches the _effect_ on the chart and the rules in real time. Sliders map directly to the engine's own parameters — `shift_sd`, `start_run`, `total_drift_sd`, `sd_multiplier` — and the three rules re-evaluate live as the curve deforms. The student's task is framed as a challenge ("make `1_2s` fire without `1_3s`", "create drift that no single point would flag").

**Five-minute activity:** "Break the run." Given a normal chart, drag `shift_sd` up until a rule trips; observe which one trips first and at which run. Then reduce it just below threshold and see the alarm disappear — building intuition for _why_ the limits are where they are.

**Pedagogical value:** Builds causal, embodied intuition for systematic vs random error that no quiz delivers: the student feels that bias is a step, drift is a ramp, imprecision is a fan. This is the one direction that clears the "interactive graphical reasoning" bar.

**Repo changes:** This requires **client-side evaluation of the three rules** (port `rule_1_2s/1_3s/2_2s` to TypeScript, ~40 lines, mirrored 1:1 from `rules.py` with a shared test vector), because static JSON cannot respond to a slider. Random draws must stay deterministic per seed to preserve auditability — regenerate from a fixed seed + parameters, not fresh randomness. New sandbox route/page.

**Complexity:** Medium–High. The risk is a second, drifting implementation of the rules. Mitigated by a golden-vector test asserting the TS port matches the Python engine on the eight exported scenarios.

**Risks:** Duplication of scientific logic (auditability risk); open-ended sandboxes can feel aimless without framed challenges.

**Do NOT build:** a general chart editor, arbitrary data upload, new statistical rules, a physics-y animation layer.

**In class:** Bea demonstrates each failure mode live by dragging one slider; the whole class sees the rule light up at the moment of violation. Strong lecture-companion.

---

## Direction C — Case Rounds (anonymous classroom session)

**Central learning loop:** A teacher opens a shared session from a set of scenarios; students join anonymously via a link/code, each commits a decision, and the class sees an **aggregated, anonymous distribution** ("60% accepted, 40% rejected") before Bea reveals the truth and runs a discussion checkpoint.

**Five-minute activity:** One hard scenario (soft drift). Everyone commits; the split appears; Bea asks two students on opposite sides to argue; reveal; debrief.

**Pedagogical value:** Surfaces misconceptions socially, drives peer discussion, and gives Bea live formative assessment of the class. Confidence calibration is natural here.

**Repo changes:** Largest. Requires shared session state, therefore a backend (Supabase already present could host session + votes) and a teacher view. Pushes toward accounts/roles and real-time — the closest to LMS territory, which the constraints forbid at first release.

**Complexity:** High. Backend, real-time, teacher tooling, moderation of an anonymous room.

**Risks:** Scope creep into an LMS; requires connectivity and a second permanent backend surface; anonymous rooms need abuse handling; violates "first activity must not require infrastructure" if made central early.

**Do NOT build (now):** accounts, grading, persistence of class rosters, chat.

**In class:** Genuinely powerful for synchronous teaching — but as a **P1/later** layer on top of A, not the first release.

---

## Divergence check

- **A** = guided, single-answer, predict-then-reveal (decision fluency).
- **B** = open manipulation, live rules on the chart (causal intuition, graphical).
- **C** = social/synchronous, aggregated class judgment (formative assessment).

They differ on the axis that matters: _who acts, on what, and when the truth appears._ See `RECOMMENDED_LEARNING_LOOP.md` for the scored decision and the A-first, B-next sequencing.
