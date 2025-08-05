from microprojects.ngit.object import GitObject
from microprojects.ngit.kvlm import kvlm_serialize, kvlm_parse


class GitCommit(GitObject):
    """

    Attributes:
        data (dict):
        fmt (bytes):
    """

    fmt = b"commit"

    def serialize(self) -> bytes:
        return kvlm_serialize(self.data)

    def deserialize(self, kvlm: bytes) -> None:
        self.data = kvlm_parse(kvlm)

    def init(self) -> None:
        """Initialize an empty dict, because otherwise all objects would share same dict"""
        self.data = dict()
