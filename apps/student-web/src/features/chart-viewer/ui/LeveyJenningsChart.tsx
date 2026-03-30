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
import type { ScenarioLimits, ScenarioPoint } from "@/entities/scenario/model/scenario";
import { formatDecimal } from "@/shared/lib/format";

type ChartRow = {
  runIndex: number;
  value: number;
  isTrigger: boolean;
};

const COLORS = {
  line: "#2456A6",
  trigger: "#B94029",
  mean: "#153E7A",
  oneSigma: "#5673A6",
  twoSigma: "#C3892C",
  threeSigma: "#A43434",
};

export function LeveyJenningsChart({
  points,
  limits,
  triggerRuns,
}: {
  points: ScenarioPoint[];
  limits: ScenarioLimits;
  triggerRuns: number[];
}): JSX.Element {
  const triggerSet = new Set(triggerRuns);
  const data: ChartRow[] = points.map((point) => ({
    runIndex: point.run_index,
    value: point.value,
    isTrigger: triggerSet.has(point.run_index),
  }));

  return (
    <section className="content-section">
      <h3>Levey-Jennings (simplificado)</h3>
      <div className="chart-shell">
        <ResponsiveContainer height={340} width="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="#D6D9E0" strokeDasharray="3 3" />
            <XAxis dataKey="runIndex" label={{ value: "Corrida", position: "insideBottom", offset: -8 }} />
            <YAxis
              domain={["auto", "auto"]}
              label={{ value: "Valor", angle: -90, position: "insideLeft" }}
            />
            <Tooltip
              formatter={(value: number) => formatDecimal(value)}
              labelFormatter={(label: number) => `Run ${label}`}
            />
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
              name="Serie QC"
              stroke={COLORS.line}
              strokeWidth={2}
              type="monotone"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="chart-caption">
        Puntos en rojo indican primera corrida de activacion reportada por alguna regla.
      </p>
    </section>
  );
}
