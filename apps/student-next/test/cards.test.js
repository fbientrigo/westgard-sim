// test/cards.test.js
import test from "node:test";
import assert from "node:assert/strict";
import { applyRating, filteredCards, restoreSession, seededShuffle } from "../src/cards.js";

const cards = [
  { id: "a", sort_order: 2, tags: ["tema-a"] },
  { id: "b", sort_order: 1, tags: ["tema-b"] },
  { id: "c", sort_order: 3, tags: ["tema-a"] },
];
const rules = [{ id: "1_2s", card_ids: ["a", "c"] }];

test("cards: deterministic ordering is sort_order then id", () => {
  assert.deepEqual(filteredCards(cards).map((card) => card.id), ["b", "a", "c"]);
});

test("cards: tag filter returns only the selected tag", () => {
  assert.deepEqual(filteredCards(cards, { tag: "tema-a" }).map((card) => card.id), ["a", "c"]);
});

test("cards: rule filter uses canonical rule card_ids", () => {
  assert.deepEqual(filteredCards(cards, { rule: "1_2s", rules }).map((card) => card.id), ["a", "c"]);
});

test("cards: seeded shuffle is stable for the same seed", () => {
  assert.deepEqual(
    seededShuffle(cards, 12345).map((card) => card.id),
    seededShuffle(cards, 12345).map((card) => card.id),
  );
});

test("cards: No la supe advances and requeues the card once", () => {
  const initial = { queue: ["a", "b"], index: 0, known: 0, again: 0, requeuedIds: [] };
  const firstMiss = applyRating(initial, "again");
  assert.deepEqual(firstMiss.queue, ["a", "b", "a"]);
  assert.equal(firstMiss.index, 1);
  assert.equal(firstMiss.again, 1);
  const toRevisit = { ...firstMiss, index: 2 };
  const secondMiss = applyRating(toRevisit, "again");
  assert.deepEqual(secondMiss.queue, ["a", "b", "a"]);
  assert.equal(secondMiss.index, 3);
});

test("cards: La supe advances without requeueing", () => {
  const next = applyRating({ queue: ["a", "b"], index: 0, known: 0, again: 0, requeuedIds: [] }, "known");
  assert.deepEqual(next.queue, ["a", "b"]);
  assert.equal(next.index, 1);
  assert.equal(next.known, 1);
});

test("cards: persisted queue, counters, and position are restored", () => {
  const restored = restoreSession(
    { order: ["a", "b"], queue: ["a", "b", "a"], index: 1, known: 1, again: 1, requeuedIds: ["a"], shuffle: true, shuffleSeed: 42 },
    ["a", "b"],
  );
  assert.deepEqual(restored.queue, ["a", "b", "a"]);
  assert.equal(restored.index, 1);
  assert.equal(restored.known, 1);
  assert.equal(restored.again, 1);
  assert.equal(restored.shuffle, true);
});

test("cards: incompatible persisted filter session is not restored", () => {
  assert.equal(
    restoreSession({ order: ["a", "b"], queue: ["a", "b"], index: 0 }, ["a"]),
    null,
  );
});
