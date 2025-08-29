class GitObject(object):
    """A generic GitObject which will be specialized later

    Attributes:
        data (bytes | dict | list): raw data stored in GitObject
        fmt (bytes): header format: `blob`, `commit`, `tag` or `tree`
    """

    data = b""
    fmt: bytes = b""

    def __init__(self, data: bytes = None) -> None:  # type: ignore
        """Loads the Object from the provided date or create a new one

        Parameters:
            data (bytes):
        """
        if data is not None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self) -> bytes:
        """Converts self.data in a meaningful representation to store in `.git/objects/`

        Returns: The data stored in this GitObject
        """
        raise NotImplementedError("Unimplemented!")

    def deserialize(self, data: bytes) -> None:
        """Load the meaningful representation into `self`

        Parameters:
            data (bytes): raw data stored in GitObject
        """
        raise NotImplementedError("Unimplemented!")

    def init(self) -> None:
        """Create a default representation of data"""
        pass  # Just do nothing, this is a reasonable default!


class GitBlob(GitObject):
    """Blobs are simplest of GitObjects with no format, thus trivial implementation

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


class GitCommit(GitObject):
    """TODO: Add description here

    Attributes:
        data (dict):
        fmt (bytes): GitCommit uses "commit" in header format
    """

    fmt = b"commit"

    def serialize(self) -> bytes:
        return kvlm_serialize(self.data)

    def deserialize(self, data: bytes) -> None:
        self.data = kvlm_parse(data)

    def init(self) -> None:
        """Initialize an empty dict, because otherwise all objects would share same dict"""
        self.data = dict()


class GitTag(GitCommit):
    """Tags are similar to commits

    Attributes:
        data (dict):
        fmt (bytes): GitTag uses "tag" in header format
    """

    fmt: bytes = b"tag"


class GitTree(GitObject):
    """Trees contains list that associate blobs to there path

    Attributes:
        data (list): list of GitTreeLeaf that associate SHA-1 to its path
        fmt (bytes): GitTree uses "tree" in header format
    """

    fmt = b"tree"

    def serialize(self) -> bytes:
        return tree_serialize(self.data)

    def deserialize(self, data: bytes) -> None:
        self.data = tree_parse(data)

    def init(self) -> None:
        self.data = list()


class GitTreeLeaf(object):
    """Single record in GitTree

    Attributes:
        mode (str): file-system permission of respective blob
        sha1 (str): sha1 of a blob (file) or another GitTree (directory)
        path (str): path of the file in file-system
    """

    def __init__(self, mode: str, sha1: str, path: str) -> None:
        self.mode: str = mode
        self.sha1: str = sha1
        self.path: str = path


def kvlm_parse(raw_gitdata: bytes) -> dict:
    """Key value list with message parser for tag and commit

    Parameters:
        raw_gitdata (bytes): Raw commit or tag, uncompressed, without headers

    Returns:
        kvlm (dict): Key-Value pairs, best Python object for RFC2822
    """
    start: int = 0
    kvlm: dict = {}

    while start < len(raw_gitdata):
        idx_space: int = raw_gitdata.find(b" ", start)
        idx_newline: int = raw_gitdata.find(b"\n", start)

        # In git commit format, the message is preceeded by a new line
        if idx_space < 0 or idx_newline < idx_space:
            kvlm[None] = raw_gitdata[start + 1 :]
            return kvlm

        # Key's are followed by a space, then a value terminated by newline '\n'
        key: bytes = raw_gitdata[start:idx_space]

        # Use ASCII of space (bytes are more int than str)
        while raw_gitdata[idx_newline + 1] == ord(b" "):
            idx_newline = raw_gitdata.find(b"\n", idx_newline + 1)

        # Replace "\n " with "\n", its more intuitive to users, just press <ENTER>
        value: bytes = raw_gitdata[idx_space + 1 : idx_newline].replace(b"\n ", b"\n")

        # Since some keys have multiple values, so we store values in
        # Rather than having a _mixed pickle_ of bytes and lists
        if key in kvlm:
            kvlm[key].append(value)
        else:
            kvlm[key] = [value]

        start = idx_newline + 1

    raise SyntaxError("kvlm parsing failed: not a valid git/RFC2822 kvlm")


def kvlm_serialize(kvlm: dict) -> bytes:
    """Converts kvlm in RFC2822 compliant form

    Parameters:
        kvlm: Dict with appropirate information to store

    Returns:
        raw_gitdata (bytes): Raw commit or tag, uncompressed, without headers
        in git/RFC2822 compliant form
    """
    raw_gitdata: bytes = b""

    for key, values in kvlm.items():
        if key is None:  # if it is message, then skip
            continue

        # if value is not list, make it for consisteny purpose
        if type(values) is list:
            for value in values:
                raw_gitdata += key + b" " + value.replace(b"\n", b"\n ") + b"\n"
        else:
            raw_gitdata += key + b" " + values + b"\n"

    raw_gitdata += b"\n" + kvlm[None]

    return raw_gitdata


def tree_parse(raw_tree: bytes) -> list[GitTreeLeaf]:
    """GitTree parser

    Parameters:
        raw_tree (bytes): Raw tree, uncompressed, without header in valid format

    Returns:
        tree_leafs (list[GitTreeLeaf]):
    """
    start: int = 0
    tree_leafs: list[GitTreeLeaf] = []

    while start < len(raw_tree):
        idx_space: int = raw_tree.find(b" ", start)
        idx_null: int = raw_tree.find(b"\0", start)

        sha1: str = f"{int.from_bytes(raw_tree[idx_null + 1 : idx_null + 21]):040x}"

        len_mode: int = idx_space - start
        if not 5 <= len_mode <= 6:  # mode should be 5 or 6 characters long
            raise ValueError(f"length of {sha1}'s mode is {len_mode}, should be 5 or 6")

        tree_leafs.append(
            GitTreeLeaf(
                mode=raw_tree[start:idx_space].decode().rjust(6, "0"),
                path=raw_tree[idx_space + 1 : idx_null].decode(),
                sha1=sha1,
            )
        )

        start = idx_null + 21

    return tree_leafs


def tree_serialize(tree_leafs: list[GitTreeLeaf]) -> bytes:
    """Converts a list of GitTreeLeafs to GitTree, and sorts to avoid duplication

    Parameters:
        tree_leafs (list[GitTreeLeaf]): list of GitTreeLeafs to put in a GitTree

    Returns:
        raw_gitdata (bytes): uncompressed raw tree, with leafs sorted as in GitTrees
    """
    raw_tree: str = ""

    tree_leafs.sort(  # append '/' for dirs
        key=lambda leaf: leaf.path if leaf.mode.startswith("10") else leaf.path + "/"
    )

    for leaf in tree_leafs:
        raw_tree = "".join([raw_tree, leaf.mode, " ", leaf.sha1, "\0", leaf.path, "\n"])

    return raw_tree.encode()
