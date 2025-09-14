import os


from microprojects.ngit.repository import GitRepository, GitIndex, GitIndexEntry
from microprojects.ngit.object_utils import flatten_tree, index_read, index_write
from microprojects.ngit.libngit import object_hash


def get_changes_head_index(repo: GitRepository, index: GitIndex) -> dict:
    """"""
    changes: dict[str, list] = {
        "modified": [],
        "new file": [],
        "deleted": [],
    }

    head: dict[str, str] = flatten_tree(repo, "HEAD")

    for entry in index.entries:
        if entry.name in head:
            if entry.sha1 != head[entry.name]:
                changes["modified"].append(entry.name)
            del head[entry.name]  # remove entry to filter deleted entried
        else:
            changes["new file"].append(entry.name)

    changes["deleted"].extend(head.keys())

    return changes


def get_changes_index_worktree(repo: GitRepository, index: GitIndex) -> dict:
    """"""
    changes: dict[str, list] = {
        "modified": [],
        "deleted": [],
        "untracked": [],
    }

    all_files: list[str] = []

    for root, _, files in os.walk(repo.worktree, True):
        if root == repo.git_dir or root.startswith(repo.git_dir + os.path.sep):
            continue  # ignore `.git/` directory entirely
        for file in files:
            # append relative path (wrt to repo.worktree) to all_files
            all_files.append(os.path.relpath(os.path.join(root, file), repo.worktree))

    for entry in index.entries:
        full_path: str = os.path.join(repo.worktree, entry.name)

        if not os.path.exists(full_path):
            changes["deleted"].append(entry.name)
        else:
            stat: os.stat_result = os.stat(full_path)
            mtime_ns: int = entry.mtime_s * 10**9 + entry.mtime_n
            ctime_ns: int = entry.ctime_s * 10**9 + entry.ctime_n

            if stat.st_mtime_ns != mtime_ns or stat.st_ctime_ns != ctime_ns:
                # file's mtime is changed, so further invesigate by comparing sha1
                with open(full_path, "rb") as object:
                    new_sha1: str = object_hash(None, object, fmt=b"blob")
                    if entry.sha1 != new_sha1:
                        changes["modified"].append(entry.name)

        if entry.name in all_files:
            all_files.remove(entry.name)  # remove entries found in index

    changes["untracked"].extend(all_files)
    return changes


def rm_from_index(
    repo: GitRepository,
    paths: list[str],
    delete: bool = True,
    skip_missing: bool = False,  # TODO: rename this flag to be shorter, or add more flags
    write: bool = True,
) -> GitIndex:
    """"""
    index: GitIndex = index_read(repo)
    worktree: str = repo.worktree + os.sep

    rm_paths: list[str] = []
    kept_entries: list[GitIndexEntry] = []

    to_be_rm: set[str] = set()

    for path in paths:
        abspath: str = os.path.abspath(path)

        if abspath.startswith(worktree):
            to_be_rm.add(abspath)
        else:  # The requested is outside worktree
            raise NameError(f"{path} is outside the repository at '{worktree}'")

    for entry in index.entries:
        abspath = os.path.join(worktree, entry.name)
        if abspath in to_be_rm:  # remove if found in to_be_rm
            rm_paths.append(abspath)
            to_be_rm.remove(abspath)
        else:
            kept_entries.append(entry)

    if len(to_be_rm) > 0 and skip_missing is False:  # not all `to_be_rm` are in index
        rel_paths: list[str] = [path.removeprefix(worktree) for path in to_be_rm]
        raise NameError(f"pathspec {rel_paths} did not match any files")

    if delete:
        for path in rm_paths:
            os.remove(path)

    index.entries = kept_entries
    if write is True:  # micro-optimization, when calling from `ngit add`
        index_write(repo, index)
    return index


def add_to_index(repo: GitRepository, paths: list[str]) -> GitIndex:
    """"""
    index: GitIndex = rm_from_index(repo, paths, delete=False, skip_missing=True, write=False)  # fmt: skip
    worktree: str = repo.worktree + os.sep

    clean_paths: set = set()

    for path in paths:
        abspath: str = os.path.abspath(path)
        relpath: str = os.path.relpath(abspath, worktree)

        # some sanity checks
        if not os.path.exists(abspath):  # file do not exists
            raise FileNotFoundError(f"{relpath} not found")
        if not os.path.isfile(abspath):  # its a directory, or
            raise IsADirectoryError(f"{abspath} is not a file")
        if not abspath.startswith(worktree):  # outside git's worktree
            raise NameError(f"{path} is outside the repository at '{worktree}'")

        clean_paths.add((abspath, relpath))

    for abspath, relpath in clean_paths:
        with open(abspath, "rb") as obj:
            sha1: str = object_hash(repo, obj, fmt=b"blob")

        stat: os.stat_result = os.stat(abspath)

        index.entries.append(
            GitIndexEntry(
                ctime_s=stat.st_ctime_ns // 10**9,
                ctime_n=stat.st_ctime_ns % 10**9,
                mtime_s=stat.st_mtime_ns // 10**9,
                mtime_n=stat.st_mtime_ns % 10**9,
                dev=stat.st_dev,
                ino=stat.st_ino,
                mode_type=0b1000,  # ngit's add only works with blob's
                mode_perms=0o644,  # git only accepts 644 and 755
                uid=stat.st_uid,
                gid=stat.st_gid,
                file_size=stat.st_size,
                sha1=sha1,
                flag_assume_valid=False,
                flag_stage=0,
                name=relpath,
            )
        )

    index_write(repo, index)
    return index


def commit_create() -> None:
    """"""


if __name__ == "__main__":
    from pprint import pprint
    from microprojects.ngit.repository import repo_find_f

    print([i.__dict__ for i in add_to_index(repo_find_f(), ["hello"]).entries])
