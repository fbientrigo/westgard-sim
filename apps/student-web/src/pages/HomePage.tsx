import { ExperimentList } from "@/features/experiment-list/ui/ExperimentList";
import { listExperiments } from "@/shared/api/studentDataApi";
import { useAsyncResource } from "@/shared/lib/useAsyncResource";
import { EmptyState, ErrorState, LoadingState } from "@/shared/ui/AsyncStates";

export function HomePage(): JSX.Element {
  const { data, error, isLoading, reload } = useAsyncResource(async () => listExperiments(), []);

  if (isLoading) {
    return <LoadingState description="Consultando indice de experimentos..." />;
  }

  if (error) {
    return (
      <ErrorState
        description={`${error}. Verifica que exista public/web_data/index.json o ejecuta sync:data.`}
        onRetry={reload}
      />
    );
  }

  if (!data || data.experiments.length === 0) {
    return (
      <EmptyState description="No hay experimentos publicados. Genera y sincroniza el dataset exportado." />
    );
  }

  return <ExperimentList experiments={data.experiments} />;
}
