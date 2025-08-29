import hashlib  # ngit uses SHA-1 hash extensively
import os  # os and os.path provide some nice filesystem abstraction routines
import zlib  # to compress & decompress files
import sys  # to access `sys.argv`


from microprojects.ngit.repository import GitRepository, repo_file
from microprojects.ngit.object import GitObject, GitBlob, GitCommit, GitTag, GitTree


def object_read(repo: GitRepository, sha1: str) -> GitObject:
    """Read the object stored in `.git/objects/$sha1`, decompress and then deserialize data

    Parameters:
        repo (GitRepository): The current working git repository
        sha1 (str): The SHA-1 hash of the object to read

    Returns:
        GitObject (GitObject): Appropirate GitObject with deserialized data
    """
    file_path: str = repo_file(repo, "objects", sha1[:2], sha1[2:])

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"object with name {sha1} not found")

    with open(file_path, "rb") as obj_file:
        raw_file: bytes = zlib.decompress(obj_file.read())

        idx_space: int = raw_file.find(b" ")  # The index of first space in raw_file
        idx_null: int = raw_file.find(b"\x00")  # The index of first null in raw_file

        fmt: bytes = raw_file[:idx_space]  # fmt followed by a space (0x20)
        size: int = int(raw_file[idx_space + 1 : idx_null])  # size is followed by 0x00

        # Check for accidental changes in file
        if size != len(raw_file) - idx_null - 1:
            print(f"WARNING: Malformed object {sha1}: bad length")

    return pick_object(fmt.decode(), raw_file[idx_null + 1 :], sha1)


def pick_object(fmt: str, data, sha1="") -> GitObject:
    """Pick the respective class to return

    Parameters:
        fmt (str): the header format: one of `blob`, `commit`, `tag` or `tree`
        sha1 (str): SHA-1 hash for debug purpose only, optional

    Returns:
        GitObject: Actually SubClass of GitObject depending on `fmt`
    """
    match fmt:
        case "blob":
            return GitBlob(data)
        case "commit":
            return GitCommit(data)
        case "tag":
            return GitTag(data)
        case "tree":
            return GitTree(data)
        case _:
            print(f"WARNING: unknown type {fmt} for object {sha1} using blob")
            return GitBlob(data)


def object_write(obj: GitObject, repo: GitRepository | None = None) -> str:
    """Writing an object is reading it in reverse: we compute the hash, insert the header,
    zlib-compress everything and write the result in the correct location.

    Parameters:
        obj (GitObject): The GitObject that we want to write in `.git/objects/`
        repo (GitRepository): The current working git repository

    Returns:
        SHA-1 (str): The computed SHA-1 hash of object after formatting header
    """
    data: bytes = obj.serialize()

    # Header: format, space, size, NULL, data
    result: bytes = obj.fmt + b" " + str(len(data)).encode() + b"\x00" + data

    sha1: str = hashlib.sha1(result).hexdigest()

    if repo:
        file_path: str = repo_file(repo, "objects", sha1[:2], sha1[2:], mkdir=True)

        if not os.path.exists(file_path):
            with open(file_path, "wb") as raw_file:
                # Compress and write
                raw_file.write(zlib.compress(result))

    return sha1


def object_find(repo: GitRepository, name: str, fmt=None, follow=True) -> str:
    """Resolve name to an Object in GitRepository, will be implemented later."""
    sha1: str = name

    return sha1


class shortify_hash:
    """Returns a shortened version of sha1, atleast of length 7, that identifies
    the object uniquely

    """

    # TODO: Implement using `functool`, rather than class
    repo: GitRepository

    def __init__(self, repo: GitRepository) -> None:
        self.repo = repo

    def __call__(self, sha1: str) -> str:
        """Returns short hash"""

        return sha1[:7]
