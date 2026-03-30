import type { RuleResult, ScenarioPayload } from "@/shared/types/webData";

export type RuleResultEntry = [ruleName: string, result: RuleResult];

export function getRuleResultEntries(payload: ScenarioPayload): RuleResultEntry[] {
  return Object.entries(payload.rule_results).sort(([left], [right]) =>
    left.localeCompare(right),
  );
}

export function getTriggerRuns(payload: ScenarioPayload): number[] {
  return Object.values(payload.rule_results)
    .map((result) => result.first_trigger_run)
    .filter((run): run is number => typeof run === "number")
    .sort((left, right) => left - right);
}
