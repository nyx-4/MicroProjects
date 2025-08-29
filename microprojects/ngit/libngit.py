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
from microprojects.ngit.repository import GitRepository, repo_find_f
from microprojects.ngit.object_utils import object_find, object_read
from microprojects.ngit.ngit_utils import cat_file, ls_tree, object_hash, repo_create
from microprojects.ngit.ngit_utils import checkout
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
        prog="ngit",
        description="Switch branches or restore working tree files",
        help="Switch branches or restore working tree files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        prog="ngit",
        description="List the contents of a tree object",
        help="List the contents of a tree object",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    # ArgParser for ngit rm
    # ArgParser for ngit show-ref
    # ArgParser for ngit status
    # ArgParser for ngit tag

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
        # TODO: if args.branch is not specified, default to current branch
        pass

    obj: GitObject = object_read(repo, object_find(repo, args.branch))

    if type(obj) is GitCommit:  # read `tree` if commit
        obj = object_read(repo, object_find(repo, obj.data[b"tree"][0].decode()))

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
        object_find(repo, args.commits),
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
        object_find(repo, args.tree, b"tree"),
        only_trees=args.only_trees,
        recurse_trees=args.recurse_trees,
        always_trees=args.always_trees,
        null_terminator=args.null_terminator,
        format_str=args.format_str,
    )


def cmd_rev_parse(args: argparse.Namespace) -> None:
    pass


def cmd_rm(args: argparse.Namespace) -> None:
    pass


def cmd_show_ref(args: argparse.Namespace) -> None:
    pass


def cmd_status(args: argparse.Namespace) -> None:
    pass


def cmd_tag(args: argparse.Namespace) -> None:
    pass
