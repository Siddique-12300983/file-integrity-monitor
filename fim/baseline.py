"""Read and write the JSON baseline file."""

from __future__ import annotations

import datetime
import json
import os
from typing import Dict, List

BASELINE_VERSION = 1


def build(root: str, files: Dict[str, dict], excludes: List[str]) -> dict:
    return {
        "version": BASELINE_VERSION,
        "algorithm": "sha256",
        "root": os.path.abspath(root),
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "excludes": list(excludes),
        "files": files,
    }


def save(baseline: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(baseline, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if "files" not in data:
        raise ValueError(f"{path} does not look like a baseline (no 'files' key)")
    return data
