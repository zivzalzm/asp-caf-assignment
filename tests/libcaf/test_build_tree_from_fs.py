from __future__ import annotations

from pathlib import Path

from libcaf import TreeRecordType
from libcaf.repository import Repository


def _snapshot_dir(root: Path) -> list[str]:
    """
    Stable snapshot of a directory tree for before/after comparisons.
    Uses relative POSIX paths sorted lexicographically.
    """
    if not root.exists():
        return []
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))


def test_build_tree_from_fs_is_read_only(temp_repo: Repository) -> None:
    wd = temp_repo.working_dir
    (wd / "a.txt").write_text("aaa", encoding="utf-8")
    (wd / "dir").mkdir()
    (wd / "dir" / "b.txt").write_text("bbb", encoding="utf-8")

    objects_dir = temp_repo.objects_dir()
    before = _snapshot_dir(objects_dir)

    temp_repo.build_tree_from_fs(wd)

    after = _snapshot_dir(objects_dir)
    assert after == before


def test_build_tree_from_fs_skips_repo_dir(temp_repo: Repository) -> None:
    wd = temp_repo.working_dir
    (wd / "x.txt").write_text("x", encoding="utf-8")

    tree, _, _ = temp_repo.build_tree_from_fs(wd)

    assert temp_repo.repo_dir.name not in tree.records


def test_build_tree_from_fs_is_deterministic_and_dfs(temp_repo: Repository) -> None:
    wd = temp_repo.working_dir

    (wd / "b.txt").write_text("b", encoding="utf-8")
    (wd / "a.txt").write_text("a", encoding="utf-8")

    (wd / "zdir").mkdir()
    (wd / "zdir" / "b2.txt").write_text("b2", encoding="utf-8")
    (wd / "zdir" / "a2.txt").write_text("a2", encoding="utf-8")

    tree, _, subtrees = temp_repo.build_tree_from_fs(wd)

    assert list(tree.records.keys()) == sorted(tree.records.keys())

    assert "zdir" in tree.records
    assert tree.records["zdir"].type == TreeRecordType.TREE

    subtree_hash = tree.records["zdir"].hash
    assert subtree_hash in subtrees

    subtree = subtrees[subtree_hash]
    assert list(subtree.records.keys()) == sorted(subtree.records.keys())
