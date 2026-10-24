# file-integrity-monitor

A Python tool that takes a SHA-256 fingerprint of every file in a directory,
saves it as a baseline, and later tells you exactly what was added, changed or
deleted. It exits with a non-zero status when anything changed, so it drops
straight into cron or CI as an alert.

Part of the blue-team work around my
[purple-team-journey](https://github.com/Siddique-12300983/purple-team-journey)
lab.

## Why it matters

File integrity monitoring is a basic detection control, and it is one of the
things a SIEM like Wazuh does for you. The idea is simple: attackers change
files. They drop a web shell, edit a config, replace a binary, or add a cron
job. If you know the good state of a directory, any change stands out. Watching
`/etc`, a web root, or a set of binaries this way catches tampering that nothing
else might notice. This is a small, dependency-free version of that idea, which
also made it a good way to learn how the control actually works.

## How it works

1. `init` walks the directory, hashes every file with SHA-256, and writes a JSON
   baseline (hash, size and mtime per file, plus the exclude patterns used).
2. `check` rescans the same directory and compares it to the baseline.
3. It prints a report of added, modified and deleted files and exits `1` if
   there were any, `0` if the directory is unchanged.

Paths in the baseline are stored relative to the root with forward slashes, so a
baseline is portable.

## Install

Python 3.9 or newer, standard library only.

```bash
git clone https://github.com/Siddique-12300983/file-integrity-monitor.git
cd file-integrity-monitor
```

Optionally install the `fim` command:

```bash
pip install .
```

## Usage

```bash
# Create a baseline, skipping log files
python -m fim init /etc -b etc-baseline.json -e '*.log'

# Later, check for changes
python -m fim check /etc -b etc-baseline.json

# Machine-readable output
python -m fim check /etc -b etc-baseline.json --json
```

Exclude patterns are glob patterns (repeatable with `-e`). They match either the
full relative path or the file's name, and a bare name like `.git` skips the
whole directory. The excludes from `init` are stored in the baseline and reused
on `check`, so the two always scan the same set of files.

Exit codes: `0` no changes, `1` changes detected, `2` error (for example a
missing baseline).

### In cron

```cron
# Email the output if anything under /etc changed overnight
30 2 * * * /usr/bin/python3 -m fim check /etc -b /var/lib/fim/etc.json || echo "integrity change on $(hostname)"
```

## Example

The repo includes a small `sample-tree/` so you can try it:

```
$ python -m fim init sample-tree -b demo.json -e '*.log'
baseline written to demo.json (3 files)

$ echo "max_connections = 500" >> sample-tree/config/app.conf
$ python -m fim check sample-tree -b demo.json
File integrity check
========================================
root            : /path/to/sample-tree
files scanned   : 3
result          : 1 change(s) detected

MODIFIED (1)
  ~ config/app.conf
```

(The `scan.log` file in the sample tree is there to show the `*.log` exclude
working: it is skipped, so changing it does not raise an alert.)

## Running the tests

```bash
pip install pytest
pytest
```

The suite covers the scanner (including excludes and a known SHA-256 value), the
added/modified/deleted diff, and the CLI init-then-check flow with exit codes.

## Layout

```
fim/
  scanner.py    walk and hash files, apply excludes
  baseline.py   read and write the JSON baseline
  diff.py       compare baseline vs current scan
  report.py     the change report
  cli.py        init and check subcommands
sample-tree/    a small directory to try it on
tests/          pytest suite
```

## License

MIT. See [LICENSE](LICENSE).
