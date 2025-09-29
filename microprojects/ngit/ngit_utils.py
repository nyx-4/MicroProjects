import os
import configparser
from datetime import datetime

from microprojects.ngit.repository import GitRepository, repo_dir, repo_file, ref_list
from microprojects.ngit.repository import GitIndex, GitIndexEntry
from microprojects.ngit.repository import GitIgnore, gitignore_check_rule
from microprojects.ngit.object import GitObject, GitCommit, GitBlob, GitTag, GitTree
from microprojects.ngit.object_utils import object_read, object_pick, object_write
from microprojects.ngit.object_utils import shortify_hash, index_read, unflat_index


def repo_default_config() -> configparser.ConfigParser:
    """Generates default configuration for repository

    Returns:
        conf_parser (ConfigParser):
            Simple config defaults with a single section (`[core]`) and three fields
    """
    conf_parser = configparser.ConfigParser()
    conf_parser.add_section("core")

    # 0 means the initial format, 1 the same with extensions.
    # If > 1, git will panic; wyag will only accept 0.
    conf_parser.set("core", "repositoryformatversion", "0")

    # enable/disable tracking of file modes (permissions) changes
    conf_parser.set("core", "filemode", "false")

    # indicates that this repository has a worktree, false sets worktree `..`
    # Git supports an optional worktree, ngit does not
    conf_parser.set("core", "bare", "false")

    return conf_parser


def repo_create(path: str, branch: str = "main", quiet: bool = False) -> GitRepository:
    """Create a new repository at path.

    Parameters:
        path (str): The path to the worktree of GitRepository
        branch (str): The initial branch in the newly created repository.
        quiet (bool): Only print error and warning messages, if True

    Returns:
        repo (GitRepository): The GitRepository just created
    """
    repo: GitRepository = GitRepository(path, force=True)

    # First, we make sure the path either doesn't exist
    #   or contain empty .git directory
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise NotADirectoryError(f"fatal: {path} is not a directory")
        if os.path.isdir(repo.git_dir) and os.listdir(repo.git_dir):
            raise FileExistsError(f"{path} is not empty")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)

    with open(repo_file(repo, "HEAD"), "wt") as file:
        file.write(f"ref: refs/heads/{branch}\n")

    # .git/description
    with open(repo_file(repo, "description"), "wt") as file:
        file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    with open(repo_file(repo, "config"), "wt") as file:
        config = repo_default_config()
        config.write(file)

    return repo


def cat_file(repo: GitRepository, sha1: str, log: bool, fmt: str | None = None) -> None:
    """Provide contents or details of GitObjects

    Parameters:
        repo (GitRepository): The current working git repository
        sha1 (str): The sha1 of object to read
        log (bool): print/log GitObject on screen or not
        fmt (str | None): The expected format of `object`

    Returns:
        None (None): have side-effect (prints on screen), so returns `None` to enforce this behavior
    """
    obj: GitObject = object_read(repo, sha1)

    if fmt is not None and fmt != obj.fmt.decode():
        print(
            f"WARNING: Invalid type '{fmt}' specified, reading '{sha1}' as '{obj.fmt.decode()}'"
        )

    if log is True:
        print(obj.data.decode())  # TODO: data can be bytes, list or dict


def object_hash(repo: GitRepository | None, file, fmt: bytes) -> str:
    """Hash-Object, and optionally write it to repo if provided

    Parameters:
        repo (GitRepository): The current working git repository
        file: The file to hash, `file.read()` should return content of file as `str`
        fmt (bytes): The format of file

    Returns:
        SHA-1 (str): The computed SHA-1 hash of object after formatting header
    """
    data: bytes = file.read()

    return object_write(repo, object_pick(fmt.decode(), data, ""))


def ls_tree(
        repo: GitRepository, sha1: str, only_trees: bool, recurse_trees: bool,
        always_trees: bool, null_terminator: bool, format_str: str, _prefix: str = "",
) -> None:  # fmt: skip
    """List the contents of a tree object

    Parameters:
        repo (GitRepository): The current working git repository
        sha1 (str): The computed SHA-1 hash of tree object whose content to show
        only_tree (bool): Show only the named tree entry itself, not its children
        recurse_tree (bool): Recurse into sub-trees
        always_tree (bool): Show tree entries even when going to recurse them
        null_terminator (bool): \\0 line termination on output and do not quote filenames.
        format_str (str): Pretty-print the contents of the tree in this format
        _prefix (str): should be empty str (`""`) on first call

    Returns:
        None (None): have side-effect (prints on screen), so returns `None` to enforce this behavior
    """

    # inlined to avoid namespace pollution
    def prettify(leaf, format_str: str, obj_fmt: str, _prefix: str) -> str:
        format_str = format_str.replace("%(objectmode)", leaf.mode)
        format_str = format_str.replace("%(objecttype)", obj_fmt)
        format_str = format_str.replace("%(objectname)", leaf.sha1)
        format_str = format_str.replace("%(path)", os.path.join(_prefix, leaf.path))

        return format_str

    obj: GitObject = object_read(repo, sha1)
    endl: str = "\0" if null_terminator else "\n"

    if type(obj) is not GitTree:
        raise TypeError(f"fatal: {sha1} do not point to valid GitTree")

    if not any([only_trees, recurse_trees, always_trees]):
        always_trees = True  # set always_trees, if no

    for leaf in obj.data:
        obj_fmt: str = ""

        match leaf.mode[:-4]:  # drop last four chars
            case "04" | "4":
                obj_fmt = "tree"
            case "10" | "12":
                obj_fmt = "blob"
            case "16":
                obj_fmt = "commit"
            case _:
                print(f"WARNING: unknown mode {leaf.mode} found in {sha1}, using blob")
                obj_fmt = "blob"

        if obj_fmt == "tree":
            if always_trees or only_trees:
                print(prettify(leaf, format_str, obj_fmt, _prefix), end=endl)
            if recurse_trees:
                ls_tree(repo, leaf.sha1, only_trees, recurse_trees, always_trees,
                    null_terminator, format_str, _prefix=os.path.join(_prefix, leaf.path))  # fmt: skip

        elif not only_trees:
            print(prettify(leaf, format_str, obj_fmt, _prefix), end=endl)


def ls_files(repo: GitRepository, fmt: str, endl: str = "\n") -> None:
    """Show information about files in the index and the working tree in desired `fmt`

    Parameters:
        repo (GitRepository): The current working git repository
        fmt (str): Pretty-print the contents of the tree in this format
        endl (str): The separater after each entry

    Returns:
        None (None): have side-effect (prints on screen), so returns `None` to enforce this behavior
    """

    def prettify(entry: GitIndexEntry, format_str: str) -> str:
        """Returns a formatted version of `format_str` using substitutions from entry

        Parameters:
            entry (GitIndexEntry): The GitIndexEntry to use for filling the `format_str`
            format_str (str): The str containing the desired format

        Returns:
            format_str (str): The format_str, with supported formats replaced by respective values
        """

        def to_iso(timestamp: int) -> str:
            return datetime.isoformat(datetime.fromtimestamp(timestamp))

        obj_type: str = {0o10: "blob", 0o12: "symlink", 0o16: "commit"}[entry.mode_type]
        obj_mode: str = f"{entry.mode_type:02o}{entry.mode_perms:04o}"
        flags: str = f"{entry.flag_assume_valid}{entry.flag_stage}"

        format_str = format_str.replace("%(objectmode)", obj_mode)
        format_str = format_str.replace("%(objecttype)", obj_type)
        format_str = format_str.replace("%(objectname)", entry.sha1)
        format_str = format_str.replace("%(objectsize)", str(entry.file_size))
        format_str = format_str.replace("%(stage)", str(entry.flag_stage))
        format_str = format_str.replace("%(path)", entry.name)

        # Extras
        format_str = format_str.replace("%(ctime)", f"{entry.ctime_s}:{entry.ctime_n}")
        format_str = format_str.replace("%(mtime)", f"{entry.mtime_s}:{entry.mtime_n}")
        format_str = format_str.replace("%(ctime:iso)", to_iso(entry.ctime_s))
        format_str = format_str.replace("%(mtime:iso)", to_iso(entry.mtime_s))
        format_str = format_str.replace("%(dev)", str(entry.dev))
        format_str = format_str.replace("%(ino)", str(entry.ino))
        format_str = format_str.replace("%(uid)", str(entry.uid))
        format_str = format_str.replace("%(gid)", str(entry.gid))
        format_str = format_str.replace("%(gid)", str(entry.gid))
        format_str = format_str.replace("%(flags)", flags)

        return format_str

    for entry in index_read(repo).entries:
        print(prettify(entry, fmt), end=endl)


def checkout(repo: GitRepository, tree: GitTree, path: str, quiet: bool) -> None:
    """Switch branches or restore working tree files

    Parameters:
        repo (GitRepository): The current working git repository
        tree (GitTree): The GitTree to checkout to
        path (str): The destination directory to checkout
        quiet (bool): Quiet, suppress feedback messages if True

    Returns:
        None (None): have side-effect (write to files), so returns `None` to enforce this behavior
    """
    for item in tree.data:
        obj: GitObject = object_read(repo, item.sha1)
        dest: str = os.path.join(path, item.path)

        if type(obj) is GitTree:
            os.makedirs(dest, exist_ok=True)
            checkout(repo, obj, dest, quiet)
        elif type(obj) is GitBlob:
            # TODO: Support symlinks (identified by mode 12****)
            with open(dest, "wb") as file:
                file.write(obj.data)


def show_ref(repo: GitRepository, refs: list, only_sha1: bool, deref: bool, prefx="refs") -> None:  # fmt: skip
    """List references in repo under ref, verify them, and print relevant information

    Parameters:
        repo (GitRepository): The current working git repository
        ref (list): a list directories and refs to show
        only_sha1 (bool): don't show ref next to SHA-1
        deref (bool): dereference tags into objectID also, shown with ^{} appended
        prefx (str): the directory in .git/ to start search for refs recursively

    Returns:
        None (None): have side-effect (print on screen), so returns `None` to enforce this behavior
    """

    for ref, val in ref_list(repo, repo_file(repo, prefx), _refs=refs).items():
        if type(val) is str:
            print(val, "" if only_sha1 else os.path.join(prefx, ref))
        else:
            show_ref(repo, val, only_sha1, deref, prefx=os.path.join(prefx, ref))


def check_ignore(rules: GitIgnore, path: str) -> bool:
    """Check whether the `path` should be ignored under given GitIgnore `rules`

    Parameters:
        rules (GitIgnore): The parsed GitIgnore rules to ckeck against
        path (str): Relative path to file of which we want to check ignore status of

    Returns:
        status (bool): True if the path will be ignored, False otherwise
    """

    if os.path.isabs(path):
        raise ValueError(f"{path=} should be relative, not absolute")

    # Checking against scoped rules first
    parent_dir: str = os.path.dirname(path)
    while True:
        if parent_dir in rules.scoped:
            status: bool | None = gitignore_check_rule(rules.scoped[parent_dir], path)
            if status is not None:
                return status
        if parent_dir == "":  # base case, reached root directory
            break

        parent_dir = os.path.dirname(parent_dir)  # recurse backward until matched

    # Check against absolute rules, if no scoped rule matched
    parent_dir = os.path.dirname(path)
    for rule in rules.absolute:
        status = gitignore_check_rule(rule, path)
        if status is not None:
            return status

    # Nothing matched, return False
    return False
