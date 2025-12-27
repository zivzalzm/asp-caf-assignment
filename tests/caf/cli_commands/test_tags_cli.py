import sys
from pathlib import Path

import pytest

from caf import cli_commands
from libcaf.repository import Repository
from libcaf.ref import HashRef


def _init_repo_with_commit(tmp_path: Path) -> tuple[Repository, HashRef]:
    """Helper: initialize a repository and create a single commit.

    Returns the Repository instance and the commit HashRef.
    """
    repo = Repository(working_dir=tmp_path)
    repo.init()

    # Create a file so there is something to commit
    work_file = tmp_path / "file1.txt"
    work_file.write_text("content for CLI tag tests")

    commit_ref = repo.commit_working_dir(author="tester", message="initial commit")
    return repo, commit_ref



def test_cli_create_tag_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI create_tag should succeed and create a tag for an existing commit."""
    repo, commit_ref = _init_repo_with_commit(tmp_path)

    code = cli_commands.create_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="v1.0",
        commit_hash=str(commit_ref),
        command="create_tag",
    )

    captured = capsys.readouterr()

    # Exit code should indicate success
    assert code == 0
    # Message to the user should mention the tag name
    assert 'Created tag "v1.0"' in captured.out

    # Verify that the tag actually exists in the repository
    tag_path = repo.tags_dir() / "v1.0"
    assert tag_path.exists()



def test_cli_create_tag_invalid_commit(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI create_tag should fail when the commit hash does not exist."""
    # Initialize repository but do not create any commit for this hash
    repo = Repository(working_dir=tmp_path)
    repo.init()

    invalid_hash = "a" * 40  # looks like a hash, but does not exist

    code = cli_commands.create_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="v1.0",
        commit_hash=invalid_hash,
        command="create_tag",
    )

    captured = capsys.readouterr()

    # Non-zero exit code indicates failure
    assert code != 0
    # Error message should go to stderr and mention that the commit does not exist
    assert "does not exist" in captured.err



def test_cli_tags_no_tags(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI tags should print a friendly message when no tags exist."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    code = cli_commands.tags(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        command="tags",
    )

    captured = capsys.readouterr()

    assert code == 0
    assert "No tags found." in captured.out



def test_cli_tags_lists_existing_tag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI tags should list existing tags and their commit hashes."""
    repo, commit_ref = _init_repo_with_commit(tmp_path)

    # First create the tag via CLI
    create_code = cli_commands.create_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="v1.0",
        commit_hash=str(commit_ref),
        command="create_tag",
    )
    assert create_code == 0

    # Now list tags via CLI
    code = cli_commands.tags(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        command="tags",
    )

    captured = capsys.readouterr()

    assert code == 0
    # Expect the tag name and its commit hash in the output
    assert "v1.0" in captured.out
    assert str(commit_ref) in captured.out



def test_cli_delete_tag_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI delete_tag should delete an existing tag and report success."""
    repo, commit_ref = _init_repo_with_commit(tmp_path)

    # Create tag
    create_code = cli_commands.create_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="v1.0",
        commit_hash=str(commit_ref),
        command="create_tag",
    )
    assert create_code == 0

    # Delete tag via CLI
    code = cli_commands.delete_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="v1.0",
        command="delete_tag",
    )

    captured = capsys.readouterr()

    assert code == 0
    assert 'Deleted tag "v1.0"' in captured.out
    assert not (repo.tags_dir() / "v1.0").exists()



def test_cli_delete_tag_non_existing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI delete_tag should fail when the tag does not exist."""
    repo = Repository(working_dir=tmp_path)
    repo.init()

    code = cli_commands.delete_tag(
        working_dir_path=str(tmp_path),
        repo_dir=".caf",
        tag_name="no-such-tag",
        command="delete_tag",
    )

    captured = capsys.readouterr()

    assert code != 0
    assert "does not exist" in captured.err
