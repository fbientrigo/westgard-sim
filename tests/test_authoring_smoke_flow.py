from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_smoke_authoring_flow_script() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "smoke_authoring_flow.py"
    _ = subprocess.run([sys.executable, str(script_path)], check=True)

    generated_index = repo_root / "outputs" / "smoke" / "web_data" / "index.json"
    assert generated_index.exists()
