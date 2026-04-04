import {
  applyStudyRating,
  createInitialStudyProgress,
  getDueCardIds,
  getPileSummaries,
  normalizeStudyProgress,
} from "@/features/flashcards-study/model/session";
import type { FlashcardStudyDeck } from "@/shared/types/flashcards";

const deck: FlashcardStudyDeck = {
  deck_id: "deck",
  format_version: "1.0",
  metadata: {
    title: "Deck",
    subtitle: "Sub",
    language: "es",
    audience: "Estudiantes",
    description: "Desc",
    author: "Westgard",
    tags: [],
    display_tags: [],
    notes: null,
  },
  cards: [
    {
      id: "a",
      card_type: "concept",
      card_type_label: "Concepto",
      sort_order: 1,
      tags: [],
      display_tags: [],
      front_html: "<p>A</p>",
      back_html: "<p>B</p>",
      front_source: "A",
      back_source: "B",
    },
    {
      id: "b",
      card_type: "concept",
      card_type_label: "Concepto",
      sort_order: 2,
      tags: [],
      display_tags: [],
      front_html: "<p>C</p>",
      back_html: "<p>D</p>",
      front_source: "C",
      back_source: "D",
    },
  ],
};

describe("flashcard session model", () => {
  it("creates all cards in pile 1 and due now", () => {
    const progress = createInitialStudyProgress(deck, "2026-04-04T12:00:00.000Z");
    expect(progress.cards.a.pile).toBe(1);
    expect(getDueCardIds(deck, progress, "2026-04-04T12:00:00.000Z")).toEqual(["a", "b"]);
  });

  it("moves a successful card to the next pile", () => {
    const progress = createInitialStudyProgress(deck, "2026-04-04T12:00:00.000Z");
    const next = applyStudyRating(progress, "a", "good", "2026-04-04T12:00:00.000Z");
    expect(next.cards.a.pile).toBe(2);
    expect(getPileSummaries(next)[1].count).toBe(1);
  });

  it("returns failed cards to pile 1", () => {
    const progress = normalizeStudyProgress(
      deck,
      {
        version: 1,
        deck_id: "deck",
        cards: {
          a: {
            pile: 3,
            due_at: "2026-04-04T12:00:00.000Z",
            last_result: "good",
            seen_count: 4,
            success_count: 4,
          },
          b: {
            pile: 1,
            due_at: "2026-04-04T12:00:00.000Z",
            last_result: null,
            seen_count: 0,
            success_count: 0,
          },
        },
      },
      "2026-04-04T12:00:00.000Z",
    );
    const next = applyStudyRating(progress, "a", "again", "2026-04-04T12:00:00.000Z");
    expect(next.cards.a.pile).toBe(1);
    expect(next.cards.a.last_result).toBe("again");
  });
});
