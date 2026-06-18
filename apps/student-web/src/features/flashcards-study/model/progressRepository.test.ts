import { localStorageProgressRepository, storageKey } from "@/features/flashcards-study/model/progressRepository";
import type { StudyProgress } from "@/features/flashcards-study/model/session";

const progress: StudyProgress = {
  version: 1,
  deck_id: "westgard_qc_basics",
  cards: {
    "card-1": {
      due_at: "2026-04-04T12:00:00.000Z",
      last_result: "good",
      pile: 2,
      seen_count: 1,
      success_count: 1,
    },
  },
};

describe("localStorageProgressRepository", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("loads saved flashcard progress", async () => {
    await localStorageProgressRepository.saveFlashcardProgress(progress.deck_id, progress);

    await expect(localStorageProgressRepository.loadFlashcardProgress(progress.deck_id)).resolves.toEqual(
      progress,
    );
  });

  it("returns null for corrupt local progress", async () => {
    window.localStorage.setItem(storageKey(progress.deck_id), "{bad-json");

    await expect(localStorageProgressRepository.loadFlashcardProgress(progress.deck_id)).resolves.toBeNull();
  });

  it("clears saved flashcard progress", async () => {
    await localStorageProgressRepository.saveFlashcardProgress(progress.deck_id, progress);
    await localStorageProgressRepository.clearFlashcardProgress(progress.deck_id);

    expect(window.localStorage.getItem(storageKey(progress.deck_id))).toBeNull();
  });
});
