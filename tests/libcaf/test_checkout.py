from libcaf.repository import Repository, RepositoryError, branch_ref
from pytest import raises
from libcaf.ref import RefError

def test_checkout_blocks_on_conflict(temp_repo: Repository) -> None:
    # Create an initial commit
    (temp_repo.working_dir / "file1.txt").write_text("v1", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "Initial")
    
    # Modify file in working directory without committing
    (temp_repo.working_dir / "file1.txt").write_text("dirty_change", encoding="utf-8")
    
    # Attempt checkout should raise RepositoryError
    with raises(RepositoryError) as excinfo:
        temp_repo.checkout("main")
    
    assert "local changes" in str(excinfo.value).lower()

def test_checkout_updates_files_and_head(temp_repo: Repository) -> None:
    # Commit something to 'main' first
    (temp_repo.working_dir / "main_file.txt").write_text("main content", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "commit 1")
    
    # Add branch 'feature'
    temp_repo.add_branch("feature")
    temp_repo.checkout("feature") 
    
    # Create a file specifically on 'feature' branch and commit
    (temp_repo.working_dir / "feature_only.txt").write_text("feature content", encoding="utf-8")
    temp_repo.commit_working_dir("Author", "commit 2")
    
    # Checkout back to 'main'
    temp_repo.checkout("main")
    
    # 'main_file.txt' should still be here
    assert (temp_repo.working_dir / "main_file.txt").exists()
    # 'feature_only.txt' should have been deleted by the clean process
    assert not (temp_repo.working_dir / "feature_only.txt").exists()
    # HEAD should now point back to main
    assert temp_repo.head_ref() == branch_ref("main")
    
def test_checkout_detached_head(temp_repo: Repository) -> None:
    (temp_repo.working_dir / "file.txt").write_text("v1")
    commit_hash = temp_repo.commit_working_dir("Author", "First")
    
    # Create a second commit so we have something to move from
    (temp_repo.working_dir / "file.txt").write_text("v2")
    temp_repo.commit_working_dir("Author", "Second")
    
    # Checkout the first commit directly (by hash)
    temp_repo.checkout(commit_hash)
    
    assert temp_repo.head_ref() == commit_hash
    assert (temp_repo.working_dir / "file.txt").read_text() == "v1"
    
def test_checkout_invalid_target_raises_error(temp_repo: Repository) -> None:
    with raises(RefError):
        temp_repo.checkout("non_existent_branch_or_hash")

def test_checkout_restores_nested_directories(temp_repo: Repository) -> None:
    # Setup: branch with nested folder
    subdir = temp_repo.working_dir / "nested" / "folder"
    subdir.mkdir(parents=True)
    (subdir / "deep_file.txt").write_text("deep content")
    temp_repo.commit_working_dir("Author", "nested commit")
    
    temp_repo.add_branch("other")
    temp_repo.checkout("other") # Move to empty branch
    
    assert not (temp_repo.working_dir / "nested").exists()
    
    temp_repo.checkout("main") # Move back
    assert (temp_repo.working_dir / "nested" / "folder" / "deep_file.txt").exists()
    
def test_checkout_blocks_if_untracked_file_would_be_overwritten(temp_repo: Repository) -> None:
    # Commit a file named 'conflict.txt' on branch A
    (temp_repo.working_dir / "conflict.txt").write_text("version A")
    temp_repo.commit_working_dir("Author", "commit A")
    
    # Go to an empty branch B
    temp_repo.add_branch("branchB")
    temp_repo.checkout("branchB")
    assert not (temp_repo.working_dir / "conflict.txt").exists()
    
    # Create 'conflict.txt' manually (it's now untracked on branch B)
    (temp_repo.working_dir / "conflict.txt").write_text("dirty untracked")
    
    # Attempting to go back to 'main' should block because it would overwrite the untracked file
    with raises(RepositoryError):
        temp_repo.checkout("main")