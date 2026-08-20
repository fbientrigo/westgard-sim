# Implementation and Upload Guide

This guide covers the current Vercel + Supabase implementation, validation steps, deployment/uploading, and a safe workflow for using Claude Design to improve the UI.

Last validated locally: 2026-06-19.

## 1. Current Architecture

The deployed student app lives in `apps/student-web`.

Runtime data flow:

- Python generates static educational data into `outputs/web_data`.
- Python exports flashcards into `outputs/flashcards`.
- `apps/student-web/scripts/run-sync.mjs` copies those generated files into `apps/student-web/public`.
- Vite builds the static frontend into `apps/student-web/dist`.
- Supabase is optional and only stores identity plus flashcard progress.

Supabase is not the source for scenarios, lessons, charts, or flashcard content. Those remain static assets generated from this repo.

Important files:

- Vercel config: `vercel.json`
- Vite app: `apps/student-web`
- Vercel build prep: `apps/student-web/scripts/prepare-static-data.mjs`
- Supabase client: `apps/student-web/src/shared/supabase/client.ts`
- Auth provider: `apps/student-web/src/features/auth/AuthProvider.tsx`
- Flashcard progress repository: `apps/student-web/src/features/flashcards-study/model/progressRepository.ts`
- Supabase SQL: `apps/student-web/supabase/001_identity_and_progress.sql`

## 2. Validation Result

Commands run during validation:

```powershell
cd apps/student-web
npm run test:run
```

Result: 17 frontend tests passed.

```powershell
cd ../..
.\.venv\Scripts\python.exe -m pytest
```

Result: 101 Python tests passed.

```powershell
cd apps/student-web
$env:PYTHON = (Resolve-Path ..\..\.venv\Scripts\python.exe).Path
npm run build:vercel
```

Result: static data export, typecheck, and Vite production build passed.

Known warning:

- Vite reports one generated JS chunk above 500 kB. This does not block deployment, but later UI work should consider route-level `React.lazy` / dynamic imports.

Important deployment finding:

- Vercel must build from the repo root. Do not set Root Directory to `apps/student-web`, because the build needs `requirements.txt`, `scripts/`, `content/`, and `qc_lab_simulator/`.

## 3. Local Implementation Setup

From the repo root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd apps/student-web
npm ci
```

Run local app:

```powershell
cd apps/student-web
npm run dev
```

Run the full deploy build locally:

```powershell
cd apps/student-web
$env:PYTHON = (Resolve-Path ..\..\.venv\Scripts\python.exe).Path
npm run build:vercel
```

## 4. Upload to GitHub

From the repo root:

```powershell
git status
git add vercel.json README.md apps/student-web/README.md docs/IMPLEMENTATION_UPLOAD_GUIDE.md qc_lab_simulator/flashcards/export.py tests/test_flashcards_export.py apps/student-web/public/flashcards/westgard_qc_basics/manifest.json
git commit -m "docs: add Vercel Supabase deployment guide"
git push origin main
```

Use a branch and PR instead if `main` is protected:

```powershell
git switch -c deploy/vercel-supabase-guide
git add .
git commit -m "docs: add Vercel Supabase deployment guide"
git push -u origin deploy/vercel-supabase-guide
```

## 5. Vercel Deployment

Recommended setup:

- Import the GitHub repo into Vercel.
- Root Directory: leave empty / repo root.
- Framework Preset: Vite.
- Install Command: `python3 -m pip install -r requirements.txt && npm --prefix apps/student-web ci`
- Build Command: `npm --prefix apps/student-web run build:vercel`
- Output Directory: `apps/student-web/dist`

These values are already stored in `vercel.json`.

Environment variables:

- `VITE_SUPABASE_URL`: optional.
- `VITE_SUPABASE_ANON_KEY`: optional.

If the variables are absent, the app still works with static content and browser `localStorage` progress.

Never add a Supabase service-role key to Vercel frontend variables. Only the anon public key belongs in the Vite client.

## 6. Supabase Setup

Create or open a Supabase project, then run:

- `apps/student-web/supabase/001_identity_and_progress.sql`

The SQL creates:

- `public.westgard_profiles`
- `public.westgard_flashcard_progress`
- RLS policies so users can only read/write their own rows.

Authentication:

1. Enable Email Auth / magic links in Supabase.
2. Add the deployed Vercel URL to allowed redirect URLs.
3. Add local dev redirect URLs if needed, for example `http://localhost:5173`.
4. Copy the Project URL and anon public key into Vercel as `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.

Smoke test after deploy:

1. Open the Vercel URL.
2. Confirm the home page loads experiments.
3. Open `/#/flashcards`.
4. Without Supabase env vars, confirm local mode message appears.
5. With Supabase env vars, request a magic link and sign in.
6. Mark flashcards as known/repeat and refresh.
7. Confirm progress persists after refresh.

## 7. Updating Content

Edit source content in:

- `content/experiment_catalog.json`
- `content/scenarios.json`
- `content/lessons.json`
- `content/flashcards/westgard_qc_basics.deck.json`

Validate locally:

```powershell
.\.venv\Scripts\python.exe -m pytest
cd apps/student-web
$env:PYTHON = (Resolve-Path ..\..\.venv\Scripts\python.exe).Path
npm run build:vercel
```

Commit source changes and any intentionally tracked generated assets. Vercel will regenerate static deploy assets during build.

## 8. Claude Design Workflow

Use Claude Design as a visual design partner, then apply the changes in this repo with normal code review and tests.

Recommended scope for Claude:

- Give it screenshots of the current app.
- Give it these files as context:
  - `apps/student-web/src/pages/HomePage.tsx`
  - `apps/student-web/src/pages/ExperimentPage.tsx`
  - `apps/student-web/src/pages/ScenarioPage.tsx`
  - `apps/student-web/src/pages/FlashcardsPage.tsx`
  - `apps/student-web/src/app/AppLayout.tsx`
  - `apps/student-web/src/styles.css`
  - `apps/student-web/src/features/chart-viewer/ui/LeveyJenningsChart.tsx`
  - `apps/student-web/src/features/flashcards-study/ui/FlashcardStudyBoard.tsx`

Design brief to use:

```text
Improve this React/Vite educational QC simulator so it feels like a polished clinical laboratory learning tool, not a generic demo.

Constraints:
- Keep the current routes and data contracts.
- Keep Supabase optional.
- Do not replace Recharts unless necessary.
- Prefer CSS and component refinements over new heavy UI libraries.
- Keep Spanish educational copy intact unless clearly improving clarity.
- Maintain responsive behavior for desktop and mobile.
- Preserve accessibility: semantic headings, visible focus states, readable contrast, and usable forms.

Deliver:
- A visual direction with colors, spacing, typography, and component hierarchy.
- Specific changes for `styles.css` and affected React components.
- Any suggested screenshots or mockups.
```

Implementation rule:

- Let Claude propose the design, but apply changes in small commits.
- After each visual pass, run `npm run test:run` and `npm run build:vercel`.
- Avoid changing API contracts or generated data formats during visual work.

High-impact UI targets:

- Home page: stronger dashboard layout, clearer experiment cards, less empty space.
- Scenario page: clearer chart and rule explanation hierarchy.
- Flashcards: more tactile card states, better progress indicators, cleaner auth area.
- Layout: better top navigation, compact responsive spacing, consistent buttons/forms.

## 9. References

- Vercel build configuration: https://vercel.com/docs/builds/configure-a-build
- Vercel project settings: https://vercel.com/docs/projects/project-configuration
- Supabase Auth redirect URLs: https://supabase.com/docs/guides/auth/redirect-urls
- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
