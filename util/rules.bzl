load(":providers.bzl", "create_digest")

def _digest_impl(ctx):
    actions = ctx.actions
    encoding = ctx.attr.encoding or None
    hash = ctx.attr._hash[DefaultInfo]
    length = ctx.attr.length or None
    name = ctx.attr.name
    srcs = ctx.files.srcs
    executable_infos = [target[DefaultInfo] for target in ctx.attr.executables]

    digest = actions.declare_file("%s.%s" % (name, "txt" if encoding else "digest"))
    create_digest(
        actions = actions,
        encoding = encoding,
        hash = hash,
        length = length,
        output = digest,
        runfiles = ctx.runfiles(files = srcs).merge_all(
            [default_info.default_runfiles for default_info in executable_infos],
        ),
    )

    default_info = DefaultInfo(files = depset([digest]))

    return [default_info]

digest = rule(
    attrs = {
        "executables": attr.label_list(),
        "length": attr.int(),
        "srcs": attr.label_list(allow_files = True),
        "encoding": attr.string(),
        "_hash": attr.label(
            cfg = "exec",
            default = "//util/hash:bin",
            executable = True,
        ),
    },
    implementation = _digest_impl,
)
