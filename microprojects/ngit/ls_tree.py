from microprojects.ngit.object import object_read


def ls_tree(
    repo,
    sha1,
    only_trees,
    recurse_trees,
    always_trees,
    null_terminator,
    format_str: str,
    prefix: str = "",
) -> None:
    """"""

    obj = object_read(repo, sha1)
    endl: str = "\0" if null_terminator else "\n"

    if not any([recurse_trees, always_trees, only_trees]):
        always_trees = True

    for leaf in obj.data:
        obj_fmt: str = ""

        match leaf.mode[:-4]:  # drop last four chars
            case "04" | "4":
                obj_fmt = "tree"
            case "10" | "12":
                obj_fmt = "blob"
            case "16":
                obj_fmt = "commit"
            case _:
                raise Exception(f"Weird tree leaf mode {leaf.mode}")

        if obj_fmt == "tree":
            if always_trees or only_trees:
                print(prettify(leaf, format_str, obj_fmt, prefix), end=endl)
            if recurse_trees:
                ls_tree(
                    repo,
                    leaf.sha1,
                    only_trees,
                    recurse_trees,
                    always_trees,
                    null_terminator,
                    format_str,
                    prefix=prefix + leaf.path + "/",
                )
        elif not only_trees:
            print(prettify(leaf, format_str, obj_fmt, prefix), end=endl)


def prettify(leaf, format_str: str, obj_fmt: str, prefix: str) -> str:
    format_str = format_str.replace("%(objectmode)", leaf.mode)
    format_str = format_str.replace("%(objecttype)", obj_fmt)
    format_str = format_str.replace("%(objectname)", leaf.sha1)
    format_str = format_str.replace("%(path)", prefix + leaf.path)

    return format_str
