from __future__ import annotations

from libcaf import TreeRecordType
from libcaf.fs_tree import build_tree_from_fs
from libcaf.repository import Repository


def test_build_tree_from_fs_skips_repo_dir(temp_repo: Repository) -> None:
    wd = temp_repo.working_dir
    (wd / "x.txt").write_text("x", encoding="utf-8")

    tree, _, _ = build_tree_from_fs(wd, temp_repo.repo_dir.name)

    assert temp_repo.repo_dir.name not in tree.records


def test_build_tree_from_fs_is_deterministic_and_dfs(temp_repo: Repository) -> None:
    wd = temp_repo.working_dir

    (wd / "b.txt").write_text("b", encoding="utf-8")
    (wd / "a.txt").write_text("a", encoding="utf-8")

    (wd / "zdir").mkdir()
    (wd / "zdir" / "b2.txt").write_text("b2", encoding="utf-8")
    (wd / "zdir" / "a2.txt").write_text("a2", encoding="utf-8")

    tree, _, subtrees = build_tree_from_fs(wd, temp_repo.repo_dir.name)

    assert list(tree.records.keys()) == sorted(tree.records.keys())

    assert "zdir" in tree.records
    assert tree.records["zdir"].type == TreeRecordType.TREE

    subtree_hash = tree.records["zdir"].hash
    assert subtree_hash in subtrees

    subtree = subtrees[subtree_hash]
    assert list(subtree.records.keys()) == sorted(subtree.records.keys())
