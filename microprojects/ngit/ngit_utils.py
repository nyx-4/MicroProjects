import os
import configparser

from microprojects.ngit.repository import GitRepository, repo_dir, repo_file
from microprojects.ngit.object import GitObject, GitCommit, GitBlob, GitTag, GitTree
from microprojects.ngit.object_utils import object_read, object_find, object_write
from microprojects.ngit.object_utils import pick_object


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

    with open(repo_file(repo, "HEAD"), "w") as file:
        file.write(f"ref: refs/heads/{branch}\n")

    # .git/description
    with open(repo_file(repo, "description"), "w") as file:
        file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    with open(repo_file(repo, "config"), "w") as file:
        config = repo_default_config()
        config.write(file)

    return repo


def cat_file(repo: GitRepository, sha1: str, flag: int, fmt: str | None = None) -> None:
    """Provide contents or details of GitObjects

    Parameters:
        repo (GitRepository): The current working git repository
        sha1 (str): The sha1 of object to read
        flag (int): controls what information gets printed on screen (range: 1-4)
        fmt (str | None): The expected format of `object`

    Returns:
        None (None): have side-effect (prints on screen), so returns `None` to enforce this behavior
    """
    obj: GitObject = object_read(repo, object_find(repo, sha1, fmt))

    if fmt is not None and fmt != obj.fmt.decode():
        print(
            f"WARNING: Invalid type '{fmt}' specified, reading '{sha1}' as '{obj.fmt.decode()}'"
        )

    # TODO: rather than reading tuple, use int because all flags are disrete
    if flag == 1:  # only_errors
        pass
    elif flag == 2:  # only_type
        print(obj.fmt.decode())
    elif flag == 3:  # only_size
        print(len(obj.data.decode()))
    else:  # pretty_print is default
        print(obj.data.decode())


def object_hash(repo: GitRepository | None, file, fmt: bytes) -> str:
    """Hash-Object, and optionally write it to repo if provided

    Parameters:
        repo (GitRepository): The current working git repository
        file: The file to hash, `file.read()` should return content of file as `str`
        fmt (bytes): The format of file

    Returns:
        SHA-1 (str): The computed SHA-1 hash of object after formatting header
    """
    data: bytes = file.read().encode()

    return object_write(pick_object(fmt.decode(), data, ""), repo)


def ls_tree(
    repo: GitRepository,
    sha1: str,
    only_trees: bool,
    recurse_trees: bool,
    always_trees: bool,
    null_terminator: bool,
    format_str: str,
    _prefix: str = "",
) -> None:
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

    if not any([recurse_trees, always_trees, only_trees]):
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
                ls_tree(
                    repo,
                    leaf.sha1,
                    only_trees,
                    recurse_trees,
                    always_trees,
                    null_terminator,
                    format_str,
                    _prefix=os.path.join(_prefix, leaf.path),
                )
        elif not only_trees:
            print(prettify(leaf, format_str, obj_fmt, _prefix), end=endl)


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
