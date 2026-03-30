import { Link, useParams } from "react-router-dom";
import { getTriggerRuns } from "@/entities/rule-result/model/ruleResult";
import { ScenarioViewer } from "@/features/scenario-viewer/ui/ScenarioViewer";
import { getEducationalContent } from "@/shared/api/educationalAdapter";
import { getExperimentManifest, getScenarioPayload, listExperiments } from "@/shared/api/studentDataApi";
import { useAsyncResource } from "@/shared/lib/useAsyncResource";
import { EmptyState, ErrorState, LoadingState, NotFoundState } from "@/shared/ui/AsyncStates";
import type { EducationalContent } from "@/shared/types/educational";
import type { ScenarioDetail } from "@/entities/scenario/model/scenario";

type ScenarioPageData = {
  scenario: ScenarioDetail;
  educational: EducationalContent | null;
  experimentTitle: string;
};

export function ScenarioPage(): JSX.Element {
  const { experimentId = "", scenarioId = "" } = useParams();

  const { data, error, isLoading, reload } = useAsyncResource<ScenarioPageData | null>(async () => {
    const index = await listExperiments();
    const experiment = index.experiments.find((item) => item.id === experimentId);
    if (!experiment) {
      return null;
    }

    const manifest = await getExperimentManifest(experiment.manifest_path);
    const scenarioManifest = manifest.scenarios.find((item) => item.id === scenarioId);
    if (!scenarioManifest) {
      return null;
    }

    const scenario = await getScenarioPayload(scenarioManifest.path);
    const educational = await getEducationalContent(scenario.scenario_type);

    return {
      scenario,
      educational,
      experimentTitle: manifest.title,
    };
  }, [experimentId, scenarioId]);

  if (isLoading) {
    return <LoadingState description="Cargando escenario..." />;
  }

  if (error) {
    return <ErrorState description={error} onRetry={reload} />;
  }

  if (!data) {
    return (
      <NotFoundState description="No se encontro el escenario solicitado dentro del experimento." />
    );
  }

  if (data.scenario.series.length === 0) {
    return <EmptyState description="El escenario no tiene corridas para visualizar." />;
  }

  return (
    <section>
      <p className="breadcrumb">
        <Link to="/">Inicio</Link> /{" "}
        <Link to={`/experiments/${encodeURIComponent(experimentId)}`}>{data.experimentTitle}</Link> /{" "}
        {data.scenario.scenario_name}
      </p>
      <ScenarioViewer
        educational={data.educational}
        scenario={data.scenario}
        triggerRuns={getTriggerRuns(data.scenario)}
      />
    </section>
  );
}
