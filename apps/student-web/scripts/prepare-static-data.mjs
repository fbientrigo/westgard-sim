import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: repoRoot,
    stdio: "inherit",
    ...options,
  });

  if (result.status !== 0) {
    throw new Error(`Command failed: ${command} ${args.join(" ")}`);
  }
}

const python = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");

run(python, [
  "scripts/export_web_data.py",
  "--catalog",
  "content/experiment_catalog.json",
  "--output-dir",
  "outputs/web_data",
]);

run(python, [
  "scripts/export_flashcards.py",
  "--deck",
  "content/flashcards/westgard_qc_basics.deck.json",
  "--output-dir",
  "outputs/flashcards/westgard_qc_basics",
]);

run(process.execPath, ["apps/student-web/scripts/run-sync.mjs", "--clean-target"]);
