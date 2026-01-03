import pytest
import time
from libcaf import Commit
from libcaf.repository import Repository
from caf.merge import merge
from libcaf.plumbing import hash_object
from libcaf.ref import HashRef
from libcaf.plumbing import save_commit


def test_merge_disconnected_histories(temp_repo, tmp_path):
    root1 = temp_repo.commit_working_dir(author="Test Author", message="A")
    child1 = temp_repo.commit_working_dir(author="Test Author", message="B")

    other_repo = Repository(tmp_path / "other_repo")
    other_repo.init()

    root2 = other_repo.commit_working_dir(author="other", message="C")
   
    with pytest.raises(RuntimeError):
        merge(temp_repo, root2)

def test_merge_up_to_date(temp_repo):
    root = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")

    merge(temp_repo, root)

    
def test_merge_fast_forward(temp_repo):
    root = temp_repo.commit_working_dir(author="Test Author", message="A")
    child = temp_repo.commit_working_dir(author="Test Author", message="B")

    merge(temp_repo, child)

    assert temp_repo.head_commit() == child

def test_merge_three_way(temp_repo, tmp_path):
    base = temp_repo.commit_working_dir(author="Test Author", message="A")
    left = temp_repo.commit_working_dir(author="Test Author", message="B")

    commit = Commit("tree_hash", "Test Author", "C", int(time.time()), [base])

    right = HashRef(hash_object(commit))
    save_commit(temp_repo.objects_dir(), commit)

    with pytest.raises(NotImplementedError):
        merge(temp_repo, right)

