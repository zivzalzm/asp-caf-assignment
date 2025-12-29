from __future__ import annotations

from pathlib import Path
from collections import deque

from libcaf import Tree, TreeRecord, TreeRecordType
from .plumbing import hash_file, hash_object


def build_tree_from_fs(root: Path, repo_dir_name: str) -> tuple[Tree, str, dict[str, Tree]]:
    if not root.exists() or not root.is_dir():
        raise NotADirectoryError(str(root))

    trees_by_path: dict[Path, Tree] = {}
    hashes_by_path: dict[Path, str] = {}
    subtrees_by_hash: dict[str, Tree] = {}

    def _build_dir_tree(dir_path: Path) -> tuple[Tree, str]:
        records: dict[str, TreeRecord] = {}

        for item in sorted(dir_path.iterdir(), key=lambda p: p.name):
            if item.name == repo_dir_name:
                continue

            if item.is_file():
                blob_hash = hash_file(item)
                records[item.name] = TreeRecord(TreeRecordType.BLOB, blob_hash, item.name)
            elif item.is_dir():
                subtree_hash = hashes_by_path[item]
                records[item.name] = TreeRecord(TreeRecordType.TREE, subtree_hash, item.name)

        tree = Tree(records)
        tree_hash = hash_object(tree)

        trees_by_path[dir_path] = tree
        hashes_by_path[dir_path] = tree_hash
        subtrees_by_hash[tree_hash] = tree

        return tree, tree_hash

    stack: deque[tuple[Path, bool]] = deque([(root, False)])

    while stack:
        dir_path, expanded = stack.pop()

        if expanded:
            _build_dir_tree(dir_path)
        else:
            stack.append((dir_path, True))
            for item in reversed(sorted(dir_path.iterdir(), key=lambda p: p.name)):
                if item.name == repo_dir_name:
                    continue
                if item.is_dir():
                    stack.append((item, False))

    return trees_by_path[root], hashes_by_path[root], subtrees_by_hash
