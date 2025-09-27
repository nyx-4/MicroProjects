import configparser
import os
from fnmatch import fnmatch


class GitRepository(object):
    """A git repository abstraction

    Attributes:
        worktree (str): The root-directory of repository
        git_dir (str): The .git directory in the worktree
        conf (ConfigParser): The .git/config file parser
    """

    worktree: str = ""
    git_dir: str = ""
    conf: configparser.ConfigParser = configparser.ConfigParser()

    def __init__(self, path: str, force: bool = False) -> None:
        """Create an empty Git repository or reinitialize an existing one

        Parameters:
            path (str): The path to the git directory
            force (bool): Disables all checks, if True
        """
        self.worktree = path
        self.git_dir = os.path.join(path, ".git")

        # if .git/ do not exists, raise Exception
        if not (force or os.path.isdir(self.git_dir)):
            raise TypeError(f"fatal: not a git repository: {path}")

        # Read configuration files in .git/config
        local_conf: str = repo_path(self, "config")
        xdg_config_home: str = os.environ.get("XDG_CONFIG_HOME", "~/.config")

        conf_files: tuple[str, ...] = (
            "/etc/gitconfig",
            os.path.expanduser(os.path.join(xdg_config_home, "git/config")),
            os.path.expanduser("~/.gitconfig"),
            local_conf,
        )

        # Read version number and raise if ver != 0
        self.conf.read(conf_files)

        if not os.path.exists(local_conf) and force is False:
            raise FileNotFoundError("Configuration file missing")

        if not force:
            ver: int = int(self.conf.get("core", "repositoryformatversion"))
            if ver != 0:
                raise NotImplementedError(f"unsupported repositoryformatversion: {ver}")


class GitIndexEntry(object):
    """GitIndexEntry that stores SHA-1 and some metadata about the file being referenced

    Attributes:
        ctime_s (int): 32-bit ctime seconds, the last time a file's metadata changed
        ctime_n (int): 32-bit ctime nanosecond fractions
        mtime_s (int): 32-bit mtime seconds, the last time a file's data changed
        mtime_n (int): 32-bit mtime nanosecond fractions
        dev (int): 32-bit device number (where file is stored)
        ino (int): 32-bit inode number (where file is stored)
        mode_type (int): 4-bit object type. valid values in binary are:
            1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)
        mode_perms (int): 9-bit unix permission
            Only 0755 and 0644 are are valid for regular files, symlinks/gitlinks have 0 here
        uid (int): 32-bit user id of owner
        gid (int): 32-bit group id of owner
        file_size (int): 32-bit file size (on-disk, truncated to 32-bit)
        sha1 (str): The SHA-1 of file being referenced by this entry
        flag_assume_valid (int): 1-bit assume-valid flag
        flag_stage (int): 2-bit stage (during merge)
        name (str): Entry path name (relative to top level directory, without leading or trailing slash)
    """

    def __init__(
        self, ctime_s: int, ctime_n: int, mtime_s: int, mtime_n: int, dev: int, ino: int,
        mode_type: int, mode_perms: int, uid: int, gid: int, file_size: int, sha1: str,
        flag_assume_valid: int, flag_stage: int, name: str,
    ) -> None:  # fmt: skip
        """GitIndexEntry that stores SHA-1 and some metadata about the file being referenced

        Parameters:
            ctime_s (int): 32-bit ctime seconds, the last time a file's metadata changed
            ctime_n (int): 32-bit ctime nanosecond fractions
            mtime_s (int): 32-bit mtime seconds, the last time a file's data changed
            mtime_n (int): 32-bit mtime nanosecond fractions
            dev (int): 32-bit device number (where file is stored)
            ino (int): 32-bit inode number (where file is stored)
            mode_type (int): 4-bit object type. valid values in binary are:
                1000 (regular file), 1010 (symbolic link) and 1110 (gitlink)
            mode_perms (int): 9-bit unix permission
                Only 0755 and 0644 are are valid for regular files, symlinks/gitlinks have 0 here
            uid (int): 32-bit user id of owner
            gid (int): 32-bit group id of owner
            file_size (int): 32-bit file size (on-disk, truncated to 32-bit)
            sha1 (str): The SHA-1 of file being referenced by this entry
            flag_assume_valid (int): 1-bit assume-valid flag
            flag_stage (int): 2-bit stage (during merge)
            name (str): Entry path name (relative to top level directory, without leading or trailing slash)
        """

        self.ctime_s: int = ctime_s
        self.ctime_n: int = ctime_n
        self.mtime_s: int = mtime_s
        self.mtime_n: int = mtime_n
        self.dev: int = dev
        self.ino: int = ino
        self.mode_type: int = mode_type
        self.mode_perms: int = mode_perms
        self.uid: int = uid
        self.gid: int = gid
        self.file_size: int = file_size
        self.sha1: str = sha1
        self.flag_assume_valid: int = flag_assume_valid
        self.flag_stage: int = flag_stage
        self.name: str = name


class GitIndex(object):
    """GitIndex version 2

    Attributes:
        version (int): The version of GitIndex (only 2 is supported)
        entries (list[GitIndexEntry]): The list of entries stored in GitIndex
    """

    version: int = 2
    entries: list[GitIndexEntry]
    # ext  # NotImplemented
    # sha1: str  # ignored

    def __init__(self, version: int = 2, entries: list[GitIndexEntry] = []) -> None:
        """Initialize a GitIndex with given version and entries

        Parameters:
            version (int): The version of GitIndex (only 2 is supported)
            entries (list[GitIndexEntry]): List of parsed entries to store in GitIndex
        """

        self.version = version
        self.entries = entries or []  # `or []` is important part


class GitIgnore(object):
    """A class to hold GitIgnore rules, both absolute and scoped

    Attributes:
        absolute (list[list[tuple[str, bool]]]): a list of absolute rules
        scoped (dict[str, list[tuple[str, bool]]]): a dict of relative rules (with dirs as keys)
    """

    absolute: list[list[tuple[str, bool]]]
    scoped: dict[str, list[tuple[str, bool]]]

    def __init__(self, absolute: list[list], scoped: dict[str, list[tuple]]) -> None:
        """Initialize the GitIgnore with these rules

        Parameters:
            absolute (list[list]): a list of absolute rules
            scoped (dict[str, list[tuple]]): a dict of relative rules (with dirs as keys)
        """

        self.absolute = absolute
        self.scoped = scoped


def repo_path(repo: GitRepository, *path: str) -> str:
    """Compute path under repo's git/ directory

    Parameters:
        repo (GitRepository): The current working git repository
        *path (str): The path in .git/

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly

    Examples:
        ```
        >>> repo_path(repo, "refs", "remotes", "origin", "HEAD")
        /path/to/repo/.git/refs/remotes/origin/HEAD
        ```
    """
    return os.path.join(repo.git_dir, *path)


def repo_file(repo: GitRepository, *path: str, mkdir: bool = False) -> str:
    """Compute path under repo's git/ directory, and create dirname(*path) if absent

    Parameters:
        repo (GitRepository): The current working git repository
        *path (str): The path in .git/
        mkdir (bool): If directory don't exist, make one

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly

    Examples:
        ```
        >>> repo_file(repo, "refs", "remotes", "origin", "HEAD")
        /path/to/repo/.git/refs/remotes/origin/HEAD
        ```
    """

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    else:
        raise FileNotFoundError(
            f"{os.path.join(*path)} do not exists and mkdir not specified."
            " (packfiles are not supported, try unpacking packfiles first)"
        )


def repo_dir(repo: GitRepository, *path: str, mkdir: bool = False) -> str | None:
    """Compute dirpath under repo's git/ directory, and mkdir *path if absent if mkdir

    Parameters:
        repo (GitRepository): The current working git repository
        *path (str): The path in .git/
        mkdir (bool): Make directory if it doesn't exists

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly  \n
            Returns **None** if *path do not exist, and mkdir is not specified.

    Examples:
        ```
        >> repo_dir(repo, "refs", "remotes", "origin")
        /path/to/repo/.git/refs/remotes/origin/
        ```
    """
    git_path: str = repo_path(repo, *path)

    if os.path.exists(git_path):
        if os.path.isdir(git_path):
            return git_path
        else:
            raise NotADirectoryError(f"Not a directory {path}")

    elif mkdir:
        os.makedirs(git_path)
        return git_path
    else:
        return None


def repo_find(path: str = ".", *, required: bool = True) -> GitRepository | None:
    """Find the repository's root (the directory containing `.git/`),
    use `repo_find_f` to avoid typing warnings because of `None`

    Parameters:
        path (str): The path from which to recurse upward (default `$PWD`)
        required (bool): raise an Exception if no GitRepository found

    Returns:
        GitRepository (GitRepository): First directory that has `.git/` recursing upward
    """
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    parent: str = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # Base-case i.e., os.path.join("/", "..") is "/"
        if required:
            raise TypeError(f"fatal: not a git repository: {path}")
        else:
            return None

    return repo_find(parent, required=required)


def repo_find_f(path: str = ".") -> GitRepository:
    """Find the repository's root (the directory containing `.git/`).
    raise `TypeError` if `path` is not under any GitRepository

    Parameters:
        path (str): The path from which to recurse upward (default `$PWD`)
        required (bool): raise an Exception if no GitRepository found

    Returns:
        GitRepository (GitRepository): First directory that has `.git/` recursing upward
    """
    return repo_find(path, required=True)  # type: ignore


def cur_branch(repo: GitRepository) -> str | None:
    """Get the currently active branch in repo by de-ref'ing .git/HEAD
    or `None` if HEAD in detached state"""
    with open(repo_file(repo, "HEAD"), "rt") as head:
        branch: str = head.read()

    if branch.startswith("ref: refs/heads/"):
        return branch[16:-1]
    else:
        return None


def resolve_ref(repo: GitRepository, ref: str) -> str | None:
    """Git References are pointers to interesting commit,
    resolve_ref converts ref to absolute sha1 of object

    Parameters:
        repo (GitRepository): The current working git repository
        ref (str): Git Reference of which we want absolute sha1

    Returns:
        SHA-1 (str): The SHA-1 identifier of commit referenced by `ref`
    """
    ref_path: str = repo_file(repo, ref)

    if not os.path.isfile(ref_path):  # sometimes refs are broken, and its fine
        return None

    with open(ref_path, "rt") as ref_file:
        new_ref: str = ref_file.read()[:-1]

    if new_ref.startswith("ref: "):  # recursive case, in case of indirect references
        return resolve_ref(repo, new_ref.removeprefix("ref: "))
    else:
        return new_ref


def ref_list(repo: GitRepository, path=None, force: bool = False, _refs=None) -> dict:
    """List all references in a directory sorted alphabetically, recursively

    Parameters:
        repo (GitRepository): The current working git repository
        path (str | None): The path in .git/ of `repo`, which has only refs
        force (bool): force show all entries in `.git/refs`

    Returns:
        ref_dict (dict[str, str | dict]): if value is dict, then key is sub_dir. if value is str, then key is ref_name
    """

    if path is None:
        path = repo_dir(repo, "refs")
    if _refs is None:
        _refs = []
    ref_dict: dict[str, str | dict | None] = dict()

    assert path is not None, ".git/refs not found"

    if any([path.endswith(ref) for ref in _refs]):
        force = True

    for sub_dir in sorted(os.listdir(path)):
        new_path: str = os.path.join(path, sub_dir)

        if os.path.isdir(new_path):  # recurse for each sub directory
            ref_dict[sub_dir] = ref_list(repo, new_path, force, _refs)
        elif force or any([new_path.endswith(ref) for ref in _refs]):
            # store if file match the patterns given in _refs
            ref_dict[sub_dir] = resolve_ref(repo, new_path)

    return ref_dict


def tag_list(repo: GitRepository, refs: dict, prefx: str = "") -> None:
    """parse and print all refs in `refs` as `f'{prefx}{tagname}'`

    Parameters:
        repo (GitRepository): The current working git repository
        refs (dict[str, str | dict]): if value is dict, then key is sub_dir. if value is str, then key is ref_name
        prefx (str): The str to prefix tagname before printing them

    Returns:
        None (None): have side-effect (print on screen), so returns `None` to enforce this behavior
    """
    for tagname, sha1 in refs.items():
        if type(sha1) is dict:
            tag_list(repo, sha1, f"{prefx}{tagname}/")
        elif os.path.exists(repo_file(repo, f"objects/{sha1[:2]}/{sha1[2:]}")):
            print(f"{prefx}{tagname}")
        else:
            print(f"WARNING: ignoring broken ref refs/tags/{prefx}{tagname}")


def gitignore_parse(rules: list[str]) -> list[tuple[str, bool]]:
    """Parse a list of raw rules from .gitignore into ngit-compatible rules
    that would allows further processing of checking whether to ignore file or not

    Parameters:
        rules (list[str]): A list of raw rules read from .gitignore

    Returns:
        parsed_rules (list[tuple[str, bool]]): Parsed rules with only necessary information
    """
    parsed_rules: list[tuple[str, bool]] = []

    for rule in rules:
        rule: str = rule.strip()
        if not rule or rule.startswith("#"):
            pass
        elif rule.startswith("!"):
            parsed_rules.append((rule[1:], False))
        elif rule.startswith("\\"):
            parsed_rules.append((rule[1:], True))
        else:
            parsed_rules.append((rule, True))

    return parsed_rules


def gitignore_check_rule(rules: list[tuple[str, bool]], path: str) -> bool | None:
    """Check whether path would be ignored under rules or not or can't say under these rules

    Parameters:
        rules (list[tuple[str, bool]]): The rules to check against
        path (str): The relative path to file of which ignore-status we want

    Returns:
        match_status (bool | None): True if ignore, False if keep, None if no rule match
    """

    def _check(path, pat, start, end) -> bool:
        return (
            fnmatch(path, pat)
            or fnmatch(path, pat + end)
            or fnmatch(path, start + pat)
            or fnmatch(path, start + pat + end)
        )

    def _stars(path: str, pat: str, start: str, end: str, idx: int = 0) -> bool:
        idx = pat.find("**", idx)
        if idx == -1:  # base case
            return _check(path, pat, start, end)

        return _stars(path, pat, start, end, idx + 1) or _stars(
            path, pat[:idx] + pat[idx + 3 :], start, end, idx + 1
        )

    def _star(path: str, pat: str, start: str, end: str, idx: int = 0) -> bool:
        # TODO: Add single asterisk support also
        raise NotImplementedError("Single asterisk `*` is not yet supported")

    match_status: bool | None = None
    path = os.path.normpath(path) + ("/" if path[-1] == "/" else "")

    if os.path.isabs(path):  # abs path raises error on `git`
        return False

    for pattern, state in rules:
        end: str = ("/" if pattern[-1] != "/" else "") + "*"
        start: str = "" if "**" in pattern else "*/"

        if _stars(path, pattern, start, end):
            match_status = state

    return match_status
