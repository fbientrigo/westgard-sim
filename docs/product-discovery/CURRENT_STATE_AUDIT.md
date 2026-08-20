# Current State Audit

_Product-discovery pass. No production code was modified to produce this document._

## Verdict in one line

A scientifically solid, deterministic QC engine is wrapped in a **read-only browsing app plus a flashcard deck**. Nothing in the student experience ever asks the learner to _decide_ anything — so the hardest part of Westgard training (judging a run) is never practiced.

## What actually exists (implemented vs documented vs abandoned)

### Implemented and working

| Area | Reality |
| --- | --- |
| Simulation core (`qc_lab_simulator/`) | Pure, deterministic, seed-stable. Generates 4 scenario shapes: `normal`, `bias`, `drift`, `imprecision`. Well tested (README cites 101 Python tests). |
| Westgard rules (`rules.py`, `metrics.py`) | **Exactly three rules: `1_2s`, `1_3s`, `2_2s`.** Each rule reports `triggered`, `first_trigger_run`, and (for `normal`) `false_alarm`. |
| Static export (`web_export.py`) | Emits validated JSON: control limits, per-run series with z-scores, rule results, summary. Contract is strict and validated both in Python and in the frontend (Zod). |
| Content catalog (`content/experiment_catalog.json`) | **Two experiments, eight scenarios total** (`baseline_glucose`, `dense_training_set`). This is the entire published dataset. |
| Student web app (`apps/student-web/`) | React + TS + Vite, hash routing. Four routes: Home (experiment list), Experiment detail, Scenario viewer (LJ chart + rule table + educational notes), Flashcards. |
| Flashcards | Three-pile Leitner session, local progress in `localStorage`, optional Supabase sync. |
| Authoring (`scripts/authoring_mvp.py`) | A **local Streamlit app** Bea runs via PowerShell + `.venv`. Edits JSON catalogs and flashcard decks, exports static data. |
| Deployment | GitHub Pages workflow **and** Vercel config, both live. Supabase optional (identity + flashcard progress only). |

### Documented but not implemented

- **Rules the content teaches but the engine cannot evaluate.** `content/lessons.json` and `content/scenarios.json` explicitly reference the **`10x` rule** (drift) and the **`R-4s` rule** (imprecision). Neither exists in `rules.py`. The app therefore tells students a rule detects a pattern while never being able to show that rule triggering. This is the headline content-model gap (see `CONTENT_MODEL_GAPS.md`).

### Abandoned / vestigial

- `outputs/`, `outputs/smoke/`, and duplicated `public/…` trees are generated artifacts, not sources. They churn and should never be read as intent.
- Supabase auth is wired but serves only flashcard progress sync — a large surface for a small payoff, and it introduces an auth path into an otherwise anonymous experience.

## Concrete friction and leaks found in the real code

1. **The scenario page reveals everything at once.** `ScenarioViewer.tsx` renders the chart, the trigger points (already colored red), the full rule-results table, _and_ the educational explanation simultaneously. There is no moment where the student commits a judgment before seeing the answer. The product shows conclusions; it never trains decisions.

2. **Implementation terminology leaks into the student UI.** Students see `Semilla` (seed), `scenario_type`, raw parameter keys (`shift_sd`, `start_run`) printed verbatim in the scenario "Parametros" block, and a chart titled "Levey-Jennings (simplificado)". These are engine internals, not learning concepts.

3. **Language split via a fragile adapter.** Source content is **English** (`lessons.json`, `scenarios.json`); the UI is **Spanish**, translated at runtime by a `scenario_type`-keyed adapter in `shared/config/localization.ts`. Any newly authored scenario key silently leaks English or renders untranslated.

4. **No structured "correct decision + rationale" per scenario.** The engine knows the truth (which rule fired, where, and whether it is a false alarm), and the content has free-text `common_mistake` prose, but there is no first-class field pairing _the right call_ with _why_. Misconception-based feedback has no data model to hang on.

5. **Bea's authoring path is developer-grade.** Creating content requires Python 3.11, a virtualenv, PowerShell execution policy changes, Streamlit, and understanding of JSON catalogs and a build/export/verify pipeline (`BEA_PILOT_CHECKLIST.md` budgets 20 minutes and lists JSON/term confusion as expected failure modes). For a non-technical Medical Technologist this is the steepest cliff in the project.

6. **Two permanent production sites.** GitHub Pages and Vercel are both configured and deployable. This duplicates the surface to maintain and the URL students must be given. (See constraint note below.)

## Constraint tripwires flagged for the recommendation

- **Do not add a third permanent site, and prefer consolidating to one.** Two are already live; that already collides with "do not recommend multiple permanent production sites."
- **The first student activity must stay anonymous.** Flashcard progress can currently require Supabase login; the core learning loop must not.
- **The engine only knows three rules.** Any decision the app asks a student to make must be answerable from `1_2s`, `1_3s`, `2_2s`, plus accept/reject — until the core is honestly extended. Do not ask students to select `10x` or `R-4s`.

## What is genuinely strong and must be preserved

- Deterministic, seed-stable, auditable scenario generation.
- A strict, validated data contract shared Python → JSON → TypeScript.
- A working Recharts Levey-Jennings chart with per-point trigger metadata already plumbed through (`triggerTooltip.ts`).
- Zero-backend static hosting that already works.
