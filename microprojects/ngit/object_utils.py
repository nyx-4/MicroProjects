import hashlib
import os
import zlib
import re


from microprojects.ngit.repository import GitRepository, repo_file, resolve_ref
from microprojects.ngit.repository import repo_dir, GitIndex, GitIndexEntry, GitIgnore
from microprojects.ngit.repository import gitignore_parse
from microprojects.ngit.object import GitObject, GitBlob, GitCommit, GitTag, GitTree
from microprojects.ngit.object import GitTreeLeaf


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


def get_obj_type(repo: GitRepository, sha1: str) -> str:
    """Get object's type without fully parsing the GitObject"""
    with open(repo_file(repo, "objects", sha1[:2], sha1[2:]), "rb") as obj_file:
        return zlib.decompress(obj_file.read()).split(b" ", 1)[0].decode()


def get_obj_size(repo: GitRepository, sha1: str) -> int:
    """Get object's size after decompressing"""
    with open(repo_file(repo, "objects", sha1[:2], sha1[2:]), "rb") as obj_file:
        return len(zlib.decompress(obj_file.read()))


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
    # TODO: add `--abbrev=[n]` in ngit sub-commands that supports it
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
            b"type": get_obj_type(repo, sha1).encode(),
            b"tag": tagname.encode(),
            b"tagger": f"{repo.conf['user']['name']} <{repo.conf['user']['email']}>".encode(),
            None: message.encode(),
        }

        sha1 = object_write(repo, tag_obj)  # update sha1 to point to GitTag

    # write to refs/tags regardless of `annotate` flag
    with open(repo_file(repo, f"refs/tags/{tagname}"), "wt") as tag_file:
        tag_file.write(sha1 + "\n")

    return sha1


def index_read(repo: GitRepository) -> GitIndex:
    """Like GitTrees, GitIndex is also stored in binary format

    Parameters:
        repo (GitRepository): GitRepository of whose GitIndex we want to read

    Returns:
        index (GitIndex): The parsed GitIndex of `repo`
    """

    def bin_read(raw_data: bytes) -> int:
        """A helper function to converts big-endian bytes to int"""
        return int.from_bytes(raw_data, byteorder="big")

    index_file: str = repo_file(repo, "index")

    # New repositories do not have .git/index file
    if not os.path.exists(index_file):
        return GitIndex()

    with open(index_file, "rb") as file:
        raw_idx: bytes = file.read()

    signature: bytes = raw_idx[:4]
    if signature != b"DIRC":
        print(f"WARNING: signature should be b'DIRC', got {signature=}")

    version: int = bin_read(raw_idx[4:8])
    if version != 2:
        print(f"WARNING: only version 2 GitIndex is supported, got {version=}")
    if version == 0:
        print("WARNING: force setting GitIndex version to 2")
        version = 2

    len_entries: int = bin_read(raw_idx[8:12])
    entries: list[GitIndexEntry] = []

    idx: int = 0
    raw_idx = raw_idx[12:]  # 12 bytes are already read

    for _ in range(len_entries):
        flags: int = bin_read(raw_idx[idx + 60 : idx + 62])

        kwargs: dict[str, int] = {  # some kwargs to pass to GitIndexEntry()
            "ctime_s": bin_read(raw_idx[idx + 0 : idx + 4]),
            "ctime_n": bin_read(raw_idx[idx + 4 : idx + 8]),
            "mtime_s": bin_read(raw_idx[idx + 8 : idx + 12]),
            "mtime_n": bin_read(raw_idx[idx + 12 : idx + 16]),
            "dev": bin_read(raw_idx[idx + 16 : idx + 20]),
            "ino": bin_read(raw_idx[idx + 20 : idx + 24]),
            "mode_type": bin_read(raw_idx[idx + 26 : idx + 28]) >> 12,
            "mode_perms": bin_read(raw_idx[idx + 26 : idx + 28]) & 0x1FF,
            "uid": bin_read(raw_idx[idx + 28 : idx + 32]),
            "gid": bin_read(raw_idx[idx + 32 : idx + 36]),
            "file_size": bin_read(raw_idx[idx + 36 : idx + 40]),
            "flag_assume_valid": flags & 0x8000,
            "flag_stage": flags & 0x3000,
        }
        sha1: str = format(bin_read(raw_idx[idx + 40 : idx + 60]), "040x")

        idx += 62  # read 62 bytes thus far
        len_name: int = flags & 0xFFF

        if len_name < 0xFFF:  # normal case, len(name) is given
            assert raw_idx[idx + len_name] == 0x00, f"No NULL at {idx + len_name=}"
            raw_name: bytes = raw_idx[idx : idx + len_name]
            idx += len_name + 1
        else:
            idx_null: int = raw_idx.find(b"\x00", idx + 0xFFF)
            raw_name = raw_idx[idx:idx_null]
            idx += idx_null + 1

        idx = (idx + 7) & ~7  # ceil to next multiple of 8

        entries.append(GitIndexEntry(**kwargs, sha1=sha1, name=raw_name.decode()))
    return GitIndex(version=version, entries=entries)


def index_write(repo: GitRepository, index: GitIndex) -> None:
    """Serialize GitIndex back to binary format and write to `.git/index`

    Parameters:
        repo (GitRepository): The repo whose GitIndex we want to update
        index (GitIndex): The index to write in GirRepository

    Returns:
        None (None): have side-effect (write to files), so returns `None` to enforce this behavior
    """

    def _bin(number: int) -> bytes:
        """A helper function to converts int to 4 big-endian bytes"""
        return number.to_bytes(4, "big")

    with open(repo_file(repo, "index"), "wb") as idx:
        if index.version == 0:
            print("WARNING: The GitIndex version specified is 0, force setting to 2")
            index.version = 2

        idx.write(b"DIRC")
        idx.write(_bin(index.version))
        idx.write(_bin(len(index.entries)))

        i: int = 0
        for entry in index.entries:
            idx.write(_bin(entry.ctime_s))
            idx.write(_bin(entry.ctime_n))
            idx.write(_bin(entry.mtime_s))
            idx.write(_bin(entry.mtime_n))
            idx.write(_bin(entry.dev))
            idx.write(_bin(entry.ino))
            idx.write(_bin((entry.mode_type << 12) | entry.mode_perms))
            idx.write(_bin(entry.uid))
            idx.write(_bin(entry.gid))
            idx.write(_bin(entry.file_size))
            idx.write(int(entry.sha1, 16).to_bytes(20, "big"))

            len_name: int = len(entry.name.encode())
            flag: int = 1 << 15 if entry.flag_assume_valid else 0
            idx.write((flag | entry.flag_stage | len_name).to_bytes(2, "big"))

            idx.write(entry.name.encode())
            idx.write((0).to_bytes(1, "big"))

            i += 62 + len_name + 1

            if i % 8 != 0:
                pad: int = 8 - (i % 8)
                idx.write((0).to_bytes(pad, "big"))
                i += pad


def gitignore_read(repo: GitRepository) -> GitIgnore:
    """Read all .gitignore files (both scoped and global), parse them, and return as GitIgnore

    Parameters:
        repo (GitRepository): The repo whose .gitignore files we want to parse

    Returns:
        ignore_list (GitIgnore): A list of absolute and scoped .gitignore rules
    """
    ignore_list: GitIgnore = GitIgnore(absolute=[], scoped={})

    # Read local configuration in .git/info/exclude
    local_gitignore: str = repo_file(repo, "info/exclude")

    # Read global configuration in $XDG_CONFIG_HOME/git/ignore
    if "XDG_CONFIG_HOME" in os.environ:  # check for $XDG_CONFIG_HOME
        global_gitignore = os.path.join(os.environ["XDG_CONFIG_HOME"], "git/ignore")
    else:  # else fall-back to ~/.config
        global_gitignore = os.path.expanduser("~/.config/git/ignore")

    # Parse local and global .gitignore configurations
    for gitignore_path in (local_gitignore, global_gitignore):
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "rt") as ignore_file:
                ignore_list.absolute.append(gitignore_parse(ignore_file.readlines()))

    #
    # Read scoped configuration (staged .gitignore files in .git/index)
    index: GitIndex = index_read(repo)
    for i in index.entries:
        if i.name == ".gitignore" or i.name.endswith("/.gitignore"):
            key: str = os.path.dirname(i.name)
            rules: list[str] = object_read(repo, i.sha1).data.decode().splitlines()
            ignore_list.scoped[key] = gitignore_parse(rules)

    ignore_list.absolute.append([(".git", True)])  # ignore `.git/` by default

    return ignore_list


def flatten_tree(repo: GitRepository, ref: str, prefix: str = "") -> dict[str, str]:
    """Convert recursive tree into flat dict to use with GitIndex

    Parameters:
        repo (GitRepository): The repo in which tree is located
        ref (str): Git reference to the `tree` we wish to flatten
        prefix (str): Internal use only (pass `""` in first call)

    Returns:
        flat_tree (dict[str, str]): flat tree with same entries as original tree (`ref`)
    """
    flat_tree: dict[str, str] = {}
    tree: GitObject = object_read(repo, object_find_f(repo, ref, fmt="tree"))

    assert type(tree) is GitTree

    for leaf in tree.data:
        if leaf.mode.startswith("04"):
            # dict1.update(dict2) appends dict2 in dict1 (like union on sets)
            flat_tree.update(flatten_tree(repo, leaf.sha1, prefix + leaf.path + "/"))
        else:
            flat_tree[prefix + leaf.path] = leaf.sha1

    return flat_tree


def unflat_index(repo: GitRepository, index: GitIndex) -> str:
    """Convert a flat tree (used in GitIndex) to a recursive format used by GitTree

    **WARNING**: This function has side-effects (write to file), use with precaution

    Parameters:
        repo (GitRepository): The repo in which `index` is located
        index (GitIndex): A GitIndex which contains required entries to put in tree

    Returns:
        SHA-1 (str): The SHA-1 of the root tree written by this function
    """
    contents: dict[str, list[GitIndexEntry | tuple]] = {"": []}

    # build contents in recursive form with each sub_dir appearing once
    for entry in index.entries:
        dirname: str = os.path.dirname(entry.name)

        key: str = dirname
        while key != "":
            if key not in contents:
                contents[key] = []
            key = os.path.dirname(key)

        contents[dirname].append(entry)

    sha1: str = ""
    sorted_paths: list[str] = sorted(contents.keys(), key=len, reverse=True)

    for path in sorted_paths:
        tree: GitTree = GitTree()

        for entry in contents[path]:
            if type(entry) is GitIndexEntry:
                mode: str = f"{entry.mode_type:02o}{entry.mode_perms:04o}"  # to octal
                leaf = GitTreeLeaf(mode, entry.sha1, os.path.basename(entry.name))
            elif type(entry) is tuple:  # tuple(basename, sha1)
                leaf = GitTreeLeaf("040000", path=entry[0], sha1=entry[1])
            else:
                raise ValueError(f"{contents} must only contain GitIndexEntry or tuple")

            tree.data.append(leaf)

        sha1 = object_write(repo, tree)
        basename: str = os.path.basename(path)
        parent: str = os.path.dirname(path)

        contents[parent].append((basename, sha1))

    return sha1
