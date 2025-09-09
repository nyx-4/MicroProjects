import hashlib  # ngit uses SHA-1 hash extensively
import os  # os and os.path provide some nice filesystem abstraction routines
import zlib  # to compress & decompress files
import re


from microprojects.ngit.repository import GitRepository, repo_file, resolve_ref
from microprojects.ngit.repository import repo_dir
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

    return object_pick(fmt.decode(), raw_file[idx_null + 1 :], sha1)


def object_pick(fmt: str, data: bytes, sha1="") -> GitObject:
    """Pick the respective class to return

    Parameters:
        fmt (str): the header format: one of `blob`, `commit`, `tag` or `tree`
        data (bytes): The raw data to store in GitObject
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


def object_write(repo: GitRepository | None, obj: GitObject) -> str:
    """Writing an object is reading it in reverse: we compute the hash, insert the header,
    zlib-compress everything and write the result in the correct location

    Parameters:
        repo (GitRepository): The git repository where to write object
            (pass `None` if you don't want to write in repo)
        obj (GitObject): The GitObject that we want to write in `.git/objects/`

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


def object_find(
    repo: GitRepository, ref: str, fmt: str | None = None, follow: bool = True
) -> str | None:
    """Find a unique object (if any) that can be referenced as `ref` in git

    Parameters:
        repo (GitRepository): The GitRepository in which `ref` is located
        ref (str): The ref, short-hash, long-hash etc. used to represent an object
        fmt (str | None): (optional) expected format of `ref`
        follow (bool): whether to follow tags or not

    Returns:
        SHA-1 (str | None): The long-hash of object referenced by `ref` or None if `fmt` mismatch

    Raises:
        NameError: if no object can be referenced as `ref`
        ReferenceError: if multiple objects can be referenced as `ref`
    """
    sha1 = object_resolve(repo, ref)

    if not sha1:
        raise NameError(f"fatal: no object with reference {ref} found")

    if len(sha1) > 1:
        cands: str = "\n - ".join(sha1)
        raise ReferenceError(f"ambiguous {ref=}, possible candidate are:\n - {cands}")

    sha1 = sha1.pop()  # since len(sha1) is 1, so pop() will return only available value
    assert type(sha1) is str, f"{sha1=} should be str"

    if not fmt:  # if fmt not specified, return the sha1 as is
        return sha1

    while True:
        obj: GitObject = object_read(repo, sha1)

        if obj.fmt.decode() == fmt:  # if fmt matches, return sha1
            return sha1

        if not follow:
            return None

        if type(obj) is GitTag:  # follow GitTag
            sha1 = obj.data[b"object"][0].decode()
        elif type(obj) is GitCommit and fmt == "tree":  # get tree from commit
            return obj.data[b"tree"][0].decode()
        else:
            return None


def object_find_f(
    repo: GitRepository, name: str, fmt: str | None = None, follow: bool = True
) -> str:
    """Helper function that do not return None, to avoid typing hell"""
    obj: str | None = object_find(repo, name, fmt, follow)

    if obj is None:
        raise ValueError(f"fatal: fmt of {name} is not {fmt}")
    else:
        return obj


def object_resolve(repo: GitRepository, obj_name: str) -> set:
    """Resolve name to an object hash in repo (where name is short-hash, long-hash, 'HEAD', tags, branches etc)

    Parameters:
        repo (GitRepository): The Git Repository in which `obj_name` is located
        obj_name (Str): The ref, short-hash, long-hash etc. used to represent an object

    Returns:
        candidates (set[str]): possible candidates for `obj_name` in `repo` without duplicates
    """
    candidates: set[str] = set()

    if not obj_name.strip():  # empty obj_name matches nothing
        return set()

    if obj_name == "HEAD":  # HEAD resolves to HEAD
        return {resolve_ref(repo, "HEAD")}

    if re.match(r"^[0-9a-fA-F]{4,40}$", obj_name):  # Try obj_name for hash of len 4-40
        sha1: str = obj_name.lower()
        if obj_dir := repo_dir(repo, "objects/" + sha1[:2]):
            candidates.update(  # append all objects that starts with matches obj_name
                sha1[:2] + _ for _ in os.listdir(obj_dir) if _.startswith(sha1[2:])
            )

    for ref_type in ["tags", "heads", "remotes"]:
        if ref := resolve_ref(repo, f"refs/{ref_type}/{obj_name}"):
            candidates.add(ref)

    return candidates


def shortify_hash(repo: GitRepository, sha1: str) -> str:
    """Returns a shortened version of sha1, atleast of length 7, that identifies
    the object uniquely

    """
    # TODO: implement shortify hash properly
    return sha1[:7]


def tag_create(
    repo: GitRepository, tagname: str, sha1: str, message: str = "", mkobj: bool = False
) -> str:
    """Create a tagfile in `.git/refs/tags` and optionally make a GitTag object in `.git/objects`

    Parameters:
        repo (GitRepository): The git repository where to make a tag
        tagname (str): The name of new tag (used in GitTag's `tag` field)
        sha1 (str): The SHA-1 of commit or object that this tag refers to
        message (str): The tag message to use in GitTag object (optional)
        mkobj (str): Whether to make a GitTag object in `.git/objects` or not

    Returns:
        SHA-1 (str): SHA-1 of GitTag object object (if mkobj) or `sha1` that is passed in
    """

    if mkobj:  # create tag object in .git/objects also
        tag_obj = GitTag()

        tag_obj.data = {
            b"object": sha1.encode(),
            b"type": b"commit",  # TODO: get proper type of sha1
            b"tag": tagname.encode(),
            b"tagger": b"Nyx <nyx@example.com> 1756495905 +0500",  # TODO: read from config file
            None: message.encode(),
        }

        sha1 = object_write(repo, tag_obj)  # update sha1 to point to GitTag

    # write to refs/tags regardless of `annotate` flag
    with open(repo_file(repo, f"refs/tags/{tagname}"), "w") as tag_file:
        tag_file.write(sha1 + "\n")

    return sha1
