## ngit - (Nyx-)Git
Git re-implementation in Python that is _perfectly compatible_ with with [Git SCM](https://git-scm.com/). **ngit is made by following a tutorial [WYAG - Thibault Polge](https://wyag.thb.lt/)**  


## Table of Content
- [ngit - (Nyx-)Git](#ngit---nyx-git)
- [Table of Content](#table-of-content)
- [Synopsis](#synopsis)
- [Description](#description)
- [Quick Start](#quick-start)
- [Getting `ngit`](#getting-ngit)
    - [Source](#source)
    - [PyPI (Python)](#pypi-python)
- [Usage](#usage)
- [Sub-commands](#sub-commands)
    - [add](#add)
    - [cat-file](#cat-file)
    - [check-ignore](#check-ignore)
    - [checkout](#checkout)
    - [commit](#commit)
    - [hash-object](#hash-object)
    - [help](#help)
    - [init](#init)
    - [log](#log)
    - [ls-files](#ls-files)
    - [ls-tree](#ls-tree)
    - [rev-parse](#rev-parse)
    - [rm](#rm)
    - [show-ref](#show-ref)
    - [status](#status)
    - [tag](#tag)
- [Contributing](#contributing)
- [License](#license)
- [WYAG License](#wyag-license)


## Synopsis
```sh
ngit [-h] <command> ...
```
Also, see [Sub Commands](#sub-commands) for further help about each `<command>`.


## Description
<!-- Add MicroProject Description here. -->


## Quick Start
<!-- Add a quick start guide here. -->


## Getting `ngit`

### Source

Clone the development version from [MicroProjects - GitHub](https://github.com/nyx-4/MicroProjects.git)

```sh
git clone https://github.com/nyx-4/MicroProjects.git
cd MicroProjects
pip install .
```

### PyPI (Python)

Use the package manager pip to install foobar.

```sh
pip install microprojects
```

## Usage


## Sub-commands
The supported subset of Git's commands are listed here.

> [!Note]
> This information is also available at `ngit <command> --help` and `ngit help <command>`.


### add

### cat-file
```sh
usage: ngit [-h] [-e | -p | -t | -s] [<type>] object

Provide contents or details of repository objects

positional arguments:
  <type>      Specify the type of object to be read. Possible values are blob, commit, tag, and tree.
  object      The name/hash of the object to show.

options:
  -h, --help  show this help message and exit
  -e          Exit with zero if <object> exists and is valid, else return non-zero and error-message
  -p          Pretty-print the contents of <object> based on its type.
  -t          Instead of the content, show the object type identified by <object>.
  -s          Instead of the content, show the object size identified by <object>.
```

### check-ignore

### checkout
```sh
usage: ngit [-h] [-q] [-f] [--dest DEST] [branch]

Switch branches or restore working tree files

positional arguments:
  branch       The branch or commit or tree to checkout

options:
  -h, --help   show this help message and exit
  -q, --quiet  Quiet, suppress feedback messages
  -f, --force  When switching branches, throw away local changes and any untracked files or directories
  --dest DEST  checkout to <dest> instead of current repository, provided <dest> is empty directory
```

### commit

### hash-object
```sh
usage: ngit [-h] [-t <type>] [-w] [--stdin-paths] [-i] [path ...]

Compute object ID and optionally create an object from a file

positional arguments:
  path               Hash object as if it were located at the given path.

options:
  -h, --help         show this help message and exit
  -t, --type <type>  Specify the type of object to be created, Possible values are blob, commit, tag, and tree.
  -w                 Actually write the object into the object database.
  --stdin-paths      Read file names from the standard input, one per line, instead of from the command-line.
  -i, --stdin        Read the object from standard input instead of from a file.
```

### help

### init
```sh
usage: ngit [-h] [-q] [-b BRANCH-NAME] [directory]

Initialize a new, empty repository.

positional arguments:
  directory             Where to create the repository.

options:
  -h, --help            show this help message and exit
  -q, --quiet           Only print error and warning messages; all other output will be suppressed.
  -b, --initial-branch BRANCH-NAME
                        Use BRANCH-NAME for the initial branch in the newly created repository. (Default: main)
```

### log
```sh
usage: ngit log [-h] [--decorate short|full|auto|no] [--log-size] [-n MAX_COUNT] [--skip SKIP]
                [--after AFTER] [--before BEFORE] [--min-parents MIN_PARENTS] [--max-parents MAX_PARENTS]
                [--no-min-parents] [--no-max-parents] [--merges] [--no-merges] [--format FORMAT_STR]
                [--date FORMAT] [commits]

Shows the commit logs

positional arguments:
  commits               Commit to start at.

options:
  -h, --help            show this help message and exit
  --decorate short|full|auto|no
                        Print out the ref names of any commits that are shown
  --log-size            Include a line "log size <number>" in the output for each commit
  -n, --max-count MAX_COUNT
                        Limit the number of commits to output.
  --skip SKIP           Skip number commits before starting to show the commit output.
  --after, --since, --since-as-filter AFTER
                        Show all commits more recent than a specific date.
  --before, --until BEFORE
                        Show commits older than a specific date.
  --min-parents MIN_PARENTS
                        Show only commits which have at least that many parent commits.
  --max-parents MAX_PARENTS
                        Show only commits which have at most that many parent commits.
  --no-min-parents      Show only commits which have at least that many parent commits.
  --no-max-parents      Show only commits which have at most that many parent commits.
  --merges              Print only merge commits. This is exactly the same as --min-parents=2.
  --no-merges           Do not print commits with more than one parent. This is exactly the same as --max-parents=1.
  --format, --pretty FORMAT_STR
                        Pretty-print the contents of the commit logs in a given format
  --date FORMAT         The format to use for dates in ngit log
```

### ls-files
### ls-tree
```sh
usage: ngit [-h] [--format FORMAT_STR] [-d] [-r] [-t] [-l] [-z] [--name-only] [--object-only] [tree]

List the contents of a tree object

positional arguments:
  tree                  Tree(-ish) object to start at.

options:
  -h, --help            show this help message and exit
  --format, --pretty FORMAT_STR
                        Pretty-print the contents of the tree in a given format
  -d                    Show only the named tree entry itself, not its children.
  -r                    Recurse into sub-trees.
  -t                    Show tree entries even when going to recurse them.
  -l, --long            Show object size of blob (file) entries.
  -z                    \0 line termination on output and do not quote filenames.
  --name-only, --name-status
                        List only filenames, one per line.
  --object-only         List only names of the objects, one per line.
```

### rev-parse
### rm
### show-ref
### status
### tag

## Contributing

## License
All my code here is licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). 

## [WYAG License](https://wyag.thb.lt/#org4973c11)
This ([WYAG - Thibault Polge](https://wyag.thb.lt/)) article is distributed under the terms of the [Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). The [program itself](https://wyag.thb.lt/wyag.zip) is also licensed under the terms of the GNU General Public License 3.0, or, at your option, any later version of the same licence.

