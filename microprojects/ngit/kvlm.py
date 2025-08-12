def kvlm_parse(raw_gitdata: bytes) -> dict:
    """_Key value list with message_ parser for tag and commit

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

    raise Exception("fatal: not a valid git object")


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
