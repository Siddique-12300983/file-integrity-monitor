"""Command-line interface: init a baseline, then check against it."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, baseline as baseline_mod
from .diff import compare
from .report import build_report
from .scanner import scan


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fim",
        description="Build a SHA-256 baseline of a directory and detect added, modified and deleted files.",
    )
    p.add_argument("--version", action="version", version=f"fim {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("directory", help="directory to scan")
    common.add_argument("-b", "--baseline", default="baseline.json",
                        help="baseline file path (default: baseline.json)")
    common.add_argument("-e", "--exclude", action="append", default=[], metavar="PATTERN",
                        help="glob pattern to skip (repeatable), e.g. -e '*.log' -e '.git'")

    sub.add_parser("init", parents=[common], help="create a baseline")
    chk = sub.add_parser("check", parents=[common], help="check a directory against its baseline")
    chk.add_argument("--json", action="store_true", help="print the changes as JSON")
    return p


def cmd_init(args) -> int:
    files = scan(args.directory, args.exclude)
    data = baseline_mod.build(args.directory, files, args.exclude)
    baseline_mod.save(data, args.baseline)
    print(f"baseline written to {args.baseline} ({len(files)} files)")
    return 0


def cmd_check(args) -> int:
    try:
        data = baseline_mod.load(args.baseline)
    except (OSError, ValueError) as exc:
        print(f"error: cannot read baseline: {exc}", file=sys.stderr)
        return 2

    # Prefer the excludes stored in the baseline so a check matches the init.
    excludes = data.get("excludes") or args.exclude
    current = scan(args.directory, excludes)
    changes = compare(data["files"], current)

    if args.json:
        print(json.dumps({
            "added": changes.added,
            "modified": changes.modified,
            "deleted": changes.deleted,
        }, indent=2))
    else:
        print(build_report(data.get("root", args.directory), changes, len(current)))

    # Non-zero exit when anything changed, so cron and CI can alert on it.
    return 1 if changes.any() else 0


def run(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        return cmd_init(args)
    if args.command == "check":
        return cmd_check(args)
    return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
