import { Link, useParams } from "react-router-dom";
import { ExperimentOverview } from "@/features/experiment-detail/ui/ExperimentOverview";
import { getExperimentManifest, listExperiments } from "@/shared/api/studentDataApi";
import { useAsyncResource } from "@/shared/lib/useAsyncResource";
import { EmptyState, ErrorState, LoadingState, NotFoundState } from "@/shared/ui/AsyncStates";
import type { ExperimentDetail } from "@/entities/experiment/model/experiment";

export function ExperimentPage(): JSX.Element {
  const { experimentId = "" } = useParams();

  const { data, error, isLoading, reload } = useAsyncResource<ExperimentDetail | null>(async () => {
    const index = await listExperiments();
    const entry = index.experiments.find((experiment) => experiment.id === experimentId);
    if (!entry) {
      return null;
    }
    return getExperimentManifest(entry.manifest_path);
  }, [experimentId]);

  if (isLoading) {
    return <LoadingState description="Cargando manifiesto del experimento..." />;
  }

  if (error) {
    return <ErrorState description={error} onRetry={reload} />;
  }

  if (data === null) {
    return (
      <NotFoundState description="El experimento solicitado no existe en index.json o no esta publicado." />
    );
  }

  if (data.scenarios.length === 0) {
    return (
      <section className="content-section">
        <ExperimentOverview experiment={data} />
        <EmptyState description="El experimento no tiene escenarios disponibles." />
      </section>
    );
  }

  return (
    <section>
      <p className="breadcrumb">
        <Link to="/">Inicio</Link> / {data.title}
      </p>
      <ExperimentOverview experiment={data} />
    </section>
  );
}
