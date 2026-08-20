// app.js — bootstrap + routing only. Rendering logic lives in src/*.js.
// This file must never contain Westgard rule predicates (see contract
// Section 5/28): no ±2/±3 SD comparisons, no same-side/consecutive checks.

import { renderChart } from "./src/chart.js";
import {
  PracticeSession,
  ruleOptions,
  actionOptions,
  ruleDisplay,
  actionLabel,
  counterfactualAt,
  gridIndexForZ,
  boundarySentenceForZ,
  loadProgress,
  saveProgress,
  markScenarioComplete,
  firstUnfinishedScenarioId,
} from "./src/practice.js";
import { renderLearn } from "./src/learn.js";
import { initCards, onCardsRouteEnter } from "./src/cards.js";

const ROUTES = new Set(["home", "rules", "practice", "cards"]);

const panels = [...document.querySelectorAll("[data-view-panel]")];
const shareButton = document.querySelector("#share-button");
const sessionProgressBar = document.querySelector("#session-progress-bar");
const sessionProgressLabel = document.querySelector("#session-progress-label");

const dataCache = {};
let practiceData = null;
let rulesData = null;
let session = null;

async function fetchJSON(path) {
  if (dataCache[path]) return dataCache[path];
  const response = await fetch(path);
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${path}`);
  const payload = await response.json();
  dataCache[path] = payload;
  return payload;
}

function currentScenarioIdFromHash() {
  const hash = window.location.hash.replace(/^#/, "");
  const parts = hash.split("/");
  if (parts[0] === "practice" && parts[1]) return parts[1];
  return null;
}

function routeFromHash() {
  const hash = window.location.hash.replace(/^#/, "") || "home";
  const route = hash.split("/")[0].split("?")[0];
  return ROUTES.has(route) ? route : "home";
}

function showRoute(route, { updateHash = true } = {}) {
  const safeRoute = ROUTES.has(route) ? route : "home";
  document.body.dataset.view = safeRoute;
  panels.forEach((panel) => {
    panel.hidden = panel.dataset.viewPanel !== safeRoute;
  });
  shareButton.hidden = safeRoute !== "practice";

  if (safeRoute === "cards") onCardsRouteEnter();
  if (safeRoute === "practice") enterPractice();
  if (safeRoute === "rules") renderRulesView();

  if (updateHash && !window.location.hash.startsWith(`#${safeRoute}`)) {
    window.location.hash = safeRoute;
  }
  window.scrollTo({ top: 0, behavior: "auto" });
}

document.addEventListener("click", (event) => {
  const routeTarget = event.target.closest("[data-route]");
  if (routeTarget) {
    event.preventDefault();
    showRoute(routeTarget.dataset.route);
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    showRoute("home");
  }
});

window.addEventListener("hashchange", () => {
  const route = routeFromHash();
  showRoute(route, { updateHash: false });
});

window.addEventListener("resize", () => {
  if (document.body.dataset.view === "practice" && session && session.phase !== "summary") {
    renderPractice();
  }
});

// --- Practice --------------------------------------------------------------

async function enterPractice() {
  if (!practiceData) {
    try {
      practiceData = await fetchJSON("./data/practice.json");
    } catch (error) {
      const chartEl = document.querySelector("#practice-chart");
      chartEl.textContent = "No fue posible cargar los escenarios de práctica.";
      console.error(error);
      return;
    }
  }

  const scenarios = practiceData.scenarios;
  let scenarioId = currentScenarioIdFromHash();
  if (!scenarioId || !scenarios.some((s) => s.id === scenarioId)) {
    const progress = loadProgress();
    scenarioId = firstUnfinishedScenarioId(scenarios, progress);
    window.location.hash = `practice/${scenarioId}`;
  }

  const scenario = scenarios.find((s) => s.id === scenarioId);
  session = new PracticeSession(scenario);
  renderPractice();
}

function scenarioIndex(scenarioId) {
  return practiceData.scenarios.findIndex((s) => s.id === scenarioId);
}

function updateSessionBar() {
  const total = practiceData.scenarios.length;
  const idx = scenarioIndex(session.scenario.id);
  sessionProgressLabel.textContent = `Escenario ${idx + 1} / ${total}`;
  sessionProgressBar.style.width = `${((idx + 1) / total) * 100}%`;
}

function currentWidthPx() {
  return window.innerWidth || 900;
}

function renderPractice() {
  if (session.phase === "summary") {
    renderSetSummary();
    return;
  }

  updateSessionBar();
  const promptEl = document.querySelector("#practice-prompt");
  const controlsEl = document.querySelector("#phase-controls");
  const revealEl = document.querySelector("#reveal-block");
  const chartEl = document.querySelector("#practice-chart");
  const statusEl = document.querySelector("#practice-status");
  const runStripEl = document.querySelector("#run-strip");

  const scenario = session.scenario;
  const phase = session.phase;
  const showReveal = (phase === "reveal" || phase === "counterfactual") && !session.revealHidden;

  let highlight = {};
  if (showReveal) {
    const governing = scenario.expected.rule;
    if (governing) {
      const governingEntry = scenario.evaluation.rules.find((r) => r.rule === governing);
      highlight = {
        evidenceRuns: governingEntry.evidence_runs,
        selectedRuns: session.answers.evidenceRuns,
        governingRuleDisplay: ruleDisplay(governing),
        locked: true,
        triggeredRules: scenario.evaluation.rules
          .filter((entry) => entry.triggered)
          .map((entry) => ({ display: ruleDisplay(entry.rule), evidenceRuns: entry.evidence_runs })),
      };
      if (governing === "2_2s") {
        highlight.bracket = {
          runs: governingEntry.evidence_runs,
          label: "2 consecutivos · mismo lado",
        };
      }
    } else {
      highlight = { selectedRuns: session.answers.evidenceRuns, locked: true, triggeredRules: [] };
    }
  } else {
    highlight = { selectedRuns: [] };
  }

  // In counterfactual phase, use the selected counterfactual record for
  // chart + evaluation + text, all from the same precomputed record.
  let activeScenarioForChart = scenario;
  if (phase === "counterfactual" && session.counterfactualIndex !== null) {
    const { result } = counterfactualAt(scenario, session.counterfactualIndex);
    const points = scenario.points.map((p) =>
      p.run === scenario.editable_run
        ? { ...p, z: result.z, value: scenario.mean + result.z * scenario.sd, zone: zoneForCounterfactualPoint(result, scenario) }
        : p
    );
    activeScenarioForChart = { ...scenario, points };
    if (result.evaluation.governing_rule) {
      const g = result.evaluation.rules.find((r) => r.rule === result.evaluation.governing_rule);
      highlight = {
        evidenceRuns: g.evidence_runs,
        selectedRuns: session.answers.evidenceRuns,
        governingRuleDisplay: ruleDisplay(result.evaluation.governing_rule),
        locked: true,
        triggeredRules: result.evaluation.rules
          .filter((entry) => entry.triggered)
          .map((entry) => ({ display: ruleDisplay(entry.rule), evidenceRuns: entry.evidence_runs })),
      };
      if (result.evaluation.governing_rule === "2_2s") {
        highlight.bracket = { runs: g.evidence_runs, label: "2 consecutivos · mismo lado" };
      }
    } else {
      highlight = { selectedRuns: session.answers.evidenceRuns, locked: true, triggeredRules: [] };
    }
  }

  const { svg, table, status } = renderChart(activeScenarioForChart, highlight, currentWidthPx());
  chartEl.innerHTML = svg + table;
  statusEl.textContent = phase === "evidence" || phase === "rule" || phase === "action" ? status : status;

  renderRunStrip(runStripEl, scenario, phase);
  renderPhaseControls(controlsEl, promptEl);
  renderRevealBlock(revealEl, showReveal);
}

function zoneForCounterfactualPoint(result, scenario) {
  // Zone comes from the precomputed evaluation's own point data when the
  // editable run participates in evidence, otherwise infer within_2sd
  // fallback is impossible here because the exporter does not ship a
  // per-counterfactual zone; instead classify purely from which rule
  // entries list the editable run, never from a numeric comparison.
  const run = scenario.editable_run;
  const rulesTriggered = result.evaluation.rules;
  const in13s = rulesTriggered.find((r) => r.rule === "1_3s").evidence_runs.includes(run);
  const in12s = rulesTriggered.find((r) => r.rule === "1_2s").evidence_runs.includes(run);
  if (in13s) return "beyond_3sd";
  if (in12s) return "beyond_2sd";
  return "within_2sd";
}

function renderRunStrip(container, scenario, phase) {
  if (phase !== "evidence") {
    container.innerHTML = "";
    container.hidden = true;
    return;
  }
  container.hidden = false;
  container.innerHTML = scenario.points
    .map((p) => {
      const pressed = session.answers.evidenceRuns.includes(p.run);
      return `<button type="button" class="run-button" data-run="${p.run}" aria-pressed="${pressed}">${p.run}</button>`;
    })
    .join("");

  container.querySelectorAll("[data-run]").forEach((button) => {
    button.addEventListener("click", () => {
      session.toggleRun(Number(button.dataset.run));
      renderPractice();
    });
  });
}

function renderPhaseControls(container, promptEl) {
  const phase = session.phase;
  const scenario = session.scenario;

  if (phase === "evidence") {
    promptEl.textContent = "Marca los controles que te parecen problemáticos.";
    const noneOn = session.answers.noneSelected;
    const canContinue = session.hasAnswerForCurrentPhase();
    container.innerHTML = `
      <button type="button" class="toggle-button" id="none-toggle" aria-pressed="${noneOn}">Ninguno: la serie está en control</button>
      <button type="button" class="confirm-button" id="confirm-button" ${canContinue ? "" : "disabled"}>Continuar</button>
    `;
    container.querySelector("#none-toggle").addEventListener("click", () => {
      session.setNoneSelected(!session.answers.noneSelected);
      renderPractice();
    });
    container.querySelector("#confirm-button").addEventListener("click", () => {
      if (session.advance()) renderPractice();
    });
    return;
  }

  if (phase === "rule") {
    promptEl.textContent = "¿Qué regla respalda esa evidencia?";
    const canContinue = session.hasAnswerForCurrentPhase();
    container.innerHTML = `
      <div class="option-row" role="group" aria-label="Opciones de regla">
        ${ruleOptions()
          .map(
            (opt) =>
              `<button type="button" class="option-button" data-rule="${opt.id}" aria-pressed="${session.answers.rule === opt.id}">${opt.label}</button>`
          )
          .join("")}
      </div>
      <p class="hint-text">Solo estas tres reglas se evalúan aquí.</p>
      <button type="button" class="confirm-button" id="confirm-button" ${canContinue ? "" : "disabled"}>Continuar</button>
    `;
    container.querySelectorAll("[data-rule]").forEach((button) => {
      button.addEventListener("click", () => {
        session.chooseRule(button.dataset.rule);
        renderPractice();
      });
    });
    container.querySelector("#confirm-button").addEventListener("click", () => {
      if (session.advance()) renderPractice();
    });
    return;
  }

  if (phase === "action") {
    promptEl.textContent = "¿Qué debe hacer el laboratorio con esta sesión?";
    const canContinue = session.hasAnswerForCurrentPhase();
    const glosses = {
      accept: "Liberar resultados.",
      review: "No rechazar todavía; inspeccionar antes de liberar.",
      reject: "No liberar; investigar y repetir.",
    };
    container.innerHTML = `
      <div class="option-row option-row-action" role="group" aria-label="Opciones de acción">
        ${actionOptions()
          .map(
            (opt) =>
              `<button type="button" class="option-button action-option" data-action="${opt.id}" aria-pressed="${session.answers.action === opt.id}">
                <span class="option-title">${opt.label}</span>
                <span class="option-gloss">${glosses[opt.id]}</span>
              </button>`
          )
          .join("")}
      </div>
      <button type="button" class="confirm-button" id="confirm-button" ${canContinue ? "" : "disabled"}>Ver resultado</button>
    `;
    container.querySelectorAll("[data-action]").forEach((button) => {
      button.addEventListener("click", () => {
        session.chooseAction(button.dataset.action);
        renderPractice();
      });
    });
    container.querySelector("#confirm-button").addEventListener("click", () => {
      if (session.advance()) {
        const grade = session.grade();
        const progress = loadProgress();
        markScenarioComplete(progress, scenario.id, grade);
        saveProgress(progress);
        renderPractice();
      }
    });
    return;
  }

  if (phase === "reveal" || phase === "counterfactual") {
    promptEl.textContent = "";
    container.innerHTML = "";
    return;
  }
}

function renderRevealBlock(container, showReveal) {
  const phase = session.phase;
  if (phase !== "reveal" && phase !== "counterfactual") {
    container.hidden = true;
    container.innerHTML = "";
    return;
  }

  if (!showReveal) {
    container.hidden = true;
    container.innerHTML = `<button type="button" class="confirm-button" id="show-reveal-button">Mostrar resultado</button>`;
    container.hidden = false;
    container.querySelector("#show-reveal-button").addEventListener("click", () => {
      session.showReveal();
      renderPractice();
    });
    return;
  }

  container.hidden = false;
  const scenario = session.scenario;
  const grade = session.grade();
  const icon = { correcta: "✓", parcial: "~", incompleta: "~", incorrecta: "✗" };

  if (phase === "reveal") {
    const teaching = scenario.teaching;
    const incompleteRuleNote = grade.rule === "incompleta"
      ? `<p class="incomplete-note">1₂s también se cumple, pero la regla que decide es ${ruleDisplay(scenario.expected.rule)}.</p>`
      : "";
    container.innerHTML = `
      <div class="verdict-block">
        <p class="verdict-line"><span aria-hidden="true">${icon[grade.evidence]}</span> Evidencia: ${grade.evidence}</p>
        <p class="verdict-line"><span aria-hidden="true">${icon[grade.rule]}</span> Regla: ${grade.rule}</p>
        <p class="verdict-line"><span aria-hidden="true">${icon[grade.action]}</span> Acción: ${grade.action}</p>
      </div>
      ${incompleteRuleNote}
      <h3>Qué pasó</h3>
      <p>${teaching.pattern}</p>
      <h3>Por qué</h3>
      <p>${teaching.why}</p>
      <h3>Qué haces</h3>
      <p>${teaching.action_text}</p>
      ${teaching.error_type ? `<h3>Tipo de error</h3><p>${teaching.error_type}</p>` : ""}
      ${teaching.capability_note ? `<h3>Nota</h3><p>${teaching.capability_note}</p>` : ""}
      <div class="reveal-controls">
        <button type="button" class="outline-button" id="try-counterfactual-button">Probar un cambio</button>
        <button type="button" class="primary-button" id="next-scenario-button">Siguiente escenario</button>
        <button type="button" class="outline-button" id="hide-reveal-button">Volver a ocultar</button>
      </div>
    `;
    container.querySelector("#try-counterfactual-button").addEventListener("click", () => {
      session.counterfactualIndex = gridIndexForZ(
        scenario,
        scenario.points.find((p) => p.run === scenario.editable_run).z
      );
      session.phase = "counterfactual";
      renderPractice();
    });
    container.querySelector("#next-scenario-button").addEventListener("click", () => goToNextScenario());
    container.querySelector("#hide-reveal-button").addEventListener("click", () => {
      session.hideReveal();
      renderPractice();
    });
    return;
  }

  if (phase === "counterfactual") {
    if (session.counterfactualIndex === null) {
      session.counterfactualIndex = gridIndexForZ(
        scenario,
        scenario.points.find((p) => p.run === scenario.editable_run).z
      );
    }
    const { index, result } = counterfactualAt(scenario, session.counterfactualIndex);
    const boundarySentence = boundarySentenceForZ(result.z);
    const sign = result.z >= 0 ? "+" : "";
    const readout = `Control ${scenario.editable_run}: ${sign}${result.z.toFixed(1)} DE${
      boundarySentence ? ` — ${boundarySentence}` : ""
    }`;

    const ruleStateRows = result.evaluation.rules
      .map((r) => {
        const state = r.triggered ? "Se cumple" : "No se cumple";
        const runsText = r.evidence_runs.length ? ` (controles ${r.evidence_runs.join(", ")})` : "";
        return `<li>${ruleDisplay(r.rule)}: ${state}${runsText}</li>`;
      })
      .join("");

    container.innerHTML = `
      <h3>Cambia el control ${scenario.editable_run} y observa qué reglas dejan de cumplirse.</h3>
      <div class="counterfactual-controls">
        <button type="button" class="step-button" id="cf-minus" aria-label="Disminuir un paso">−</button>
        <input type="range" id="cf-range" min="0" max="40" step="1" value="${index}" aria-label="Valor del control ${scenario.editable_run} en desviaciones estándar" />
        <button type="button" class="step-button" id="cf-plus" aria-label="Aumentar un paso">+</button>
      </div>
      <p class="cf-readout">${readout}</p>
      <ul class="cf-rule-states">${ruleStateRows}</ul>
      <p class="cf-consequence">${result.consequence}</p>
      <div class="reveal-controls">
        <button type="button" class="outline-button" id="back-to-result-button">Volver al resultado</button>
        <button type="button" class="primary-button" id="next-scenario-button-cf">Siguiente escenario</button>
      </div>
    `;

    const rangeInput = container.querySelector("#cf-range");
    rangeInput.addEventListener("input", () => {
      session.counterfactualIndex = Number(rangeInput.value);
      renderPractice();
    });
    container.querySelector("#cf-minus").addEventListener("click", () => {
      session.counterfactualIndex = Math.max(0, session.counterfactualIndex - 1);
      renderPractice();
    });
    container.querySelector("#cf-plus").addEventListener("click", () => {
      session.counterfactualIndex = Math.min(40, session.counterfactualIndex + 1);
      renderPractice();
    });
    container.querySelector("#back-to-result-button").addEventListener("click", () => {
      session.phase = "reveal";
      renderPractice();
    });
    container.querySelector("#next-scenario-button-cf").addEventListener("click", () => goToNextScenario());
  }
}

function renderSetSummary() {
  const promptEl = document.querySelector("#practice-prompt");
  const chartEl = document.querySelector("#practice-chart");
  const runStripEl = document.querySelector("#run-strip");
  const controlsEl = document.querySelector("#phase-controls");
  const revealEl = document.querySelector("#reveal-block");
  const progress = loadProgress();
  const completed = practiceData.scenarios.filter((scenario) => progress.completed[scenario.id]);
  const actionCorrect = completed.filter((scenario) => progress.completed[scenario.id].action === "correcta");
  const handled = actionCorrect.map((scenario) => scenario.label);
  const missed = completed
    .filter((scenario) => progress.completed[scenario.id].action !== "correcta")
    .map((scenario) => scenario.label);

  updateSessionBar();
  promptEl.textContent = "Set completo";
  chartEl.innerHTML = "";
  document.querySelector("#practice-status").textContent = "Set de práctica completado.";
  runStripEl.hidden = true;
  runStripEl.innerHTML = "";
  controlsEl.innerHTML = "";
  revealEl.hidden = false;
  revealEl.innerHTML = `
    <div class="verdict-block">
      <p class="verdict-line">Acciones correctas: ${actionCorrect.length} / ${practiceData.scenarios.length}</p>
    </div>
    <p>${handled.length ? `Manejaste: ${handled.join("; ")}.` : "Aún no acertaste acciones en este set."}</p>
    <p>${missed.length ? `Para revisar: ${missed.join("; ")}.` : "No quedó ninguna familia de escenarios por revisar."}</p>
    <div class="reveal-controls">
      <button type="button" class="primary-button" id="repeat-set-button">Repetir set</button>
      <button type="button" class="outline-button" id="summary-home-button">Volver al inicio</button>
    </div>
  `;
  revealEl.querySelector("#repeat-set-button").addEventListener("click", () => {
    saveProgress({ completed: {}, currentScenarioId: practiceData.scenarios[0].id });
    window.location.hash = `practice/${practiceData.scenarios[0].id}`;
    enterPractice();
  });
  revealEl.querySelector("#summary-home-button").addEventListener("click", () => showRoute("home"));
}

function goToNextScenario() {
  const scenarios = practiceData.scenarios;
  const idx = scenarioIndex(session.scenario.id);
  const next = scenarios[idx + 1];
  if (next) {
    window.location.hash = `practice/${next.id}`;
    enterPractice();
  } else {
    session.phase = "summary";
    renderPractice();
  }
}

shareButton.addEventListener("click", async () => {
  const url = window.location.href;
  try {
    if (navigator.clipboard) await navigator.clipboard.writeText(url);
  } catch {
    // Clipboard may be unavailable; the URL remains visible in the address bar.
  }
});

// --- Rules -------------------------------------------------------------

async function ensureRulesData() {
  if (!rulesData) {
    rulesData = await fetchJSON("./data/rules.json");
  }
  return rulesData;
}

async function renderRulesView() {
  const container = document.querySelector("#rules-list");
  try {
    const data = await ensureRulesData();
    renderLearn(container, data);
  } catch (error) {
    container.textContent = "No fue posible cargar las reglas.";
    console.error(error);
  }
}

// --- init --------------------------------------------------------------

initCards({ fetchJSON });

showRoute(routeFromHash(), { updateHash: false });
