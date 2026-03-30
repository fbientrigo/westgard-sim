export type ExperimentIndexRecord = {
  id: string;
  title: string;
  description: string;
  manifest_path: string;
  scenario_count: number;
};

export type ExperimentIndexPayload = {
  experiments: ExperimentIndexRecord[];
};

export type ExperimentConfig = {
  mean: number;
  sd: number;
  n_runs: number;
  seed: number;
  analyte: string;
};

export type ManifestScenarioRecord = {
  id: string;
  scenario_key: string;
  path: string;
};

export type ExperimentManifest = {
  id: string;
  title: string;
  description: string;
  config: ExperimentConfig;
  scenarios: ManifestScenarioRecord[];
};

export type ScenarioSeriesPoint = {
  run_index: number;
  value: number;
  z_score: number;
};

export type ControlLimits = {
  mean: number;
  plus_1s: number;
  plus_2s: number;
  plus_3s: number;
  minus_1s: number;
  minus_2s: number;
  minus_3s: number;
};

export type RuleResult = {
  triggered: boolean;
  first_trigger_run: number | null;
  false_alarm: boolean;
};

export type ScenarioSummary = {
  analyte: string;
  n_runs: number;
  triggered_rule_count: number;
  triggered_rules: string[];
};

export type ScenarioPayload = {
  scenario_name: string;
  scenario_type: string;
  description: string;
  parameters: Record<string, unknown>;
  control_limits: ControlLimits;
  series: ScenarioSeriesPoint[];
  rule_results: Record<string, RuleResult>;
  summary: ScenarioSummary;
};
