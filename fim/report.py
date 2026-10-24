"""Format a change report for the terminal."""

from __future__ import annotations

from .diff import Changes


def build_report(root: str, changes: Changes, scanned: int) -> str:
    lines = ["File integrity check", "=" * 40, f"root            : {root}",
             f"files scanned   : {scanned}"]
    if not changes.any():
        lines.append("result          : OK, no changes since baseline")
        return "\n".join(lines)

    lines.append(f"result          : {changes.total} change(s) detected")
    if changes.added:
        lines.append(f"\nADDED ({len(changes.added)})")
        lines += [f"  + {p}" for p in changes.added]
    if changes.modified:
        lines.append(f"\nMODIFIED ({len(changes.modified)})")
        lines += [f"  ~ {p}" for p in changes.modified]
    if changes.deleted:
        lines.append(f"\nDELETED ({len(changes.deleted)})")
        lines += [f"  - {p}" for p in changes.deleted]
    return "\n".join(lines)
