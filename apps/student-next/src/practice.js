// src/practice.js
// Practice phase machine + grading. This module contains no Westgard rule
// predicates: all "which rule fired" facts come from the pre-generated
// practice.json bundle (evidence_runs, evaluation, expected, counterfactuals).
// Grading here is presentation-state *comparison*, never rule evaluation.

import { renderChart } from "./chart.js";
import { readJSON, writeJSON, PRACTICE_KEY } from "./storage.js";

export const PHASES = ["evidence", "rule", "action", "reveal", "counterfactual"];

const RULE_OPTIONS = ["1_2s", "1_3s", "2_2s", "none"];
const RULE_DISPLAY = { "1_2s": "1₂s", "1_3s": "1₃s", "2_2s": "2₂s", none: "Ninguna regla se activa" };
const ACTION_OPTIONS = ["accept", "review", "reject"];
const ACTION_LABEL = { accept: "Aceptar", review: "Revisar", reject: "Rechazar" };

/**
 * Compare the student's evidence selection against expected.evidence_runs.
 * Returns "correcta" | "parcial" | "incorrecta".
 */
export function gradeEvidence(selectedRuns, expectedRuns) {
  const selected = new Set(selectedRuns);
  const expected = new Set(expectedRuns);

  const selectedIsNone = selected.size === 0;
  const expectedIsEmpty = expected.size === 0;

  if (expectedIsEmpty) {
    return selectedIsNone ? "correcta" : "incorrecta";
  }
  if (selectedIsNone) {
    return "incorrecta";
  }
  if (setsEqual(selected, expected)) return "correcta";

  const isSubset = isStrictSubset(selected, expected);
  const isSuperset = isStrictSubset(expected, selected);
  if (isSubset || isSuperset) return "parcial";

  return "incorrecta";
}

function setsEqual(a, b) {
  if (a.size !== b.size) return false;
  for (const v of a) if (!b.has(v)) return false;
  return true;
}

function isStrictSubset(smaller, larger) {
  if (smaller.size === 0 || smaller.size >= larger.size) return false;
  for (const v of smaller) if (!larger.has(v)) return false;
  return true;
}

/**
 * Compare the student's rule choice against expected.rule and the set of
 * rules actually triggered (from evaluation.rules), per the grading table.
 * Returns "correcta" | "incompleta" | "incorrecta".
 */
export function gradeRule(choice, expectedRule, triggeredRuleIds) {
  const expected = expectedRule === null ? "none" : expectedRule;
  if (choice === expected) return "correcta";

  const triggered = new Set(triggeredRuleIds);
  if (choice === "1_2s" && (expected === "1_3s" || expected === "2_2s") && triggered.has("1_2s")) {
    return "incompleta";
  }
  if (choice !== "none" && triggered.has(choice) && choice !== expected) {
    return "incompleta";
  }
  return "incorrecta";
}

/**
 * Action grading: correct iff it equals expected.action exactly.
 */
export function gradeAction(choice, expectedAction) {
  return choice === expectedAction ? "correcta" : "incorrecta";
}

/**
 * A minimal phase machine. `advance()` refuses to move forward without an
 * answer for the current phase; once `locked` is true (after action is
 * confirmed) evidence/rule/action can no longer be edited for this scenario.
 */
export class PracticeSession {
  constructor(scenario) {
    this.scenario = scenario;
    this.phase = "evidence";
    this.locked = false;
    this.answers = { evidenceRuns: [], noneSelected: false, rule: null, action: null };
    this.revealHidden = false;
    this.counterfactualIndex = null;
  }

  hasAnswerForCurrentPhase() {
    if (this.phase === "evidence") {
      return this.answers.noneSelected || this.answers.evidenceRuns.length > 0;
    }
    if (this.phase === "rule") {
      return this.answers.rule !== null;
    }
    if (this.phase === "action") {
      return this.answers.action !== null;
    }
    return true;
  }

  toggleRun(run) {
    if (this.locked) return;
    if (this.answers.noneSelected) return;
    const idx = this.answers.evidenceRuns.indexOf(run);
    if (idx === -1) this.answers.evidenceRuns.push(run);
    else this.answers.evidenceRuns.splice(idx, 1);
  }

  setNoneSelected(value) {
    if (this.locked) return;
    this.answers.noneSelected = value;
    if (value) this.answers.evidenceRuns = [];
  }

  chooseRule(rule) {
    if (this.locked) return;
    this.answers.rule = rule;
  }

  chooseAction(action) {
    if (this.locked) return;
    this.answers.action = action;
  }

  advance() {
    if (!this.hasAnswerForCurrentPhase()) return false;
    if (this.phase === "evidence") {
      this.phase = "rule";
      return true;
    }
    if (this.phase === "rule") {
      this.phase = "action";
      return true;
    }
    if (this.phase === "action") {
      this.lock();
      this.phase = "reveal";
      return true;
    }
    if (this.phase === "reveal") {
      this.phase = "counterfactual";
      return true;
    }
    return false;
  }

  lock() {
    this.locked = true;
  }

  hideReveal() {
    // Re-hides the reveal block without changing locked answers.
    this.revealHidden = true;
  }

  showReveal() {
    this.revealHidden = false;
  }

  grade() {
    const expected = this.scenario.expected;
    const triggeredRuleIds = this.scenario.evaluation.rules
      .filter((r) => r.triggered)
      .map((r) => r.rule);

    const evidenceJudgement = gradeEvidence(this.answers.evidenceRuns, expected.evidence_runs);
    const ruleJudgement = gradeRule(this.answers.rule, expected.rule, triggeredRuleIds);
    const actionJudgement = gradeAction(this.answers.action, expected.action);

    return { evidence: evidenceJudgement, rule: ruleJudgement, action: actionJudgement };
  }
}

export function ruleOptions() {
  return RULE_OPTIONS.map((id) => ({ id, label: RULE_DISPLAY[id] }));
}

export function actionOptions() {
  return ACTION_OPTIONS.map((id) => ({ id, label: ACTION_LABEL[id] }));
}

export function ruleDisplay(ruleId) {
  return RULE_DISPLAY[ruleId === null ? "none" : ruleId];
}

export function actionLabel(actionId) {
  return ACTION_LABEL[actionId];
}

/**
 * Look up a counterfactual result by grid index. Performs array lookup
 * only, no threshold arithmetic. Clamps to [0, length-1].
 */
export function counterfactualAt(scenario, index) {
  const results = scenario.counterfactuals.results;
  const clamped = Math.max(0, Math.min(results.length - 1, index));
  return { index: clamped, result: results[clamped] };
}

export function gridIndexForZ(scenario, z) {
  const values = scenario.counterfactuals.z_values;
  let closest = 0;
  let bestDiff = Infinity;
  for (let i = 0; i < values.length; i += 1) {
    const diff = Math.abs(values[i] - z);
    if (diff < bestDiff) {
      bestDiff = diff;
      closest = i;
    }
  }
  return closest;
}

export function boundarySentenceForZ(z) {
  // The range input reads the exporter’s discrete grid values exactly. This
  // is presentation copy for an explicit boundary position, not a predicate
  // used to evaluate any rule (evaluation remains in Python at build time).
  if (![2.0, -2.0, 3.0, -3.0].includes(z)) return null;
  return "Exactamente en el límite: la regla exige superarlo, así que no se cumple.";
}

// --- Progress persistence -------------------------------------------------

export function loadProgress() {
  return readJSON(PRACTICE_KEY, { completed: {}, currentScenarioId: null });
}

export function saveProgress(progress) {
  writeJSON(PRACTICE_KEY, progress);
}

export function markScenarioComplete(progress, scenarioId, judgement) {
  progress.completed[scenarioId] = judgement;
  return progress;
}

export function firstUnfinishedScenarioId(scenarios, progress) {
  for (const scenario of scenarios) {
    if (!progress.completed[scenario.id]) return scenario.id;
  }
  return scenarios[0] ? scenarios[0].id : null;
}

export { renderChart };
