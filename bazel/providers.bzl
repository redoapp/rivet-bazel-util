def runfiles_files(runfiles):
    return depset(
        [entry.target_file for entry in runfiles.symlinks.to_list()] +
        [entry.target_file for entry in runfiles.root_symlinks.to_list()],
        transitive = [runfiles.files],
    )

def create_digest(actions, output, runfiles, hash):
    args = actions.args()
    args.set_param_file_format("multiline")
    args.use_param_file("@%s", use_always = True)
    args.add(output)

    actions.run(
        arguments = [args],
        executable = hash.files_to_run.executable,
        execution_requirements = {
            "requires-worker-protocol": "json",
            "supports-workers": "1",
        },
        inputs = runfiles_files(runfiles),
        mnemonic = "Hash",
        outputs = [output],
        progress_message = "Creating digest %{output}",
        tools = [hash.files_to_run],
    )
