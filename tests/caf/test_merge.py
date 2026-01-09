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

    result = merge(temp_repo, root2_ref)
    assert result == MergeCase.DISCONNECTED
    assert temp_repo.head_commit() == child1
    assert temp_repo.is_merging() is False


def test_merge_up_to_date(temp_repo):
    root_target = temp_repo.commit_working_dir(author="Test Author", message="A")
    child_head = temp_repo.commit_working_dir(author="Test Author", message="B")

    result = merge(temp_repo, root_target)
    assert result == MergeCase.UP_TO_DATE
    assert temp_repo.head_commit() == child_head
    assert temp_repo.is_merging() is False


def test_merge_fast_forward(temp_repo):
    root_head = temp_repo.commit_working_dir(author="Test Author", message="A")

    child_target = Commit("tree_hash", "Test Author", "B", int(time.time()), [root_head])
    child_target_ref = HashRef(hash_object(child_target))
    save_commit(temp_repo.objects_dir(), child_target)

    result = merge(temp_repo, child_target_ref)
    assert result == MergeCase.FAST_FORWARD
    assert temp_repo.head_commit() == child_target_ref
    assert temp_repo.is_merging() is False


def test_merge_three_way(temp_repo):
    base = temp_repo.commit_working_dir(author="Test Author", message="A")
    left = temp_repo.commit_working_dir(author="Test Author", message="B")

    commit = Commit("tree_hash", "Test Author", "C", int(time.time()), [base])

    right = HashRef(hash_object(commit))
    save_commit(temp_repo.objects_dir(), commit)

    result = merge(temp_repo, right)
    assert result == MergeCase.THREE_WAY
    assert temp_repo.is_merging() 
    assert temp_repo.head_commit() == left


def test_merge_three_way_abort_merge_exits_merge_state(temp_repo):
    temp_repo._enter_merge_state()
    assert temp_repo.is_merging()

    temp_repo.abort_merge()
    assert temp_repo.is_merging() is False
