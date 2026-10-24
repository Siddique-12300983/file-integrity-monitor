"""Walk a directory and hash every file with SHA-256."""

from __future__ import annotations

import fnmatch
import hashlib
import os
from typing import Dict, List

_CHUNK = 65536


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_excluded(relpath: str, excludes: List[str]) -> bool:
    """A relative path is excluded if it, or its basename, matches a pattern."""
    base = os.path.basename(relpath)
    for pattern in excludes:
        if fnmatch.fnmatch(relpath, pattern) or fnmatch.fnmatch(base, pattern):
            return True
        # Treat a directory pattern like "logs" or ".git" as "everything under it".
        if relpath == pattern or relpath.startswith(pattern.rstrip("/") + "/"):
            return True
    return False


def scan(root: str, excludes: List[str] = None) -> Dict[str, dict]:
    """Return {relative_path: {sha256, size, mtime}} for every file under root.

    Paths are relative to root and use forward slashes, so a baseline is
    portable between machines.
    """
    excludes = excludes or []
    root = os.path.abspath(root)
    result: Dict[str, dict] = {}

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        rel_dir = "" if rel_dir == "." else rel_dir.replace(os.sep, "/")

        # Prune excluded directories so we do not descend into them.
        kept = []
        for d in dirnames:
            rel = f"{rel_dir}/{d}" if rel_dir else d
            if not _is_excluded(rel, excludes):
                kept.append(d)
        dirnames[:] = kept

        for name in filenames:
            rel = f"{rel_dir}/{name}" if rel_dir else name
            if _is_excluded(rel, excludes):
                continue
            full = os.path.join(dirpath, name)
            if not os.path.isfile(full) or os.path.islink(full):
                continue
            try:
                stat = os.stat(full)
                result[rel] = {
                    "sha256": sha256_file(full),
                    "size": stat.st_size,
                    "mtime": round(stat.st_mtime, 3),
                }
            except OSError:
                # Unreadable file: record it so its disappearance is still noticed.
                result[rel] = {"sha256": None, "size": None, "mtime": None}
    return result
