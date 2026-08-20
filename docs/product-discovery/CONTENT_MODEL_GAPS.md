# Content Model Gaps

What the Decision Trainer needs from the data that the current content model does
not provide. Ordered by severity.

## 1. ⚠ Rule mismatch: content teaches rules the engine cannot evaluate

**Headline gap.** `content/lessons.json` and `content/scenarios.json` explicitly
tell students that:

- drift is caught by the **`10x`** rule (10 consecutive points on one side), and
- imprecision is caught by the **`R-4s`** rule.

But `qc_lab_simulator/rules.py` implements **only** `1_2s`, `1_3s`, `2_2s`. So the
engine can never show `10x` or `R-4s` firing.

**Consequence for the trainer:** the rule picker must offer **only the three
implemented rules**, and drift/imprecision scenarios must be framed around what
those three rules actually detect — not around rules the app cannot demonstrate.

**Options (pick one, do not silently ship the mismatch):**
- **P1, preferred:** extend the core with `10x` and `R-4s` (pure functions
  mirroring the existing style, with tests), then let the trainer use them.
- **Now:** correct the content copy so it only claims what the three rules do.

## 2. No structured "correct decision + rationale + misconception" per scenario

The engine knows the truth (`rule_results.first_trigger_run`, `summary`,
`false_alarm`), and content has free-text `common_mistake`, but there is no
first-class, machine-readable field pairing:

```jsonc
"decision_key": {
  "correct_decision": "reject",          // "accept" | "reject"
  "governing_rule": "2_2s",              // one of the three implemented rules, or null when accept
  "first_break_run": 12,                 // int | null
  "rationale": "Dos puntos seguidos sobre +2SD del mismo lado…",
  "misconceptions": [
    { "when": "rejected_normal_on_single_2s",
      "note": "Un solo valor sobre 2SD no basta para rechazar…" }
  ]
}
```

- `correct_decision`, `governing_rule`, `first_break_run` can be **derived** from
  the existing payload at export time (no authoring burden).
- `rationale` and `misconceptions` are new authored fields — the trainer's
  reveal/explain steps depend on them for misconception-based feedback.

## 3. Language split leaks untranslated content

Source content is **English**; the UI is **Spanish**, translated at runtime by a
`scenario_type`-keyed adapter (`shared/config/localization.ts`). Any new scenario
key or free-text field bypasses the adapter and surfaces English.

**Recommendation:** author student-facing content **in Spanish at source** (the
class language), and treat the translation adapter as legacy for the four
built-in keys only. New `rationale`/`misconception` copy must be authored in
Spanish.

## 4. Scenario identity vs learning intent

The catalog keys scenarios by engine mechanics (`scenario_key`: normal/bias/
drift/imprecision) and raw parameters (`shift_sd`, `start_run`). Students should
never see these. The content model needs a plain-language **learning label**
("cambio brusco", "deriva lenta") separate from the engine key, so the UI stops
printing internals (`Semilla`, `shift_sd`) as it does today.

## 5. No notion of a "set" (ordered sequence for transfer)

The trainer teaches by varying one thing across an ordered sequence. There is no
`set` concept today (only experiments → scenarios). A minimal addition:

```jsonc
"sets": [
  { "id": "shift_intro",
    "title": "Reconocer cambios bruscos",
    "scenario_refs": ["baseline_glucose/normal_default",
                      "baseline_glucose/bias_early", ...] }
]
```

Sets can reference the **existing eight scenarios** — no new simulation content is
required for the first release.

## What does NOT need to change

- The simulation engine, its determinism, or the export contract shape (fields
  are added, not altered).
- The strict Zod contracts — extend them additively.
- The eight already-exported scenarios remain the entire P0 dataset.
