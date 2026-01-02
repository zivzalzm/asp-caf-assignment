import pytest
from libcaf import Commit
from libcaf.repository import Repository
from caf.merge import find_common_ancestor
from libcaf.plumbing import hash_object
from libcaf.ref import HashRef
from libcaf.plumbing import save_commit

import time

def test_same_commit(temp_repo: Repository) -> None:
    a = temp_repo.commit_working_dir(author="Test Author", message="A")

    assert find_common_ancestor(temp_repo.working_dir, a, a) == a


def test_direct_ancestor(temp_repo: Repository) -> None:
    parent = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")

    assert find_common_ancestor(temp_repo.working_dir, parent, child) == parent


def test_linear_history(temp_repo: Repository) -> None:
    parent = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")
    grandchild = temp_repo.commit_working_dir(author="Test Author",message="C")

    assert find_common_ancestor(temp_repo.working_dir, child, grandchild) == child

def test_disconnected_histories(temp_repo, temp_repo_dir) -> None:
    root1 = temp_repo.commit_working_dir(author="Test Author", message="A")
    child1 = temp_repo.commit_working_dir(author="Test Author", message="B")

    tree_hash = temp_repo.save_dir(temp_repo.working_dir)
    commit = Commit(tree_hash, "Test Author", "C", int(time.time()), [])

    root2 = HashRef(hash_object(commit))
    save_commit(temp_repo.objects_dir(), commit)

    assert find_common_ancestor(temp_repo_dir, root1, root2) is None


def test_common_ancestor_diverged_history(temp_repo: Repository, temp_repo_dir) -> None:
    base = temp_repo.commit_working_dir(author="Test Author", message="A")

    left = temp_repo.commit_working_dir(author="Test Author", message="B")

    commit = Commit("tree_hash", "Test Author", "C", int(time.time()), [base])

    right = HashRef(hash_object(commit))
    save_commit(temp_repo.objects_dir(), commit)

    assert find_common_ancestor(temp_repo_dir, left, right) == base
