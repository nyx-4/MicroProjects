import hashlib  # ngit uses SHA-1 hash extensively
import os  # os and os.path provide some nice filesystem abstraction routines
import zlib  # to compress & decompress files
import sys  # to access `sys.argv`


from microprojects.ngit.repository import GitRepository, repo_file


class GitObject(object):
    """A generic GitObject which will be specialized later.

    Attributes:
        data (bytes | dict): raw data stored in GitObject
        fmt (bytes): header format: `blob`, `commit`, `tag` or `tree`
    """

    data: bytes | dict = b""
    fmt: bytes = b""

    def __init__(self, data: bytes | dict | None = None) -> None:
        """Loads the Object from the provided date or create a new one.

        Parameters:
            data (bytes | dict):
        """
        if data is not None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self) -> bytes:
        """Converts self.data in a meaningful representation to store in `.git/objects/`

        Returns: The data stored in this GitObject
        """
        raise Exception("Unimplemented!")

    def deserialize(self, data: bytes) -> None:
        """Load the meaningful representation into `self`

        Parameters:
            data (bytes): raw data stored in GitObject
        """
        raise Exception("Unimplemented!")

    def init(self) -> None:
        """Create a default representation of data."""
        pass  # Just do nothing. This is a reasonable default!


class GitBlob(GitObject):
    """Blobs are simplest of GitObjects with no format, thus trivial implementation.

    Attributes:
        data (bytes): raw blob-data stored in GitBlob
        fmt (bytes): GitBlob uses "blob" in header format
    """

    fmt = b"blob"

    def serialize(self) -> bytes:
        """Convert data into Git's representation of a blob

        Returns:
            data (bytes): raw blob-data stored in this GitBlob
        """
        return self.data

    def deserialize(self, data: bytes) -> None:
        """Load the data from a blob into `self`

        Parameters:
            data (bytes): raw blob-data that is read from `.git/objects`
        """
        self.data = data


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
        raise Exception(f"Not a valid object name: {sha1}")

    with open(file_path, "rb") as obj_file:
        raw_file: bytes = zlib.decompress(obj_file.read())

        idx_space: int = raw_file.find(b" ")  # The index of first space in raw_file
        idx_null: int = raw_file.find(b"\x00")  # The index of first null in raw_file

        fmt: bytes = raw_file[:idx_space]  # fmt followed by a space (0x20)
        size: int = int(raw_file[idx_space + 1 : idx_null])  # size is followed by 0x00

        # Check for accidental changes in file
        if size != len(raw_file) - idx_null - 1:
            raise Exception(f"Malformed object {sha1}: bad length")

        # Pick the respective class to return
        match fmt:
            case b"blob":
                return GitBlob(raw_file[idx_null + 1 :])
            # case b"commit":   return GitCommit(raw_file[idx_null:])
            # case b"tag":      return GitTag(raw_file[idx_null:])
            # case b"tree":     return GitTree(raw_file[idx_null:])
            case _:
                raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha1}")


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


def object_hash(file, fmt: bytes, repo: GitRepository | None = None) -> str:
    """Hash-Object, and optionally write it to repo if provided."""
    data: bytes = file.read().encode()

    match fmt:
        case b"blob":
            obj = GitBlob(data)
        # case b"commit":
        #     obj = GitCommit(data)
        # case b"tag":
        #     obj = GitTag(data)
        # case b"tree":
        #     obj = GitTree(data)
        case _:
            raise Exception(f"Unknown type {fmt.decode('ascii')} for object")

    return object_write(obj, repo)


def object_find(repo: GitRepository, name: str, fmt=None, follow=True) -> str:
    """Resolve name to an Object in GitRepository, will be implemented later."""
    sha1: str = name

    return sha1


def cat_file(repo: GitRepository, object: str, flag: tuple, fmt: str | None) -> None:
    """Provide contents or details of GitObjects"""
    obj: GitObject = object_read(repo, object_find(repo, object, fmt))

    if fmt is not None and fmt != obj.fmt.decode():
        print(
            f"Warning: Invalid type '{fmt}' specified, reading '{object}' as '{obj.fmt.decode()}'"
        )

    if flag[0]:  # only_errors
        pass
    elif flag[2]:  # only_type
        print(obj.fmt.decode())
    elif flag[3]:  # only_size
        print(len(obj.data.decode()))
    else:  # pretty_print is Default
        print(obj.data.decode())
