import argparse  # ngit is CLI tool, so we need to parse CLI args

# import configparser  # ngit's config file uses INI format
# from datetime import datetime  # to store time of each commit
# import grp, pwd  # because ngit saves numerical owner/group ID of files author
# from fnmatch import fnmatch  # to match .gitignore patterns like *.txt
# import hashlib  # ngit uses SHA-1 hash extensively
# import math
import os  # os and os.path provide some nice filesystem abstraction routines

# import re  # just a little-bit of RegEx
import sys  # to access `sys.argv`
# import zlib  # to compress & decompress files

from microprojects.ngit.object import GitObject, GitCommit, GitTree
from microprojects.ngit.repository import GitRepository, repo_file, repo_find_f
from microprojects.ngit.repository import resolve_ref, ref_list, tag_list
from microprojects.ngit.object_utils import object_find_f, object_read, tag_create
from microprojects.ngit.ngit_utils import cat_file, ls_tree, object_hash, repo_create
from microprojects.ngit.ngit_utils import checkout, show_ref
from microprojects.ngit.log import print_logs


def ngit_main() -> None:
    # The ngit's main (arg_)parser
    parser = argparse.ArgumentParser(
        prog="ngit",
        description="ngit - the stupid content tracker",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # The subparser for parsing add, init, rm etc
    arg_subparser = parser.add_subparsers(
        prog="ngit",
        title="Commands",
        dest="command",
        metavar="<command>",
        description="See 'ngit help <command>' or 'ngit <command> --help' to read about a specific subcommand",
    )
    arg_subparser.required = True

    # ArgParser for ngit add

    # ArgParser for ngit cat-file
    argsp_cat_file = arg_subparser.add_parser(  # cat-file
        "cat-file",
        prog="ngit cat-file",
        description="Provide contents or details of repository objects",
        help="Provide contents or details of repository objects",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_cat_file.add_argument(  # type
        "type",
        metavar="<type>",
        choices=["blob", "commit", "tag", "tree", None],
        default=None,
        nargs="?",
        help="Specify the type of object to be read. Possible values are blob, commit, tag, and tree.",
    )
    arggrp_cat_file_type = argsp_cat_file.add_mutually_exclusive_group(required=False)
    arggrp_cat_file_type.add_argument(  # -e only-error
        "-e",
        dest="only_error",
        action="store_true",
        help="Exit with zero if <object> exists and is valid, else return non-zero and error-message",
    )
    arggrp_cat_file_type.add_argument(  # -p pretty-print
        "-p",
        dest="pretty_print",
        action="store_true",
        help="Pretty-print the contents of <object> based on its type.",
    )
    arggrp_cat_file_type.add_argument(  # -t only-type
        "-t",
        dest="only_type",
        action="store_true",
        help="Instead of the content, show the object type identified by <object>.",
    )
    arggrp_cat_file_type.add_argument(  # -s only-size
        "-s",
        dest="only_size",
        action="store_true",
        help="Instead of the content, show the object size identified by <object>.",
    )
    argsp_cat_file.add_argument(  # object
        "object",
        help="The name/hash of the object to show.",
    )

    # ArgParser for ngit check-ignore

    # ArgParser for ngit checkout
    argsp_checkout = arg_subparser.add_parser(  # checkout
        "checkout",
        prog="ngit checkout",
        description="Switch branches or restore working tree files",
        help="Switch branches or restore working tree files",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_checkout.add_argument(  # -q --quiet
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Quiet, suppress feedback messages",
    )
    argsp_checkout.add_argument(  # -f --force
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="When switching branches, throw away local changes and any untracked files or directories",
    )
    argsp_checkout.add_argument(  # --dest
        "--dest",
        default=None,
        help="checkout to <dest> instead of current repository, provided <dest> is empty directory",
    )
    argsp_checkout.add_argument(  # branch
        "branch",
        nargs="?",
        default=None,
        help="The branch or commit or tree to checkout",
    )

    # ArgParser for ngit commit

    # ArgParser for ngit hash-object
    argsp_hash_object = arg_subparser.add_parser(  # hash-object
        "hash-object",
        prog="ngit hash-object",
        description="Compute object ID and optionally create an object from a file",
        help="Compute object ID and optionally create an object from a file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_hash_object.add_argument(  # -t --type
        "-t",
        "--type",
        metavar="<type>",
        default="blob",
        choices=["blob", "commit", "tag", "tree"],
        help="Specify the type of object to be created, Possible values are blob, commit, tag, and tree.",
    )
    argsp_hash_object.add_argument(  # -w write
        "-w",
        dest="write",
        action="store_true",
        help="Actually write the object into the object database.",
    )
    argsp_hash_object.add_argument(  # --stdin-path
        "--stdin-paths",
        action="store_true",
        help="Read file names from the standard input, one per line, instead of from the command-line.",
    )
    argsp_hash_object.add_argument(  # -i --stdin
        "-i",
        "--stdin",
        dest="stdin",
        action="store_true",
        help="Read the object from standard input instead of from a file.",
    )
    argsp_hash_object.add_argument(  # path
        "path",
        nargs="*",
        help="Hash object as if it were located at the given path.",
    )

    # ArgParser for ngit help

    # ArgParser for ngit init
    argsp_init = arg_subparser.add_parser(  # init
        "init",
        prog="ngit init",
        description="Initialize a new, empty repository.",
        help="Initialize a new, empty repository.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_init.add_argument(  # path
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )
    argsp_init.add_argument(  # -q --quiet
        "-q",
        "--quiet",
        action="store_true",
        help="Only print error and warning messages; all other output will be suppressed.",
    )
    argsp_init.add_argument(  # -b --initial-branch
        "-b",
        "--initial-branch",
        metavar="BRANCH-NAME",
        default="main",
        help="Use BRANCH-NAME for the initial branch in the newly created repository. (Default: main)",
    )

    # ArgParser for ngit log
    argsp_log = arg_subparser.add_parser(  # log
        "log",
        prog="ngit log",
        description="Shows the commit logs",
        help="Shows the commit logs",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_log.add_argument(  # --decorate
        "--decorate",
        default="short",
        choices=["short", "full", "auto", "no"],
        metavar="short|full|auto|no",
        help="Print out the ref names of any commits that are shown",
    )
    argsp_log.add_argument(  # --log-size
        "--log-size",
        action="store_true",
        help='Include a line "log size <number>" in the output for each commit',
    )
    argsp_log.add_argument(  # -n --max-count
        "-n",
        "--max-count",
        default=-1,
        type=int,
        help="Limit the number of commits to output.",
    )
    argsp_log.add_argument(  # --skip
        "--skip",
        type=int,
        default=0,
        help="Skip number commits before starting to show the commit output.",
    )
    argsp_log.add_argument(  # --after --since --since-as-filter
        "--after",
        "--since",
        "--since-as-filter",
        dest="after",
        help="Show all commits more recent than a specific date.",
    )
    argsp_log.add_argument(  # --before --until
        "--before",
        "--until",
        dest="before",
        help="Show commits older than a specific date.",
    )
    argsp_log.add_argument(  # --min-parents
        "--min-parents",
        type=int,
        default=0,
        help="Show only commits which have at least that many parent commits.",
    )
    argsp_log.add_argument(  # --max-parents
        "--max-parents",
        type=int,
        default=-1,
        help="Show only commits which have at most that many parent commits.",
    )
    argsp_log.add_argument(  # --no-min-parents
        "--no-min-parents",
        action="store_const",
        const=0,
        dest="min_parents",
        help="Show only commits which have at least that many parent commits.",
    )
    argsp_log.add_argument(  # --no-max-parents
        "--no-max-parents",
        action="store_const",
        const=-1,
        dest="max_parents",
        help="Show only commits which have at most that many parent commits.",
    )
    argsp_log.add_argument(  # --merges
        "--merges",
        action="store_const",
        const=2,
        dest="min_parents",
        help="Print only merge commits. This is exactly the same as --min-parents=2.",
    )
    argsp_log.add_argument(  # --no-merges
        "--no-merges",
        action="store_const",
        const=1,
        dest="max_parents",
        help="Do not print commits with more than one parent. This is exactly the same as --max-parents=1.",
    )
    argsp_log.add_argument(  # --format --pretty
        "--format",
        "--pretty",
        default="medium",
        dest="format_str",
        help="Pretty-print the contents of the commit logs in a given format",
    )
    argsp_log.add_argument(  # --date
        "--date",
        choices=["relative", "local", "iso", "iso8601", "iso-strict", "iso8601-strict"]
        + ["rfc", "rfc2822", "short", "raw", "unix", "human", "default"],
        default="default",
        dest="date_fmt",
        metavar="FORMAT",
        help="The format to use for dates in ngit log",
    )
    argsp_log.add_argument(  # commits
        "commits",
        default="HEAD",
        nargs="?",
        help="Commit to start at.",
    )

    # ArgParser for ngit ls-files

    # ArgParser for ngit ls-tree
    argsp_ls_tree = arg_subparser.add_parser(  # ls-tree
        "ls-tree",
        prog="ngit ls-tree",
        description="List the contents of a tree object",
        help="List the contents of a tree object",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_ls_tree.add_argument(  # --format --pretty
        "--format",
        "--pretty",
        default="%(objectmode) %(objecttype) %(objectname)\t%(path)",
        dest="format_str",
        help="Pretty-print the contents of the tree in a given format",
    )
    argsp_ls_tree.add_argument(  # -d
        "-d",
        dest="only_trees",
        action="store_true",
        help="Show only the named tree entry itself, not its children.",
    )
    argsp_ls_tree.add_argument(  # -r
        "-r",
        dest="recurse_trees",
        action="store_true",
        help="Recurse into sub-trees.",
    )
    argsp_ls_tree.add_argument(  # -t
        "-t",
        dest="always_trees",
        action="store_true",
        help="Show tree entries even when going to recurse them.",
    )
    argsp_ls_tree.add_argument(  # -l --long
        "-l",
        "--long",
        action="store_const",
        const="%(objectmode) %(objecttype) %(objectname) %(objectsize:padded)\t%(path)",
        dest="format_str",
        help="Show object size of blob (file) entries.",
    )
    argsp_ls_tree.add_argument(  # -z
        "-z",
        dest="null_terminator",
        action="store_true",
        help="\\0 line termination on output and do not quote filenames.",
    )
    argsp_ls_tree.add_argument(  # --name-only --name-status
        "--name-only",
        "--name-status",
        action="store_const",
        const="%(path)",
        dest="format_str",
        help="List only filenames, one per line.",
    )
    argsp_ls_tree.add_argument(  # --object-only
        "--object-only",
        action="store_const",
        const="%(objectname)",
        dest="format_str",
        help="List only names of the objects, one per line.",
    )
    argsp_ls_tree.add_argument(  # tree
        "tree",
        default="HEAD",
        nargs="?",
        help="Tree(-ish) object to start at.",
    )

    # ArgParser for ngit rev-parse
    argsp_rev_parse = arg_subparser.add_parser(  # rev-parse
        "rev-parse",
        prog="ngit rev-parse",
        description="Parse revision names or give repo information",
        help="Parse revision names or give repo information",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_rev_parse.add_argument(  # -t --type
        "-t",
        "--type",
        metavar="<type>",
        choices=["blob", "commit", "tag", "tree"],
        default=None,
        help="Specify the type of object to be created, Possible values are blob, commit, tag, and tree",
    )
    argsp_rev_parse.add_argument(  # name
        "name",
        nargs="+",
        help="The name of object to parse",
    )
    argsp_rev_parse.add_argument(  # --follow
        "--follow",
        dest="follow",
        action="store_true",
        help="follow tags objects",
    )

    # ArgParser for ngit rm

    # ArgParser for ngit show-ref
    argsp_show_ref = arg_subparser.add_parser(  # show-ref
        "show-ref",
        prog="ngit show-ref",
        description="List references in a local repository",
        help="List references in a local repository",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_show_ref.add_argument(  # ref
        "ref",
        nargs="*",
        action="extend",
        help="if verify or exists are specified, then these are ref to verify,\n"
        "otherwise print refs under these sub-directory of `.git/refs/`",
    )
    argsp_show_ref.add_argument(  # --head
        "--head",
        dest="head",
        action="store_true",
        help="Show the HEAD reference, even if it would normally be filtered out",
    )
    argsp_show_ref.add_argument(  # --branches --heads
        "--branches",
        "--heads",
        dest="ref",
        action="append_const",
        const="heads",
        help="Limit to local branches only",
    )
    argsp_show_ref.add_argument(  # --tags
        "--tags",
        dest="ref",
        action="append_const",
        const="tags",
        help="Limit to local tags only",
    )
    argsp_show_ref.add_argument(  # --remotes
        "--remotes",
        dest="ref",
        action="append_const",
        const="remotes",
        help="Limit to remote branches only",
    )
    argsp_show_ref.add_argument(  # -q --quiet
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Do not print any results to stdout. "
        "Can be used with --verify to silently check if a reference exists",
    )
    argsp_show_ref.add_argument(  # -s --hash
        "-s",
        "--hash",
        default=None,
        const=40,
        nargs="?",
        help="Only show the object SHA-1, not the reference name",
    )
    argsp_show_ref.add_argument(  # -d --dereference
        "-d",
        "--dereference",
        dest="deref",
        action="store_true",
        help="Dereference tags into object IDs as well. They will be shown with ^{} appended",
    )
    arggrp_show_ref_verify = argsp_show_ref.add_mutually_exclusive_group(required=False)
    arggrp_show_ref_verify.add_argument(  # --exists
        "--exists",
        dest="exists",
        action="store_true",
        help="Check whether the given reference exists",
    )
    arggrp_show_ref_verify.add_argument(  # --verify
        "--verify",
        dest="verify",
        action="store_true",
        help="Enable stricter reference checking by requiring an exact ref path, "
        "also prints error message unless -q passed",
    )

    # ArgParser for ngit status
    # ArgParser for ngit tag
    argsp_tag = arg_subparser.add_parser(
        "tag",
        prog="ngit tag",
        description="Create, list or delete a tag object",
        help="Create, list or delete a tag object",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    argsp_tag.add_argument(  # -a --annotate
        "-a",
        "--annotate",
        dest="annotate",
        action="store_true",
        help="Make an unsigned, annotated tag object",
    )
    argsp_tag.add_argument(  # -d --delete
        "-d",
        "--delete",
        dest="delete",
        action="store_true",
        help="Delete existing tags with the given names",
    )
    argsp_tag.add_argument(  # -l --list
        "-l",
        "--list",
        dest="list",
        action="store_true",
        help="List tags. Running `git tag` without arguments also lists all tags",
    )
    argsp_tag.add_argument(  # -f --force
        "-f",
        "--force",
        dest="force",
        action="store_true",
        help="Replace an existing tag with the given name (instead of failing)",
    )
    argsp_tag.add_argument(  # -m --message
        "-m",
        "--message",
        dest="message",
        metavar="MSG",
        default=None,
        help="Use the given tag message (instead of prompting or reading from file)",
    )
    argsp_tag.add_argument(  # -F --file
        "-F",
        "--file",
        dest="file",
        nargs="?",
        const="-",
        default="-",
        help="Take the tag message from the given file. Use - to read the message from the standard input",
    )
    argsp_tag.add_argument(  # tagname
        "tagname",
        nargs="?",
        default=None,
        help="The name of the tag to create, delete, or describe",
    )
    argsp_tag.add_argument(  # commit
        "commit",
        nargs="?",
        default="HEAD",
        help="The object that the new tag will refer to, usually a commit (Defaults to HEAD)",
    )

    args: argparse.Namespace = parser.parse_args()
    main(args)


def main(args: argparse.Namespace) -> None:
    match args.command:
        case "add":
            cmd_add(args)
        case "cat-file":
            cmd_cat_file(args)
        case "check-ignore":
            cmd_check_ignore(args)
        case "checkout":
            cmd_checkout(args)
        case "commit":
            cmd_commit(args)
        case "hash-object":
            cmd_hash_object(args)
        case "help":
            cmd_help(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
        case "ls-files":
            cmd_ls_files(args)
        case "ls-tree":
            cmd_ls_tree(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "rm":
            cmd_rm(args)
        case "show-ref":
            cmd_show_ref(args)
        case "status":
            cmd_status(args)
        case "tag":
            cmd_tag(args)
        case _:
            print(f"WARNING: bad command '{args.command}'.")


# Bridge functions for CLI argument processing.


def cmd_add(args: argparse.Namespace) -> None:
    pass


def cmd_cat_file(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()

    # fmt: off
    flag: int = (
        1 if args.only_error else
        2 if args.only_type else
        3 if args.only_size else
        4 # default flag is 4
    )
    # fmt: on

    cat_file(repo, args.object, fmt=args.type, flag=flag)


def cmd_check_ignore(args: argparse.Namespace) -> None:
    pass


def cmd_checkout(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()

    if args.branch is None:
        args.branch = resolve_ref(repo, "HEAD")

    if args.branch is None:  # still None
        raise ValueError("branch is not specified and HEAD is a broken reference")

    obj: GitObject = object_read(repo, object_find_f(repo, args.branch))

    if type(obj) is GitCommit:  # read `tree` if commit
        obj = object_read(repo, object_find_f(repo, obj.data[b"tree"][0].decode()))

    assert type(obj) is GitTree

    if args.dest is None:  # if --dest not specified, use current repo
        # TODO: don't delete files in .gitignore
        # TODO: raise Exception if working tree is not clean
        args.dest = repo.worktree

    if os.path.exists(args.dest):
        if not os.path.isdir(args.dest):
            raise NotADirectoryError(f"fatal: {args.dest} is not a directory")
        if args.force is False and os.listdir(args.dest):
            raise FileExistsError(f"{args.dest} is not empty, use -f to overwrite")
    else:
        os.makedirs(args.dest)

    checkout(repo, obj, os.path.realpath(args.dest), args.quiet)


def cmd_commit(args: argparse.Namespace) -> None:
    pass


def cmd_hash_object(args: argparse.Namespace) -> None:
    if args.write:
        repo: GitRepository | None = repo_find_f()
    else:
        repo = None

    if args.stdin:
        print(object_hash(repo, sys.stdin, args.type.encode()))

    # if args.stdin_path is set, then read path from sys.stdin
    # else use paths passed in args.path
    for path in sys.stdin if args.stdin_paths else args.path:
        with open(path) as fd:
            print(object_hash(repo, fd, args.type.encode()))


def cmd_help(args: argparse.Namespace) -> None:
    pass


def cmd_init(args: argparse.Namespace) -> None:
    repo_create(args.path, args.initial_branch, args.quiet)


def cmd_log(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()

    # TODO: Add support for common format_str

    print_logs(
        repo,
        object_find_f(repo, args.commits),
        decorate=args.decorate,  # TODO
        log_size=args.log_size,  # TODO
        max_count=args.max_count,
        skip=args.skip,
        after=args.after,
        before=args.before,
        min_parents=args.min_parents,
        max_parents=args.max_parents,
        format_str=args.format_str,
        date_fmt=args.date_fmt,
    )


def cmd_ls_files(args: argparse.Namespace) -> None:
    pass


def cmd_ls_tree(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()

    ls_tree(
        repo,
        object_find_f(repo, args.tree, "tree"),
        only_trees=args.only_trees,
        recurse_trees=args.recurse_trees,
        always_trees=args.always_trees,
        null_terminator=args.null_terminator,
        format_str=args.format_str,
    )


def cmd_rev_parse(args: argparse.Namespace) -> None:
    for name in args.name:
        print(object_find_f(repo_find_f(), name, args.type, args.follow))


def cmd_rm(args: argparse.Namespace) -> None:
    pass


def cmd_show_ref(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()

    if not args.ref:  # no ref specified, default to refs/ one
        args.ref = ["refs"]

    if args.head or "HEAD" in args.ref:
        print(resolve_ref(repo, "HEAD"), "" if args.hash else "HEAD")

    args.ref = sorted(set(args.ref))

    # fmt: off
    verify: int = (
        1 if args.verify and args.quiet else
        2 if args.verify else
        3 if args.exists else
        0 # default, nothing specified
    )

    # TODO: some bugs here, hunt 'em down!!
    # TODO: Simplify the convuluted logic here.
    if verify == 3:
        sys.exit(0 if all(os.path.exists(repo_file(repo, path)) for path in args.ref) else 2)
    if verify == 0 or verify == 2:
        show_ref(repo, args.ref, args.hash, args.deref)
    if verify == 1 or verify == 2:
        sys.exit(0 if all(os.path.exists(resolve_ref(repo, path) or "") for path in args.ref) else 1)
    # fmt: on


def cmd_status(args: argparse.Namespace) -> None:
    pass


def cmd_tag(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find_f()
    tagfile: str = repo_file(repo, f"refs/tags/{args.tagname}")

    if args.delete:
        try:
            os.remove(tagfile)
        except FileNotFoundError:
            print(f"WARNING: tag `{args.tagname}' not found")

    # As `-d` also uses tagname, so that case must be handled before
    elif args.tagname is not None:
        # if tag alreadt exists but -f was not specified, raise Exception
        if args.force is False and os.path.exists(tagfile):
            raise FileExistsError(f"tag {args.tagname} already exists, -f to overwrite")

        if args.message is None:  # if -m is not specified
            if args.file == "-":  # read from stdin
                print("# Write a message for tag... (Ctrl+D to continue)")
                args.message = sys.stdin.read()
            else:  # or from a file, if specified
                with open(args.file) as msg_file:
                    args.message = msg_file.read()

        sha1: str = object_find_f(repo, args.commit)
        tag_create(repo, args.tagname, sha1, args.message, args.annotate)

    else:  # if args.list or nothing else specified
        tag_list(repo, ref_list(repo, repo_file(repo, "refs/tags"), force=True))
