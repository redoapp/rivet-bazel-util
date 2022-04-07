load(":providers.bzl", "create_digest")

def _digest_impl(target, ctx):
    actions = ctx.actions
    bin = target[DefaultInfo]
    hash = ctx.attr._hash[DefaultInfo]
    name = ctx.rule.attr.name

    if "digest" in target[OutputGroupInfo]:
        return []

    digest = create_digest(
        actions = actions,
        hash = hash,
        name = name,
        runfiles = bin.default_runfiles,
    )

    output_group_info = OutputGroupInfo(
        digest = depset([digest]),
    )

    return [output_group_info]

digest = aspect(
    attrs = {
        "_hash": attr.label(
            cfg = "exec",
            default = "//util/hash:bin",
            executable = True,
        ),
    },
    implementation = _digest_impl,
)
