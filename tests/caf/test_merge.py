import pytest
import time
from libcaf import Commit
from libcaf.repository import Repository
from caf.merge import merge, MergeCase
from libcaf.plumbing import hash_object, save_commit
from libcaf.ref import HashRef


def test_merge_disconnected_histories(temp_repo):
    root1 = temp_repo.commit_working_dir(author="Test Author", message="A")
    child1 = temp_repo.commit_working_dir(author="Test Author", message="B")

    root2 = Commit("tree_hash", "Test Author", "C", int(time.time()), [])
    root2_ref = HashRef(hash_object(root2))
    save_commit(temp_repo.objects_dir(), root2)

    assert merge(temp_repo, root2_ref) == MergeCase.DISCONNECTED

def test_merge_up_to_date(temp_repo):
    root_target = temp_repo.commit_working_dir(author="Test Author", message="A")
    child_head = temp_repo.commit_working_dir(author="Test Author", message="B")

    assert merge(temp_repo, root_target) == MergeCase.UP_TO_DATE

def test_merge_fast_forward(temp_repo):
    root_head = temp_repo.commit_working_dir(author="Test Author", message="A")

    child_target = Commit("tree_hash", "Test Author", "B", int(time.time()), [root_head])
    child_target_ref = HashRef(hash_object(child_target))
    save_commit(temp_repo.objects_dir(), child_target)

    assert merge(temp_repo, child_target_ref) == MergeCase.FAST_FORWARD

def test_merge_three_way(temp_repo):
    base = temp_repo.commit_working_dir(author="Test Author", message="A")
    left = temp_repo.commit_working_dir(author="Test Author", message="B")

    commit = Commit("tree_hash", "Test Author", "C", int(time.time()), [base])

    right = HashRef(hash_object(commit))
    save_commit(temp_repo.objects_dir(), commit)

    assert merge(temp_repo, right) == MergeCase.THREE_WAY
