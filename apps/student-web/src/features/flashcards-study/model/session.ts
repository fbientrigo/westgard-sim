import type { FlashcardStudyDeck } from "@/shared/types/flashcards";

export type StudyPile = 1 | 2 | 3;
export type StudyRating = "again" | "good";

export type CardProgress = {
  pile: StudyPile;
  due_at: string;
  last_result: StudyRating | null;
  seen_count: number;
  success_count: number;
};

export type StudyProgress = {
  version: 1;
  deck_id: string;
  cards: Record<string, CardProgress>;
};

export type StudyPileSummary = {
  pile: StudyPile;
  title: string;
  description: string;
  count: number;
};

const PILE_LABELS: Record<StudyPile, { title: string; description: string }> = {
  1: {
    title: "Pila 1: Nuevas",
    description: "Tarjetas nuevas o que deben repetirse de inmediato.",
  },
  2: {
    title: "Pila 2: En practica",
    description: "Tarjetas que ya respondiste una vez y necesitan consolidacion.",
  },
  3: {
    title: "Pila 3: Repaso",
    description: "Tarjetas dominadas para repaso espaciado basico.",
  },
};

const DELAYS_MS: Record<StudyPile, number> = {
  1: 0,
  2: 12 * 60 * 60 * 1000,
  3: 3 * 24 * 60 * 60 * 1000,
};

function sortCards(deck: FlashcardStudyDeck) {
  return [...deck.cards].sort((left, right) => {
    const leftOrder = left.sort_order ?? Number.MAX_SAFE_INTEGER;
    const rightOrder = right.sort_order ?? Number.MAX_SAFE_INTEGER;
    return leftOrder - rightOrder || left.id.localeCompare(right.id);
  });
}

export function createInitialStudyProgress(
  deck: FlashcardStudyDeck,
  nowIso: string,
): StudyProgress {
  const cards = Object.fromEntries(
    deck.cards.map((card) => [
      card.id,
      {
        pile: 1,
        due_at: nowIso,
        last_result: null,
        seen_count: 0,
        success_count: 0,
      } satisfies CardProgress,
    ]),
  );
  return {
    version: 1,
    deck_id: deck.deck_id,
    cards,
  };
}

export function normalizeStudyProgress(
  deck: FlashcardStudyDeck,
  stored: StudyProgress | null | undefined,
  nowIso: string,
): StudyProgress {
  if (!stored || stored.version !== 1 || stored.deck_id !== deck.deck_id) {
    return createInitialStudyProgress(deck, nowIso);
  }

  const fallback = createInitialStudyProgress(deck, nowIso);
  const cards = Object.fromEntries(
    deck.cards.map((card) => [card.id, stored.cards[card.id] ?? fallback.cards[card.id]]),
  );
  return {
    version: 1,
    deck_id: deck.deck_id,
    cards,
  };
}

export function getDueCardIds(deck: FlashcardStudyDeck, progress: StudyProgress, nowIso: string): string[] {
  const nowMs = Date.parse(nowIso);
  return sortCards(deck)
    .filter((card) => Date.parse(progress.cards[card.id].due_at) <= nowMs)
    .map((card) => card.id);
}

export function getNextDueAt(progress: StudyProgress): string | null {
  const dueValues = Object.values(progress.cards).map((card) => Date.parse(card.due_at));
  if (dueValues.length === 0) {
    return null;
  }
  return new Date(Math.min(...dueValues)).toISOString();
}

export function getPileSummaries(progress: StudyProgress): StudyPileSummary[] {
  return ([1, 2, 3] as StudyPile[]).map((pile) => ({
    pile,
    title: PILE_LABELS[pile].title,
    description: PILE_LABELS[pile].description,
    count: Object.values(progress.cards).filter((card) => card.pile === pile).length,
  }));
}

export function applyStudyRating(
  progress: StudyProgress,
  cardId: string,
  rating: StudyRating,
  nowIso: string,
): StudyProgress {
  const current = progress.cards[cardId];
  if (!current) {
    return progress;
  }

  const nextPile: StudyPile =
    rating === "again" ? 1 : (Math.min(3, current.pile + 1) as StudyPile);
  const nextDue = new Date(Date.parse(nowIso) + DELAYS_MS[nextPile]).toISOString();

  return {
    ...progress,
    cards: {
      ...progress.cards,
      [cardId]: {
        pile: nextPile,
        due_at: nextDue,
        last_result: rating,
        seen_count: current.seen_count + 1,
        success_count: current.success_count + (rating === "good" ? 1 : 0),
      },
    },
  };
}
