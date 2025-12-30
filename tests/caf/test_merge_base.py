import pytest
from libcaf.repository import Repository
from caf.merge import find_common_ancestor


def test_same_commit(temp_repo: Repository) -> None:
    a = temp_repo.commit_working_dir(author="Test Author", message="A")

    assert find_common_ancestor(temp_repo, a, a) == a


def test_direct_ancestor(temp_repo: Repository) -> None:
    parent = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")

    assert find_common_ancestor(temp_repo, parent, child) == parent


def test_linear_history(temp_repo: Repository) -> None:
    parent = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")
    grandchild = temp_repo.commit_working_dir(author="Test Author",message="C")

    assert find_common_ancestor(temp_repo, child, grandchild) == child

def test_disconnected_histories(temp_repo, temp_repo_dir) -> None:
    root1 = temp_repo.commit_working_dir(author="Test Author", message="A")
    child1 = temp_repo.commit_working_dir(author="Test Author", message="B")

    other_repo = Repository(working_dir=temp_repo_dir / "other")
    other_repo.init()
    root2 = other_repo.commit_working_dir(author="Test Author", message="X")

    with pytest.raises(RuntimeError):
        find_common_ancestor(temp_repo, child1, root2)

    with pytest.raises(RuntimeError):
        find_common_ancestor(other_repo, root2, root1)