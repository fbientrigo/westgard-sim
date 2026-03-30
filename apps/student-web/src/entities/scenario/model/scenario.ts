import type {
  ControlLimits,
  ManifestScenarioRecord,
  ScenarioPayload,
  ScenarioSeriesPoint,
  ScenarioSummary,
} from "@/shared/types/webData";

export type ScenarioManifestItem = ManifestScenarioRecord;
export type ScenarioDetail = ScenarioPayload;
export type ScenarioPoint = ScenarioSeriesPoint;
export type ScenarioLimits = ControlLimits;
export type ScenarioStats = ScenarioSummary;
