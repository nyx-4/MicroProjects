from datetime import datetime, timezone, timedelta


from microprojects.ngit.object_utils import object_read, shortify_hash
from microprojects.ngit.repository import GitRepository
from microprojects.ngit.object import GitCommit, GitObject


def print_logs(
    repo: GitRepository,
    sha1: str,
    *,
    decorate: str,
    log_size: bool,
    max_count: int,
    skip: int,
    after: str,
    before: str,
    min_parents: int,
    max_parents: int,
    format_str: str,
    date_fmt: str,
) -> None:
    """Show commit logs, according to specified flags

    Parameters:
        repo (GitRepository): The repository in which commit is located
        sha1 (str): The SHA1 hash of the commit object to start at.
        decorate (str): Also print the ref names of any commits that are shown
        log_size (bool): Include a line "log size <number>" in the output for each commit
        max_count (int): Limit the number of commits to output.
        skip (int): Skip number commits before starting to show the commit output.
        after (str): Show all commits more recent than a specific date.
        before (str): Show commits older than a specific date.
        min_parents (int): Show only commits which have at least that many parent commits.
        max_parents (int): Show only commits which have at most that many parent commits.
        format_str (str): Pretty-print the contents of the commit logs in a given format.
        date_fmt (str): The format to use for dates in `ngit log`.

    Returns:
        None (None): print_log just has side-effects, no return value
    """
    obj: GitObject = object_read(repo, sha1)

    if type(obj) is not GitCommit:
        raise TypeError(f"fatal: {sha1} do not point to valid GitCommit")

    frontier_commits: list[tuple[GitCommit, str]] = [(obj, sha1)]
    explored_commits: set[str] = {sha1}

    while frontier_commits:
        # pop the most recent commit from `frontier_commit`
        cur_commit, cur_sha1 = max(
            frontier_commits,
            key=lambda c: c[0].data.get(b"committer", [])[0].split(b" ")[-2],
        )
        frontier_commits.remove((cur_commit, cur_sha1))

        # add all unexplored parent commits in frontier_commit
        for commit in cur_commit.data.get(b"parent", []):
            commit = commit.decode()
            if commit not in explored_commits:
                obj = object_read(repo, commit)
                if type(obj) is not GitCommit:
                    raise TypeError(f"fatal: {commit} do not point to valid GitCommit")
                frontier_commits.append((obj, commit))
                explored_commits.add(commit)

        # skip if min_parent or max_parents constraints are not followed
        if min_parents > len(cur_commit.data.get(b"parent", [])):
            continue
        if max_parents >= 0 and max_parents < len(cur_commit.data.get(b"parent", [])):
            continue

        # TODO: make a separate function for handling datetime stuff
        # TODO: support other standards also for after and before
        # TODO: make checks for if the author field is missing

        # skip if after and before constraints are not followed
        _date: datetime = datetime.fromtimestamp(
            int(cur_commit.data.get(b"committer", [])[-1].split()[2]),
        )

        _date_tz: datetime = datetime.fromtimestamp(
            int(cur_commit.data.get(b"committer", [])[-1].split()[2]),
            tz(cur_commit.data.get(b"committer", [])[-1].split()[3]),
        )

        if after is not None:
            # Offset-aware (with Timezone, thus + or -) or offset-naive
            if after[-5] in "+-":
                if _date_tz < datetime.fromisoformat(after):
                    continue
            elif _date < datetime.fromisoformat(after):
                continue

        if before is not None:
            if before[-5] in "+-":
                if _date_tz > datetime.fromisoformat(before):
                    continue
            elif _date > datetime.fromisoformat(before):
                continue

        # skip this commit, if skip is positive
        if skip > 0:
            skip -= 1
            continue

        # limit the number of commits to show
        if max_count == 0:
            break
        max_count -= 1

        print(prettify(cur_commit.data, format_str, repo, cur_sha1, date_fmt))


def prettify(
    kvlm: dict, format_str: str, repo: GitRepository, commit_sha1: str, date_fmt: str
) -> str:
    """Returns a formatted version of `format_str` using substitutions from kvlm

    Parameters:
        kvlm (dict): The dict with required information to put in `format_str`
        format_str (str): The str containing the required format
        repo (GitRepository): The working repository, helps in abbriviation of commit_sha1
        commit_sha1 (str): The SHA1 of current commit, as it's not in KVLM
        date_fmt (str): The date format to use for dates

    Returns:
        format_str (str): The format_str, with supported formats replaced by respective value
    """

    # Git escape character
    format_str = format_str.replace("%n", "\n")
    format_str = format_str.replace("%%", "%")
    format_str = format_str.replace("%m", "<")

    # Replace colors with ANSI escape
    format_str = format_str.replace("%Cblack", "\033[30m")
    format_str = format_str.replace("%Cred", "\033[31m")
    format_str = format_str.replace("%Cgreen", "\033[32m")
    format_str = format_str.replace("%Cyellow", "\033[33m")
    format_str = format_str.replace("%Cblue", "\033[34m")
    format_str = format_str.replace("%Cmagenta", "\033[35m")
    format_str = format_str.replace("%Ccyan", "\033[36m")
    format_str = format_str.replace("%Cwhite", "\033[37m")
    format_str = format_str.replace("%Creset", "\033[39m")
    format_str = format_str.replace("%Cauto", "\033[39m")
    format_str = format_str.replace("%C(auto)", "\033[39m")

    # KVLM-extracted information
    shortify = shortify_hash(repo)

    format_str = format_str.replace("%H", commit_sha1)
    format_str = format_str.replace("%h", abbrified([commit_sha1.encode()], shortify))
    format_str = format_str.replace("%T", longified(kvlm.get(b"tree", [])))
    format_str = format_str.replace("%t", abbrified(kvlm.get(b"tree", []), shortify))
    format_str = format_str.replace("%P", longified(kvlm.get(b"parent", [])))
    format_str = format_str.replace("%p", abbrified(kvlm.get(b"parent", []), shortify))

    # Author information
    author: list = list(zip(*map(bytes.split, kvlm.get(b"author", []))))

    format_str = format_str.replace("%an", longified(author[0]))
    format_str = format_str.replace("%ae", longified(map(lambda x: x[1:-1], author[1])))
    format_str = format_str.replace(
        "%al", longified(map(lambda x: x[1 : x.index(b"@")], author[1]))
    )

    format_str = format_str.replace(
        "%ad", fmt_date(kvlm.get(b"author", []), _ftime(date_fmt))
    )
    format_str = format_str.replace(
        "%aD", fmt_date(kvlm.get(b"author", []), _ftime("rfc2822"))
    )
    format_str = format_str.replace("%at", longified(author[2]))
    format_str = format_str.replace(
        "%ai", fmt_date(kvlm.get(b"author", []), _ftime("iso8601"))
    )
    format_str = format_str.replace(
        "%aI", fmt_date(kvlm.get(b"author", []), _ftime("iso8601-strict"))
    )
    format_str = format_str.replace(
        "%as", fmt_date(kvlm.get(b"author", []), _ftime("short"))
    )

    # Committer information
    committer: list = list(zip(*map(bytes.split, kvlm.get(b"committer", []))))

    format_str = format_str.replace("%cn", longified(committer[0]))
    format_str = format_str.replace(
        "%ce", longified(map(lambda x: x[1:-1], committer[1]))
    )
    format_str = format_str.replace(
        "%cl", longified(map(lambda x: x[1 : x.index(b"@")], committer[1]))
    )

    format_str = format_str.replace(
        "%cd", fmt_date(kvlm.get(b"committer", []), _ftime(date_fmt))
    )
    format_str = format_str.replace(
        "%cD", fmt_date(kvlm.get(b"committer", []), _ftime("rfc2822"))
    )
    format_str = format_str.replace("%ct", longified(committer[2]))
    format_str = format_str.replace(
        "%ci", fmt_date(kvlm.get(b"committer", []), _ftime("iso8601"))
    )
    format_str = format_str.replace(
        "%cI", fmt_date(kvlm.get(b"committer", []), _ftime("iso8601-strict"))
    )
    format_str = format_str.replace(
        "%cs", fmt_date(kvlm.get(b"committer", []), _ftime("short"))
    )

    commit_msg: tuple = kvlm.get(None, b"\n").decode().partition("\n")
    format_str = format_str.replace("%s", commit_msg[0])
    format_str = format_str.replace("%b", commit_msg[2][1:])
    format_str = format_str.replace("%B", kvlm.get(None, b"\n").decode())

    return format_str


def longified(values) -> str:
    """Join all values, space separated, in a list"""
    return b" ".join(values).decode()


def abbrified(values, shortify) -> str:
    """Join all values, space separated, in a list after applying shortify on all of them"""
    return b" ".join(map(shortify, values)).decode()


def tz(time_zone: bytes) -> timezone:
    """A helper function to return timezone based on"""
    return timezone(timedelta(hours=int(time_zone) / 100))


def fmt_date(authors: list, time_format: str) -> str:
    """Extract timestamp and timezone from author field, and format them as specified in `time_format`"""
    values: list[str] = [
        datetime.fromtimestamp(int(time_stamp), tz(time_zone)).strftime(time_format)
        for _, _, time_stamp, time_zone in map(bytes.split, authors)
    ]
    return " ".join(values)


def _ftime(fmt: str) -> str:
    """Convert human-readable/standard time formats to one used by `strftime`"""
    fmt = fmt.lower()
    match fmt:
        case "local":
            return ""
        case "iso" | "iso8601":
            return "%Y-%m-%d %H:%M:%S %z"
        case "iso-strict" | "iso8601-strict":
            return "%Y-%m-%dT%H:%M:%S%:z"
        case "rfc" | "rfc2822":
            return "%a, %-d %b %Y %H:%M:%S %z"
        case "short":
            return "%Y-%m-%d"
        case "default":
            return "%c %z"
        case _:
            return fmt
