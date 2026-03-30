# Student Frontend Plan

## Scope

Build and maintain a student-facing frontend in `apps/student-web` that consumes static JSON exported by the Python pipeline (`outputs/web_data`) and deploys to GitHub Pages without modifying simulation contracts.

## Decisions

- Stack: `React + TypeScript + Vite`.
- Routing: `react-router-dom` with `HashRouter` for robust GitHub Pages compatibility without server rewrites.
- Data strategy: strict runtime parsing with `zod` for `index.json`, `manifest.json`, and scenario payloads.
- Dataset integration: **Option A** (automated sync) using `apps/student-web/scripts/run-sync.mjs` (and Python helper `scripts/sync_student_web_assets.py`) to copy `outputs/web_data` into `apps/student-web/public/web_data`.
- Educational content: optional adapter loads `content/scenarios.json` and `content/lessons.json` copied to `public/educational`; app keeps working if files are missing.
- Deploy: GitHub Actions workflow builds dataset + frontend and publishes `apps/student-web/dist` to Pages with dynamic base path.

## Incremental Deliverables

1. Phase 1: Audit and plan
- Confirm real export contract in `qc_lab_simulator/web_export.py`.
- Confirm current ops scripts and output paths.
- Document architecture and rollout.

2. Phase 2: Scaffold and foundation
- Create frontend app under `apps/student-web`.
- Configure Vite, TypeScript, Vitest.
- Establish folder boundaries:
  - `src/app`
  - `src/pages`
  - `src/features`
  - `src/entities`
  - `src/shared`

3. Phase 3: Core product views
- Implement pages:
  - Home experiment list
  - Experiment detail
  - Scenario viewer
- Implement required UX states:
  - loading
  - error
  - empty
  - not found
- Add Levey-Jennings chart with series + control limits and trigger highlighting.

4. Phase 4: Pipeline and deploy integration
- Automate dataset sync from `outputs/web_data` to app `public`.
- Add root helper script for frontend operations.
- Add GitHub Pages workflow with base-path handling.

5. Phase 5: Quality and documentation
- Add tests for contracts, path building, and core rendering states.
- Add app-specific README and integration guide in `docs`.
- Update root README with quick operational commands.

## Risks and Mitigations

- Contract drift risk:
  - Mitigation: runtime `zod` parsing + contract tests.
- GitHub Pages route risk:
  - Mitigation: HashRouter and Vite base path config.
- Data freshness risk:
  - Mitigation: explicit sync script in local workflow + CI export/sync steps.
- Responsibility-mixing risk:
  - Mitigation: all student UI code isolated in `apps/student-web`; Python simulation/authoring untouched.
