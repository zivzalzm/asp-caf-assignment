import pytest
from caf.merge import find_common_ancestor

def test_same_commit():
    assert find_common_ancestor("A", "A", {}) == "A"


def test_direct_ancestor():
    parents = {"B": ["A"]}

    assert find_common_ancestor("A", "B", {"B": ["A"]}) == "A"

def test_linear_history():
    parents = {
        "B": ["A"],
        "C": ["B"]
    }

    assert find_common_ancestor("B", "C", parents) == "B"


def test_diamond_history():
    parents = {
        "B": ["A"],
        "C": ["A"],
        "D": ["B", "C"]
    }

    assert find_common_ancestor("B", "C", parents) == "A"


def test_disconnected_histories():
    parents = {
        "B": ["A"],
        "Y": ["X"]
    }

    assert find_common_ancestor("B", "Y", parents) is None

def test_root_vs_unrelated_commit():
    parents = {
        "B": ["A"]
    }

    assert find_common_ancestor("A", "C", parents) is None


def test_two_roots():
    parents = {}

    assert find_common_ancestor("A", "B", parents) is None


def test_nearest_common_ancestor():
    parents = {
        "B": ["A"],
        "C": ["B"],
        "D": ["A"]
    }

    assert find_common_ancestor("C", "D", parents) == "A"


def test_merge_commit_and_parent():
    parents = {
        "B": ["A"],
        "C": ["A"],
        "M": ["B", "C"]
    }

    assert find_common_ancestor("M", "B", parents) == "B"

def test_commit_not_in_parents_map():
    parents = {
        "B": ["A"]
    }

    assert find_common_ancestor("X", "B", parents) is None

