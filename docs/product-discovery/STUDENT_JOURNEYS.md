# Current Journeys (reconstructed from the real app)

Each journey below is what the code does _today_, not what the docs aspire to. Friction is marked ⚠.

## 1. First-time student

1. Opens the deployed URL → **Home**. Sees a "Estudio rapido con flashcards" banner and a list of experiment cards ("Baseline Glucose Class", "Dense Training Set").
2. No orientation, no "start here", no statement of what they will be able to do. ⚠ The first screen presents two unrelated entry points (flashcards vs experiments) with no recommended path.
3. Clicks an experiment → **Experiment detail**. Sees stats including `Media`, `SD`, `Ejecuciones`, and `Semilla` (seed). ⚠ "Semilla" is an engine internal with no learning meaning.
4. Clicks a scenario → **Scenario viewer**. The chart appears with **trigger points already colored red**, a rule table showing exactly which rules fired and where, and the full educational explanation — all at once. ⚠ The answer is revealed before the student forms any opinion. There is nothing to _do_.
5. Reads, scrolls, leaves. ⚠ **Dead end:** no next scenario, no score, no sense of progress, no reason to return.

**Net:** a first-timer browses pre-solved charts. They never decide accept/reject, never pick a rule, never find out whether their reading of a chart was right.

## 2. Returning student

1. Reopens URL. ⚠ The app does not remember which scenarios were viewed (only flashcards persist). There is no "continue" and no mastery signal.
2. Likely goes to **Flashcards**, the only stateful surface. Works the three-pile deck: show front → "Mostrar respuesta" → "Repetir" / "La supe". Progress persists locally (or via Supabase if logged in).
3. ⚠ Flashcards test recall of definitions, not the transferable skill of judging an unseen chart. A student can "know" all cards and still be unable to accept/reject a run.

**Net:** the only thing worth returning for is recall practice, which is the least important outcome.

## 3. Bea preparing material

1. Opens PowerShell in the repo root. Activates `.venv` (may need `Set-ExecutionPolicy -Scope Process Bypass`). ⚠ Developer environment required.
2. Runs `.\westgard_ops.ps1 -Action ui` to launch the **Streamlit authoring app**.
3. Loads `content/authoring_catalog.example.json`, edits experiments/scenarios/flashcards through form fields, saves back to JSON. ⚠ Must reason about scenario `type`, `parameters` (`shift_sd`, `start_run`, …), and understand validation errors.
4. Runs `-Action release` then `-Action verify` to build the technical catalog, export static data, and check output. ⚠ A build/export/verify pipeline is conceptually developer work.
5. To publish, hands off to the developer (git push / redeploy). ⚠ Bea cannot ship to students herself.

**Net:** authoring is technically real but sits behind a Python/venv/Streamlit/JSON/CLI wall. `BEA_PILOT_CHECKLIST.md` itself budgets 20 minutes and anticipates term-confusion and "lost state" failures.

## 4. Developer updating and publishing

1. Edits source content or code. Runs `pytest` (101 tests) and `npm --prefix apps/student-web run test:run` (17 tests).
2. Runs the deploy-equivalent build `build:vercel`, which invokes Python export → flashcard export → static sync → typecheck → Vite build.
3. Reviews generated diffs under `apps/student-web/public/…` (⚠ generated assets are tracked and churn), commits, pushes.
4. ⚠ **Two deploy targets** (GitHub Pages workflow + Vercel) must both be kept working; `PRE_MORTEM_GUIDE.md` exists largely to defuse the Vercel-root-directory footgun.

**Net:** the developer path is coherent and well-documented, but carries a dual-hosting tax and a generated-artifact-in-git tax.

## Cross-cutting friction summary

| Friction | Where | Cost |
| --- | --- | --- |
| No decision moment | `ScenarioViewer.tsx` | The core skill is never practiced |
| Answer shown immediately | Scenario page | No prediction, no productive struggle |
| Engine terms leak (`Semilla`, params, `scenario_type`) | Experiment + Scenario pages | Confuses non-technical students |
| No progress / no next step for experiments | Home + Scenario | Dead ends, no reason to return |
| Two entry points, no recommended path | Home | Cognitive load on first screen |
| English content / Spanish UI via key adapter | `localization.ts` | New content leaks untranslated |
| Authoring requires dev tooling | Streamlit + PowerShell | Bea depends on the developer |
| Two permanent sites | Pages + Vercel | Duplicate maintenance + URL confusion |
