import type { SupabaseClient } from "@supabase/supabase-js";
import type { StudyProgress } from "@/features/flashcards-study/model/session";
import { getSupabaseClient } from "@/shared/supabase/client";

const STORAGE_PREFIX = "westgard.flashcards.progress";
const FLASHCARD_PROGRESS_TABLE = "westgard_flashcard_progress";

export type ProgressRepository = {
  loadFlashcardProgress: (deckId: string) => Promise<StudyProgress | null>;
  saveFlashcardProgress: (deckId: string, progress: StudyProgress) => Promise<void>;
  clearFlashcardProgress: (deckId: string) => Promise<void>;
  mode: "local" | "supabase";
};

export function storageKey(deckId: string): string {
  return `${STORAGE_PREFIX}.${deckId}`;
}

export const localStorageProgressRepository: ProgressRepository = {
  mode: "local",
  async loadFlashcardProgress(deckId) {
    if (typeof window === "undefined") {
      return null;
    }

    const raw = window.localStorage.getItem(storageKey(deckId));
    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as StudyProgress;
    } catch {
      return null;
    }
  },
  async saveFlashcardProgress(deckId, progress) {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem(storageKey(deckId), JSON.stringify(progress));
  },
  async clearFlashcardProgress(deckId) {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.removeItem(storageKey(deckId));
  },
};

export function createSupabaseProgressRepository(
  client: SupabaseClient,
  userId: string,
): ProgressRepository {
  return {
    mode: "supabase",
    async loadFlashcardProgress(deckId) {
      const { data, error } = await client
        .from(FLASHCARD_PROGRESS_TABLE)
        .select("progress")
        .eq("user_id", userId)
        .eq("deck_id", deckId)
        .maybeSingle();

      if (error) {
        console.warn("No se pudo cargar progreso desde Supabase.", error.message);
        return null;
      }

      return (data?.progress as StudyProgress | undefined) ?? null;
    },
    async saveFlashcardProgress(deckId, progress) {
      const { error } = await client.from(FLASHCARD_PROGRESS_TABLE).upsert(
        {
          deck_id: deckId,
          progress,
          updated_at: new Date().toISOString(),
          user_id: userId,
        },
        { onConflict: "user_id,deck_id" },
      );

      if (error) {
        console.warn("No se pudo guardar progreso en Supabase.", error.message);
      }
    },
    async clearFlashcardProgress(deckId) {
      const { error } = await client
        .from(FLASHCARD_PROGRESS_TABLE)
        .delete()
        .eq("user_id", userId)
        .eq("deck_id", deckId);

      if (error) {
        console.warn("No se pudo eliminar progreso en Supabase.", error.message);
      }
    },
  };
}

export function createHybridProgressRepository(userId: string | null): ProgressRepository {
  const client = getSupabaseClient();
  const remote = client && userId ? createSupabaseProgressRepository(client, userId) : null;

  if (!remote) {
    return localStorageProgressRepository;
  }

  return {
    mode: "supabase",
    async loadFlashcardProgress(deckId) {
      const [remoteProgress, localProgress] = await Promise.all([
        remote.loadFlashcardProgress(deckId),
        localStorageProgressRepository.loadFlashcardProgress(deckId),
      ]);

      if (remoteProgress) {
        return remoteProgress;
      }

      if (localProgress) {
        await remote.saveFlashcardProgress(deckId, localProgress);
        return localProgress;
      }

      return null;
    },
    async saveFlashcardProgress(deckId, progress) {
      await localStorageProgressRepository.saveFlashcardProgress(deckId, progress);
      await remote.saveFlashcardProgress(deckId, progress);
    },
    async clearFlashcardProgress(deckId) {
      await localStorageProgressRepository.clearFlashcardProgress(deckId);
      await remote.clearFlashcardProgress(deckId);
    },
  };
}
