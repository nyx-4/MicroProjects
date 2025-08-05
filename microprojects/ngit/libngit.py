import argparse  # ngit is CLI tool, so we need to parse CLI args

# import configparser  # ngit's config file uses INI format
# from datetime import datetime  # to store time of each commit
# import grp, pwd  # because ngit saves numerical owner/group ID of files author
# from fnmatch import fnmatch  # to match .gitignore patterns like *.txt
# import hashlib  # ngit uses SHA-1 hash extensively
# import math
# import os  # os and os.path provide some nice filesystem abstraction routines
# import re  # just a little-bit of RegEx
import sys  # to access `sys.argv`
# import zlib  # to compress & decompress files


from microprojects.ngit.repository import GitRepository, repo_create, repo_find
from microprojects.ngit.object import object_hash, cat_file


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
    # ArgParser for ngit ls-files
    # ArgParser for ngit ls-tree
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
            print(f"Bad command '{args.command}'.")


# Bridge functions for CLI argument processing.


def cmd_add(args: argparse.Namespace) -> None:
    pass


def cmd_cat_file(args: argparse.Namespace) -> None:
    repo: GitRepository = repo_find(required=True)
    flags: tuple = (args.only_error, args.pretty_print, args.only_type, args.only_size)
    cat_file(repo, args.object, fmt=args.type, flag=flags)


def cmd_check_ignore(args: argparse.Namespace) -> None:
    pass


def cmd_checkout(args: argparse.Namespace) -> None:
    pass


def cmd_commit(args: argparse.Namespace) -> None:
    pass


def cmd_hash_object(args: argparse.Namespace) -> None:
    if args.write:
        repo: GitRepository | None = repo_find()
    else:
        repo = None

    if args.stdin:
        print(object_hash(sys.stdin, args.type.encode(), repo))

    # if args.stdin_path is set, then read path from sys.stdin
    # else use paths passed in args.path
    for path in sys.stdin if args.stdin_paths else args.path:
        with open(path) as fd:
            print(object_hash(fd, args.type.encode(), repo))


def cmd_help(args: argparse.Namespace) -> None:
    pass


def cmd_init(args: argparse.Namespace) -> None:
    repo_create(args.path, args.initial_branch, args.quiet)


def cmd_log(args: argparse.Namespace) -> None:
    pass


def cmd_ls_files(args: argparse.Namespace) -> None:
    pass


def cmd_ls_tree(args: argparse.Namespace) -> None:
    pass


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


if __name__ == "__main__":
    ngit_main()
