import os

from fim import cli


def _tree(root):
    os.makedirs(os.path.join(root, "config"), exist_ok=True)
    with open(os.path.join(root, "config", "app.conf"), "w") as fh:
        fh.write("setting=1\n")
    with open(os.path.join(root, "notes.log"), "w") as fh:
        fh.write("ignore me\n")


def test_init_then_clean_check(tmp_path, capsys):
    root = str(tmp_path / "tree")
    _tree(root)
    baseline = str(tmp_path / "baseline.json")

    assert cli.run(["init", root, "-b", baseline, "-e", "*.log"]) == 0
    assert os.path.exists(baseline)

    rc = cli.run(["check", root, "-b", baseline])
    out = capsys.readouterr().out
    assert rc == 0
    assert "no changes" in out


def test_check_detects_change_and_exits_nonzero(tmp_path, capsys):
    root = str(tmp_path / "tree")
    _tree(root)
    baseline = str(tmp_path / "baseline.json")
    cli.run(["init", root, "-b", baseline, "-e", "*.log"])

    # Modify a file after the baseline.
    with open(os.path.join(root, "config", "app.conf"), "w") as fh:
        fh.write("setting=2\n")

    rc = cli.run(["check", root, "-b", baseline])
    out = capsys.readouterr().out
    assert rc == 1
    assert "MODIFIED" in out
    assert "config/app.conf" in out


def test_excluded_log_is_ignored_on_check(tmp_path, capsys):
    root = str(tmp_path / "tree")
    _tree(root)
    baseline = str(tmp_path / "baseline.json")
    cli.run(["init", root, "-b", baseline, "-e", "*.log"])

    # Changing an excluded file must not count as a change.
    with open(os.path.join(root, "notes.log"), "w") as fh:
        fh.write("changed but excluded\n")

    assert cli.run(["check", root, "-b", baseline]) == 0


def test_missing_baseline_errors(tmp_path, capsys):
    rc = cli.run(["check", str(tmp_path), "-b", str(tmp_path / "nope.json")])
    assert rc == 2
    assert "cannot read baseline" in capsys.readouterr().err
