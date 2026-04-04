import type { RuleResult } from "@/shared/types/webData";

export type RuleSeverity = "warning" | "rejection";

export type RulePresentation = {
  displayName: string;
  severity: RuleSeverity;
  reason: string;
};

export type TriggerDetail = {
  ruleName: string;
  displayName: string;
  severity: RuleSeverity;
  reason: string;
};

const RULE_PRESENTATION: Record<string, RulePresentation> = {
  "1_2s": {
    displayName: "1 2s",
    severity: "warning",
    reason: "Un resultado supero +/-2DE; es una alerta para vigilar la serie.",
  },
  "1_3s": {
    displayName: "1 3s",
    severity: "rejection",
    reason: "Un resultado supero +/-3DE; la ejecucion debe considerarse fuera de control.",
  },
  "2_2s": {
    displayName: "2 2s",
    severity: "rejection",
    reason: "Dos resultados seguidos superaron +/-2DE del mismo lado; sugiere sesgo sistematico.",
  },
};

function getRulePresentation(ruleName: string): RulePresentation {
  return (
    RULE_PRESENTATION[ruleName] ?? {
      displayName: ruleName,
      severity: "rejection",
      reason: "Se detecto una senal fuera de control; revise causa probable y tendencia.",
    }
  );
}

export function buildTriggerDetailsByRun(
  ruleResults: Record<string, RuleResult>,
): Map<number, TriggerDetail[]> {
  const detailsByRun = new Map<number, TriggerDetail[]>();

  Object.entries(ruleResults).forEach(([ruleName, result]) => {
    if (!result.triggered || typeof result.first_trigger_run !== "number") {
      return;
    }

    const presentation = getRulePresentation(ruleName);
    const currentDetails = detailsByRun.get(result.first_trigger_run) ?? [];

    currentDetails.push({
      ruleName,
      displayName: presentation.displayName,
      severity: presentation.severity,
      reason: presentation.reason,
    });

    detailsByRun.set(result.first_trigger_run, currentDetails);
  });

  detailsByRun.forEach((details, runIndex) => {
    const sortedDetails = [...details].sort((left, right) => {
      if (left.severity === right.severity) {
        return left.ruleName.localeCompare(right.ruleName);
      }

      return left.severity === "rejection" ? -1 : 1;
    });

    detailsByRun.set(runIndex, sortedDetails);
  });

  return detailsByRun;
}
