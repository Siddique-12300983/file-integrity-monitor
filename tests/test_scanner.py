import os

from fim.scanner import scan, sha256_file


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def test_scan_hashes_all_files(tmp_path):
    _write(str(tmp_path / "a.txt"), "hello")
    _write(str(tmp_path / "sub" / "b.txt"), "world")
    result = scan(str(tmp_path))
    assert set(result) == {"a.txt", "sub/b.txt"}
    assert len(result["a.txt"]["sha256"]) == 64


def test_sha256_known_value(tmp_path):
    p = tmp_path / "x"
    p.write_text("abc")
    # SHA-256("abc") is a known constant.
    assert sha256_file(str(p)) == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_exclude_glob_pattern(tmp_path):
    _write(str(tmp_path / "keep.txt"), "a")
    _write(str(tmp_path / "noise.log"), "b")
    result = scan(str(tmp_path), excludes=["*.log"])
    assert "keep.txt" in result
    assert "noise.log" not in result


def test_exclude_directory(tmp_path):
    _write(str(tmp_path / "app.py"), "a")
    _write(str(tmp_path / ".git" / "config"), "b")
    result = scan(str(tmp_path), excludes=[".git"])
    assert "app.py" in result
    assert not any(p.startswith(".git/") for p in result)


def test_paths_use_forward_slashes(tmp_path):
    _write(str(tmp_path / "deep" / "nested" / "f.txt"), "x")
    result = scan(str(tmp_path))
    assert "deep/nested/f.txt" in result
