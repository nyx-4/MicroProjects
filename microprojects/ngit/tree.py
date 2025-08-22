class GitTreeLeaf(object):
    def __init__(self, mode: str, sha1: str, path: str) -> None:
        self.mode: str = mode
        self.sha1: str = sha1
        self.path: str = path


def tree_parse(raw_tree: bytes) -> list[GitTreeLeaf]:
    """"""
    start: int = 0
    tree_leafs: list[GitTreeLeaf] = []

    while start < len(raw_tree):
        idx_space: int = raw_tree.find(b" ", start)
        idx_null: int = raw_tree.find(b"\0", start)

        sha1: int = int.from_bytes(raw_tree[idx_null + 1 : idx_null + 21], "big")

        tree_leafs.append(
            GitTreeLeaf(
                mode=raw_tree[start:idx_space].decode().rjust(6, "0"),
                sha1=format(sha1, "040x"),
                path=raw_tree[idx_space + 1 : idx_null].decode(),
            )
        )

        start = idx_null + 21

    return tree_leafs


def tree_serialize(tree_leafs: list[GitTreeLeaf]) -> bytes:
    raw_tree: str = ""

    tree_leafs.sort(  # append '/' for dirs
        key=lambda leaf: leaf.path if leaf.mode.startswith("10") else leaf.path + "/"
    )

    for leaf in tree_leafs:
        raw_tree = "".join([raw_tree, leaf.mode, " ", leaf.sha1, "\0", leaf.path, "\n"])

    return raw_tree.encode()
