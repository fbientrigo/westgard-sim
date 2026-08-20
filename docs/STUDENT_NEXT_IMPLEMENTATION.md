# Student Next Implementation Contract

Status: authoritative for `apps/student-next/`. Written on branch
`feat/greenfield-student-experience`. Supersedes, for the greenfield app only,
the `apps/student-web`-targeted plans in `docs/product-discovery/IMPLEMENTATION_BRIEF_FOR_CLAUDE.md`
and `docs/product-discovery/SCREEN_FLOW.md`. Those documents remain valid as
product research; their route names, React/Zod/Recharts assumptions and
"reuse `LeveyJenningsChart`" instructions do **not** apply here.

This document is self-contained. Everything needed to implement is either stated
here or located by an exact repository path given here. No external repository,
no other conversation, and no further product decisions are required.

All student-facing copy in this document is final Spanish copy. Use it verbatim
unless a criterion says otherwise.

---

## Product objective

`apps/student-next` is a small learning instrument for clinical laboratory
students (course context: Bioquímica Clínica) that trains one skill:

> Look at a Levey–Jennings chart, identify the evidence, name the rule that the
> evidence supports, and decide what the laboratory should do with the run.

It is not a reference site. Static Westgard tables, definitions and videos
already exist elsewhere. The product's only reason to exist is that the student
**commits a judgement and then sees the evidence checked against a validated
engine**.

Three top-level destinations, permanently: **Practicar**, **Reglas**, **Tarjetas**.
A fourth top-level destination is out of scope.

---

## Student learning model

Every practice scenario runs one loop:

```
observe  →  mark evidence  →  name rule  →  decide action  →  reveal + explain  →  counterfactual / next
```

Ordering rationale (pattern → rule → interpretation → action): the student must
point at the chart *before* any rule name is offered, so the rule name cannot be
guessed from the option list and then justified backwards.

Nothing about the answer exists in the DOM before the student locks all three
answers. Progressive disclosure is enforced at data level: the reveal payload is
in the loaded JSON, so the implementation must not render it, and must not
place it in `title`, `aria-label`, `data-*` or visually hidden text before lock.

---

## Current repository findings

Evidence gathered on this branch (`git status` clean at audit time; baseline
`101 passed` from `pytest -q`; `node --check apps/student-next/app.js` exits 0).

### `apps/student-next/` (4 files: `index.html`, `styles.css`, `app.js`, `README.md`)

Good, keep:

- Zero-dependency static app: 3 files copied by CI, no bundler, no npm. This is
  the correct baseline for this product.
- Flashcard session mechanics in `app.js` (`ensureDeck`, `renderCurrentCard`,
  `revealCard`, `rateCard`, keyboard `Space/←/→`, pointer swipe with
  `touch-action: pan-y`, summary card).
- Mobile "study session" CSS pattern in `styles.css` under
  `@media (max-width: 640px)`: `body[data-view="cards"]` hides the topbar and
  desktop intro, shows `.session-bar`, uses `100dvh` and
  `env(safe-area-inset-*)`, sticky rating row, 58px rating buttons. This pattern
  is correct and must be generalised to Practice.
- `prefers-reduced-motion` block.

Prototype-quality or wrong, must be deleted (see "What should be discarded"):

- `rule12s`, `rule13s`, `rule22s`, `evaluate()` in `app.js`: a second
  implementation of the scientific rules in JavaScript.
- The `RULES` array in `app.js`: rule definitions, severities, interpretations
  and actions hardcoded in presentation code.
- The `PRESETS` array in `app.js`: scenario data hardcoded in presentation code.
- The whole current Practice view. It is a sandbox that prints the verdict
  (`#run-status`, `#rule-results`) continuously with `aria-live="polite"`. The
  student is never asked anything, so no reasoning is tested. It answers the
  question before it is asked.
- The home hero (`.hero`, `h1` at `clamp(2.55rem, 7vw, 5.4rem)`, `.hero-copy`)
  and `.topbar-note`: marketing furniture; the student reads before doing.
- `<svg ... aria-hidden="true">` inside a `role="img"` container whose only
  alternative is the static string "Gráfico de Levey-Jennings interactivo": the
  chart is unreadable to a screen reader and carries no data alternative.
- Point styling that encodes meaning in fill colour only, plus an `active` flag
  tied to "last two indices" rather than to rule evidence.
- `.entry-card:focus-visible { outline: none }`: focus visibility is replaced by
  a transform and shadow.
- Card session position is in memory only; reload restarts the deck.
- `apps/student-next/data/cards.json` is produced only by CI
  (`.github/workflows/student-pages.yml`), is not in the repository, and is not
  git-ignored. A fresh clone served locally shows "No fue posible cargar las
  tarjetas." until the file is copied by hand as documented in
  `apps/student-next/README.md`.

Shortest current path from open to a meaningful learning action: Home → tap
"Repasar tarjetas" → tap card → rate. Practice currently offers no action to
judge. After this contract, the shortest path is Home → "Empezar práctica" →
first scenario is already on screen.

### Domain

- Authoritative rule behaviour: `qc_lab_simulator/rules.py` (only
  `rule_1_2s`, `rule_1_3s`, `rule_2_2s`, `first_violation`), tested by
  `tests/test_rules.py`, registered in `qc_lab_simulator/metrics.py::_RULES`.
- Rule functions return **`bool` only**. No point-level evidence exists anywhere
  in the repository. `first_violation` returns a 1-based *run number at which the
  rule becomes detectable*, which for `2_2s` is the **second** point of the pair
  (`tests/test_rules.py::TestFirstViolation::test_2_2s_needs_two_runs` asserts
  `2` for a pair at runs 1–2; verified again in this audit: pair at runs 2–3
  returns `3`). It is therefore **not** "the offending point" and must never be
  presented as such.
- Rule logic is duplicated in JavaScript today: `apps/student-next/app.js`
  (thresholds `2` and `3` inline) and, in the legacy app, presentation-level rule
  metadata in `apps/student-web/src/features/chart-viewer/model/triggerTooltip.ts`.
  Both are second sources of truth. The greenfield app must contain none.
- `qc_lab_simulator/rules.py` imports only `typing`; importing
  `qc_lab_simulator.rules` does **not** import numpy (verified:
  `'numpy' in sys.modules` is `False` after import, because
  `qc_lab_simulator/__init__.py` only sets `__version__`). The numpy dependency
  lives in `simulate.py` / `scenarios.py` / `web_export.py`.
- `qc_lab_simulator/web_export.py` emits a strict validated contract
  (`series`, `control_limits`, `rule_results`, `summary`) for the legacy app over
  RNG scenarios of 30 runs. It is not used by `student-next` and must not become
  a dependency of it: 30 RNG points are unreadable at 360 px, `drift` and
  `imprecision` are shaped for rules the engine cannot evaluate, and the payload
  carries no point-level evidence.

### Content

- Authoritative flashcard deck: `content/flashcards/westgard_qc_basics.deck.json`
  (`deck_id: westgard_qc_basics`, 20 cards, stable string `id`s, `sort_order`,
  `tags`, `card_type`, Spanish text). CI copies this exact file to
  `_site/data/cards.json`. Keep these IDs stable.
- Copies exist under `apps/student-web/public/flashcards/westgard_qc_basics/`
  (`study_deck.json`, `manifest.json`) and under `outputs/`. Those are generated
  artifacts of the legacy pipeline. Never read or edit them from `student-next`.
- Markup convention is canonical and defined in
  `qc_lab_simulator/flashcards/markup.py`: `[[kind:text]]` with
  `SEMANTIC_KINDS = {rule, warning, rejection, specimen, instrument, qc}`, plus
  `**bold**`, `*italic*`, `` `code` ``. `app.js` currently reimplements a subset
  with regexes and silently drops `` `code` ``. Keep a renderer in the frontend
  (a static site cannot run Python at view time) but restrict it to exactly these
  four constructs and cover it with a unit test; treat `markup.py` as the spec.
- High-value cards for this experience (link them from Reglas):
  `one-two-s-rule`, `one-three-s-rule`, `two-two-s-rule`,
  `warning-versus-rejection`, `same-side-shift`, `wide-scatter`,
  `reject-run-action`, `multi-rule-rationale`, `control-levels`, `mean-and-sd`,
  `r-four-s-rule`, `four-one-s-rule`, `ten-x-rule`.
- Lower-value/generic for this experience but harmless, keep unchanged:
  `qc-purpose`, `control-material-definition`, `specimen-versus-control`,
  `delta-check-context`, `manual-review-note`, `post-maintenance-review`,
  `reagent-lot-change`.
- Do not rewrite card text in this work. No new deck, no UI-only card copies.
- `content/lessons.json` and `content/scenarios.json` are legacy English content
  for `apps/student-web`, translated at runtime by
  `apps/student-web/src/shared/config/localization.ts`. They are **not** inputs
  to `student-next`, and two of their strings are scientifically wrong (see
  "Scientific findings" below). Do not consume them.

### Deployment

- `.github/workflows/student-pages.yml` is already minimal and greenfield-only:
  it checks out, runs `node --check apps/student-next/app.js`, validates the deck
  with `python3 -m json.tool`, copies `index.html`/`styles.css`/`app.js` plus the
  deck into `_site/`, touches `.nojekyll`, and deploys. No npm, no secrets, no
  `apps/student-web` step. Paths filter is `apps/student-next/**`, the deck, and
  the workflow file. Deploy is `main`-only; pull requests build without
  deploying.
- Legacy build dependencies do not leak into it. `vercel.json`,
  `student_web_ops.ps1`, `scripts/sync_student_web_assets.py` all belong to the
  legacy app and stay untouched.
- The site can be produced from a clean checkout with no secrets today, and must
  remain so after this work: the data-generation step added by this contract runs
  on the runner's stock `python3` with **stdlib only** (no `pip install`).

---

## What remains valuable

1. `qc_lab_simulator/rules.py` + `tests/test_rules.py` — the only scientific
   source of truth.
2. `content/flashcards/westgard_qc_basics.deck.json` — canonical educational
   content and stable IDs.
3. `qc_lab_simulator/flashcards/markup.py` — canonical markup semantics.
4. The zero-dependency static delivery model and the existing Pages workflow.
5. The mobile session CSS pattern already present for cards.
6. The flashcard session interaction (reveal → "No la supe" / "La supe").

## What should be discarded

Delete, do not migrate:

- All JavaScript rule evaluation (`rule12s`, `rule13s`, `rule22s`, `evaluate`).
- `RULES` and `PRESETS` arrays in `app.js`.
- The slider sandbox layout (`.practice-layout` two-column with a sticky
  `.control-panel`, `#prev-slider`, `#last-slider`, `#rule-results` live region).
- The home hero and `.topbar-note`.
- Any dependency on `content/lessons.json`, `content/scenarios.json`,
  `qc_lab_simulator/web_export.py`, `outputs/**`, `apps/student-web/**`.
- Anything in `apps/student-web/` as a design reference. No migration.

---

## Scientific capability contract

Verified against `qc_lab_simulator/rules.py` and re-confirmed empirically during
this audit (mean `100.0`, sd `2.0`).

### Interactive rules (evaluated by the engine)

| Rule | Exact condition in code | Boundary | Severity |
| --- | --- | --- | --- |
| `1_2s` | `any(abs(v - mean) > 2.0 * sd)` | strict `>`; exactly ±2 SD does **not** trigger | warning |
| `1_3s` | `any(abs(v - mean) > 3.0 * sd)` | strict `>`; exactly ±3 SD does **not** trigger | rejection |
| `2_2s` | some `i` with `(v[i]-mean > 2sd and v[i+1]-mean > 2sd)` or `(v[i]-mean < -2sd and v[i+1]-mean < -2sd)` | strict `>` / `<`; adjacent pair only; **same side required** | rejection |

Confirmed behaviours (each is a required teaching point):

- `z = +2.0` → `1_2s` False. `z = +2.2` → True.
- `z = +3.0` and `z = -3.0` → `1_3s` False.
- Opposite-side adjacent pair (`+2.4`, `-2.6`) → `2_2s` False, `1_2s` True.
- Isolated `z = +3.4` → `1_3s` True **and** `1_2s` True. `1_3s` always implies
  `1_2s`; nothing in the engine suppresses the warning.
- Non-adjacent pair (`+2.1`, `0`, `+2.1`) → `2_2s` False
  (`tests/test_rules.py::TestRule2_2s::test_non_consecutive_pair_does_not_trigger`).
- Sequence order matters; only adjacency in the given order is examined.

### Reference-only rules (not evaluated, and not representable)

`R_4s`, `4_1s`, `10x` are absent from `rules.py`. Additionally, `R_4s` is a
within-run range rule between **two control levels**, and every data structure
in this contract carries a **single control level**, so `R_4s` cannot even be
represented, let alone evaluated.

UI treatment, mandatory:

- Label interactive rules `Evaluable aquí` and reference rules
  `Solo referencia`. Never the words "no soportado", "no disponible" or
  "no implementado".
- Reference rules appear in Reglas and in Tarjetas with full pattern,
  interpretation and action text. They are never offered as an answer option in
  Practice, and never rendered with a triggered/not-triggered state.
- The `Evaluable aquí` flag is **derived at build time** from the engine's own
  registry, not authored (see "Domain/presentation architecture"). It is
  therefore impossible for content to claim evaluation the engine cannot perform.
- Whenever Practice reveals a `1_2s`-only outcome, feedback must include this
  exact sentence: `Este simulador solo evalúa 1₂s, 1₃s y 2₂s. En el laboratorio, una advertencia 1₂s obliga a revisar también R₄s, 4₁s y 10x antes de decidir.`

### Error-type interpretation

Attribution of random vs systematic error is permitted **only** in these two
cases, and only as compatibility, never as proof:

- `2_2s` triggered → `Compatible con error sistemático (desplazamiento en un solo sentido).`
- `1_3s` triggered with exactly one point beyond ±3 SD and `2_2s` not triggered →
  `Compatible con error aleatorio o un error grosero puntual.`

In every other case the feedback omits error type entirely. Rationale: with one
control level and three rules, error type is under-determined; `R_4s` (the rule
that discriminates random error) is unavailable.

---

## Scientific findings and discrepancies

Findings from this audit that change what may be implemented. None of them
authorises changing `qc_lab_simulator/rules.py` in this work.

**SF1 — Strict inequality everywhere.** All three rules use `>` (and `<` for the
negative side). A control at exactly ±2.0 or ±3.0 SD does not trigger. Impact:
the product must teach this explicitly (fixture `boundary-exact-2s-01` and the
boundary sentence in the counterfactual), and the chart must not shape/colour an
exactly-±2.0 point as if it were outside.

**SF2 — `1_3s` implies `1_2s`.** Nothing suppresses the warning when a point is
beyond ±3 SD. Impact: reveal shows both as applying, and the grading table treats
"student said `1_2s`" as *incompleta*, not incorrect.

**SF3 — `2_2s` requires adjacency and the same side, earliest pair only.**
`rules.rule_2_2s` returns on the first qualifying pair. Impact: `evidence_runs`
for `2_2s` is exactly one pair; the distractor fixture teaches the same-side
requirement.

**SF4 — No point-level evidence exists in the repository.** Rule functions return
`bool`; `metrics.py` adds only `triggered` / `first_run` / `false_alarm`. Impact:
`evidence.py` is genuinely new domain code, and it is the only new domain code.

**SF5 — `first_violation` is detectability, not the offending point.** For `2_2s`
it returns the second point of the pair. Impact: see decision D5; the legacy
app's highlighting approach must not be copied.

**SF6 — `R_4s` is not merely unimplemented, it is unrepresentable.** It compares
two control levels within one run; every structure here carries one level.
Impact: reference-only status is permanent until a multi-level data model exists;
do not present it as "coming soon".

**SF7 — Legacy content states `R-4s` incorrectly.**
`content/scenarios.json` (`imprecision.common_mistake`) defines it as "4
consecutive values >1SD on the same side" — that is `4_1s`, not `R_4s`.
`content/lessons.json` (`imprecision.reveal_text`) says "consecutive values
alternating >1SD", also wrong. The canonical deck card `r-four-s-rule` states it
correctly ("dos resultados de control en la misma ejecución difieren en más de
4 DE"). Impact: those two files are legacy inputs to `apps/student-web` only and
must not be consumed by `student-next`; the correct definition to use is the deck's
and `content/rules_reference.json`'s. Minimal corrective action, to be done as a
separate content-only change with no code impact: fix those two strings in
`content/scenarios.json` and `content/lessons.json`. Not part of this work.

**SF8 — The RNG scenarios cannot be honestly graded.** `drift` and `imprecision`
are shaped for `10x` and `R_4s`. With only three rules, a drift series may trigger
`1_2s`/`2_2s` late or not at all, and asking a student to name the governing rule
teaches the wrong lesson. Impact: excluded from practice fixtures (D6).

**SF9 — The current JS rules happen to match today.** `app.js`'s inline
thresholds are numerically equivalent to `rules.py` at present, so nothing is
currently wrong on screen; the defect is structural (untested second source of
truth). Impact: deletion, not verification.

## Canonical data/content sources

| Source | Path | Owner | Consumed by |
| --- | --- | --- | --- |
| Rule evaluation | `qc_lab_simulator/rules.py` | Python (do not modify) | evidence module |
| Evidence derivation | `qc_lab_simulator/evidence.py` (new) | Python | export script |
| Rule reference text | `content/rules_reference.json` (new) | authored Spanish | Reglas view |
| Practice fixtures | `content/practice_scenarios.json` (new) | authored z-values | Practice view |
| Flashcards | `content/flashcards/westgard_qc_basics.deck.json` | existing canonical | Tarjetas view |
| Generated bundle | `apps/student-next/data/*.json` | generated, git-ignored | the whole app |

Rule: presentation code contains no thresholds, no rule conditions, no severity
mapping, no verdict mapping, and no scenario values. All of those arrive as data.


---

## Target UX

Routing stays hash-based, in `app.js`, with four routes:
`#home`, `#practice`, `#rules`, `#cards`. Practice accepts a scenario permalink:
`#practice/<scenario-id>` (used so a group of students on separate phones can
open the same chart). Unknown routes fall back to `#home`.

### Home

Information hierarchy, top to bottom, nothing else on the page:

1. Compact bar: brand `W Westgard` (32 px mark, links to `#home`). No tagline.
2. `h1`, one line, `clamp(1.75rem, 5vw, 2.6rem)`:
   `¿Aceptas o rechazas esta sesión?`
3. One supporting line, `0.95rem`, muted:
   `Practica con gráficos de Levey–Jennings y comprueba tu razonamiento.`
4. **Primary action**, full-width button, dark filled, min-height 56 px:
   `Empezar práctica` → `#practice` (first unfinished scenario, or scenario 1).
   Directly under it, muted `0.8rem`: `6 escenarios · sin cuenta · sin instalar`.
   (Do not claim offline capability: there is no service worker and none is in
   scope.)
5. Two secondary actions as a single row of two quiet outline buttons
   (min-height 52 px): `Reglas` and `Tarjetas`.
6. Nothing below the fold. No hero paragraph, no feature list, no rule table, no
   footer, no "how it works", no download links, no capability disclaimer (that
   belongs in Reglas and in Practice feedback where it is actionable).

Desktop (≥ 861 px): same order, content column capped at 560 px, left-aligned,
vertically centred in the viewport. The secondary row stays two columns. Do not
expand into a three-card dashboard grid; Practice must be visually dominant.

Mobile (≤ 640 px): same order, 18 px side padding, primary button full width,
secondary row remains two columns of 50/50. Total content height must fit
without scrolling at 360 × 640 CSS px.

Delete the current `.entry-grid` / `.entry-card` / `.entry-number` markup and
styles. Learn and Cards remain recognisable as named destinations, not as equal
tiles.

### Learn (`#rules`)

Purpose: visual comparison, not six essays. One compact row per rule, six rows,
one screen on desktop, vertically scrollable list on mobile.

Row structure (collapsed state, height ~92 px):

- Left: a 96 × 48 px inline SVG mini-pattern rendered from the canonical
  `mini_pattern` data (see "Scenario model"): mean line, dashed ±2 SD lines, the
  points, and the participating points ringed. `R_4s` renders two series
  (level 1 solid marker, level 2 hollow marker) plus a vertical connector between
  the two run-1 points to show the ~4 SD span.
- Middle: rule code (`1₂s`, `1₃s`, `2₂s`, `R₄s`, `4₁s`, `10x`) at `1.35rem`, and
  under it the one-line pattern text from `content/rules_reference.json`.
- Right: two badges stacked — severity (`Advertencia` / `Rechazo` /
  `Interpretación`) and capability (`Evaluable aquí` / `Solo referencia`).
  Badges carry text, not colour alone.
- The whole row is a `<button aria-expanded>` that expands a panel with:
  `Qué ves` (pattern), `Qué significa` (interpretation), `Qué haces` (action),
  and a link row `Repasar en tarjetas →` that opens
  `#cards?rule=<rule_id>` filtered to that rule's `card_ids`.

Ordering: the three `Evaluable aquí` rules first, then a divider row with the
text `Reglas de referencia (no se evalúan en este simulador)`, then the three
reference rules. Interactive rules are never visually diminished; reference rules
are never visually diminished either — only the badge differs and the divider
explains why.

First visual layer per rule is the mini-pattern plus the one-line pattern text.
Interpretation and action are second layer (collapsed). No rule gets more than
the three second-layer fields above.

### Practice (`#practice`) — core product

Layout order on every viewport (single column, no side panel):

1. Session bar, 44 px: `←` back to Home, progress `Escenario 3 / 6`, and a
   `Compartir` affordance that copies `#practice/<scenario-id>` (classroom use).
2. Scenario prompt, one line, `1.05rem`, changes by phase (copy below).
3. Chart (see "Chart contract").
4. Run strip: one `<button>` per run, labelled with the run number, min
   44 × 44 px, `aria-pressed` for selection. This is the evidence-marking
   control and the keyboard-accessible equivalent of tapping a point.
5. Phase controls (only the current phase's controls exist in the DOM).
6. Feedback region (only after lock).

#### Phases

**P1 `observe` + `evidence`** (one screen, no reveal)

- Prompt: `Marca los controles que te parecen problemáticos.`
- Controls: the run strip, plus a checkbox-styled toggle button
  `Ninguno: la serie está en control`. Selecting it clears and disables run
  selection. Confirm button: `Continuar` (disabled until either ≥1 run is
  selected or the "Ninguno" toggle is on).

**P2 `rule`**

- Prompt: `¿Qué regla respalda esa evidencia?`
- Options as four buttons, in this fixed order: `1₂s`, `1₃s`, `2₂s`,
  `Ninguna regla se activa`. Never more, never a reference rule.
- Under the options, muted `0.8rem`:
  `Solo estas tres reglas se evalúan aquí.`
- Confirm button: `Continuar`.

**P3 `action`**

- Prompt: `¿Qué debe hacer el laboratorio con esta sesión?`
- Three buttons, fixed order, with a one-line gloss each:
  - `Aceptar` — `Liberar resultados.`
  - `Revisar` — `No rechazar todavía; inspeccionar antes de liberar.`
  - `Rechazar` — `No liberar; investigar y repetir.`
- Confirm button: `Ver resultado` — this is the lock. After lock the three
  answers cannot be edited for this scenario.

**P4 `reveal`**

Rendered in this order:

1. A three-line verdict block. Each line is `icon + text`, never colour alone:
   - `Evidencia: correcta | parcial | incorrecta`
   - `Regla: correcta | incompleta | incorrecta`
   - `Acción: correcta | incorrecta`
   Icons: `✓` correct, `~` partial/incomplete, `✗` incorrect. Each icon has an
   adjacent text word; the icon is `aria-hidden` and the word is the label.
2. The chart re-renders with evidence highlighting (see "Chart contract").
3. `Qué pasó` — `teaching.pattern`.
4. `Por qué` — `teaching.why`, which must name the runs and the threshold, e.g.
   `Los controles 7 y 8 superan +2 DE y están del mismo lado, así que 2₂s se cumple.`
5. `Qué haces` — `teaching.action_text`.
6. `Tipo de error` — only when permitted by the capability contract.
7. `Nota` — the mandatory capability sentence when the outcome is `1_2s`-only.
8. Controls: `Probar un cambio` (→ P5), `Siguiente escenario`, and
   `Volver a ocultar` (re-hides the whole reveal block and the highlighting so a
   group can argue again without losing their locked answers).

**P5 `counterfactual`** (optional, entered from reveal)

- Prompt: `Cambia el control <n> y observa qué reglas dejan de cumplirse.`
- One control: a `<input type="range">` over the scenario's precomputed z-grid
  (`min` 0, `max` 40, `step` 1, mapping index → z), plus `−` / `+` buttons
  (44 × 44 px) for precise single-step changes on touch, and a readout
  `Control <n>: +2.6 DE`.
- On every change, the chart, the rule state list and the one-line consequence
  text update **together** from the precomputed table. No JS evaluation.
- The rule state list here shows all three interactive rules with
  `Se cumple` / `No se cumple` plus the participating runs.
- Boundary teaching: when the selected z is exactly `+2.0`, `-2.0`, `+3.0` or
  `-3.0`, the readout appends the scenario-independent sentence
  `Exactamente en el límite: la regla exige superarlo, así que no se cumple.`
- Exit: `Volver al resultado` and `Siguiente escenario`.

#### Grading (deterministic, computed in the frontend by comparing to generated data)

`expected` fields come from the generated bundle. Comparison only, no rule logic.

Evidence:

| Student selection | Judgement |
| --- | --- |
| set equals `expected.evidence_runs` | correcta |
| `expected.evidence_runs` is empty and student chose "Ninguno" | correcta |
| non-empty strict subset or strict superset of `expected.evidence_runs` | parcial |
| anything else (including "Ninguno" when evidence exists, or a selection when none exists) | incorrecta |

Rule:

| Condition | Judgement |
| --- | --- |
| choice equals `expected.rule` (or "Ninguna" when `expected.rule` is null) | correcta |
| choice is `1_2s`, and `expected.rule` is `1_3s` or `2_2s`, and `1_2s` is also triggered | incompleta |
| choice is a rule that is triggered but is not `expected.rule` | incompleta |
| any other case | incorrecta |

Action: correct if and only if it equals `expected.action`
(`accept` / `review` / `reject`).

The "incompleta" rule row exists because `1_3s` always implies `1_2s`; a student
naming the warning is not wrong, only insufficient. Feedback for that case reads:
`1₂s también se cumple, pero la regla que decide es <X>.`

Set summary after scenario 6: `Acciones correctas: X / 6`, plus one line naming
the family the student handled and the family they missed (from
`scenario.family`), and buttons `Repetir set` and `Volver al inicio`. No score
history, no streaks, no timers.

### Chart contract

One renderer, `src/chart.js`, pure function of `(scenarioPoints, highlight)`.

- Y axis fixed to −4 … +4 SD so charts are comparable across scenarios.
- Gridlines at −3, −2, −1, 0, +1, +2, +3 SD. Mean solid. ±2 SD dashed `5 5`.
  ±3 SD dashed `2 5`. Axis labels `Media`, `+2 DE`, `−2 DE`, `+3 DE`, `−3 DE`
  (omit ±1 DE labels below 480 px, keep the lines).
- Point marker shape encodes zone, redundantly with colour. The frontend never
  classifies a `z` value with `±2`/`±3` comparisons. Instead every point in the
  bundle carries a categorical `zone` annotated at build time
  (`"within_2sd" | "beyond_2sd" | "beyond_3sd"`), and JS only maps that value to
  a shape: `within_2sd` → circle, `beyond_2sd` → triangle, `beyond_3sd` → square.
  The exporter derives `zone` from the canonical rule functions on the single
  point (`beyond_3sd` when `rules.rule_1_3s([value], mean, sd)`, else
  `beyond_2sd` when `rules.rule_1_2s([value], mean, sd)`, else `within_2sd`), so
  a point exactly at ±2.0 or ±3.0 SD stays the *inner* shape, matching engine
  semantics, with no threshold arithmetic anywhere in JS.
- Before lock: no highlighting whatsoever, and the marker shape rule still
  applies (shape describes position, not a verdict; a student can already see a
  point is outside ±2 SD — that is the observation the task depends on).
- After lock: each run in the governing rule's `evidence_runs` gets a 3 px ring,
  a bold run label, and a vertical dotted connector from the point to the
  relevant threshold line, which is drawn solid and labelled with the fixed axis
  label (`+2 DE`). For `2_2s`, additionally draw a horizontal bracket spanning
  the two evidence points, labelled `2 consecutivos · mismo lado`.
- Student-selected runs (their answer) are marked with a small caret under the
  run label so the student can see their marks next to the truth.
- Accessibility: the `<svg>` keeps `aria-hidden="true"`; immediately after it,
  render a `.visually-hidden` `<table>` with one row per run
  (`Control`, `Desviación en DE`, `Zona`) and a `<p role="status">` summary that
  is phase-dependent:
  - before lock: `Serie de 10 controles. Desviaciones en DE: +0,4; −0,6; …`
  - after lock: appends `Reglas que se cumplen: 2₂s en los controles 7 y 8.`
  The `role="status"` node must not exist before lock with reveal content.

### Cards (`#cards`)

Two contexts, one canonical deck.

**Browse** (`#cards` on ≥ 861 px, or `#cards?browse=1` anywhere): a list of the
20 cards grouped by `tags[0]`, front text only, with a filter row of tag chips
and a `rule=` filter honoured from the URL (used by Reglas). One primary button
`Iniciar repaso` starts the session with the current filter applied.

**Session** (default on ≤ 860 px, and after `Iniciar repaso`): only session bar
(`←`, progress bar, `3 / 20`), card, `Mostrar respuesta`, then `No la supe` /
`La supe`. Nothing else in the DOM: no tag chips, no filters, no hints on mobile,
no deck metadata.

- Order: deterministic by `sort_order` then `id`. A `Mezclar` toggle exists only
  in Browse and, when on, uses a seeded shuffle stored with the session so the
  order is stable across reloads.
- Rating behaviour is unchanged from today: `La supe` advances, `No la supe`
  advances and appends the card once to the end of the queue (a single re-show,
  not a scheduling algorithm).
- Session position, queue and counters persist in `localStorage` under
  `wnext:cards:v1` and are restored on load; a `Reiniciar` control appears only
  on the summary card.
- Keyboard: `Space` reveals, `←` = No la supe, `→` = La supe, `Esc` = back to
  Home. Swipe kept as today. The card must be a real `<button>` element, not a
  `div` with `role="button"`.

### Mobile session behavior

Breakpoints: `≤ 640 px` = session mode, `641–860 px` = single column with topbar,
`≥ 861 px` = desktop.

In session mode, for `body[data-view="practice"]` and `body[data-view="cards"]`:

- Hide the topbar, all descriptive intros, all secondary navigation.
- Show the 44 px session bar only (back, progress, and for practice the
  `Compartir` icon button).
- Use `100dvh` and `env(safe-area-inset-*)` as the existing cards CSS already
  does; extend the same rules to practice.
- Practice vertical budget at 360 × 640 CSS px (worst case in scope):
  session bar 44 + prompt 28 + chart 200 + run strip 52 + phase controls
  (max 3 stacked buttons at 52 + 8 gap = 180) + confirm 56 = 560 px, leaving
  ≥ 60 px slack. The chart and the active controls must be simultaneously visible
  without scrolling in every phase; the reveal block is allowed to require
  scrolling, and on entering reveal the page must scroll the verdict block into
  view while keeping the chart's top edge visible.
- Chart SVG uses `viewBox="0 0 320 200"` below 481 px, `0 0 480 260` at
  481–860 px, `0 0 720 340` above. Axis label font-size is set per breakpoint so
  rendered text is ≥ 11 px at all widths (never scale a 760 px viewBox into
  324 px of screen).
- Run strip: 10 buttons of 30 px + 2 px gaps fits 320 px. Buttons are 30 px wide
  but 44 px tall, and the strip's tap area is padded to 44 px; no horizontal
  scrolling at 360 px.
- 390 px and 430 px: same layout, extra width goes to the chart and run strip
  only. No layout change, no extra content revealed.
- No horizontal page scroll at any width ≥ 320 px.


---

## Domain/presentation architecture

Four layers, one direction of flow:

```
qc_lab_simulator/rules.py          (unchanged, canonical truth)
        ↑ called by
qc_lab_simulator/evidence.py       (new, pure stdlib: derives WHY)
        ↑ called by
scripts/export_student_next_data.py (new, stdlib only, build time)
        ↓ writes
apps/student-next/data/*.json      (generated, git-ignored)
        ↓ fetched by
apps/student-next/src/*.js         (presentation: renders + compares, never evaluates)
```

Rules for the boundary, non-negotiable:

1. `qc_lab_simulator/rules.py` is not modified by this work.
2. `evidence.py` reproduces **no** rule logic. It contains no numeric SD
   threshold, no sign or same-side test, and no adjacency predicate. It derives
   every `triggered` flag and every `evidence_runs` entry by *calling the
   canonical `rules.py` functions on the smallest candidate subsets*:
   - `1_2s` participation of run `i`: `rules.rule_1_2s([values[i]], mean, sd)`.
   - `1_3s` participation of run `i`: `rules.rule_1_3s([values[i]], mean, sd)`.
   - `2_2s` participation of pair `(i, i+1)`:
     `rules.rule_2_2s([values[i], values[i+1]], mean, sd)`, scanned left to right,
     reporting the first pair that returns `True` (mirrors `rules.rule_2_2s`,
     which returns on the first match).
   The per-rule `triggered` flag is the canonical whole-series call
   (`rules.rule_1_2s(values, mean, sd)`, etc.). Because both come from the same
   functions, `triggered` is `True` **iff** `evidence_runs` is non-empty by
   construction, not by a re-implemented condition. `evidence.py` may import only
   the standard library, `.rules`, and `.metrics` (for the canonical registry in
   rule 4); all three are numpy-free.
3. The export script must not import `simulate.py`, `scenarios.py`,
   `web_export.py` or numpy, so CI needs no `pip install`.
4. There is exactly **one** supported-rule registry in this pipeline: the
   engine's own table `qc_lab_simulator.metrics._RULES`, which maps each rule ID
   directly to its canonical `rules.py` function. `evidence.py` imports and
   iterates that table; it does **not** declare a parallel supported-rule list.
   It declares only `REFERENCE_RULES = ("R_4s", "4_1s", "10x")` — the names that
   have no engine function. `evaluation: "interactive" | "reference"` in the
   generated rules payload is set by the export script purely from membership in
   that one registry (`rule_id in metrics._RULES`), never authored. Because there
   is a single source, no drift is possible and no capability-comparison test is
   maintained. `content/rules_reference.json` must not contain an `evaluation`
   field; if it does, the export exits non-zero.
5. Frontend JS contains no numeric SD threshold in any comparison, no severity
   table, no verdict derivation, no zone classification, and no scenario values.

## Evidence model

`evidence.py` public API:

```python
from qc_lab_simulator.metrics import _RULES as SUPPORTED_RULES  # {id: rules.py fn}
REFERENCE_RULES: tuple[str, ...] = ("R_4s", "4_1s", "10x")

def evaluate_series(values: list[float], mean: float, sd: float) -> dict
```

`SUPPORTED_RULES` is the engine's own registry (rule ID → canonical `rules.py`
function); `evidence.py` does not maintain a second list. Evidence is derived by
calling those functions on the smallest candidate subsets, never by re-testing a
threshold (see "Domain/presentation architecture", rules 2 and 4).

`evaluate_series` returns exactly this shape (keys in this order):

```json
{
  "rules": [
    {
      "rule": "1_2s",
      "triggered": true,
      "severity": "warning",
      "evidence_runs": [7, 8],
      "side": "positive"
    },
    { "rule": "1_3s", "triggered": false, "severity": "rejection",
      "evidence_runs": [], "side": null },
    { "rule": "2_2s", "triggered": true, "severity": "rejection",
      "evidence_runs": [7, 8], "side": "positive" }
  ],
  "verdict": "reject",
  "governing_rule": "2_2s"
}
```

Exact semantics:

- `triggered` is the canonical whole-series call for that rule
  (`rules.rule_1_2s(values, mean, sd)`, etc.). `evidence.py` never recomputes it
  from a threshold.
- `evidence_runs` are 1-based run numbers, ascending, obtained by applying the
  same canonical function to candidate subsets:
  - `1_2s`: every run `i` for which `rules.rule_1_2s([values[i]], mean, sd)` is
    `True`.
  - `1_3s`: every run `i` for which `rules.rule_1_3s([values[i]], mean, sd)` is
    `True`.
  - `2_2s`: the **earliest** adjacent pair `(i, i+1)` for which
    `rules.rule_2_2s([values[i], values[i+1]], mean, sd)` is `True`, reported as
    `[i+1, i+2]`. Later pairs are not reported; the scan mirrors
    `rules.rule_2_2s`, which returns on the first match. The same-side and
    adjacency requirements are enforced by the function itself, not re-checked
    here.
  By construction `triggered` is `True` iff `evidence_runs` is non-empty.
- `side`: a descriptive summary of where the reported evidence runs sit relative
  to the mean — `"positive"` if all are above, `"negative"` if all below,
  `"mixed"` if both (possible for `1_2s`, e.g. the distractor fixture), `null`
  when not triggered. It is computed from the already-identified `evidence_runs`
  and is never used to decide triggering.
- The earliest offending point, when the UI needs one, is simply
  `min(evidence_runs)`; there is no separate field for it. Do **not** use
  `rules.first_violation` in this pipeline — for `2_2s` it returns the run at
  which the rule becomes *detectable* (the second point of the pair), not the
  first offending point — and never present any value as "the offending point"
  unless it comes from `evidence_runs`.
- `verdict`: `"reject"` if any triggered rule has `severity == "rejection"`;
  else `"review"` if `1_2s` triggered; else `"accept"`. Severity mapping comes
  from the docstrings in `rules.py` (`1_2s` is documented as the warning rule;
  `1_3s` and `2_2s` as rejection rules).
- `governing_rule`: the triggered rule with the highest severity, tie-broken by
  the order `1_3s` before `2_2s` (a value beyond ±3 SD is the stronger single
  finding). `null` when nothing is triggered.
- `severity` values are exactly `"warning"` and `"rejection"`.

This is the minimal model the UI needs: which points, which side, what to do. No
threshold numbers or comparison predicates are reproduced in the payload; the
chart's SD lines are fixed axis gridlines and the reveal wording comes from
authored `teaching` text. No additional fields.

## Scenario model

### `content/practice_scenarios.json`

Authored, deterministic, no RNG. Every scenario: 10 runs, one control level,
`mean: 100.0`, `sd: 2.0`, values authored as one-decimal z-values. The exporter
converts with `value = mean + z * sd`.

Float safety was verified for this exact configuration: across the 41-value grid
`-4.0 … +4.0` step `0.2`, `rules.rule_1_2s`/`rule_1_3s` agree with exact
`abs(z) > 2` / `abs(z) > 3` in every case, with zero mismatches, and `z = ±2.0`
/ `±3.0` do not trigger. Do not change `mean`/`sd` or the grid step without
re-running that check.

Authored fields per scenario: `id`, `label`, `family`, `z_values`,
`editable_run`, `teaching.pattern`, `teaching.why`, `teaching.action_text`.
Nothing else is authored — `expected`, `evaluation`, `counterfactuals`,
`teaching.error_type` and `teaching.capability_note` are all derived at export.

### The six MVP fixtures (verified against the engine)

Use these exact z arrays. The verified engine outcome is given for each; the
export script must reproduce it and a golden test must assert it.

| id | family | z_values (runs 1…10) | editable_run | verified outcome |
| --- | --- | --- | --- | --- |
| `in-control-01` | `in_control` | `0.4, -0.6, 0.9, -0.3, 0.7, -1.1, 0.2, 1.4, -0.8, 0.5` | 8 | nothing triggers → `accept`, `governing_rule: null` |
| `warning-1-2s-01` | `isolated_warning` | `-0.5, 0.6, -0.2, 1.1, -0.9, 0.3, 1.6, -0.4, 2.4, -0.7` | 9 | `1_2s` only, evidence `[9]`, side positive → `review`, governing `1_2s` |
| `reject-1-3s-01` | `single_extreme` | `0.3, -0.7, 0.5, -1.2, 0.8, -0.4, 1.0, -3.3, 0.6, -0.5` | 8 | `1_2s` `[8]` and `1_3s` `[8]`, side negative, `2_2s` false → `reject`, governing `1_3s` |
| `reject-2-2s-01` | `systematic_shift` | `0.5, -0.4, 0.7, -0.6, 0.9, 1.2, 2.3, 2.6, 1.8, 0.4` | 8 | `1_2s` `[7,8]`, `2_2s` `[7,8]`, side positive, `1_3s` false → `reject`, governing `2_2s` |
| `boundary-exact-2s-01` | `near_boundary` | `-0.3, 0.8, -0.6, 1.3, -0.9, 0.4, 1.7, 2.0, -0.5, 0.7` | 8 | nothing triggers (run 8 is exactly +2.0 SD) → `accept`, `governing_rule: null` |
| `distractor-opposite-01` | `misleading_distractor` | `0.4, -0.8, 0.6, -0.5, 1.1, -0.7, 2.3, -2.4, 0.9, -0.3` | 8 | `1_2s` `[7,8]` side **mixed**, `2_2s` **false** (opposite sides) → `review`, governing `1_2s` |

Set order is exactly the table order. It varies one thing at a time:
in-control → one warning → one extreme → same-side pair → exact boundary →
opposite-side trap.

`expected` per scenario, derived at export:

- `expected.action` = `evaluation.verdict`
- `expected.rule` = `evaluation.governing_rule`
- `expected.evidence_runs` = `evidence_runs` of the governing rule, or `[]` when
  `governing_rule` is null.

### Counterfactual table

For each scenario the exporter emits, for the single `editable_run`, the full
grid `z ∈ [-4.0, -3.8, …, 3.8, 4.0]` (41 entries, indices 0…40), each with the
complete `evaluate_series` result for the series with that run replaced, plus a
`consequence` string built from a fixed template set (below). Payload size is
6 × 41 evaluations; no client-side evaluation is possible or needed.

`consequence` templates (chosen by comparing the counterfactual result with the
scenario's baseline result; the export script contains this mapping, the frontend
does not):

- unchanged: `Sin cambios: las mismas reglas se cumplen.`
- a rule stops applying:
  `Con este valor, <regla> ya no se cumple.` (list all that stopped, comma-separated)
- a rule starts applying: `Con este valor, <regla> empieza a cumplirse.`
- both: `Con este valor, <regla A> ya no se cumple y <regla B> empieza a cumplirse.`
- verdict change is appended when it changes:
  `La decisión pasa de <acción anterior> a <acción nueva>.`

Verified counterfactual teaching moments that must work (checked against the
engine during this audit):

| Scenario | Change | Verified result |
| --- | --- | --- |
| `warning-1-2s-01` | run 9: `+2.4 → +1.8` | all rules false → verdict `accept` |
| `reject-2-2s-01` | run 8: `+2.6 → -2.4` | `2_2s` false, `1_2s` `[7,8]` mixed → verdict `review` |
| `reject-2-2s-01` | run 8: `+2.6 → +1.8` | `2_2s` false, `1_2s` `[7]` → verdict `review` |
| `reject-2-2s-01` | run 8: `+2.6 → +3.2` | `1_3s` `[8]`, `2_2s` `[7,8]` → still `reject` |
| `boundary-exact-2s-01` | run 8: `+2.0 → +2.2` | `1_2s` `[8]` → verdict `review` |
| `distractor-opposite-01` | run 8: `-2.4 → +2.4` | `2_2s` `[7,8]` appears → verdict `reject` |
| `reject-1-3s-01` | run 8: `-3.3 → -2.8` | `1_3s` false, `1_2s` `[8]` → verdict `review` |

### `content/rules_reference.json`

Authored Spanish rule reference, six entries, no `evaluation` field:

```jsonc
{
  "format_version": "1.0",
  "rules": [
    {
      "id": "1_2s",
      "display": "1₂s",
      "severity_label": "Advertencia",
      "pattern": "Un control supera ±2 DE.",
      "interpretation": "Señal sensible y poco específica: obliga a mirar el resto del patrón antes de decidir.",
      "action": "Revisa la sesión y las demás reglas antes de liberar resultados.",
      "mini_pattern": { "series": [[-0.4, 0.6, -0.3, 0.8, 2.4, -0.2]], "highlight": [[5]] },
      "card_ids": ["one-two-s-rule", "warning-versus-rejection"]
    }
    // 1_3s, 2_2s, R_4s, 4_1s, 10x follow the same shape
  ]
}
```

Required content for the remaining five entries (author exactly this):

- `1_3s` — severity `Rechazo`; pattern `Un control supera ±3 DE.`;
  interpretation `Un desvío aislado de esta magnitud es compatible con un problema analítico importante o un error grosero.`;
  action `No liberes resultados: investiga, corrige y repite los controles.`;
  mini `[[0.2, -0.5, 0.4, -0.3, 3.3, 0.1]]`, highlight `[[5]]`;
  cards `["one-three-s-rule", "warning-versus-rejection", "reject-run-action"]`.
- `2_2s` — severity `Rechazo`; pattern `Dos controles consecutivos superan 2 DE del mismo lado.`;
  interpretation `La repetición en el mismo sentido orienta a un desplazamiento sistemático.`;
  action `No liberes resultados: busca una causa persistente (calibración, lote, instrumento).`;
  mini `[[-0.3, 0.5, -0.4, 1.1, 2.3, 2.6]]`, highlight `[[5, 6]]`;
  cards `["two-two-s-rule", "same-side-shift"]`.
- `R_4s` — severity `Interpretación`; pattern `En una misma sesión, dos niveles de control se separan por más de 4 DE.`;
  interpretation `El contraste entre un nivel alto y otro bajo orienta a error aleatorio.`;
  action `Busca una fuente de imprecisión (mezclado, pipeteo, inestabilidad del sistema).`;
  mini two series `[[2.2, 0.3, -0.4], [-2.1, 0.2, 0.5]]`, highlight `[[1], [1]]`;
  cards `["r-four-s-rule", "wide-scatter"]`.
- `4_1s` — severity `Interpretación`; pattern `Cuatro controles consecutivos superan 1 DE del mismo lado.`;
  interpretation `Una secuencia sostenida hacia un lado sugiere un desplazamiento sistemático incipiente.`;
  action `Busca un cambio persistente en calibración, lote o instrumento.`;
  mini `[[-0.2, 1.3, 1.5, 1.2, 1.6, 0.4]]`, highlight `[[2, 3, 4, 5]]`;
  cards `["four-one-s-rule", "same-side-shift"]`.
- `10x` — severity `Interpretación`; pattern `Diez controles consecutivos caen del mismo lado de la media.`;
  interpretation `Aunque cada punto esté cerca de la media, la persistencia de un solo lado es la señal.`;
  action `Interpreta la serie completa; no evalúes cada punto por separado.`;
  mini `[[0.3, 0.6, 0.4, 0.8, 0.5, 0.7]]`, highlight `[[1, 2, 3, 4, 5, 6]]`;
  cards `["ten-x-rule", "same-side-shift", "multi-rule-rationale"]`.

Every `card_ids` entry must exist in
`content/flashcards/westgard_qc_basics.deck.json`; the export script fails if not.

## Generated bundle

`scripts/export_student_next_data.py --output-dir apps/student-next/data` writes
exactly three files, each with `"format_version": "1.0"` and
`"generated_by": "scripts/export_student_next_data.py"`:

- `cards.json` — byte-identical copy of
  `content/flashcards/westgard_qc_basics.deck.json` (keeps the current loader and
  the current CI copy step semantically identical).
- `rules.json` — `{ "format_version", "generated_by", "engine": { "supported_rules", "reference_rules", "control_levels": 1, "boundary_semantics": "strict_greater_than" }, "rules": [ …authored fields + "evaluation": "interactive"|"reference" ] }`.
- `practice.json` — `{ "format_version", "generated_by", "engine": {…same…}, "scenarios": [ … ] }` where each scenario is
  `{ id, label, family, mean, sd, points: [{run, value, z, zone}], editable_run, evaluation, expected, counterfactuals: { run, z_values, results: [{ z, evaluation, consequence }] }, teaching: { pattern, why, action_text, error_type, capability_note } }`.
  Each point's `zone` is the categorical presentation value
  (`"within_2sd" | "beyond_2sd" | "beyond_3sd"`) derived at build time from the
  canonical rule functions (see "Chart contract"); the frontend maps it to a
  marker shape and never recomputes it.

The script exits non-zero, with a message naming the offending id, if: an
authored `evaluation` field is present; a `card_ids` reference is missing; a
scenario has ≠ 10 z-values; `editable_run` is out of range; a z-value is outside
`[-4.0, 4.0]` or not a multiple of `0.1`; or two scenarios share an `id`.

## Directory/file plan

```
qc_lab_simulator/
  rules.py                          # unchanged
  evidence.py                       # NEW  (stdlib only)
content/
  practice_scenarios.json           # NEW  (authored fixtures)
  rules_reference.json              # NEW  (authored rule reference)
  flashcards/westgard_qc_basics.deck.json   # unchanged canonical deck
scripts/
  export_student_next_data.py       # NEW  (stdlib only)
tests/
  test_evidence.py                  # NEW  (parity + boundaries)
  test_student_next_export.py       # NEW  (golden bundle + guards)
apps/student-next/
  index.html                        # rewritten markup
  styles.css                        # extended (session mode for practice)
  app.js                            # bootstrap + routing only
  src/chart.js                      # NEW  SVG + a11y table (no rule logic)
  src/practice.js                   # NEW  phase machine + answer comparison
  src/learn.js                      # NEW  rule rows from rules.json
  src/cards.js                      # NEW  session (moved out of app.js)
  src/storage.js                    # NEW  localStorage helpers
  src/markup.js                      # NEW  4-construct renderer
  test/practice.test.js             # NEW  node --test
  test/markup.test.js               # NEW  node --test
  data/                             # generated, git-ignored
  README.md                         # updated commands
.gitignore                          # add: apps/student-next/data/
.github/workflows/student-pages.yml # add setup-python + export step + tests
```

No other files are touched. No `package.json`, no bundler, no npm dependency, no
CSS framework. Total new JS is expected under ~900 lines; if a module needs a
build step, the design is wrong.


---

## Implementation slices

Order is mandatory. Each slice is independently useful, independently testable,
and leaves the deployed site working.

### Slice 1 — Canonical evidence + generated bundle (no UI change)

**Goal.** Make Python able to say *why* a rule fired, and ship that as static JSON.

**Student behavior.** Nothing visible yet; the site keeps working unchanged.

**Files.** `qc_lab_simulator/evidence.py`, `content/practice_scenarios.json`,
`content/rules_reference.json`, `scripts/export_student_next_data.py`,
`tests/test_evidence.py`, `tests/test_student_next_export.py`, `.gitignore`.

**Domain changes.** New `evidence.py` exactly as specified in "Evidence model".
`rules.py` untouched.

**UI changes.** None.

**Acceptance criteria.**
- `evidence.evaluate_series` returns the documented shape for all six fixtures.
- The export writes `cards.json`, `rules.json`, `practice.json`.
- `rules.json` marks `1_2s`/`1_3s`/`2_2s` as `interactive` and
  `R_4s`/`4_1s`/`10x` as `reference`, derived, not authored.
- Adding an `"evaluation"` key to `content/rules_reference.json` makes the export
  exit non-zero.

**Tests.** `tests/test_evidence.py` (defense-in-depth, since evidence already
comes from the canonical functions): parity against `rules.py` for all six
fixtures **and** all 41 counterfactual values of each (246 series × 3 rules);
`triggered` ⇔ non-empty `evidence_runs` equivalence; boundary cases `±2.0`/`±3.0`
non-triggering; opposite-side pair non-triggering; `2_2s` earliest-pair only.
No test compares a supported-rule list against `metrics._RULES`, because
`evidence.py` reuses that one registry rather than declaring its own.
`tests/test_student_next_export.py`: golden assertions for the six verified
outcomes in the fixture table; every point carries a `zone` consistent with the
canonical functions (`±2.0`/`±3.0` points stay `within_2sd`/`beyond_2sd`
respectively); every `card_ids` id exists in the deck; `cards.json` is
byte-identical to the source deck; the export imports no numpy
(`assert "numpy" not in sys.modules` after importing the script module).

**Correct if:**
```
python scripts/export_student_next_data.py --output-dir apps/student-next/data
python -m pytest tests/test_evidence.py tests/test_student_next_export.py -q
```
both exit 0, and
```
python -c "import json;d=json.load(open('apps/student-next/data/practice.json'));s=[x for x in d['scenarios'] if x['id']=='reject-2-2s-01'][0];print(s['expected'])"
```
prints `{'action': 'reject', 'rule': '2_2s', 'evidence_runs': [7, 8]}`.

---

### Slice 2 — Practice loop with locked decision and evidence reveal

**Goal.** Replace the sandbox with the observe → mark → rule → action → reveal loop.

**Student behavior.** The student marks points, names a rule, decides an action,
and only then sees the engine's evidence highlighted on the same chart with an
explanation naming the runs and the threshold.

**Files.** `apps/student-next/index.html`, `styles.css`, `app.js`,
`src/chart.js`, `src/practice.js`, `src/storage.js`,
`apps/student-next/test/practice.test.js`.

**Domain changes.** None (consumes `data/practice.json`).

**UI changes.** Delete `RULES`, `PRESETS`, `rule12s`, `rule13s`, `rule22s`,
`evaluate`, `renderResults`, both sliders and `#run-status`. Implement phases P1–P4
and the chart contract, including marker shapes, ring/connector/bracket
highlighting, the student's caret marks, the visually hidden data table and the
phase-dependent `role="status"` summary. Home is rewritten to the specified
hierarchy in the same slice (it is the entry point to this loop).

**Acceptance criteria.**
- Before lock, `document.body.innerHTML` contains none of: `expected`,
  `evidence_runs`, the governing rule display string, or any verdict word.
- `Continuar` is disabled until the current phase has an answer.
- Rule options are exactly `1₂s`, `1₃s`, `2₂s`, `Ninguna regla se activa`.
- Grading follows the three grading tables verbatim, including `parcial` and
  `incompleta`.
- `Volver a ocultar` removes the reveal block and highlighting without changing
  the locked answers.
- Progress within the set persists in `localStorage` under `wnext:practice:v1`.

**Tests.** `apps/student-next/test/practice.test.js` with `node --test`:
grade-evidence subset/superset/equal/empty cases; grade-rule
correct/incompleta/incorrecta cases including `1_2s` chosen when governing is
`1_3s`; grade-action mapping; phase machine refuses to advance without an answer
and refuses to un-lock.

**Correct if:**
```
node --test apps/student-next/test/
node --check apps/student-next/app.js
grep -nE "(rule12s|rule13s|rule22s|Math\.abs\([^)]*\)\s*[<>])" apps/student-next/app.js apps/student-next/src/*.js
```
the first two exit 0 and the `grep` finds nothing (exit 1), and, serving the
directory, `#practice/reject-2-2s-01` after locking any answer shows exactly two
ringed points at runs 7 and 8 with the `+2 DE` line drawn solid and the
`2 consecutivos · mismo lado` bracket spanning them.

---

### Slice 3 — Counterfactual control point

**Goal.** Let the student change one control and see rules stop or start applying.

**Student behavior.** From the reveal, the student moves control 8 of
`reject-2-2s-01` from `+2.6` to `−2.4` and reads
`Con este valor, 2₂s ya no se cumple. La decisión pasa de Rechazar a Revisar.`
while the chart drops the bracket and re-marks the evidence.

**Files.** `apps/student-next/src/practice.js`, `src/chart.js`, `styles.css`.

**Domain changes.** None (consumes the precomputed `counterfactuals` table).

**UI changes.** Phase P5 as specified: range over grid indices, `−`/`+` buttons
at 44 × 44 px, readout, three-rule state list, consequence line, boundary
sentence at exactly `±2.0`/`±3.0`, chart and text updating in the same render.

**Acceptance criteria.**
- The frontend reads `counterfactuals.results[index]` and performs no arithmetic
  on thresholds.
- Every grid index is reachable by keyboard (arrow keys on the range input).
- Selecting `z = +2.0` on `boundary-exact-2s-01` shows the boundary sentence and
  no rule as applying.

**Tests.** Extend `practice.test.js`: given a stub counterfactual table, the
selected index maps to the expected `consequence` and rule-state list; index
clamping at 0 and 40.

**Correct if:**
```
python -c "import json;d=json.load(open('apps/student-next/data/practice.json'));s=[x for x in d['scenarios'] if x['id']=='reject-2-2s-01'][0];r=[q for q in s['counterfactuals']['results'] if abs(q['z']+2.4)<1e-9][0];print(r['evaluation']['verdict'], r['consequence'])"
```
prints `review` followed by a consequence string containing
`2₂s ya no se cumple`.

---

### Slice 4 — Mobile session shell and accessibility

**Goal.** Make the practice loop a focused phone session that is operable by
keyboard and screen reader.

**Student behavior.** On a 360 px phone the student sees only the session bar,
chart, run strip and the current controls, with no scrolling needed to answer.

**Files.** `apps/student-next/styles.css`, `index.html`, `src/chart.js`,
`app.js`.

**Domain changes.** None.

**UI changes.** Extend `body[data-view="practice"]` session mode to match the
existing cards pattern; per-breakpoint `viewBox` and font sizes; 44 px targets;
restore visible focus rings (remove `outline: none` on `:focus-visible` and use a
3 px `--brand` ring with 2 px offset); `Esc` returns Home from any view.

**Acceptance criteria.**
- At 360 × 640, chart plus active phase controls are fully visible without
  scrolling in P1, P2, P3 and P5.
- No horizontal scrollbar at 320 px.
- Every interactive element is reachable by `Tab` in DOM order, with a visible
  ring, and operable by `Enter`/`Space`.
- The visually hidden table lists all 10 runs with z values and zone labels.
- Zone information is conveyed by marker shape as well as colour.

**Tests.** No automated browser tests (no test runner in this static app, and
adding one is out of scope). Manual checklist recorded in
`apps/student-next/README.md` covering 360/390/430 px, keyboard-only completion
of one scenario, and one screen-reader pass over the reveal.

**Correct if:** at 360 × 640 in a device-emulated viewport, completing
`in-control-01` from P1 to P4 requires zero scrolls before lock, and
`document.querySelectorAll('[tabindex="-1"]:not([hidden])').length` is `0` while
`getComputedStyle(document.activeElement).outlineWidth` is not `0px` after
tabbing to any control.

---

### Slice 5 — Learn from canonical rule metadata

**Goal.** Replace the hardcoded `RULES` array with the generated reference and
make the capability distinction visible.

**Student behavior.** The student compares six rules as mini-patterns on one
screen, expands one for interpretation and action, and jumps to the matching
cards.

**Files.** `apps/student-next/src/learn.js`, `src/chart.js` (mini renderer),
`index.html`, `styles.css`.

**Domain changes.** None.

**UI changes.** Rule rows per the Learn spec, badges `Evaluable aquí` /
`Solo referencia`, divider text, `aria-expanded` disclosure,
`Repasar en tarjetas →` deep link with `?rule=`.

**Acceptance criteria.**
- `apps/student-next/src/*.js` contains no rule text, no severity string and no
  rule code list; all six rows come from `data/rules.json`.
- The three reference rules render full pattern/interpretation/action and never a
  triggered state.
- The words `no soportado`, `no disponible`, `no implementado` appear nowhere.

**Tests.** Covered by the export tests (Slice 1) plus the source guard in
"Correct if".

**Correct if:**
```
grep -nE "(1₂s|1₃s|2₂s|R₄s|4₁s|10x|Advertencia|Rechazo|no soportado|no disponible)" apps/student-next/src/*.js apps/student-next/app.js
```
finds nothing except occurrences inside the fixed rule-option labels of
`src/practice.js` (`1₂s`, `1₃s`, `2₂s` only), and `#rules` renders six rows with
three `Evaluable aquí` and three `Solo referencia` badges.

---

### Slice 6 — Cards: browse/session split and persisted position

**Goal.** Keep the good card session, add resumability and a quiet browse view.

**Student behavior.** The student closes the tab mid-deck and returns to the same
card; from Reglas they open cards filtered to one rule.

**Files.** `apps/student-next/src/cards.js`, `src/storage.js`, `src/markup.js`,
`index.html`, `styles.css`, `apps/student-next/test/markup.test.js`.

**Domain changes.** None.

**UI changes.** Move card code out of `app.js` into `src/cards.js`; card becomes a
real `<button>`; session persists under `wnext:cards:v1`; browse view with tag
chips and `?rule=` filter; `Mezclar` only in browse with a stored seed;
`No la supe` re-queues the card once at the end.

**Acceptance criteria.**
- Reload mid-session restores index, queue, and counters.
- `#cards?rule=2_2s` starts with only the cards listed in that rule's `card_ids`.
- The markup renderer handles exactly `[[kind:text]]`, `**bold**`, `*italic*`,
  `` `code` `` and escapes everything else.

**Tests.** `apps/student-next/test/markup.test.js`: one case per construct, one
unbalanced-marker case left as literal text, one HTML-injection case
(`<script>` renders escaped).

**Correct if:**
```
node --test apps/student-next/test/
```
exits 0, and after rating three cards and reloading, the progress label shows
`4 / 20`.

---

### Slice 7 — Build and deploy contract

**Goal.** Generate data in CI with stock `python3`, no pip install, no secrets.

**Student behavior.** The published site loads real data on first visit from a
clean checkout.

**Files.** `.github/workflows/student-pages.yml`, `apps/student-next/README.md`,
`.gitignore`.

**Domain changes.** None.

**UI changes.** None.

**Acceptance criteria.**
- Workflow steps, in exactly this order:
  1. `actions/checkout@v4`
  2. `actions/setup-python@v5` with `python-version: '3.11'`
  3. `node --check apps/student-next/app.js`
  4. `node --test apps/student-next/test/`
  5. `pip install pytest` (the only install in the workflow; the export script
     itself needs no third-party package)
  6. `python -m pytest tests/test_evidence.py tests/test_student_next_export.py -q`
  7. `python scripts/export_student_next_data.py --output-dir _site/data`
  8. copy `apps/student-next/index.html`, `styles.css`, `app.js` and the whole
     `src/` directory into `_site/`, then `touch _site/.nojekyll`
  9. verify `_site/data/cards.json`, `_site/data/rules.json` and
     `_site/data/practice.json` are non-empty
  10. `actions/upload-pages-artifact@v3` and the existing deploy job, both still
      skipped for `pull_request`
- The `python3 -m json.tool` deck check is removed: the export script validates
  the deck and fails loudly, so the separate check is redundant.
- The paths filter adds `content/practice_scenarios.json`,
  `content/rules_reference.json`, `qc_lab_simulator/evidence.py`,
  `scripts/export_student_next_data.py`.
- `apps/student-next/data/` is git-ignored and never committed.
- No secret, token or environment variable beyond the Pages defaults.

**Tests.** None beyond the workflow run itself.

**Correct if:** from a clean clone,
```
python scripts/export_student_next_data.py --output-dir apps/student-next/data
python -m http.server 8000 -d apps/student-next
```
serves a site where `#practice`, `#rules` and `#cards` all render real data with
no console error, and `git status --short` reports no untracked file under
`apps/student-next/data/`.

---

## Testing strategy

Each fact is tested in exactly one place.

| Layer | What is tested | Where |
| --- | --- | --- |
| Python domain | rule conditions and boundaries | existing `tests/test_rules.py` (unchanged) |
| Python domain | evidence agrees with `rules.py` for every fixture and every counterfactual value (defense-in-depth); `evidence_runs` semantics; side; verdict; governing rule | `tests/test_evidence.py` |
| Generated contract | bundle shape, per-point `zone`, derived `evaluation` flags, golden expected answers for the six fixtures, `card_ids` integrity, deck byte-identity, numpy-free import | `tests/test_student_next_export.py` |
| Frontend logic | answer grading, phase machine, counterfactual index mapping, markup rendering | `apps/student-next/test/*.test.js` via `node --test` (no new dependency) |
| Frontend rendering | not automated; guarded by `node --check`, the source `grep` guards in Slices 2 and 5, and the manual mobile/a11y checklist in `apps/student-next/README.md` | CI + manual |

Rule conditions are never re-tested in JavaScript, because JavaScript never
evaluates them. The `grep` guards are the tripwire that keeps that true.

## Accessibility requirements

- Semantic controls only: `<button>` for actions (including the flashcard),
  `<input type="range">` for the counterfactual, real headings `h1`→`h2`→`h3`, one
  `<main>`.
- Visible focus on every interactive element: 3 px `--brand` ring, 2 px offset.
  The existing `outline: none` on `.entry-card:focus-visible` is removed with the
  element itself.
- Touch targets ≥ 44 × 44 px for every control in Practice and Cards, including
  run-strip buttons and the counterfactual `−`/`+`.
- The chart is never the only carrier of information: marker shape encodes zone,
  evidence is ringed *and* named in text ("controles 7 y 8"), and every verdict
  line pairs an `aria-hidden` icon with a text word.
- Screen-reader path: `<svg aria-hidden="true">` plus a `.visually-hidden`
  `<table>` of all runs plus a phase-dependent `<p role="status">` summary. The
  status text must never contain reveal content before lock.
- Keyboard: full completion of a scenario and of a card session without a
  pointer. `Esc` returns Home. Arrow keys drive the counterfactual range.
- Contrast: keep the existing token palette, which meets AA for body text
  (`--muted #657086` on `--bg #f7f8fb`), and do not introduce lighter greys for
  text. Chart axis labels use `--muted` at ≥ 11 px.
- `prefers-reduced-motion`: keep the existing block; the card flip and any chart
  transition must be disabled by it.

## Deployment/build contract

- One production target: GitHub Pages via
  `.github/workflows/student-pages.yml`. No second host is configured or
  referenced for `student-next`. `vercel.json` remains for the legacy app and is
  not touched.
- Build inputs: the repository only. No secrets, no tokens, no network calls at
  build or run time.
- Runtime: static files. No backend, no API, no service worker requirement. The
  app must function with `file://`-like constraints aside (it needs `fetch` of
  relative JSON, so an HTTP server is required locally — documented in the
  README).
- Local commands, documented verbatim in `apps/student-next/README.md`:
  ```
  python scripts/export_student_next_data.py --output-dir apps/student-next/data
  python -m http.server 8000 -d apps/student-next
  ```
- `apps/student-next/data/` is generated and git-ignored. Never commit it.

## Explicit non-goals

Do not build, add, or prepare for any of the following. Their absence is a
feature, and adding them is a contract violation, not an improvement:

- User accounts, login, magic links, identity of any kind.
- Supabase, any database, any backend API, any cloud function, any server-side
  rendering.
- Cloud sync of progress. `localStorage` only.
- Analytics, telemetry, event tracking, error reporting services.
- Teacher dashboard, student dashboard, class management, rosters, per-student
  records.
- Gamification: points, XP, streaks, badges, achievements, leaderboards, timers.
- AI tutor, chatbot, generated explanations, LLM calls at runtime.
- A full laboratory simulator: multiple analytes, patient results, reagent lots,
  instrument models, calibration workflows, shift/QC scheduling.
- Authoring CMS or admin UI for scenarios or cards. Content is edited as JSON in
  `content/`.
- Plugin architecture, dependency injection, event bus, global state framework,
  component framework, design system, CSS framework, icon library.
- Any npm dependency, `package.json`, bundler, transpiler or CSS preprocessor in
  `apps/student-next`.
- Migration, refactor, or reuse of `apps/student-web`, including its Zod
  contracts, Recharts chart, localization adapter and Supabase code.
- Consumption of `content/lessons.json`, `content/scenarios.json`,
  `qc_lab_simulator/web_export.py` output, or anything under `outputs/`.
- Spaced repetition scheduling (SM-2, Leitner intervals, due dates). The single
  re-queue of a missed card is the entire mechanism.
- Random scenario generation in the frontend, and any client-side rule
  evaluation, including "just for the sliders".
- Computing, displaying, or implying evaluation of `R_4s`, `4_1s` or `10x`.
- Modifying `qc_lab_simulator/rules.py` or its tests.
- Adding a fourth top-level destination, a settings screen, an onboarding tour, a
  marketing hero, or a documentation portal inside the app.
- Multi-level control series or multi-analyte data structures.
- Internationalisation machinery. The app is Spanish-only, authored in Spanish.

## Decision log

**D1. Vanilla ES modules, no framework.**
Why: the app is three views and one state machine; the current static app already
ships with zero dependencies and CI copies three files.
Rejected: React/Vite (the legacy `apps/student-web` proves the cost: npm install,
build, Zod contracts, and a second place where rule text lives).
Evidence: `.github/workflows/student-pages.yml` has no npm step; `apps/student-next`
is 4 files.

**D2. Python `rules.py` stays the only scientific source of truth; no JS rule port.**
Why: two implementations diverge silently, and the Python one is the tested one.
Rejected: porting the three rules to JS with golden vectors — it still creates a
second implementation to keep in sync and invites a fourth rule to be added there
first.
Evidence: `apps/student-next/app.js` already contains `rule12s`/`rule13s`/`rule22s`
with inline thresholds, untested; `apps/student-web/.../triggerTooltip.ts` holds a
second copy of severities and explanations.

**D3. Build-time JSON generation, including a precomputed counterfactual table.**
Why: it is the only way to keep interactive point-editing while keeping zero rule
logic in the browser. One editable point × a 41-value grid × 6 scenarios is a
small file and fully deterministic.
Rejected: (a) live JS evaluation (violates D2); (b) dropping the counterfactual
(it is the highest-value interaction for classroom discussion and for boundary
intuition).
Evidence: `rules.py` imports only `typing`, so generation needs no numpy;
verified that the 41-value grid has zero float mismatches at `mean=100, sd=2`.

**D4. New `evidence.py` instead of changing `rules.py`.**
Why: the UI needs point indices, side and threshold; `rules.py` returns booleans
only, and changing its signatures would invalidate the audited tests.
Rejected: extending `rules.py` to return dataclasses (breaks
`metrics.py`/`web_export.py`/101 passing tests for no student-visible gain).
Evidence: `rules.py` signature `(...) -> bool`; `metrics.py::_RULES` and
`first_violation(rule_fn)` depend on that signature.

**D5. `rules.first_violation` is detectability, not "the offending point"; do not use it here.**
Why: `first_violation` re-evaluates prefixes, so for `2_2s` it returns the second
point of the pair; highlighting it alone teaches the wrong thing. `evidence_runs`
from `evidence.py` is the sole authority for which points to mark; when a single
earliest point is needed it is just `min(evidence_runs)`. No `first_trigger_run`
field is introduced, precisely so nothing in this pipeline can conflict with
`rules.first_violation` semantics.
Rejected: reusing the existing exported `rule_results.first_trigger_run` contract
for highlighting (what the legacy app does).
Evidence: `tests/test_rules.py::TestFirstViolation::test_2_2s_needs_two_runs`
expects `2` for a pair at runs 1–2; verified in audit that a pair at runs 2–3
returns `3`.

**D6. Curated 10-point fixtures, not the RNG scenarios.**
Why: teaching needs exact boundary and same-side cases, and 10 points is the most
that stays legible at 360 px.
Rejected: reusing `content/experiment_catalog.json` + `web_export.py` (30 RNG
points, and `drift`/`imprecision` are designed for `10x`/`R_4s`, which the engine
cannot evaluate).
Evidence: `SimConfig(n_runs=30)`; `content/scenarios.json` attributes drift to
`10x` and imprecision to `R-4s`, neither in `rules.py`.

**D7. Capability flag derived from the engine, never authored.**
Why: it makes it structurally impossible for content to claim the app evaluates a
rule it cannot.
Rejected: an authored `engine: true/false` field (the current `app.js` `RULES`
array does exactly that, and nothing prevents it from lying).
Evidence: `apps/student-next/app.js` `RULES[].engine` is hand-maintained.

**D8. Staged three-part answer (evidence → rule → action), one question per screen.**
Why: marking points first prevents label-matching; separating action from rule
teaches warning vs rejection, which is the distinction `1_2s` exists to make.
Rejected: a single "which rule?" quiz (memorisable from the option list) and a
single "accept/reject?" question (a coin flip that never touches the chart).
Evidence: `rules.py` documents `1_2s` as a warning rule and `1_3s`/`2_2s` as
rejection rules, so a three-way action question is grounded in the engine.

**D9. Run-strip buttons as the evidence control, not SVG point taps.**
Why: 44 px targets are impossible on a 320 px-wide chart with 10 points, and a
tap-only interaction is not keyboard accessible.
Rejected: clicking points on the chart (the plan the legacy discovery docs
proposed), and a plain numeric `<select>` (no visual link to the chart).
Evidence: at 360 px the content column is 324 px wide; 10 points give ~32 px of
horizontal room each.

**D10. Error-type attribution restricted to two cases and never graded.**
Why: with one control level and three rules, random vs systematic is
under-determined; `R_4s`, the discriminating rule, is unavailable.
Rejected: a fourth graded question "¿qué tipo de error?".
Evidence: no rule in `rules.py` examines two control levels; `content/scenarios.json`
already overstates this and states `R-4s` incorrectly.

**D11. Session position in `localStorage`, one namespace, no accounts.**
Why: resumability is the only persistence students need, and the current app
loses the deck position on reload.
Rejected: Supabase progress sync (present in the legacy app; large surface, no
learning value here).
Evidence: `state` in `app.js` is in-memory only.

**D12. Single deployment target, existing Pages workflow, one added Python step.**
Why: the workflow is already minimal and greenfield-only; only data generation is
missing.
Rejected: committing generated JSON (churn, and it can silently disagree with
`content/`), and a second host.
Evidence: workflow already copies the deck to `_site/data/cards.json`;
`apps/student-next/data/` is absent from the repository and from `.gitignore`.

## Gauntlet record

Changes the adversarial review forced, kept here so they are not undone:

- **C (memorisation trap).** The first draft asked "which rule triggered?" first.
  A student could match the option list to a remembered picture. Fixed by making
  evidence marking the first, mandatory step, and by grading it separately.
- **D/E (scientific honesty and boundaries).** The first draft had no exact
  boundary scenario and let the UI imply full multirule evaluation. Fixed by
  adding `boundary-exact-2s-01` (exactly `+2.0` SD, verified non-triggering), the
  boundary sentence in the counterfactual, the mandatory capability sentence on
  `1_2s`-only outcomes, and the derived `evaluation` flag.
- **D10 (error type).** The first draft graded random vs systematic error. With
  one control level and no `R_4s`, that is not answerable from the engine. Reduced
  to a compatibility statement in two justified cases.
- **B (classroom reality).** A group of three needs a shared object and a reason
  to argue. Added `#practice/<scenario-id>` permalinks with `Compartir`, and
  `Volver a ocultar` so a group can re-hide the answer and re-argue without
  losing their locked decision.
- **F/G (mobile and architecture).** The first draft kept the two-column
  chart+panel layout and SVG point tapping. At 360 px that forces scrolling
  between chart and controls and gives 32 px tap targets. Replaced by a single
  column, per-breakpoint `viewBox`, and the 44 px run strip; the counterfactual
  was reduced from two sliders to one point on a precomputed grid, which also
  removed the need for any JS evaluation.

## Final acceptance criteria

The work is complete when all of the following hold from a clean checkout:

1. `python -m pytest -q` passes, with at least the pre-existing 101 tests plus
   the new evidence and export tests.
2. `python scripts/export_student_next_data.py --output-dir apps/student-next/data`
   exits 0 and writes `cards.json`, `rules.json`, `practice.json`.
3. `node --check apps/student-next/app.js` and `node --test apps/student-next/test/`
   exit 0.
4. `grep -rnE "(rule12s|rule13s|rule22s|Math\.abs\([^)]*\)\s*[<>]|>\s*2\s*\*|>\s*3\s*\*)" apps/student-next/app.js apps/student-next/src/` finds nothing.
5. `#practice/reject-2-2s-01`: before lock the DOM contains no verdict, rule name
   or evidence run; after lock exactly runs 7 and 8 are ringed, the `+2 DE` line
   is emphasised, the bracket is labelled `2 consecutivos · mismo lado`, and the
   explanation names controls 7 and 8.
6. `#practice/boundary-exact-2s-01`: the correct action is `Aceptar`, no rule is
   reported, and moving control 8 to `+2.2` in the counterfactual makes `1₂s`
   apply and the decision become `Revisar`.
7. `#practice/distractor-opposite-01`: `2₂s` is reported as not applying, and the
   explanation states the same-side requirement.
8. `#rules` shows six rules, three badged `Evaluable aquí`, three badged
   `Solo referencia`, each with a mini-pattern and a link into the canonical deck.
9. `#cards`: a session resumes after reload at the same card; the canonical deck
   is the only card source; card ids are unchanged.
10. At 360 × 640, chart and active controls are visible without scrolling in every
    pre-reveal phase; one scenario can be completed with the keyboard only.
11. The site builds and deploys through `.github/workflows/student-pages.yml` with
    no secret and no `apps/student-web` step.
12. `apps/student-web/` and `qc_lab_simulator/rules.py` are unmodified by the
    entire change set.
