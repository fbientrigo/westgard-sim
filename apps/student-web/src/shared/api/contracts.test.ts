import {
  parseFlashcardStudyDeck,
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

  it("accepts valid flashcard study deck payload", () => {
    const parsed = parseFlashcardStudyDeck({
      deck_id: "westgard_qc_basics",
      format_version: "1.0",
      metadata: {
        title: "Deck",
        subtitle: "Sub",
        language: "es",
        audience: "Estudiantes",
        description: "Desc",
        author: "Westgard",
        tags: ["westgard"],
        display_tags: ["Westgard"],
        notes: null,
      },
      cards: [
        {
          id: "card_1",
          card_type: "concept",
          card_type_label: "Concepto",
          sort_order: 1,
          tags: ["fundamentos"],
          display_tags: ["Fundamentos"],
          front_html: "<p>uno</p>",
          back_html: "<p>dos</p>",
          front_source: "uno",
          back_source: "dos",
        },
      ],
    });
    expect(parsed.cards[0].card_type_label).toBe("Concepto");
  });
});
