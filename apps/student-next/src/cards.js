// src/cards.js
// Browse/session UI for the canonical flashcard deck. The only persisted
// state is a lightweight local session under wnext:cards:v1; this is not a
// spaced-repetition system. The module has no Westgard evaluation logic.

import { renderCardMarkup } from "./markup.js";
import { readJSON, writeJSON, clearKey, CARDS_KEY } from "./storage.js";

const SWIPE_THRESHOLD = 104;

const state = {
  allCards: [],
  rules: [],
  activeTag: null,
  activeRule: null,
  shuffle: false,
  shuffleSeed: null,
  queue: [],
  index: 0,
  known: 0,
  again: 0,
  requeuedIds: [],
  revealed: false,
  sessionActive: false,
  pointerId: null,
  pointerStartX: null,
  pointerStartY: null,
  pointerMoved: false,
  suppressNextClick: false,
};

let fetchJSONRef = null;
let elements = null;

function cacheElements() {
  if (elements) return elements;
  elements = {
    browse: document.querySelector("#cards-browse"),
    session: document.querySelector("#cards-session"),
    card: document.querySelector("#review-card"),
    tag: document.querySelector("#card-tag"),
    question: document.querySelector("#card-question"),
    answer: document.querySelector("#card-answer"),
    rating: document.querySelector("#rating-actions"),
    progressBar: document.querySelector("#session-progress-bar"),
    progressLabel: document.querySelector("#session-progress-label"),
  };
  return elements;
}

function isDesktopBrowse() {
  return window.innerWidth >= 861;
}

function queryValue(key) {
  const hash = window.location.hash;
  const query = hash.includes("?") ? hash.slice(hash.indexOf("?") + 1) : "";
  return new URLSearchParams(query).get(key);
}

function wantsBrowse() {
  return isDesktopBrowse() || queryValue("browse") === "1";
}

function orderedCards(cards) {
  return [...cards].sort((a, b) => a.sort_order - b.sort_order || a.id.localeCompare(b.id));
}

export function filteredCards(cards, { tag = null, rule = null, rules = [] } = {}) {
  let result = orderedCards(cards);
  if (tag) result = result.filter((card) => card.tags?.[0] === tag);
  if (rule) {
    const matchingRule = rules.find((entry) => entry.id === rule);
    const allowed = new Set(matchingRule?.card_ids || []);
    result = result.filter((card) => allowed.has(card.id));
  }
  return result;
}

// Deterministic seeded shuffle. The seed is stored with the session so a
// reload retains the same order, while no external random/state library is
// necessary.
export function seededShuffle(cards, seed) {
  const result = [...cards];
  let value = seed >>> 0;
  const next = () => {
    value += 0x6d2b79f5;
    let t = value;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(next() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function applyRating(session, rating) {
  const next = {
    ...session,
    queue: [...session.queue],
    requeuedIds: [...(session.requeuedIds || [])],
  };
  const cardId = next.queue[next.index];
  if (!cardId) return next;
  if (rating === "known") {
    next.known += 1;
  } else {
    next.again += 1;
    if (!next.requeuedIds.includes(cardId)) {
      next.queue.push(cardId);
      next.requeuedIds.push(cardId);
    }
  }
  next.index += 1;
  return next;
}

export function restoreSession(saved, allowedCardIds) {
  if (!saved || !Array.isArray(saved.queue) || !Array.isArray(saved.order)) return null;
  const allowed = new Set(allowedCardIds);
  if (saved.order.length !== allowedCardIds.length || saved.order.some((id) => !allowed.has(id))) return null;
  if (saved.queue.some((id) => !allowed.has(id))) return null;
  return {
    queue: saved.queue,
    index: Math.max(0, Math.min(saved.index || 0, saved.queue.length)),
    known: saved.known || 0,
    again: saved.again || 0,
    requeuedIds: Array.isArray(saved.requeuedIds) ? saved.requeuedIds.filter((id) => allowed.has(id)) : [],
    shuffle: Boolean(saved.shuffle),
    shuffleSeed: Number.isInteger(saved.shuffleSeed) ? saved.shuffleSeed : null,
  };
}

function resetCardMotion() {
  const card = cacheElements().card;
  card.classList.remove("dragging", "leaving");
  card.style.transform = "";
}

function setCardDragMotion(dx, dy) {
  const card = cacheElements().card;
  const limitedY = Math.max(-72, Math.min(72, dy));
  const tiltX = Math.max(-6, Math.min(6, -dy / 32));
  const tiltY = Math.max(-9, Math.min(9, dx / 24));
  const rotationZ = Math.max(-9, Math.min(9, dx / 28));
  card.style.transform = `perspective(1200px) translate3d(${dx}px, ${limitedY}px, 0) rotateX(${tiltX}deg) rotateY(${tiltY}deg) rotateZ(${rotationZ}deg)`;
}

function setCardHoverMotion(event) {
  if (event.pointerType !== "mouse" || state.pointerId !== null) return;
  const card = cacheElements().card;
  const rect = card.getBoundingClientRect();
  const nx = (event.clientX - rect.left) / Math.max(rect.width, 1) - 0.5;
  const ny = (event.clientY - rect.top) / Math.max(rect.height, 1) - 0.5;
  card.style.transform = `perspective(1200px) rotateX(${-ny * 5}deg) rotateY(${nx * 7}deg)`;
}

function animateSwipeRating(rating) {
  const card = cacheElements().card;
  const direction = rating === "known" ? 1 : -1;
  card.classList.remove("dragging");
  card.classList.add("leaving");
  card.style.transform = `perspective(1200px) translate3d(${direction * 440}px, -12px, 0) rotateZ(${direction * 10}deg)`;

  const reducedMotion = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
  window.setTimeout(() => {
    resetCardMotion();
    rateCard(rating);
  }, reducedMotion ? 0 : 180);
}

export function initCards({ fetchJSON }) {
  fetchJSONRef = fetchJSON;
  const els = cacheElements();

  els.card.addEventListener("click", () => {
    if (state.suppressNextClick) {
      state.suppressNextClick = false;
      return;
    }
    revealCard();
  });
  els.rating.addEventListener("click", (event) => {
    const button = event.target.closest("[data-rating]");
    if (button) rateCard(button.dataset.rating);
  });
  els.card.addEventListener("pointerdown", (event) => {
    if (event.button !== 0 || isFinished()) return;
    state.pointerId = event.pointerId;
    state.pointerStartX = event.clientX;
    state.pointerStartY = event.clientY;
    state.pointerMoved = false;
    state.suppressNextClick = false;
    els.card.classList.add("dragging");
    els.card.setPointerCapture?.(event.pointerId);
  });
  els.card.addEventListener("pointermove", (event) => {
    if (state.pointerId === event.pointerId && state.pointerStartX !== null && state.pointerStartY !== null) {
      const dx = event.clientX - state.pointerStartX;
      const dy = event.clientY - state.pointerStartY;
      state.pointerMoved ||= Math.hypot(dx, dy) > 7;
      setCardDragMotion(dx, dy);
      return;
    }
    setCardHoverMotion(event);
  });
  els.card.addEventListener("pointerup", (event) => {
    if (state.pointerId !== event.pointerId || state.pointerStartX === null || state.pointerStartY === null) return;
    els.card.releasePointerCapture?.(event.pointerId);
    const dx = event.clientX - state.pointerStartX;
    state.suppressNextClick = state.pointerMoved;
    state.pointerId = null;
    state.pointerStartX = null;
    state.pointerStartY = null;
    state.pointerMoved = false;

    if (state.revealed && Math.abs(dx) >= SWIPE_THRESHOLD && !isFinished()) {
      animateSwipeRating(dx > 0 ? "known" : "again");
      return;
    }
    resetCardMotion();
  });
  els.card.addEventListener("pointercancel", () => {
    state.pointerId = null;
    state.pointerStartX = null;
    state.pointerStartY = null;
    state.pointerMoved = false;
    resetCardMotion();
  });
  els.card.addEventListener("pointerleave", () => {
    if (state.pointerId === null) resetCardMotion();
  });

  document.addEventListener("keydown", (event) => {
    if (document.body.dataset.view !== "cards" || !state.sessionActive) return;
    if (event.key === " " && !state.revealed && !isFinished()) {
      event.preventDefault();
      revealCard();
    } else if (event.key === "ArrowLeft" && (state.revealed || isFinished())) {
      event.preventDefault();
      rateCard("again");
    } else if (event.key === "ArrowRight" && (state.revealed || isFinished())) {
      event.preventDefault();
      rateCard("known");
    }
  });
}

async function ensureData() {
  if (!state.allCards.length) {
    const deck = await fetchJSONRef("./data/cards.json");
    state.allCards = orderedCards(deck.cards);
  }
  if (!state.rules.length) {
    const data = await fetchJSONRef("./data/rules.json");
    state.rules = data.rules;
  }
}

export async function onCardsRouteEnter() {
  const els = cacheElements();
  try {
    await ensureData();
  } catch (error) {
    els.question.textContent = "No fue posible cargar las tarjetas.";
    els.tag.textContent = "Error de carga";
    console.error(error);
    return;
  }

  state.activeRule = queryValue("rule");
  if (wantsBrowse()) {
    state.sessionActive = false;
    els.browse.hidden = false;
    els.session.hidden = true;
    renderBrowse();
  } else {
    startSession(currentBrowseCards());
  }
}

function currentBrowseCards() {
  return filteredCards(state.allCards, {
    tag: state.activeTag,
    rule: state.activeRule,
    rules: state.rules,
  });
}

function ruleFilterNotice() {
  if (!state.activeRule) return "";
  const rule = state.rules.find((item) => item.id === state.activeRule);
  return rule ? `<p class="filter-notice">Tarjetas vinculadas a ${rule.display}.</p>` : "";
}

function renderBrowse() {
  const els = cacheElements();
  const tags = [...new Set(state.allCards.map((card) => card.tags?.[0]).filter(Boolean))];
  const cards = currentBrowseCards();
  const grouped = new Map();
  for (const card of cards) {
    const tag = card.tags?.[0] || "otros";
    if (!grouped.has(tag)) grouped.set(tag, []);
    grouped.get(tag).push(card);
  }

  els.browse.innerHTML = `
    <div class="browse-tools">
      <div class="tag-chips" role="group" aria-label="Filtrar tarjetas por tema">
        <button type="button" class="tag-chip" data-tag="" aria-pressed="${state.activeTag === null}">Todas</button>
        ${tags.map((tag) => `<button type="button" class="tag-chip" data-tag="${tag}" aria-pressed="${state.activeTag === tag}">${tag.replaceAll("-", " ")}</button>`).join("")}
      </div>
      ${ruleFilterNotice()}
      <label class="shuffle-toggle"><input type="checkbox" id="shuffle-toggle" ${state.shuffle ? "checked" : ""}> Mezclar</label>
    </div>
    ${[...grouped.entries()].map(([tag, group]) => `
      <section class="card-group"><h3>${tag.replaceAll("-", " ")}</h3>
      <ul>${group.map((card) => `<li>${renderCardMarkup(card.front)}</li>`).join("")}</ul></section>
    `).join("")}
    ${cards.length ? '<button type="button" class="primary-button" id="start-review-button">Iniciar repaso</button>' : '<p>No hay tarjetas para este filtro.</p>'}
  `;

  els.browse.querySelectorAll("[data-tag]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeTag = button.dataset.tag || null;
      renderBrowse();
    });
  });
  els.browse.querySelector("#shuffle-toggle").addEventListener("change", (event) => {
    state.shuffle = event.target.checked;
    state.shuffleSeed = state.shuffle ? Date.now() >>> 0 : null;
  });
  els.browse.querySelector("#start-review-button")?.addEventListener("click", () => {
    startSession(currentBrowseCards());
  });
}

function startSession(cards) {
  const els = cacheElements();
  const selectedCards = state.shuffle ? seededShuffle(cards, state.shuffleSeed) : orderedCards(cards);
  const ids = selectedCards.map((card) => card.id);
  const saved = restoreSession(readJSON(CARDS_KEY, null), ids);

  if (saved) {
    state.queue = saved.queue;
    state.index = saved.index;
    state.known = saved.known;
    state.again = saved.again;
    state.requeuedIds = saved.requeuedIds;
    state.shuffle = saved.shuffle;
    state.shuffleSeed = saved.shuffleSeed;
  } else {
    state.queue = ids;
    state.index = 0;
    state.known = 0;
    state.again = 0;
    state.requeuedIds = [];
  }

  state.revealed = false;
  state.sessionActive = true;
  els.browse.hidden = true;
  els.session.hidden = false;
  renderCurrentCard();
}

function currentCard() {
  const id = state.queue[state.index];
  return state.allCards.find((card) => card.id === id) || null;
}

function isFinished() {
  return state.index >= state.queue.length;
}

function persist() {
  const initialOrder = state.queue.slice(0, Math.max(0, state.queue.length - state.requeuedIds.length));
  writeJSON(CARDS_KEY, {
    order: initialOrder,
    queue: state.queue,
    index: state.index,
    known: state.known,
    again: state.again,
    requeuedIds: state.requeuedIds,
    shuffle: state.shuffle,
    shuffleSeed: state.shuffleSeed,
  });
}

function updateSessionProgress() {
  const els = cacheElements();
  const total = state.queue.length;
  const displayed = isFinished() ? total : state.index + 1;
  els.progressLabel.textContent = `${displayed} / ${total}`;
  els.progressBar.style.width = `${total ? (state.index / total) * 100 : 0}%`;
}

function renderCurrentCard() {
  const els = cacheElements();
  resetCardMotion();
  if (isFinished()) {
    renderSummaryCard();
    return;
  }
  const card = currentCard();
  if (!card) return;

  state.revealed = false;
  state.suppressNextClick = false;
  els.card.classList.remove("revealed");
  els.rating.hidden = true;
  els.card.disabled = false;
  els.card.setAttribute("aria-label", "Tarjeta de estudio. Pulsa para revelar la respuesta.");
  els.tag.textContent = card.tags?.[0]?.replaceAll("-", " ") || "Tarjeta";
  els.question.innerHTML = renderCardMarkup(card.front);
  els.answer.innerHTML = renderCardMarkup(card.back);
  els.rating.querySelector('[data-rating="again"]').textContent = "No la supe";
  els.rating.querySelector('[data-rating="known"]').textContent = "La supe";
  updateSessionProgress();
  persist();
}

function revealCard() {
  if (!state.sessionActive || isFinished() || !currentCard()) return;
  const els = cacheElements();
  resetCardMotion();
  state.revealed = true;
  els.card.classList.add("revealed");
  els.card.setAttribute("aria-label", "Respuesta de la tarjeta. Usa No la supe o La supe para continuar.");
  els.rating.hidden = false;
}

function rateCard(rating) {
  if (!state.sessionActive) return;
  if (isFinished()) {
    if (rating === "known") restartCards();
    return;
  }
  if (!state.revealed) return;
  const updated = applyRating(
    {
      queue: state.queue,
      index: state.index,
      known: state.known,
      again: state.again,
      requeuedIds: state.requeuedIds,
    },
    rating,
  );
  state.queue = updated.queue;
  state.index = updated.index;
  state.known = updated.known;
  state.again = updated.again;
  state.requeuedIds = updated.requeuedIds;
  persist();
  renderCurrentCard();
}

function renderSummaryCard() {
  const els = cacheElements();
  resetCardMotion();
  els.card.classList.remove("revealed");
  els.card.disabled = true;
  els.card.setAttribute("aria-label", "Sesión completa.");
  els.tag.textContent = "Sesión completa";
  els.question.innerHTML = `Terminaste ${state.queue.length} tarjetas.<br><span class="term">${state.known}</span> recuperadas · <span class="term">${state.again}</span> para reforzar.`;
  els.answer.textContent = "";
  els.rating.hidden = true;
  updateSessionProgress();
  persist();
  if (!els.session.querySelector("#cards-restart")) {
    els.session.insertAdjacentHTML("beforeend", '<button type="button" class="outline-button cards-restart" id="cards-restart">Reiniciar</button>');
    els.session.querySelector("#cards-restart").addEventListener("click", restartCards);
  }
}

function restartCards() {
  const existing = cacheElements().session.querySelector("#cards-restart");
  existing?.remove();
  clearKey(CARDS_KEY);
  const cards = currentBrowseCards();
  state.queue = state.shuffle ? seededShuffle(cards, state.shuffleSeed) : orderedCards(cards);
  state.queue = state.queue.map((card) => card.id || card);
  state.index = 0;
  state.known = 0;
  state.again = 0;
  state.requeuedIds = [];
  state.revealed = false;
  renderCurrentCard();
}