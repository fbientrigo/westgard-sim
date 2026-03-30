from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Iterator
from uuid import uuid4

import pytest


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture
def tmp_path() -> Iterator[Path]:
    """Use a repo-local tmp directory to avoid host TEMP permission issues."""
    root = ROOT_DIR / ".pytest_local_tmp"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"case_{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
