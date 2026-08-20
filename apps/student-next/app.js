const ROUTES = new Set(["home", "rules", "practice", "cards"]);

const RULES = [
  {
    code: "1₂s",
    role: "Advertencia",
    roleClass: "warning",
    pattern: "Un punto supera ±2 DE.",
    detail: "Es sensible, pero por sí sola no significa rechazo automático. Sirve para mirar la corrida con más atención.",
    action: "Revisa si aparece otra regla antes de decidir.",
    engine: true,
  },
  {
    code: "1₃s",
    role: "Rechazo",
    roleClass: "reject",
    pattern: "Un punto supera ±3 DE.",
    detail: "Un desvío aislado de esta magnitud es compatible con un problema analítico importante.",
    action: "No liberes resultados hasta investigar y recuperar control.",
    engine: true,
  },
  {
    code: "2₂s",
    role: "Rechazo",
    roleClass: "reject",
    pattern: "Dos puntos consecutivos superan 2 DE del mismo lado.",
    detail: "La repetición en la misma dirección orienta a un desplazamiento sistemático.",
    action: "Investiga una fuente persistente de sesgo antes de continuar.",
    engine: true,
  },
  {
    code: "R₄s",
    role: "Referencia",
    roleClass: "",
    pattern: "Dos controles de una corrida quedan separados por más de 4 DE.",
    detail: "El contraste entre un valor alto y otro bajo orienta principalmente a error aleatorio.",
    action: "Busca una fuente de imprecisión o variación aleatoria.",
    engine: false,
  },
  {
    code: "4₁s",
    role: "Referencia",
    roleClass: "",
    pattern: "Cuatro puntos consecutivos superan 1 DE del mismo lado.",
    detail: "Una secuencia sostenida hacia un lado de la media sugiere un desplazamiento sistemático.",
    action: "Busca un cambio persistente en calibración, lote o instrumento.",
    engine: false,
  },
  {
    code: "10x",
    role: "Referencia",
    roleClass: "",
    pattern: "Diez puntos consecutivos quedan del mismo lado de la media.",
    detail: "Aunque varios puntos estén cerca de la media, la persistencia de un solo lado es la señal importante.",
    action: "Interpreta la serie completa; no evalúes cada punto de forma aislada.",
    engine: false,
  },
];

const PRESETS = [
  { id: "stable", label: "En control", values: [-0.6, 0.4, -0.3, 0.7, -0.5, 0.2, 0.6, 0.8] },
  { id: "1-2s", label: "1₂s", values: [-0.4, 0.3, -0.6, 0.5, -0.2, 0.7, 0.9, 2.4] },
  { id: "1-3s", label: "1₃s", values: [0.1, -0.4, 0.5, -0.3, 0.6, 0.2, 0.4, 3.2] },
  { id: "2-2s", label: "2₂s", values: [-0.5, 0.2, -0.4, 0.5, -0.2, 0.4, 2.3, 2.5] },
];

const state = {
  values: [...PRESETS[0].values],
  deck: [],
  cardIndex: 0,
  revealed: false,
  known: 0,
  again: 0,
  finished: false,
  pointerStartX: null,
};

const panels = [...document.querySelectorAll("[data-view-panel]")];
const reviewCard = document.querySelector("#review-card");
const ratingActions = document.querySelector("#rating-actions");
const question = document.querySelector("#card-question");
const answer = document.querySelector("#card-answer");
const cardTag = document.querySelector("#card-tag");
const progressBar = document.querySelector("#card-progress-bar");
const progressLabel = document.querySelector("#card-progress-label");

function routeFromHash() {
  const route = window.location.hash.replace(/^#/, "") || "home";
  return ROUTES.has(route) ? route : "home";
}

function showRoute(route, { updateHash = true } = {}) {
  const safeRoute = ROUTES.has(route) ? route : "home";
  document.body.dataset.view = safeRoute;
  panels.forEach((panel) => {
    panel.hidden = panel.dataset.viewPanel !== safeRoute;
  });

  if (safeRoute === "cards") ensureDeck();
  if (safeRoute === "practice") renderPractice();

  if (updateHash && window.location.hash !== `#${safeRoute}`) {
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

window.addEventListener("hashchange", () => showRoute(routeFromHash(), { updateHash: false }));

function renderRules() {
  const grid = document.querySelector("#rules-grid");
  grid.innerHTML = RULES.map((rule) => `
    <article class="rule-card">
      <div class="rule-card-top">
        <span class="rule-code">${rule.code}</span>
        <span class="rule-role ${rule.roleClass}">${rule.role}</span>
      </div>
      <p class="rule-pattern">${rule.pattern}</p>
      <p class="rule-detail">${rule.detail}</p>
      <p class="rule-action"><strong>Qué haces:</strong> ${rule.action}</p>
      ${rule.engine ? "" : '<p class="scope-note">Disponible como referencia y tarjetas; aún no se evalúa en el laboratorio visual.</p>'}
    </article>
  `).join("");
}

function rule12s(values) {
  return values.some((value) => Math.abs(value) > 2);
}

function rule13s(values) {
  return values.some((value) => Math.abs(value) > 3);
}

function rule22s(values) {
  for (let index = 0; index < values.length - 1; index += 1) {
    const a = values[index];
    const b = values[index + 1];
    if ((a > 2 && b > 2) || (a < -2 && b < -2)) return true;
  }
  return false;
}

function evaluate(values) {
  return [
    {
      code: "1₂s",
      triggered: rule12s(values),
      level: "warning",
      note: "Algún control supera ±2 DE. Es una advertencia: revisa el resto del patrón.",
    },
    {
      code: "1₃s",
      triggered: rule13s(values),
      level: "reject",
      note: "Algún control supera ±3 DE. La corrida requiere rechazo e investigación.",
    },
    {
      code: "2₂s",
      triggered: rule22s(values),
      level: "reject",
      note: "Dos controles consecutivos superan 2 DE del mismo lado: patrón sistemático.",
    },
  ];
}

function formatZ(value) {
  const number = Number(value);
  return `${number >= 0 ? "+" : ""}${number.toFixed(1)} DE`;
}

function renderChart(values) {
  const chart = document.querySelector("#chart");
  const width = 760;
  const height = 390;
  const margin = { top: 22, right: 24, bottom: 36, left: 48 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const x = (index) => margin.left + (index / (values.length - 1)) * plotWidth;
  const y = (z) => margin.top + ((3.5 - z) / 7) * plotHeight;

  const lines = [-3, -2, -1, 0, 1, 2, 3].map((z) => {
    const strong = z === 0;
    const label = z === 0 ? "Media" : `${z > 0 ? "+" : ""}${z} DE`;
    return `
      <line x1="${margin.left}" y1="${y(z)}" x2="${width - margin.right}" y2="${y(z)}"
        stroke="${strong ? "#77839a" : "#dce2eb"}" stroke-width="${strong ? 1.6 : 1}" ${Math.abs(z) === 2 ? 'stroke-dasharray="5 5"' : ""} ${Math.abs(z) === 3 ? 'stroke-dasharray="2 5"' : ""}/>
      <text x="${margin.left - 10}" y="${y(z) + 4}" text-anchor="end" fill="#657086" font-size="12">${label}</text>
    `;
  }).join("");

  const path = values.map((value, index) => `${index === 0 ? "M" : "L"} ${x(index)} ${y(value)}`).join(" ");
  const points = values.map((value, index) => {
    const active = index >= values.length - 2;
    const outside3 = Math.abs(value) > 3;
    const outside2 = Math.abs(value) > 2;
    const fill = outside3 ? "#b23a3a" : outside2 ? "#a36100" : active ? "#3157d5" : "#ffffff";
    const stroke = outside3 ? "#b23a3a" : outside2 ? "#a36100" : "#3157d5";
    return `
      <circle cx="${x(index)}" cy="${y(value)}" r="${active ? 7 : 5.5}" fill="${fill}" stroke="${stroke}" stroke-width="2.2" />
      <text x="${x(index)}" y="${height - 12}" text-anchor="middle" fill="#657086" font-size="12">${index + 1}</text>
    `;
  }).join("");

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" aria-hidden="true">
      ${lines}
      <path d="${path}" fill="none" stroke="#3157d5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      ${points}
    </svg>
  `;
}

function renderResults(values) {
  const results = evaluate(values);
  const container = document.querySelector("#rule-results");
  container.innerHTML = results.map((result) => `
    <div class="rule-result ${result.triggered ? `triggered ${result.level}` : ""}">
      <div class="rule-result-title">
        <span>${result.code}</span>
        <span>${result.triggered ? "Activada" : "No activada"}</span>
      </div>
      <p>${result.note}</p>
    </div>
  `).join("");

  const status = document.querySelector("#run-status");
  const reject = results.some((result) => result.triggered && result.level === "reject");
  const warning = results.some((result) => result.triggered && result.level === "warning");
  status.className = "status-pill";
  if (reject) {
    status.textContent = "Rechazar corrida";
    status.classList.add("reject");
  } else if (warning) {
    status.textContent = "Revisar";
    status.classList.add("warn");
  } else {
    status.textContent = "En control";
  }
}

function renderPractice() {
  renderChart(state.values);
  renderResults(state.values);
  document.querySelector("#prev-value").textContent = formatZ(state.values.at(-2));
  document.querySelector("#last-value").textContent = formatZ(state.values.at(-1));
  document.querySelector("#prev-slider").value = state.values.at(-2);
  document.querySelector("#last-slider").value = state.values.at(-1);
}

const presetRow = document.querySelector("#preset-row");
presetRow.innerHTML = PRESETS.map((preset) => `<button class="preset-button" type="button" data-preset="${preset.id}">${preset.label}</button>`).join("");
presetRow.addEventListener("click", (event) => {
  const button = event.target.closest("[data-preset]");
  if (!button) return;
  const preset = PRESETS.find((item) => item.id === button.dataset.preset);
  if (!preset) return;
  state.values = [...preset.values];
  renderPractice();
});

function updateEditablePoint(offset, rawValue) {
  const value = Number(rawValue);
  state.values[state.values.length + offset] = value;
  renderPractice();
}

document.querySelector("#prev-slider").addEventListener("input", (event) => updateEditablePoint(-2, event.target.value));
document.querySelector("#last-slider").addEventListener("input", (event) => updateEditablePoint(-1, event.target.value));

function formatCardMarkup(text) {
  return String(text)
    .replace(/\[\[[^:\]]+:([^\]]+)\]\]/g, '<span class="term">$1</span>')
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

async function ensureDeck() {
  if (state.deck.length) {
    renderCurrentCard();
    return;
  }

  try {
    const response = await fetch("./data/cards.json");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.deck = [...payload.cards].sort((a, b) => a.sort_order - b.sort_order);
    renderCurrentCard();
  } catch (error) {
    question.textContent = "No fue posible cargar las tarjetas.";
    answer.textContent = "La referencia y el laboratorio visual siguen disponibles.";
    cardTag.textContent = "Error de carga";
    console.error(error);
  }
}

function currentCard() {
  return state.deck[state.cardIndex];
}

function updateProgress() {
  const total = state.deck.length;
  const completed = Math.min(state.cardIndex, total);
  const shown = state.finished ? total : Math.min(state.cardIndex + 1, total);
  progressLabel.textContent = `${shown} / ${total}`;
  progressBar.style.width = `${total ? (completed / total) * 100 : 0}%`;
}

function renderCurrentCard() {
  if (!state.deck.length) return;

  if (state.cardIndex >= state.deck.length) {
    renderSummaryCard();
    return;
  }

  state.finished = false;
  state.revealed = false;
  reviewCard.classList.remove("revealed");
  ratingActions.hidden = true;
  const card = currentCard();
  cardTag.textContent = card.tags?.[0]?.replaceAll("-", " ") || "Tarjeta";
  question.innerHTML = formatCardMarkup(card.front);
  answer.innerHTML = formatCardMarkup(card.back);
  document.querySelector('[data-rating="again"]').textContent = "No la supe";
  document.querySelector('[data-rating="known"]').textContent = "La supe";
  updateProgress();
}

function revealCard() {
  if (state.finished || !currentCard()) return;
  state.revealed = true;
  reviewCard.classList.add("revealed");
  ratingActions.hidden = false;
}

function rateCard(rating) {
  if (state.finished) {
    if (rating === "known") restartCards();
    else showRoute("home");
    return;
  }
  if (!state.revealed) return;
  if (rating === "known") state.known += 1;
  else state.again += 1;
  state.cardIndex += 1;
  renderCurrentCard();
}

function renderSummaryCard() {
  state.finished = true;
  state.revealed = false;
  reviewCard.classList.remove("revealed");
  cardTag.textContent = "Sesión completa";
  question.innerHTML = `Terminaste ${state.deck.length} tarjetas.<br><span class="term">${state.known}</span> recuperadas · <span class="term">${state.again}</span> para reforzar.`;
  answer.textContent = "";
  ratingActions.hidden = false;
  document.querySelector('[data-rating="again"]').textContent = "Volver al inicio";
  document.querySelector('[data-rating="known"]').textContent = "Repasar de nuevo";
  progressLabel.textContent = `${state.deck.length} / ${state.deck.length}`;
  progressBar.style.width = "100%";
}

function restartCards() {
  state.cardIndex = 0;
  state.known = 0;
  state.again = 0;
  state.finished = false;
  renderCurrentCard();
}

reviewCard.addEventListener("click", () => revealCard());
reviewCard.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    revealCard();
  }
});

ratingActions.addEventListener("click", (event) => {
  const button = event.target.closest("[data-rating]");
  if (button) rateCard(button.dataset.rating);
});

document.addEventListener("keydown", (event) => {
  if (document.body.dataset.view !== "cards") return;
  if (event.key === " " && !state.revealed && !state.finished) {
    event.preventDefault();
    revealCard();
  } else if (event.key === "ArrowLeft" && (state.revealed || state.finished)) {
    rateCard("again");
  } else if (event.key === "ArrowRight" && (state.revealed || state.finished)) {
    rateCard("known");
  }
});

reviewCard.addEventListener("pointerdown", (event) => {
  state.pointerStartX = event.clientX;
});
reviewCard.addEventListener("pointerup", (event) => {
  if (state.pointerStartX === null || !state.revealed || state.finished) return;
  const delta = event.clientX - state.pointerStartX;
  state.pointerStartX = null;
  if (Math.abs(delta) < 80) return;
  rateCard(delta > 0 ? "known" : "again");
});
reviewCard.addEventListener("pointercancel", () => { state.pointerStartX = null; });

renderRules();
renderPractice();
showRoute(routeFromHash(), { updateHash: false });
