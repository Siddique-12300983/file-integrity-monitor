from fim.diff import compare


def _f(h):
    return {"sha256": h, "size": 1, "mtime": 0}


def test_detects_added_modified_deleted():
    base = {"keep": _f("aaa"), "change": _f("bbb"), "gone": _f("ccc")}
    curr = {"keep": _f("aaa"), "change": _f("ZZZ"), "new": _f("ddd")}
    changes = compare(base, curr)
    assert changes.added == ["new"]
    assert changes.modified == ["change"]
    assert changes.deleted == ["gone"]
    assert changes.total == 3
    assert changes.any()


def test_no_changes():
    base = {"a": _f("x"), "b": _f("y")}
    changes = compare(base, dict(base))
    assert not changes.any()
    assert changes.total == 0


def test_lists_are_sorted():
    base = {}
    curr = {"c": _f("1"), "a": _f("2"), "b": _f("3")}
    assert compare(base, curr).added == ["a", "b", "c"]
