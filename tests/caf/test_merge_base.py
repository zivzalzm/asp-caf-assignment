from libcaf.repository import Repository

from caf import cli_commands
from caf.merge import find_common_ancestor


def test_same_commit(temp_repo: Repository) -> None:
    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="A",
    )
    a = temp_repo.head_commit

    assert find_common_ancestor(a, a) == a


def test_direct_ancestor(temp_repo: Repository) -> None:
    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="A",
    )
    a = temp_repo.head_commit

    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="B",
    )
    b = temp_repo.head_commit

    assert find_common_ancestor(a, b) == a


def test_linear_history(temp_repo: Repository) -> None:
    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="A",
    )
    a = temp_repo.head_commit

    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="B",
    )
    b = temp_repo.head_commit

    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="C",
    )
    c = temp_repo.head_commit

    assert find_common_ancestor(b, c) == b


def test_disconnected_histories(temp_repo, temp_repo_dir) -> None:
    # first repository
    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="A",
    )
    a = temp_repo.head_commit()

    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="B",
    )
    b = temp_repo.head_commit()

    # second, completely separate repository
    other_repo = Repository(working_dir=temp_repo_dir / "other")
    other_repo.init()

    cli_commands.commit(
        working_dir_path=other_repo.working_dir,
        author="Test Author",
        message="X",
    )
    x = other_repo.head_commit()

    assert find_common_ancestor(b, x) is None


def test_root_vs_unrelated_commit(temp_repo, temp_repo_dir) -> None:
    cli_commands.commit(
        working_dir_path=temp_repo.working_dir,
        author="Test Author",
        message="A",
    )
    a = temp_repo.head_commit()

    # unrelated repository
    other_repo = Repository(working_dir=temp_repo_dir / "other_root")
    other_repo.init()

    cli_commands.commit(
        working_dir_path=other_repo.working_dir,
        author="Test Author",
        message="C",
    )
    c = other_repo.head_commit()

    assert find_common_ancestor(a, c) is None
