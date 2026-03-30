import fs from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");

const datasetSource = path.resolve(repoRoot, "outputs/web_data");
const datasetTarget = path.resolve(repoRoot, "apps/student-web/public/web_data");
const educationalTarget = path.resolve(repoRoot, "apps/student-web/public/educational");
const scenariosSource = path.resolve(repoRoot, "content/scenarios.json");
const lessonsSource = path.resolve(repoRoot, "content/lessons.json");

const args = new Set(process.argv.slice(2));
const cleanTarget = args.has("--clean-target");
const skipEducational = args.has("--skip-educational");

async function ensureDataset() {
  if (!existsSync(datasetSource)) {
    throw new Error(
      `Dataset source not found: ${datasetSource}. Run westgard_ops.ps1 -Action release first.`,
    );
  }

  if (cleanTarget) {
    await fs.rm(datasetTarget, { recursive: true, force: true });
  }

  await fs.mkdir(path.dirname(datasetTarget), { recursive: true });
  await fs.cp(datasetSource, datasetTarget, { recursive: true, force: true });
  console.log(`[sync] dataset copied: ${datasetSource} -> ${datasetTarget}`);
}

async function syncEducational() {
  if (skipEducational) {
    console.log("[sync] educational copy skipped");
    return;
  }

  if (cleanTarget) {
    await fs.rm(educationalTarget, { recursive: true, force: true });
  }

  await fs.mkdir(educationalTarget, { recursive: true });
  let copiedScenarios = false;
  let copiedLessons = false;

  if (existsSync(scenariosSource)) {
    await fs.copyFile(scenariosSource, path.resolve(educationalTarget, "scenarios.json"));
    copiedScenarios = true;
  }
  if (existsSync(lessonsSource)) {
    await fs.copyFile(lessonsSource, path.resolve(educationalTarget, "lessons.json"));
    copiedLessons = true;
  }

  console.log(
    `[sync] educational files: scenarios=${copiedScenarios ? "ok" : "missing"}, lessons=${copiedLessons ? "ok" : "missing"}`,
  );
}

await ensureDataset();
await syncEducational();
