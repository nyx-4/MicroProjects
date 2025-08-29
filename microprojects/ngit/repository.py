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
            raise TypeError(f"fatal: not a git repository: {path}")

        # Read configuration files in .git/config
        self.conf = configparser.ConfigParser()
        conf_file = repo_path(self, "config")

        # Read version number and raise if ver != 0
        if conf_file and os.path.exists(conf_file):
            self.conf.read([conf_file])
        elif not force:
            raise FileNotFoundError("Configuration file missing")

        if not force:
            ver: int = int(self.conf.get("core", "repositoryformatversion"))
            if ver != 0:
                raise NotImplementedError(f"unsupported repositoryformatversion: {ver}")


def repo_path(repo: GitRepository, *path: str) -> str:
    """Compute path under repo's git/ directory

    Parameters:
        repo (GitRepository): The current working git repository
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
    """Same as repo_path, but create dirname(*path) if absent

    Parameters:
        repo (GitRepository): The current working git repository
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
        raise FileNotFoundError(f"{path} do not exists and mkdir not specified")


def repo_dir(repo: GitRepository, *path: str, mkdir: bool = False) -> str | None:
    """Same as repo_path, but mkdir *path if absent if mkdir

    Parameters:
        repo (GitRepository): The current working git repository
        *path (str): The path in .git/
        mkdir (bool): Make directory if it doesn't exists

    Returns:
        path (str): The *path, but prefixed with $worktree/.git and delimited properly  \n
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
    """Helper function that do not return None, to avoid typing hell"""
    return repo_find(path, required=True)  # type: ignore
