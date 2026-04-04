import { FlashcardStudyBoard } from "@/features/flashcards-study/ui/FlashcardStudyBoard";
import { getFlashcardStudyDeck } from "@/shared/api/studentDataApi";
import { useAsyncResource } from "@/shared/lib/useAsyncResource";
import { ErrorState, LoadingState } from "@/shared/ui/AsyncStates";

const DEFAULT_DECK_ID = "westgard_qc_basics";

export function FlashcardsPage(): JSX.Element {
  const { data, error, isLoading, reload } = useAsyncResource(
    async () => getFlashcardStudyDeck(DEFAULT_DECK_ID),
    [],
  );

  if (isLoading) {
    return <LoadingState description="Cargando deck de flashcards..." />;
  }

  if (error) {
    return (
      <ErrorState
        description={`${error}. Verifica que exista public/flashcards/${DEFAULT_DECK_ID}/study_deck.json o ejecuta la exportacion y sync:data.`}
        onRetry={reload}
      />
    );
  }

  if (!data) {
    return <ErrorState description="No se pudo cargar el deck de estudio." onRetry={reload} />;
  }

  return <FlashcardStudyBoard deck={data} />;
}
