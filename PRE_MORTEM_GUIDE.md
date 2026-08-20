# Westgard Sim Pre-Mortem and Launch Guide

Date: 2026-06-19

Purpose: identify likely failure modes before deploying or visually redesigning the student web app, then give a clear runbook for implementation, upload, Vercel deployment, Supabase setup, validation, and recovery.

This is a pre-mortem, not a blame document. Read it before touching deployment settings, Supabase, content exports, or broad UI styling.

## 1. Executive Summary

The repo is deployable as a static Vite frontend backed by generated JSON assets. Supabase is optional and only stores identity plus flashcard progress.

The highest-risk mistake is configuring Vercel with `apps/student-web` as the Root Directory. That looks natural, but it breaks the current build because the Vercel build needs repo-root Python files:

- `requirements.txt`
- `scripts/`
- `content/`
- `qc_lab_simulator/`
- `apps/student-web/`

Correct Vercel shape:

- Root Directory: repo root / empty value
- Install Command: `python3 -m pip install -r requirements.txt && npm --prefix apps/student-web ci`
- Build Command: `npm --prefix apps/student-web run build:vercel`
- Output Directory: `apps/student-web/dist`

The repo now includes `vercel.json` with those settings.

## 2. Current System Map

Main app:

- Frontend: `apps/student-web`
- Framework: React + Vite + TypeScript
- Router: hash-based routes, for example `/#/flashcards`
- Charting: Recharts
- Runtime validation: Zod contracts

Static data pipeline:

1. Python reads source content from `content/`.
2. Python exports web data to `outputs/web_data`.
3. Python exports flashcards to `outputs/flashcards`.
4. `apps/student-web/scripts/run-sync.mjs` copies outputs into `apps/student-web/public`.
5. Vite builds `apps/student-web/dist`.

Supabase role:

- Optional auth.
- Optional flashcard progress sync.
- No scenario content storage.
- No chart data storage.
- No educational lesson storage.

Important files:

- `vercel.json`
- `requirements.txt`
- `pyproject.toml`
- `apps/student-web/package.json`
- `apps/student-web/scripts/prepare-static-data.mjs`
- `apps/student-web/scripts/run-sync.mjs`
- `apps/student-web/supabase/001_identity_and_progress.sql`
- `apps/student-web/src/shared/supabase/client.ts`
- `apps/student-web/src/features/auth/AuthProvider.tsx`
- `apps/student-web/src/features/flashcards-study/model/progressRepository.ts`

## 3. Validation Baseline

Last local validation performed:

```powershell
npm --prefix apps/student-web run test:run
```

Expected result:

- 6 frontend test files pass.
- 17 frontend tests pass.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Expected result:

- 101 Python tests pass.

```powershell
$env:PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
npm --prefix apps/student-web run build:vercel
```

Expected result:

- Python static data export succeeds.
- Flashcard export succeeds.
- Static sync succeeds.
- TypeScript typecheck succeeds.
- Vite production build succeeds.

Known non-blocking warning:

- Vite reports one JS chunk above 500 kB after minification.
- This is not a launch blocker.
- Treat it as a future code-splitting improvement, especially before adding visual libraries.

## 4. Pre-Mortem: Likely Failures

### Failure 1: Vercel builds from the wrong root

What happens:

- Vercel root is set to `apps/student-web`.
- `npm run build:vercel` cannot access repo-root Python code and content.
- Build fails during static export.

Signals:

- `ModuleNotFoundError` for Python modules.
- Missing `content/experiment_catalog.json`.
- Missing `scripts/export_web_data.py`.
- Missing `requirements.txt`.

Prevention:

- Keep Vercel Root Directory empty / repo root.
- Keep `vercel.json` at repo root.
- Use `npm --prefix apps/student-web run build:vercel`.

Recovery:

1. Open Vercel Project Settings.
2. Clear Root Directory or set it to repo root.
3. Confirm output directory is `apps/student-web/dist`.
4. Redeploy.

### Failure 2: Python dependencies are missing on Vercel

What happens:

- Node dependencies install.
- Python export starts.
- Import fails for `numpy`, `pandas`, `jsonschema`, or other Python packages.

Signals:

- `ModuleNotFoundError: No module named 'numpy'`.
- Build fails before Vite starts.

Prevention:

- Install command must include `python3 -m pip install -r requirements.txt`.
- Do not rely on Node install alone.

Recovery:

1. Update Vercel Install Command.
2. Redeploy without build cache if needed.
3. Confirm logs show Python dependencies installing before npm build.

### Failure 3: Supabase service-role key leaks to frontend

What happens:

- A privileged Supabase secret is added as a Vite env var.
- Vite embeds it into the browser bundle.
- Anyone can inspect it.

Signals:

- Variable names include `SERVICE_ROLE`, `SECRET`, or non-anon keys.
- Frontend code references service-role keys.

Prevention:

- Only use `VITE_SUPABASE_URL`.
- Only use `VITE_SUPABASE_ANON_KEY`.
- Never put a service-role key in Vercel frontend environment variables.

Recovery:

1. Remove the secret from Vercel immediately.
2. Rotate the leaked Supabase key.
3. Redeploy.
4. Audit Supabase logs and policies.

### Failure 4: Supabase RLS blocks legitimate users

What happens:

- User signs in.
- Flashcard progress does not save or load.
- UI silently falls back to local behavior or logs warnings.

Signals:

- Browser console warnings:
  - `No se pudo cargar progreso desde Supabase.`
  - `No se pudo guardar progreso en Supabase.`
- Supabase table exists but inserts/updates fail.

Prevention:

- Run `apps/student-web/supabase/001_identity_and_progress.sql`.
- Confirm RLS is enabled.
- Confirm policies use `auth.uid()`.

Recovery:

1. Re-run the SQL migration.
2. Confirm tables:
   - `public.westgard_profiles`
   - `public.westgard_flashcard_progress`
3. Confirm authenticated user can insert one progress row.
4. Refresh the app and retry flashcards.

### Failure 5: Magic link redirect is not allowed

What happens:

- User receives magic link.
- Login fails or redirects to the wrong place.

Signals:

- Supabase auth error about redirect URL.
- User lands outside the app.
- Session is not detected after clicking link.

Prevention:

- Add Vercel production URL to Supabase redirect URLs.
- Add preview URLs if using Vercel preview deployments.
- Add local dev URL for testing: `http://localhost:5173`.

Recovery:

1. Open Supabase Auth URL settings.
2. Add the deployed Vercel URL.
3. Request a fresh magic link.

### Failure 6: Static content is stale

What happens:

- Source content changes.
- Deployed app still shows old experiments, lessons, or flashcards.

Signals:

- `content/` has updates but `public/` or deployed app does not.
- Build logs do not show static export.

Prevention:

- Use `npm --prefix apps/student-web run build:vercel` for deploy builds.
- Do not deploy with plain `vite build` unless static assets are already synced intentionally.

Recovery:

1. Run the Vercel build command locally.
2. Inspect:
   - `apps/student-web/public/web_data`
   - `apps/student-web/public/educational`
   - `apps/student-web/public/flashcards`
3. Commit intentional generated asset changes if they are tracked.
4. Redeploy.

### Failure 7: Generated files churn across machines

What happens:

- Generated manifests contain absolute local paths.
- Every developer changes the same generated file even without content changes.

Signals:

- Diffs show paths like `C:/Users/...`.
- Only local filesystem paths change.

Prevention:

- Keep generated manifest paths repo-relative where possible.
- The flashcard exporter now writes:
  - `content/flashcards/westgard_qc_basics.deck.json`
  - `content/flashcards/theme_tokens.json`

Recovery:

1. Regenerate flashcards with the current exporter.
2. Review manifest diffs.
3. Commit only portable generated values.

### Failure 8: UI redesign breaks data contracts

What happens:

- Visual refactor changes expected JSON shape or API calls.
- Pages stop rendering even though data is valid.

Signals:

- Zod contract errors in browser console.
- Tests in `src/shared/api/contracts.test.ts` fail.
- Experiment or scenario pages show error states.

Prevention:

- Keep visual work in CSS and component layout first.
- Do not change `shared/api/contracts.ts` during a purely visual pass.
- Run frontend tests after every design pass.

Recovery:

1. Revert contract changes from the design commit.
2. Restore old data access shape.
3. Re-run `npm --prefix apps/student-web run test:run`.

### Failure 9: UI redesign adds heavy dependencies

What happens:

- A design pass adds a UI framework, animation package, or chart replacement.
- Bundle size grows.
- Vercel still builds but app becomes slower.

Signals:

- Vite chunk warning gets worse.
- `package-lock.json` changes heavily.
- Initial JS grows significantly beyond current baseline.

Prevention:

- Prefer CSS and current components.
- Keep Recharts unless there is a specific chart limitation.
- Add libraries only after a concrete need is identified.

Recovery:

1. Remove unnecessary dependency.
2. Rebuild.
3. Compare bundle output in Vite logs.

### Failure 10: Local-only assumptions enter deploy scripts

What happens:

- Script assumes Windows paths or a local `.venv`.
- Vercel Linux build fails.

Signals:

- Backslash-only paths fail in Vercel.
- Commands reference `.venv\Scripts\python.exe`.
- `python` exists locally but not on Vercel.

Prevention:

- In Vercel config, use `python3`.
- In Node scripts, keep path handling through `node:path`.
- Use `PYTHON` only as an override for local validation.

Recovery:

1. Replace local absolute paths with repo-relative paths.
2. Use `python3` in deploy settings.
3. Validate with `npm --prefix apps/student-web run build:vercel`.

## 5. Implementation Runbook

### One-time local setup

From repo root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
npm --prefix apps/student-web ci
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Routine local development

Start frontend:

```powershell
npm --prefix apps/student-web run dev
```

Run frontend tests:

```powershell
npm --prefix apps/student-web run test:run
```

Run Python tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Run deploy-equivalent build:

```powershell
$env:PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
npm --prefix apps/student-web run build:vercel
```

## 6. Content Update Runbook

Use this when changing experiments, scenarios, lessons, or flashcards.

Source files:

- `content/experiment_catalog.json`
- `content/scenarios.json`
- `content/lessons.json`
- `content/flashcards/westgard_qc_basics.deck.json`

Validation:

```powershell
.\.venv\Scripts\python.exe -m pytest
$env:PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
npm --prefix apps/student-web run build:vercel
```

Review generated diffs:

```powershell
git status --short
git diff -- apps/student-web/public
```

Commit rule:

- Commit source content changes.
- Commit tracked generated assets only when the repo expects them to stay versioned.
- Do not commit `outputs/`, `.venv/`, `node_modules/`, or `dist/`.

## 7. Vercel Upload and Deployment Runbook

### Before first deploy

Confirm `vercel.json` exists at repo root:

```powershell
Get-Content vercel.json
```

Expected important values:

```json
{
  "installCommand": "python3 -m pip install -r requirements.txt && npm --prefix apps/student-web ci",
  "buildCommand": "npm --prefix apps/student-web run build:vercel",
  "outputDirectory": "apps/student-web/dist"
}
```

### Vercel project settings

Use:

- Root Directory: empty / repo root
- Framework Preset: Vite
- Install Command: use `vercel.json`
- Build Command: use `vercel.json`
- Output Directory: use `vercel.json`

Add optional environment variables:

- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Do not add:

- Supabase service-role key
- Database password
- Any private API key intended for server-side use only

### Deploy

Push to GitHub:

```powershell
git status
git add .
git commit -m "docs: add deployment pre-mortem guide"
git push origin main
```

If using a branch:

```powershell
git switch -c deploy/pre-mortem-guide
git add .
git commit -m "docs: add deployment pre-mortem guide"
git push -u origin deploy/pre-mortem-guide
```

Then import or redeploy from Vercel.

## 8. Supabase Runbook

### Create schema

Open Supabase SQL editor and run:

```text
apps/student-web/supabase/001_identity_and_progress.sql
```

Expected tables:

- `public.westgard_profiles`
- `public.westgard_flashcard_progress`

Expected security:

- RLS enabled.
- Users can only select, insert, update, and delete their own progress rows.

### Configure auth

In Supabase Auth settings:

1. Enable Email Auth / magic links.
2. Add production Vercel URL to redirect URLs.
3. Add preview URLs if needed.
4. Add local dev URL if needed: `http://localhost:5173`.

### Smoke test

Without Supabase variables:

1. Open the app.
2. Go to `/#/flashcards`.
3. Confirm local mode message appears.
4. Mark cards as known/repeat.
5. Refresh and confirm progress remains in the browser.

With Supabase variables:

1. Open the app.
2. Go to `/#/flashcards`.
3. Request magic link.
4. Sign in.
5. Mark cards as known/repeat.
6. Refresh and confirm progress remains.
7. Inspect Supabase table for the authenticated user row.

## 9. Claude Design Runbook

Goal: improve visual quality without breaking static data, Supabase optional mode, deploy scripts, or tests.

### Context to give Claude Design

Provide screenshots of:

- Home page.
- Experiment page.
- Scenario page with chart.
- Flashcards page.
- Mobile layout if available.

Provide these files:

- `apps/student-web/src/styles.css`
- `apps/student-web/src/app/AppLayout.tsx`
- `apps/student-web/src/pages/HomePage.tsx`
- `apps/student-web/src/pages/ExperimentPage.tsx`
- `apps/student-web/src/pages/ScenarioPage.tsx`
- `apps/student-web/src/pages/FlashcardsPage.tsx`
- `apps/student-web/src/features/chart-viewer/ui/LeveyJenningsChart.tsx`
- `apps/student-web/src/features/flashcards-study/ui/FlashcardStudyBoard.tsx`

### Prompt to use

```text
Improve this React/Vite educational QC simulator so it feels like a polished clinical laboratory learning tool, not a generic demo.

Constraints:
- Keep current routes and data contracts.
- Keep Supabase optional.
- Keep static educational content generated from repo files.
- Prefer CSS and component layout improvements over new heavy UI libraries.
- Do not replace Recharts unless there is a clear reason.
- Keep Spanish educational copy intact unless improving clarity.
- Maintain desktop and mobile usability.
- Preserve accessibility: semantic headings, visible focus states, readable contrast, usable forms, and keyboard navigation.

Deliver:
- Visual direction.
- Color, spacing, typography, and component hierarchy.
- Specific edits for `styles.css` and affected React components.
- Any risks or tests to rerun.
```

### Safe implementation sequence

1. First pass: CSS-only polish.
2. Second pass: component structure where needed.
3. Third pass: responsive refinements.
4. Fourth pass: accessibility and keyboard review.
5. Only then consider new dependencies.

After each pass:

```powershell
npm --prefix apps/student-web run test:run
$env:PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
npm --prefix apps/student-web run build:vercel
```

### UI areas with highest return

Home page:

- Clearer first screen.
- Better experiment cards.
- More useful status summary.
- Better empty and loading states.

Scenario page:

- Stronger chart hierarchy.
- Better rule-result explanations.
- Clearer relationship between QC points, triggers, and educational notes.

Flashcards:

- More tactile card surface.
- Better pile/progress visualization.
- Cleaner auth panel.
- Better review completion state.

Global layout:

- More professional clinical-learning visual language.
- Better spacing.
- More consistent buttons and form controls.
- Mobile header and navigation polish.

## 10. Quality Gates

Every deploy candidate must pass:

```powershell
npm --prefix apps/student-web run test:run
.\.venv\Scripts\python.exe -m pytest
$env:PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
npm --prefix apps/student-web run build:vercel
```

Manual checks:

- Home loads experiments.
- Experiment detail opens.
- Scenario detail opens and chart renders.
- Flashcards load.
- Local progress works without Supabase.
- Supabase progress works when env vars are present.
- Magic link redirect returns to the app.
- Mobile viewport does not clip main controls.

## 11. Rollback Plan

If Vercel deployment fails:

1. Read first failing command in Vercel logs.
2. If failure is Python import, check Install Command.
3. If failure is missing content/scripts, check Root Directory.
4. If failure is TypeScript, reproduce locally with `npm --prefix apps/student-web run build`.
5. Revert only the offending commit or open a fix-forward commit.

If Supabase login fails:

1. Remove Supabase env vars to confirm app still works in local mode.
2. Check redirect URLs.
3. Check Email Auth setting.
4. Re-run SQL migration if policies/tables are missing.

If UI redesign breaks production:

1. Revert the visual commit.
2. Keep content and deployment commits intact.
3. Re-apply design in smaller passes.

## 12. Launch Checklist

Before pushing:

- `git status --short` reviewed.
- No `.venv/`, `node_modules/`, `dist/`, or `outputs/` staged.
- Frontend tests pass.
- Python tests pass.
- Vercel build passes locally.
- Generated manifest paths are repo-relative.

Before Vercel deploy:

- Root Directory is repo root / empty.
- `vercel.json` is present.
- Python deps install in Vercel.
- Output Directory is `apps/student-web/dist`.
- Supabase env vars are optional and use only anon public credentials.

After deploy:

- Home page loads.
- `/#/flashcards` loads.
- Static experiments and lessons load.
- Supabase magic link works if enabled.
- Flashcard progress persists.

## 13. Related Documentation

- Detailed implementation/upload guide: `docs/IMPLEMENTATION_UPLOAD_GUIDE.md`
- Student frontend guide: `apps/student-web/README.md`
- Main repo guide: `README.md`
- Supabase SQL: `apps/student-web/supabase/001_identity_and_progress.sql`
- Vercel config: `vercel.json`
