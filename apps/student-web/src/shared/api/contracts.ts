import { z } from "zod";
import type {
  ExperimentIndexPayload,
  ExperimentManifest,
  ScenarioPayload,
} from "@/shared/types/webData";
import type {
  LessonEducation,
  ScenarioEducation,
} from "@/shared/types/educational";
import type { FlashcardStudyDeck } from "@/shared/types/flashcards";

export const experimentIndexSchema = z.object({
  experiments: z.array(
    z.object({
      id: z.string().min(1),
      title: z.string(),
      description: z.string(),
      manifest_path: z.string().min(1),
      scenario_count: z.number().int().nonnegative(),
    }),
  ),
});

export const experimentManifestSchema = z.object({
  id: z.string().min(1),
  title: z.string(),
  description: z.string(),
  config: z.object({
    mean: z.number(),
    sd: z.number(),
    n_runs: z.number().int().positive(),
    seed: z.number().int(),
    analyte: z.string().min(1),
  }),
  scenarios: z.array(
    z.object({
      id: z.string().min(1),
      scenario_key: z.string().min(1),
      path: z.string().min(1),
    }),
  ),
});

export const scenarioPayloadSchema = z.object({
  scenario_name: z.string().min(1),
  scenario_type: z.string().min(1),
  description: z.string(),
  parameters: z.record(z.unknown()),
  control_limits: z.object({
    mean: z.number(),
    plus_1s: z.number(),
    plus_2s: z.number(),
    plus_3s: z.number(),
    minus_1s: z.number(),
    minus_2s: z.number(),
    minus_3s: z.number(),
  }),
  series: z.array(
    z.object({
      run_index: z.number().int().positive(),
      value: z.number(),
      z_score: z.number(),
    }),
  ),
  rule_results: z.record(
    z.object({
      triggered: z.boolean(),
      first_trigger_run: z.number().int().positive().nullable(),
      false_alarm: z.boolean(),
    }),
  ),
  summary: z.object({
    analyte: z.string().min(1),
    n_runs: z.number().int().positive(),
    triggered_rule_count: z.number().int().nonnegative(),
    triggered_rules: z.array(z.string()),
  }),
});

export const scenarioEducationSchema = z.object({
  display_name: z.string(),
  short_description: z.string(),
  educational_message: z.string(),
  pattern_hint: z.string(),
  common_mistake: z.string(),
});

export const lessonEducationSchema = z.object({
  guiding_questions: z.array(z.string()),
  challenge_prompt: z.string(),
  reveal_text: z.string(),
});

export const scenarioEducationMapSchema = z.record(scenarioEducationSchema);
export const lessonEducationMapSchema = z.record(lessonEducationSchema);
export const flashcardStudyDeckSchema = z.object({
  deck_id: z.string().min(1),
  format_version: z.string().min(1),
  metadata: z.object({
    title: z.string().min(1),
    subtitle: z.string(),
    language: z.string().min(1),
    audience: z.string().min(1),
    description: z.string(),
    author: z.string().min(1),
    tags: z.array(z.string()),
    display_tags: z.array(z.string()),
    notes: z.string().nullable(),
  }),
  cards: z.array(
    z.object({
      id: z.string().min(1),
      card_type: z.string().min(1),
      card_type_label: z.string().min(1),
      sort_order: z.number().int().nullable(),
      tags: z.array(z.string()),
      display_tags: z.array(z.string()),
      front_html: z.string().min(1),
      back_html: z.string().min(1),
      front_source: z.string().min(1),
      back_source: z.string().min(1),
    }),
  ),
});

export function parseExperimentIndex(payload: unknown): ExperimentIndexPayload {
  return experimentIndexSchema.parse(payload);
}

export function parseExperimentManifest(payload: unknown): ExperimentManifest {
  return experimentManifestSchema.parse(payload);
}

export function parseScenarioPayload(payload: unknown): ScenarioPayload {
  return scenarioPayloadSchema.parse(payload);
}

export function parseScenarioEducationMap(payload: unknown): Record<string, ScenarioEducation> {
  return scenarioEducationMapSchema.parse(payload);
}

export function parseLessonEducationMap(payload: unknown): Record<string, LessonEducation> {
  return lessonEducationMapSchema.parse(payload);
}

export function parseFlashcardStudyDeck(payload: unknown): FlashcardStudyDeck {
  return flashcardStudyDeckSchema.parse(payload);
}
