from pytest import raises

from libcaf.ref import HashRef, RefError
from libcaf.repository import Repository, RepositoryError, branch_ref


def test_checkout_updates_files_and_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / "main_file.txt").write_text("main content", encoding="utf-8")
    base_hash = temp_repo.commit_working_dir("Author", "commit 1")

    temp_repo.add_branch("feature")
    temp_repo.update_ref(branch_ref("feature"), HashRef(base_hash))

    before_text = (temp_repo.working_dir / "main_file.txt").read_text(encoding="utf-8")
    before_diffs = temp_repo.diff(HashRef(base_hash), temp_repo.working_dir)

    temp_repo.checkout(branch_ref("feature"))

    assert (temp_repo.working_dir / "main_file.txt").exists()
    assert (temp_repo.working_dir / "main_file.txt").read_text(encoding="utf-8") == before_text
    assert temp_repo.diff(HashRef(base_hash), temp_repo.working_dir) == before_diffs

    assert temp_repo.head_ref() == branch_ref("feature")
    assert temp_repo.resolve_ref(temp_repo.head_ref()) == base_hash



def test_checkout_detached_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / "file.txt").write_text("v1", encoding="utf-8")
    commit_hash = temp_repo.commit_working_dir("Author", "First")

    (temp_repo.working_dir / "file.txt").write_text("v2", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "Second")

    temp_repo.checkout(HashRef(commit_hash))

    assert temp_repo.head_ref() == commit_hash
    assert (temp_repo.working_dir / "file.txt").read_text(encoding="utf-8") == "v1"


def test_checkout_invalid_target_raises_error(temp_repo: Repository) -> None:
    with raises(RefError):
        temp_repo.checkout(branch_ref("non_existent_branch_or_hash"))


def test_checkout_restores_nested_directories(temp_repo: Repository) -> None:
    subdir = temp_repo.working_dir / "nested" / "folder"
    subdir.mkdir(parents=True)
    (subdir / "deep_file.txt").write_text("deep content", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "nested commit")

    # Create an empty branch ref file directly (per TA comments)
    empty_branch_ref_path = temp_repo.refs_dir() / "heads" / "other"
    empty_branch_ref_path.parent.mkdir(parents=True, exist_ok=True)
    empty_branch_ref_path.write_text("", encoding="utf-8")

    temp_repo.checkout(branch_ref("other"))
    assert not (temp_repo.working_dir / "nested").exists()

    temp_repo.checkout(branch_ref("main"))
    assert (temp_repo.working_dir / "nested" / "folder" / "deep_file.txt").exists()


def test_checkout_from_empty_branch_blocks_if_working_dir_has_new_files(temp_repo: Repository) -> None:
    # Make a commit on main first
    (temp_repo.working_dir / "tracked.txt").write_text("v1", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "commit on main")

    # Now create an empty branch and move HEAD to it without using checkout
    empty_ref_path = temp_repo.refs_dir() / "heads" / "empty"
    empty_ref_path.parent.mkdir(parents=True, exist_ok=True)
    empty_ref_path.write_text("", encoding="utf-8")
    temp_repo.update_ref("HEAD", branch_ref("empty"))

    # Working dir has a "new file" relative to empty branch
    (temp_repo.working_dir / "new_file.txt").write_text("new", encoding="utf-8")

    with raises(RepositoryError):
        temp_repo.checkout(branch_ref("main"))


def test_checkout_blocks_if_new_file_would_be_overwritten(temp_repo: Repository) -> None:
    (temp_repo.working_dir / "conflict.txt").write_text("version A", encoding="utf-8")
    commit_a = temp_repo.commit_working_dir("Author", "commit A")

    temp_repo.add_branch("branchB")
    temp_repo.update_ref(branch_ref("branchB"), HashRef(commit_a))

    temp_repo.update_ref("HEAD", branch_ref("branchB"))

    assert (temp_repo.working_dir / "conflict.txt").exists()

    (temp_repo.working_dir / "conflict.txt").write_text("local change", encoding="utf-8")

    with raises(RepositoryError):
        temp_repo.checkout(branch_ref("main"))

    assert (temp_repo.working_dir / "conflict.txt").read_text(encoding="utf-8") == "local change"

