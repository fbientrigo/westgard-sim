import { Link } from "react-router-dom";
import type { ExperimentListItem } from "@/entities/experiment/model/experiment";

export function ExperimentList({
  experiments,
}: {
  experiments: ExperimentListItem[];
}): JSX.Element {
  return (
    <section className="content-section">
      <h2>Experimentos disponibles</h2>
      <div className="card-grid">
        {experiments.map((experiment) => (
          <article className="info-card" key={experiment.id}>
            <header>
              <h3>{experiment.title}</h3>
              <p>{experiment.description || "Sin descripcion."}</p>
            </header>
            <div className="card-meta">
              <span>{experiment.scenario_count} escenarios</span>
              <Link
                className="button-primary"
                to={`/experiments/${encodeURIComponent(experiment.id)}`}
              >
                Abrir experimento
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
