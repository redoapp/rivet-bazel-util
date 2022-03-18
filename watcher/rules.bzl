load("@bazel_skylib//lib:shell.bzl", "shell")
load("@rules_file//util:path.bzl", "runfile_path")
load(":providers.bzl", "runfiles_files")

def _restart_service_impl(ctx):
    actions = ctx.actions
    bin = ctx.attr.bin[DefaultInfo]
    hash = ctx.attr._hash[DefaultInfo]
    name = ctx.attr.name
    restart = ctx.attr._restart[DefaultInfo]
    runner = ctx.file._runner
    workspace_name = ctx.workspace_name

    digest = actions.declare_file("%s.digest" % name)
    args = actions.args()
    args.set_param_file_format("multiline")
    args.use_param_file("@%s", use_always = True)
    args.add(digest)
    actions.run(
        arguments = [args],
        executable = hash.files_to_run.executable,
        execution_requirements = {
            "supports-workers": "1",
            "requires-worker-protocol": "json",
        },
        inputs = runfiles_files(bin.default_runfiles),
        outputs = [digest],
        tools = [hash.files_to_run],
    )

    executable = actions.declare_file(name)
    actions.expand_template(
        is_executable = True,
        output = executable,
        template = runner,
        substitutions = {
            "%{bin}": shell.quote(runfile_path(workspace_name, bin.files_to_run.executable)),
            "%{digest}": shell.quote(runfile_path(workspace_name, digest)),
        },
    )

    runfiles = ctx.runfiles(files = [digest])
    runfiles = runfiles.merge(restart.default_runfiles)
    runfiles = runfiles.merge(bin.default_runfiles)
    default_info = DefaultInfo(
        executable = executable,
        runfiles = runfiles,
    )

    return [default_info]

restart_service = rule(
    attrs = {
        "bin": attr.label(
            cfg = "target",
            executable = True,
            mandatory = True,
        ),
        "_hash": attr.label(
            cfg = "exec",
            default = "//util/hash:bin",
            executable = True,
        ),
        "_restart": attr.label(
            cfg = "target",
            default = "//watcher/restart:bin",
            executable = True,
        ),
        "_runner": attr.label(
            allow_single_file = True,
            default = ":runner.sh.tpl",
        ),
    },
    executable = True,
    implementation = _restart_service_impl,
)
