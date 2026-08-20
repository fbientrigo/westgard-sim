// src/learn.js
// Renders the Reglas (Learn) view from generated rules.json. No rule text,
// severity strings, or rule code lists are hardcoded here; everything comes
// from data/rules.json (see contract Slice 5).

import { renderMiniPattern } from "./chart.js";

export function renderLearn(container, rulesPayload) {
  const rules = rulesPayload.rules;
  const interactive = rules.filter((r) => r.evaluation === "interactive");
  const reference = rules.filter((r) => r.evaluation === "reference");

  const rowHtml = (rule) => `
    <button type="button" class="rule-row" data-rule-id="${rule.id}" aria-expanded="false">
      <span class="rule-row-pattern-cell">
        ${renderMiniPattern(rule.mini_pattern)}
      </span>
      <span class="rule-row-middle">
        <span class="rule-row-code">${rule.display}</span>
        <span class="rule-row-pattern-text">${rule.pattern}</span>
      </span>
      <span class="rule-row-badges">
        <span class="badge badge-severity">${rule.severity_label}</span>
        <span class="badge badge-capability">${rule.evaluation === "interactive" ? "Evaluable aquí" : "Solo referencia"}</span>
      </span>
    </button>
    <div class="rule-row-panel" id="panel-${rule.id}" hidden>
      <h4>Qué ves</h4>
      <p>${rule.pattern}</p>
      <h4>Qué significa</h4>
      <p>${rule.interpretation}</p>
      <h4>Qué haces</h4>
      <p>${rule.action}</p>
      <a class="cards-deep-link" href="#cards?rule=${rule.id}" data-rule-link="${rule.id}">Repasar en tarjetas →</a>
    </div>
  `;

  container.innerHTML = `
    ${interactive.map(rowHtml).join("")}
    <div class="rules-divider">Reglas de referencia (no se evalúan en este simulador)</div>
    ${reference.map(rowHtml).join("")}
  `;

  container.querySelectorAll(".rule-row").forEach((button) => {
    button.addEventListener("click", () => {
      const panel = document.querySelector(`#panel-${button.dataset.ruleId}`);
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      panel.hidden = expanded;
    });
  });
}
