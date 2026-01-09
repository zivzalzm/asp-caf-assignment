from pathlib import Path

from libcaf.repository import Repository


def test_start_merge_creates_merge_dir(temp_repo: Repository) -> None:
    temp_repo.start_merge()

    merge_dir = temp_repo.repo_path() / "merge"
    assert merge_dir.exists()
    assert merge_dir.is_dir()


def test_is_merging_true_when_merge_dir_exists(temp_repo: Repository) -> None:
    temp_repo.start_merge()

    assert temp_repo.is_merging() is True


def test_is_merging_false_when_no_merge(temp_repo: Repository) -> None:
    assert temp_repo.is_merging() is False
