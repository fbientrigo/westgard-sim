import { ZodError } from "zod";
import {
  parseFlashcardStudyDeck,
  parseExperimentIndex,
  parseExperimentManifest,
  parseScenarioPayload,
} from "@/shared/api/contracts";
import { fetchJson } from "@/shared/api/http";
import { buildAssetPath } from "@/shared/config/paths";
import type {
  ExperimentIndexPayload,
  ExperimentManifest,
  ScenarioPayload,
} from "@/shared/types/webData";
import type { FlashcardStudyDeck } from "@/shared/types/flashcards";

const DATA_ROOT = "web_data";
const FLASHCARD_ROOT = "flashcards";

function validationError(path: string, error: unknown): Error {
  if (!(error instanceof ZodError)) {
    return error as Error;
  }
  const details = error.issues
    .map((issue) => `${issue.path.join(".") || "root"}: ${issue.message}`)
    .join("; ");
  return new Error(`Contrato JSON invalido en ${path}. ${details}`);
}

export async function listExperiments(): Promise<ExperimentIndexPayload> {
  const path = buildAssetPath(`${DATA_ROOT}/index.json`);
  try {
    const payload = await fetchJson(path);
    return parseExperimentIndex(payload);
  } catch (error) {
    throw validationError(path, error);
  }
}

export async function getExperimentManifest(manifestPath: string): Promise<ExperimentManifest> {
  const path = buildAssetPath(`${DATA_ROOT}/${manifestPath}`);
  try {
    const payload = await fetchJson(path);
    return parseExperimentManifest(payload);
  } catch (error) {
    throw validationError(path, error);
  }
}

export async function getScenarioPayload(payloadPath: string): Promise<ScenarioPayload> {
  const path = buildAssetPath(`${DATA_ROOT}/${payloadPath}`);
  try {
    const payload = await fetchJson(path);
    return parseScenarioPayload(payload);
  } catch (error) {
    throw validationError(path, error);
  }
}

export async function getFlashcardStudyDeck(deckId: string): Promise<FlashcardStudyDeck> {
  const path = buildAssetPath(`${FLASHCARD_ROOT}/${deckId}/study_deck.json`);
  try {
    const payload = await fetchJson(path);
    return parseFlashcardStudyDeck(payload);
  } catch (error) {
    throw validationError(path, error);
  }
}
