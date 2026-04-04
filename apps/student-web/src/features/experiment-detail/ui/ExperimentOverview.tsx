import { Link } from "react-router-dom";
import type { ExperimentDetail } from "@/entities/experiment/model/experiment";
import {
  translateAnalyte,
  translateExperimentTitle,
  translateScenarioId,
  translateScenarioType,
} from "@/shared/config/localization";
import { StatGrid } from "@/shared/ui/StatGrid";
import { formatDecimal } from "@/shared/lib/format";

export function ExperimentOverview({ experiment }: { experiment: ExperimentDetail }): JSX.Element {
  return (
    <section className="content-section">
      <header className="section-header">
        <h2>{translateExperimentTitle(experiment.title)}</h2>
        <p>{experiment.description || "Sin descripcion."}</p>
      </header>

      <StatGrid
        items={[
          { label: "Analito", value: translateAnalyte(experiment.config.analyte) },
          { label: "Media", value: formatDecimal(experiment.config.mean) },
          { label: "SD", value: formatDecimal(experiment.config.sd) },
          { label: "Ejecuciones", value: experiment.config.n_runs },
          { label: "Semilla", value: experiment.config.seed },
        ]}
      />

      <h3>Escenarios</h3>
      <div className="card-grid">
        {experiment.scenarios.map((scenario) => (
          <article className="info-card" key={scenario.id}>
            <header>
              <h4>{translateScenarioId(scenario.id)}</h4>
              <p>Tipo: {translateScenarioType(scenario.scenario_key)}</p>
            </header>
            <Link
              className="button-primary"
              to={`/experiments/${encodeURIComponent(experiment.id)}/scenarios/${encodeURIComponent(
                scenario.id,
              )}`}
            >
              Ver escenario
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
