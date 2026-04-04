import { getRuleResultEntries } from "@/entities/rule-result/model/ruleResult";
import { LeveyJenningsChart } from "@/features/chart-viewer/ui/LeveyJenningsChart";
import {
  translateAnalyte,
  translateScenarioDescription,
  translateScenarioType,
} from "@/shared/config/localization";
import { formatDecimal } from "@/shared/lib/format";
import { StatGrid } from "@/shared/ui/StatGrid";
import type { EducationalContent } from "@/shared/types/educational";
import type { ScenarioDetail } from "@/entities/scenario/model/scenario";

export function ScenarioViewer({
  scenario,
  triggerRuns,
  educational,
}: {
  scenario: ScenarioDetail;
  triggerRuns: number[];
  educational: EducationalContent | null;
}): JSX.Element {
  const ruleEntries = getRuleResultEntries(scenario);

  return (
    <div className="scenario-layout">
      <section className="content-section">
        <header className="section-header">
          <h2>{translateScenarioType(scenario.scenario_type)}</h2>
          <p>{translateScenarioDescription(scenario.description)}</p>
        </header>

        <StatGrid
          items={[
            { label: "Analito", value: translateAnalyte(scenario.summary.analyte) },
            { label: "Ejecuciones", value: scenario.summary.n_runs },
            {
              label: "Reglas activadas",
              value: `${scenario.summary.triggered_rule_count}`,
            },
            {
              label: "Media",
              value: formatDecimal(scenario.control_limits.mean),
            },
          ]}
        />
        <p className="soft-text">
          Reglas en summary:{" "}
          {scenario.summary.triggered_rules.length > 0
            ? scenario.summary.triggered_rules.join(", ")
            : "Ninguna"}
        </p>
      </section>

      <LeveyJenningsChart
        limits={scenario.control_limits}
        points={scenario.series}
        ruleResults={scenario.rule_results}
        triggerRuns={triggerRuns}
      />

      <section className="content-section">
        <h3>Parametros del escenario</h3>
        {Object.keys(scenario.parameters).length === 0 ? (
          <p className="soft-text">No hay parametros adicionales para este escenario.</p>
        ) : (
          <dl className="key-value-grid">
            {Object.entries(scenario.parameters).map(([key, value]) => (
              <div className="key-value-item" key={key}>
                <dt>{key}</dt>
                <dd>{String(value)}</dd>
              </div>
            ))}
          </dl>
        )}
      </section>

      <section className="content-section">
        <h3>Resultados de reglas</h3>
        <div className="table-scroll">
          <table className="rule-table">
            <thead>
              <tr>
                <th>Regla</th>
                <th>Activada</th>
                <th>Primera activación</th>
                <th>Falsa alarma</th>
              </tr>
            </thead>
            <tbody>
              {ruleEntries.map(([ruleName, result]) => (
                <tr key={ruleName}>
                  <td>{ruleName}</td>
                  <td>{result.triggered ? "Sí" : "No"}</td>
                  <td>{result.first_trigger_run ?? "-"}</td>
                  <td>{result.false_alarm ? "Sí" : "No"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {(educational?.scenario || educational?.lesson) && (
        <section className="content-section content-section-educational">
          <h3>Contexto educativo</h3>
          {educational.scenario && (
            <div className="educational-block">
              <p className="educational-highlight">{educational.scenario.short_description}</p>
              <p>{educational.scenario.educational_message}</p>
              <p>
                <strong>Patron esperado:</strong> {educational.scenario.pattern_hint}
              </p>
              <p>
                <strong>Error comun:</strong> {educational.scenario.common_mistake}
              </p>
            </div>
          )}
          {educational.lesson && (
            <div className="educational-block">
              <h4>Preguntas guia</h4>
              <ul className="flat-list">
                {educational.lesson.guiding_questions.map((question) => (
                  <li key={question}>{question}</li>
                ))}
              </ul>
              <p>
                <strong>Desafio:</strong> {educational.lesson.challenge_prompt}
              </p>
              <p>
                <strong>Pista docente:</strong> {educational.lesson.reveal_text}
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
