from collections import deque
from pathlib import Path
from enum import Enum

from libcaf.repository import Repository
from libcaf.ref import HashRef
from libcaf.plumbing import load_commit

class MergeCase(Enum):
    DISCONNECTED = 'no-common-ancestor'
    UP_TO_DATE = 'up-to-date'
    FAST_FORWARD = 'fast-forward'
    THREE_WAY = 'three-way'

def find_common_ancestor(repo_dir: Path, commit_a: HashRef, commit_b: HashRef) -> HashRef | None:
    """
    Return the lowest common ancestor of two commits, or None if no common ancestor exists.
    """
    # Trivial case: identical commits
    if commit_a == commit_b:
        return commit_a
    
    repo = Repository(repo_dir)
    objects_dir = repo.objects_dir()
            
    # Collect all ancestors of commit_a (including commit_a itself)
    ancestors_of_a: set[HashRef] = set()
    stack: list[HashRef] = [commit_a]

    while stack:
        current = stack.pop()
        ancestors_of_a.add(current)

        try:
            commit = load_commit(objects_dir, current)
        except Exception as e:
            raise RuntimeError(f"Failed to load commit {current}: {e}") from e

        stack.extend(commit.parents)

    # BFS from commit_b 
    # This also handles the case where commit_b is an ancestor of commit_a,
    # since commit_a is already included in ancestors_of_a.
    queue: deque[HashRef] = deque([commit_b])
    visited: set[HashRef] = set()

    while queue:
        current = queue.popleft()
        if current not in visited:
            visited.add(current)

            if current in ancestors_of_a:
                return current

            try:
                commit = load_commit(objects_dir, current)
            except Exception as e:
                raise RuntimeError(f"Failed to load commit {current}: {e}") from e
            
            queue.extend(commit.parents)

    return None    

def merge(repo: Repository, target: HashRef) -> MergeCase:
    """
    Determine and perform the appropriate merge operation between the current HEAD
    of the repository and the given target commit.

    :return: A MergeCase value describing the outcome of the merge decision.
    :raises NotImplementedError: If a three-way merge is required."""

    head = repo.head_commit()
    merge_base = find_common_ancestor(repo.working_dir, head, target)

    if merge_base == None:
        return MergeCase.DISCONNECTED
    
    elif merge_base == target:
        return MergeCase.UP_TO_DATE

    elif merge_base == head:
        head_ref = repo.head_ref()
        repo.update_ref(head_ref, target)
        return MergeCase.FAST_FORWARD

    elif merge_base != head and merge_base != target:
        repo._enter_merge_state()
        return MergeCase.THREE_WAY
