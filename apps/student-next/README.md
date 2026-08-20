# Student Next — greenfield Westgard experience

This app is intentionally independent from `apps/student-web`.

## Product goal

Help a student recognize a QC pattern, connect it to a Westgard rule, and understand the immediate decision without turning the site into a dashboard or documentation portal.

## Three entry points

1. **Rules** — compact visual reference: pattern → meaning → action.
2. **Practice** — Levey–Jennings sandbox with immediate rule feedback.
3. **Cards** — active recall session using the canonical deck in `content/flashcards/`.

## Guardrails

- Mobile card review behaves like a focused study session: card, progress, rating, home.
- The practice engine only evaluates rules currently implemented in `qc_lab_simulator/rules.py`: `1_2s`, `1_3s`, and `2_2s`.
- `R_4s`, `4_1s`, and `10x` remain reference/study content until the canonical rule engine supports them.
- No auth, database, analytics, framework, or backend is required for the student experience.
- Interactions must explain state changes instead of decorating the page.
- Generated/exported content remains separate from presentation code.

## Local preview

The deployed workflow copies the canonical deck to `data/cards.json`. For a local preview, serve this directory over HTTP and provide the same file path, for example:

```bash
mkdir -p apps/student-next/data
cp content/flashcards/westgard_qc_basics.deck.json apps/student-next/data/cards.json
python -m http.server 8000 -d apps/student-next
```

Then open `http://localhost:8000`.
