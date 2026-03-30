import {
  parseExperimentIndex,
  parseExperimentManifest,
  parseScenarioPayload,
} from "@/shared/api/contracts";

describe("contracts parser", () => {
  it("accepts valid experiment index payload", () => {
    const parsed = parseExperimentIndex({
      experiments: [
        {
          id: "exp_1",
          title: "Exp 1",
          description: "Desc",
          manifest_path: "experiments/exp_1/manifest.json",
          scenario_count: 2,
        },
      ],
    });
    expect(parsed.experiments[0].id).toBe("exp_1");
  });

  it("accepts valid manifest payload", () => {
    const parsed = parseExperimentManifest({
      id: "exp_1",
      title: "Exp 1",
      description: "Desc",
      config: { mean: 100, sd: 2, n_runs: 30, seed: 42, analyte: "Glucose" },
      scenarios: [
        {
          id: "bias_a",
          scenario_key: "bias",
          path: "experiments/exp_1/bias_a.json",
        },
      ],
    });
    expect(parsed.scenarios).toHaveLength(1);
  });

  it("rejects scenario payload without required keys", () => {
    expect(() => parseScenarioPayload({ scenario_name: "only name" })).toThrow();
  });
});
