import {
  parseLessonEducationMap,
  parseScenarioEducationMap,
} from "@/shared/api/contracts";
import { fetchJson } from "@/shared/api/http";
import { buildAssetPath } from "@/shared/config/paths";
import type { EducationalContent } from "@/shared/types/educational";

type CacheShape = {
  scenarios: Record<string, EducationalContent["scenario"]> | null;
  lessons: Record<string, EducationalContent["lesson"]> | null;
};

const cache: CacheShape = {
  scenarios: null,
  lessons: null,
};

async function loadScenarioMap(): Promise<Record<string, EducationalContent["scenario"]>> {
  if (cache.scenarios) {
    return cache.scenarios;
  }
  const path = buildAssetPath("educational/scenarios.json");
  const payload = await fetchJson(path);
  const parsed = parseScenarioEducationMap(payload);
  cache.scenarios = parsed;
  return parsed;
}

async function loadLessonMap(): Promise<Record<string, EducationalContent["lesson"]>> {
  if (cache.lessons) {
    return cache.lessons;
  }
  const path = buildAssetPath("educational/lessons.json");
  const payload = await fetchJson(path);
  const parsed = parseLessonEducationMap(payload);
  cache.lessons = parsed;
  return parsed;
}

export async function getEducationalContent(
  scenarioType: string,
): Promise<EducationalContent | null> {
  try {
    const [scenarios, lessons] = await Promise.all([loadScenarioMap(), loadLessonMap()]);
    const scenario = scenarios[scenarioType];
    const lesson = lessons[scenarioType];
    if (!scenario && !lesson) {
      return null;
    }
    return { scenario, lesson };
  } catch {
    return null;
  }
}
