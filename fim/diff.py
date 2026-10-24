"""Compare a baseline against a fresh scan."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Changes:
    added: List[str] = field(default_factory=list)
    modified: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.modified) + len(self.deleted)

    def any(self) -> bool:
        return self.total > 0


def compare(baseline_files: Dict[str, dict], current_files: Dict[str, dict]) -> Changes:
    base_keys = set(baseline_files)
    curr_keys = set(current_files)

    added = sorted(curr_keys - base_keys)
    deleted = sorted(base_keys - curr_keys)
    modified = sorted(
        path for path in (base_keys & curr_keys)
        if baseline_files[path].get("sha256") != current_files[path].get("sha256")
    )
    return Changes(added=added, modified=modified, deleted=deleted)
