from collections import deque
from typing import Optional


def find_common_ancestor(commit_a: str, commit_b: str, parents: dict[str, list[str]]) -> Optional[str]:
    """
    Return the lowest common ancestor of two commits, or None if no common ancestor exists.
    """

    # Trivial case: identical commits
    if commit_a == commit_b:
        return commit_a

    # Collect all ancestors of commit_a
    ancestors_of_a = set()
    stack = [commit_a]

    while stack:
        current = stack.pop()
        if current in ancestors_of_a:
            continue
        ancestors_of_a.add(current)

        for p in parents.get(current, []):
            stack.append(p)

    # Traverse ancestors of commit_b from closest to farthest (using BFS)
    queue = deque([commit_b])
    visited = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        if current in ancestors_of_a:
            return current

        for p in parents.get(current, []):
            queue.append(p)

    return None
