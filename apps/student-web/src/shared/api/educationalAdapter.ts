import { getEducationalContentEs } from "@/shared/config/localization";
import type { EducationalContent } from "@/shared/types/educational";

export async function getEducationalContent(
  scenarioType: string,
): Promise<EducationalContent | null> {
  return getEducationalContentEs(scenarioType);
}
