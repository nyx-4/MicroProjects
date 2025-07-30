import configparser  # ngit's config file uses INI format
import os  # os and os.path provide some nice filesystem abstraction routines


class GitRepository(object):
    """A git repository abstraction

    Attributes:
        worktree (str): The root-directory of repository
        git_dir (str): The .git directory in the worktree
        conf (ConfigParser): The .git/config file parser
    """

    worktree: str = ""
    git_dir: str = ""
    conf = None

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
            raise Exception(f"fatal: not a git repository: {path}")

        # Read configuration files in .git/config
        self.conf = configparser.ConfigParser()
        conf_file = repo_path(self, "config")

        # Read version number and raise if ver != 0
        if conf_file and os.path.exists(conf_file):
            self.conf.read([conf_file])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers: int = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")


def repo_path(repo: GitRepository, *path: str) -> str:
    """Compute path under repo's git/ directory

    Parameters:
        repo (GitRepository): The working git repository
        *path (str): The path in .git/

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly

    Examples:
        ```
        repo_path(repo, "refs", "remotes", "origin", "HEAD")
        # return $worktree/.git/refs/remotes/origin/HEAD
        ```
    """
    return os.path.join(repo.git_dir, *path)


def repo_file(repo: GitRepository, *path: str, mkdir: bool = False) -> str:
    """Same as repo_path, but create dirname(*path) if absent.

    Parameters:
        repo (GitRepository): The working git repository
        *path (str): The path in .git/

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly

    Examples:
        ```
        repo_file(repo, "refs", "remotes", "origin", "HEAD")
        # return $worktree/.git/refs/remotes/origin/HEAD
        ```
    """
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)
    else:
        raise Exception(f"{path} do not exists and mkdir not specified")


def repo_dir(repo: GitRepository, *path: str, mkdir: bool = False) -> str | None:
    """Same as repo_path, but mkdir *path if absent if mkdir.

    Parameters:
        repo (GitRepository): The working git repository
        *path (str): The path in .git/
        mkdir (bool): Make directory if it doesn't exists

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly.  \n
            Returns **None** if *path do not exist, and mkdir is not specified.

    Examples:
        ```
        repo_dir(repo, "refs", "remotes", "origin")
        # return $worktree/.git/refs/remotes/origin/
        ```
    """
    git_path: str = repo_path(repo, *path)

    if os.path.exists(git_path):
        if os.path.isdir(git_path):
            return git_path
        else:
            raise Exception(f"Not a directory {path}")

    elif mkdir:
        os.makedirs(git_path)
        return git_path
    else:
        return None


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
            raise Exception(f"fatal: {path} is not a directory")
        if os.path.isdir(repo.git_dir) and os.listdir(repo.git_dir):
            raise Exception(f"{path} is not empty")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)

    with open(repo_file(repo, "HEAD"), "w") as file:
        file.write("ref: refs/heads/main\n")

    # .git/description
    with open(repo_file(repo, "description"), "w") as file:
        file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    with open(repo_file(repo, "config"), "w") as file:
        config = repo_default_config()
        config.write(file)

    return repo


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


def repo_find(path: str = ".", required: bool = True) -> GitRepository | None:
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    parent: str = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # Base-case i.e., os.path.join("/", "..") is "/"
        if required:
            raise Exception("fatal: not a git repository")
        else:
            return None

    return repo_find(parent, required)
