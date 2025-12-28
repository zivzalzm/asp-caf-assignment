from pathlib import Path

from libcaf.plumbing import hash_file
from libcaf.repository import Repository


def test_working_dir_snapshot_ignores_repo_dir(temp_repo: Repository) -> None:
    # A freshly initialized repo contains only the .caf metadata directory.
    assert temp_repo.working_dir_snapshot() == {}


def test_working_dir_snapshot_includes_nested_files(temp_repo: Repository) -> None:
    (temp_repo.working_dir / 'a.txt').write_text('A')

    nested_dir = temp_repo.working_dir / 'dir' / 'sub'
    nested_dir.mkdir(parents=True)
    nested_file = nested_dir / 'b.txt'
    nested_file.write_text('B')

    snapshot = temp_repo.working_dir_snapshot()

    assert snapshot['a.txt'] == hash_file(temp_repo.working_dir / 'a.txt')
    assert snapshot['dir/sub/b.txt'] == hash_file(nested_file)


def test_working_dir_snapshot_hash_changes_when_file_changes(temp_repo: Repository) -> None:
    file_path: Path = temp_repo.working_dir / 'x.txt'
    file_path.write_text('first')
    snap1 = temp_repo.working_dir_snapshot()

    file_path.write_text('second')
    snap2 = temp_repo.working_dir_snapshot()

    assert snap1['x.txt'] != snap2['x.txt']
