import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { NameType, ValueType } from "recharts/types/component/DefaultTooltipContent";
import type { TooltipProps } from "recharts";
import type { ScenarioLimits, ScenarioPoint } from "@/entities/scenario/model/scenario";
import { buildTriggerDetailsByRun, type TriggerDetail } from "@/features/chart-viewer/model/triggerTooltip";
import { formatDecimal } from "@/shared/lib/format";
import type { RuleResult } from "@/shared/types/webData";

type ChartRow = {
  runIndex: number;
  value: number;
  isTrigger: boolean;
  triggerDetails: TriggerDetail[];
};

const COLORS = {
  line: "#2456A6",
  trigger: "#B94029",
  mean: "#153E7A",
  oneSigma: "#5673A6",
  twoSigma: "#C3892C",
  threeSigma: "#A43434",
  warning: "#C3892C",
  rejection: "#A43434",
};

function TriggerTooltip({
  active,
  label,
  payload,
}: TooltipProps<ValueType, NameType>): JSX.Element | null {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  const pointPayload = payload[0]?.payload as ChartRow | undefined;
  if (!pointPayload) {
    return null;
  }

  return (
    <div className="chart-tooltip" role="status">
      <p className="chart-tooltip-title">Ejecucion {label}</p>
      <p className="chart-tooltip-value">
        Valor: <strong>{formatDecimal(pointPayload.value)}</strong>
      </p>
      {pointPayload.triggerDetails.length > 0 && (
        <div className="chart-tooltip-trigger-block">
          <p className="chart-tooltip-trigger-heading">Trigger detectado</p>
          {pointPayload.triggerDetails.map((detail) => (
            <article className="chart-tooltip-rule" key={detail.ruleName}>
              <p className="chart-tooltip-rule-title">
                <span
                  aria-hidden="true"
                  className={`chart-tooltip-dot chart-tooltip-dot-${detail.severity}`}
                  style={{
                    backgroundColor:
                      detail.severity === "warning" ? COLORS.warning : COLORS.rejection,
                  }}
                />
                Regla {detail.displayName}
              </p>
              <p className="chart-tooltip-rule-reason">{detail.reason}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export function LeveyJenningsChart({
  points,
  limits,
  triggerRuns,
  ruleResults,
}: {
  points: ScenarioPoint[];
  limits: ScenarioLimits;
  triggerRuns: number[];
  ruleResults: Record<string, RuleResult>;
}): JSX.Element {
  const triggerSet = new Set(triggerRuns);
  const triggerDetailsByRun = buildTriggerDetailsByRun(ruleResults);
  const data: ChartRow[] = points.map((point) => ({
    runIndex: point.run_index,
    value: point.value,
    triggerDetails: triggerDetailsByRun.get(point.run_index) ?? [],
    isTrigger:
      triggerSet.has(point.run_index) || (triggerDetailsByRun.get(point.run_index)?.length ?? 0) > 0,
  }));

  return (
    <section className="content-section">
      <h3>Gráfico de Levey-Jennings (simplificado)</h3>
      <div className="chart-shell">
        <ResponsiveContainer height={340} width="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#D6D9E0" strokeDasharray="3 3" />
            <XAxis dataKey="runIndex" label={{ value: "Ejecucion", position: "insideBottom", offset: -8 }} />
            <YAxis
              domain={["auto", "auto"]}
              label={{ value: "Valor", angle: -90, position: "insideLeft" }}
            />
            <Tooltip content={<TriggerTooltip />} />
            <Legend />
            <ReferenceLine label="Media" stroke={COLORS.mean} strokeWidth={2} y={limits.mean} />
            <ReferenceLine stroke={COLORS.oneSigma} strokeDasharray="6 3" y={limits.plus_1s} />
            <ReferenceLine stroke={COLORS.oneSigma} strokeDasharray="6 3" y={limits.minus_1s} />
            <ReferenceLine stroke={COLORS.twoSigma} strokeDasharray="4 3" y={limits.plus_2s} />
            <ReferenceLine stroke={COLORS.twoSigma} strokeDasharray="4 3" y={limits.minus_2s} />
            <ReferenceLine stroke={COLORS.threeSigma} strokeDasharray="2 3" y={limits.plus_3s} />
            <ReferenceLine stroke={COLORS.threeSigma} strokeDasharray="2 3" y={limits.minus_3s} />
            <Line
              dataKey="value"
              dot={(props) => {
                const isTrigger = Boolean(props.payload?.isTrigger);
                return (
                  <circle
                    cx={props.cx}
                    cy={props.cy}
                    fill={isTrigger ? COLORS.trigger : COLORS.line}
                    r={isTrigger ? 5 : 3}
                    stroke={isTrigger ? "#FFFFFF" : "transparent"}
                    strokeWidth={isTrigger ? 2 : 0}
                  />
                );
              }}
              name="Serie de control"
              stroke={COLORS.line}
              strokeWidth={2}
              type="monotone"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="chart-caption">
        Puntos en rojo indican la primera ejecucion de activacion reportada por alguna regla.
      </p>
    </section>
  );
}
