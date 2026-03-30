import { buildTriggerDetailsByRun } from "@/features/chart-viewer/model/triggerTooltip";

describe("buildTriggerDetailsByRun", () => {
  it("maps triggered rules by first run and sorts by severity", () => {
    const detailsByRun = buildTriggerDetailsByRun({
      "1_2s": {
        triggered: true,
        first_trigger_run: 7,
        false_alarm: false,
      },
      "2_2s": {
        triggered: true,
        first_trigger_run: 7,
        false_alarm: false,
      },
      "1_3s": {
        triggered: true,
        first_trigger_run: 5,
        false_alarm: false,
      },
    });

    expect(detailsByRun.get(5)).toEqual([
      {
        ruleName: "1_3s",
        displayName: "1 3s",
        severity: "rejection",
        reason: "Un resultado supero +/-3DE; la corrida debe considerarse fuera de control.",
      },
    ]);

    expect(detailsByRun.get(7)).toEqual([
      {
        ruleName: "2_2s",
        displayName: "2 2s",
        severity: "rejection",
        reason: "Dos resultados seguidos superaron +/-2DE del mismo lado; sugiere sesgo sistematico.",
      },
      {
        ruleName: "1_2s",
        displayName: "1 2s",
        severity: "warning",
        reason: "Un resultado supero +/-2DE; es una alerta para vigilar la serie.",
      },
    ]);
  });

  it("ignores rules without trigger run and uses fallback for unknown rules", () => {
    const detailsByRun = buildTriggerDetailsByRun({
      custom_rule: {
        triggered: true,
        first_trigger_run: 3,
        false_alarm: false,
      },
      "1_2s": {
        triggered: false,
        first_trigger_run: 2,
        false_alarm: false,
      },
      "1_3s": {
        triggered: true,
        first_trigger_run: null,
        false_alarm: false,
      },
    });

    expect(detailsByRun.get(2)).toBeUndefined();
    expect(detailsByRun.get(3)).toEqual([
      {
        ruleName: "custom_rule",
        displayName: "custom_rule",
        severity: "rejection",
        reason: "Se detecto una senal fuera de control; revise causa probable y tendencia.",
      },
    ]);
  });
});
