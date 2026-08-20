// test/practice.test.js
import test from "node:test";
import assert from "node:assert/strict";
import {
  gradeEvidence,
  gradeRule,
  gradeAction,
  PracticeSession,
  counterfactualAt,
  gridIndexForZ,
  boundarySentenceForZ,
} from "../src/practice.js";

// --- gradeEvidence ---------------------------------------------------------

test("gradeEvidence: exact set match is correcta", () => {
  assert.equal(gradeEvidence([7, 8], [7, 8]), "correcta");
});

test("gradeEvidence: empty expected + none selected is correcta", () => {
  assert.equal(gradeEvidence([], []), "correcta");
});

test("gradeEvidence: strict subset is parcial", () => {
  assert.equal(gradeEvidence([7], [7, 8]), "parcial");
});

test("gradeEvidence: strict superset is parcial", () => {
  assert.equal(gradeEvidence([6, 7, 8], [7, 8]), "parcial");
});

test("gradeEvidence: none selected when evidence exists is incorrecta", () => {
  assert.equal(gradeEvidence([], [7, 8]), "incorrecta");
});

test("gradeEvidence: selection made when no evidence exists is incorrecta", () => {
  assert.equal(gradeEvidence([3], []), "incorrecta");
});

test("gradeEvidence: disjoint sets are incorrecta", () => {
  assert.equal(gradeEvidence([1, 2], [7, 8]), "incorrecta");
});

// --- gradeRule ---------------------------------------------------------

test("gradeRule: exact match is correcta", () => {
  assert.equal(gradeRule("2_2s", "2_2s", ["1_2s", "2_2s"]), "correcta");
});

test("gradeRule: none matches null expected", () => {
  assert.equal(gradeRule("none", null, []), "correcta");
});

test("gradeRule: 1_2s chosen when governing is 1_3s and 1_2s also triggered is incompleta", () => {
  assert.equal(gradeRule("1_2s", "1_3s", ["1_2s", "1_3s"]), "incompleta");
});

test("gradeRule: 1_2s chosen when governing is 2_2s and 1_2s also triggered is incompleta", () => {
  assert.equal(gradeRule("1_2s", "2_2s", ["1_2s", "2_2s"]), "incompleta");
});

test("gradeRule: a triggered-but-not-governing rule is incompleta", () => {
  assert.equal(gradeRule("2_2s", "1_3s", ["1_2s", "1_3s", "2_2s"]), "incompleta");
});

test("gradeRule: a non-triggered rule choice is incorrecta", () => {
  assert.equal(gradeRule("2_2s", "1_2s", ["1_2s"]), "incorrecta");
});

test("gradeRule: none chosen when a rule triggered is incorrecta", () => {
  assert.equal(gradeRule("none", "1_2s", ["1_2s"]), "incorrecta");
});

// --- gradeAction ---------------------------------------------------------

test("gradeAction: matching action is correcta", () => {
  assert.equal(gradeAction("reject", "reject"), "correcta");
});

test("gradeAction: mismatched action is incorrecta", () => {
  assert.equal(gradeAction("accept", "reject"), "incorrecta");
});

// --- PracticeSession phase machine ---------------------------------------

function stubScenario() {
  return {
    id: "stub",
    expected: { action: "reject", rule: "2_2s", evidence_runs: [7, 8] },
    evaluation: {
      rules: [
        { rule: "1_2s", triggered: true, evidence_runs: [7, 8] },
        { rule: "1_3s", triggered: false, evidence_runs: [] },
        { rule: "2_2s", triggered: true, evidence_runs: [7, 8] },
      ],
    },
    counterfactuals: {
      run: 8,
      z_values: Array.from({ length: 41 }, (_, i) => Math.round((-4 + i * 0.2) * 10) / 10),
      results: Array.from({ length: 41 }, (_, i) => ({ z: -4 + i * 0.2, consequence: `c${i}` })),
    },
  };
}

test("PracticeSession: cannot advance from evidence phase without an answer", () => {
  const session = new PracticeSession(stubScenario());
  assert.equal(session.advance(), false);
  assert.equal(session.phase, "evidence");
});

test("PracticeSession: toggling a run and advancing moves to rule phase", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.toggleRun(8);
  assert.equal(session.advance(), true);
  assert.equal(session.phase, "rule");
});

test("PracticeSession: selecting 'ninguno' satisfies the evidence phase", () => {
  const session = new PracticeSession(stubScenario());
  session.setNoneSelected(true);
  assert.equal(session.advance(), true);
});

test("PracticeSession: cannot advance from rule phase without a choice", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.advance();
  assert.equal(session.advance(), false);
  assert.equal(session.phase, "rule");
});

test("PracticeSession: full flow locks after action confirm and reaches reveal", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.toggleRun(8);
  session.advance();
  session.chooseRule("2_2s");
  session.advance();
  session.chooseAction("reject");
  session.advance();
  assert.equal(session.phase, "reveal");
  assert.equal(session.locked, true);
});

test("PracticeSession: locked session refuses further edits", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.toggleRun(8);
  session.advance();
  session.chooseRule("2_2s");
  session.advance();
  session.chooseAction("reject");
  session.advance();
  session.chooseAction("accept"); // should be a no-op once locked
  assert.equal(session.answers.action, "reject");
  session.toggleRun(1); // should be a no-op once locked
  assert.deepEqual(session.answers.evidenceRuns, [7, 8]);
});

test("PracticeSession: grade reflects correct evidence/rule/action", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.toggleRun(8);
  session.advance();
  session.chooseRule("2_2s");
  session.advance();
  session.chooseAction("reject");
  session.advance();
  const grade = session.grade();
  assert.equal(grade.evidence, "correcta");
  assert.equal(grade.rule, "correcta");
  assert.equal(grade.action, "correcta");
});

test("PracticeSession: hideReveal/showReveal do not change locked answers", () => {
  const session = new PracticeSession(stubScenario());
  session.toggleRun(7);
  session.toggleRun(8);
  session.advance();
  session.chooseRule("2_2s");
  session.advance();
  session.chooseAction("reject");
  session.advance();
  session.hideReveal();
  assert.equal(session.revealHidden, true);
  assert.deepEqual(session.answers.evidenceRuns, [7, 8]);
  session.showReveal();
  assert.equal(session.revealHidden, false);
  assert.equal(session.answers.rule, "2_2s");
});

// --- counterfactual lookup ---------------------------------------------

test("counterfactualAt: returns the record at the given index", () => {
  const scenario = stubScenario();
  const { index, result } = counterfactualAt(scenario, 10);
  assert.equal(index, 10);
  assert.equal(result.consequence, "c10");
});

test("counterfactualAt: clamps below zero", () => {
  const scenario = stubScenario();
  const { index } = counterfactualAt(scenario, -5);
  assert.equal(index, 0);
});

test("counterfactualAt: clamps above max index", () => {
  const scenario = stubScenario();
  const { index } = counterfactualAt(scenario, 999);
  assert.equal(index, 40);
});

test("gridIndexForZ: maps a z value to the nearest grid index", () => {
  const scenario = stubScenario();
  const idx = gridIndexForZ(scenario, 2.6);
  assert.equal(scenario.counterfactuals.z_values[idx], 2.6);
});

test("boundarySentenceForZ: returns the sentence at exactly +2.0", () => {
  assert.match(boundarySentenceForZ(2.0), /límite/);
});

test("boundarySentenceForZ: returns the sentence at exactly -3.0", () => {
  assert.match(boundarySentenceForZ(-3.0), /límite/);
});

test("boundarySentenceForZ: returns null away from boundaries", () => {
  assert.equal(boundarySentenceForZ(1.4), null);
});
