from collections import deque
from libcaf.ref import HashRef
from libcaf.plumbing import load_commit

def find_common_ancestor(commit_a: HashRef, commit_b: HashRef) -> HashRef | None:
    """
    Return the lowest common ancestor of two commits, or None if no common ancestor exists.
    """

    # Trivial case: identical commits
    if commit_a == commit_b:
        return commit_a

    # Collect all ancestors of commit_a (including commit_a itself)
    ancestors_of_a: set[HashRef] = set()
    stack: list[HashRef] = [commit_a]

    while stack:
        current = stack.pop()
        ancestors_of_a.add(current)

        try:
            commit = load_commit(current)
        except Exception:
            # commit not found in this repository
            continue

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
                commit = load_commit(current)
            except Exception:
                # commit not found in this repository
                continue
            
            queue.extend(commit.parents)

    return None
