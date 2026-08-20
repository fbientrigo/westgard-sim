# Open Decisions for the Teacher (Bea)

Decisions only Bea (or the product owner) can make. Each has a recommended
default so implementation is not blocked.

## 1. The rule mismatch — fix content or extend the engine?

The content currently tells students that the `10x` rule catches drift and the
`R-4s` rule catches imprecision, but the engine only evaluates `1_2s`, `1_3s`,
`2_2s`.
- **Option A (now):** reword content so it only claims what the three rules do.
- **Option B (P1):** add `10x` and `R-4s` to the engine, then teach them for real.
- **Recommended default:** A for the first release, B soon after. The trainer must
  not ask students to select a rule the app cannot demonstrate.

## 2. Which rules should the first release actually teach?

Given (1), should the first decision sets focus on **bias** (cleanly caught by
`1_3s`/`2_2s`) and defer drift/imprecision until the engine can show the rules
that truly detect them?
- **Recommended default:** yes — lead with bias and false-alarm discrimination
  (accept a normal run despite a lone 2s point). These are honestly teachable
  with the three implemented rules today.

## 3. Language of authored content

Student-facing content is currently English translated to Spanish at runtime.
- **Recommended default:** author all new student-facing copy (`rationale`,
  `misconceptions`, labels) **in Spanish at source**. Confirm this is the class
  language.

## 4. Single production site

Two permanent sites (GitHub Pages + Vercel) are live. The constraint is to not
maintain multiple permanent production sites.
- **Question for Bea:** which single URL will you give students?
- **Recommended default:** keep **GitHub Pages** as the canonical student URL
  (simplest, already wired, no serverless functions needed); demote Vercel to an
  optional preview or retire it. Confirm before the developer changes anything.

## 5. Misconception feedback — how specific?

The reveal can give a generic rationale or a note targeting the student's exact
mistake (e.g. "you rejected a normal run on a single 2s excursion").
- **Question for Bea:** which student mistakes do you see most often in class?
- **Recommended default:** start with two misconceptions per scenario type;
  Bea's real classroom observations should drive which ones are authored first.

## 6. Class use pattern

How will Bea run this in a real session?
- **Options:** (a) individual warm-up/exit-ticket on phones; (b) projected,
  whole-class predict-then-discuss; (c) both.
- **Recommended default:** design copy and pacing for (a) first (works with zero
  infrastructure), knowing (b) is possible manually today and becomes first-class
  with Direction C later.

## 7. Progress and identity

The trainer is anonymous/local for P0. Does Bea need any per-student record
(e.g. to see who practiced)?
- **Recommended default:** no for the first release — keep it anonymous. Revisit
  only if Bea explicitly needs accountability, and even then prefer the
  classroom-session model (Direction C) over mandatory accounts.
