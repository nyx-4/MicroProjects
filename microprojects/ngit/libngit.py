import argparse  # ngit is CLI tool, so we need to parse CLI args
# import configparser  # ngit's config file uses INI format
# from datetime import datetime  # to store time of each commit
# import grp, pwd  # because ngit saves numerical owner/group ID of files author
# from fnmatch import fnmatch  # to match .gitignore patterns like *.txt
# import hashlib  # ngit uses SHA-1 hash extensively
# import math
# import os  # os and os.path provide some nice filesystem abstraction routines
# import re  # just a little-bit of RegEx
# import sys  # to access `sys.argv`
# import zlib  # to compress files


from microprojects.ngit.repository import repo_create


def ngit_main() -> None:
    # The ngit's main (arg_)parser
    parser = argparse.ArgumentParser(
        prog="ngit",
        description="ngit - the stupid content tracker",
    )

    # The subparser for parsing add, init, rm etc
    arg_subparser = parser.add_subparsers(
        prog="ngit",
        title="Commands",
        dest="command",
        description="See 'ngit help <command>' or 'ngit <command> --help' to read about a specific subcommand",
    )
    arg_subparser.required = True

    # ArgParser for ngit init
    argsp_init = arg_subparser.add_parser(
        "init",
        prog="ngit",
        description="Initialize a new, empty repository.",
        help="Initialize a new, empty repository.",
    )
    argsp_init.add_argument(
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )
    argsp_init.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print error and warning messages; all other output will be suppressed.",
    )
    argsp_init.add_argument(
        "-b",
        "--initial-branch",
        metavar="BRANCH-NAME",
        default="main",
        help="Use BRANCH-NAME for the initial branch in the newly created repository. Default: main",
    )

    args: argparse.Namespace = parser.parse_args()
    main(args)


def main(args) -> None:
    match args.command:
        # case "add"          : cmd_add(args)
        # case "cat-file"     : cmd_cat_file(args)
        # case "check-ignore" : cmd_check_ignore(args)
        # case "checkout"     : cmd_checkout(args)
        # case "commit"       : cmd_commit(args)
        # case "hash-object"  : cmd_hash_object(args)
        # case "help"         : cmd_help(args)
        case "init":
            cmd_init(args)
        # case "log"          : cmd_log(args)
        # case "ls-files"     : cmd_ls_files(args)
        # case "ls-tree"      : cmd_ls_tree(args)
        # case "rev-parse"    : cmd_rev_parse(args)
        # case "rm"           : cmd_rm(args)
        # case "show-ref"     : cmd_show_ref(args)
        # case "status"       : cmd_status(args)
        # case "tag"          : cmd_tag(args)
        case _:
            print(f"Bad command '{args.command}'.")


def cmd_init(args):
    repo_create(args.path, args.initial_branch, args.quiet)


if __name__ == "__main__":
    ngit_main()
