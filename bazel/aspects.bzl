load(":providers.bzl", "runfiles_files")

def _digest_impl(target, ctx):
    actions = ctx.actions
    bin = target[DefaultInfo]
    hash = ctx.attr._hash[DefaultInfo]
    hash_executable = ctx.executable._hash
    name = ctx.rule.attr.name

    digest = actions.declare_file("%s.digest" % name)
    args = actions.args()
    args.set_param_file_format("multiline")
    args.use_param_file("@%s", use_always = True)
    args.add(digest)
    actions.run(
        arguments = [args],
        executable = hash_executable,
        execution_requirements = {
            "supports-workers": "1",
            "requires-worker-protocol": "json",
        },
        inputs = runfiles_files(bin.default_runfiles),
        outputs = [digest],
        tools = [hash.files_to_run],
    )

    output_group_info = OutputGroupInfo(
        digest = depset([digest]),
        pass_events = depset(),
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
