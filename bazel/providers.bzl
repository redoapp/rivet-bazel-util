def _runfiles_files(runfiles):
    return (
        [entry.target_file for entry in runfiles.symlinks.to_list()] +
        [entry.target_file for entry in runfiles.root_symlinks.to_list()] +
        runfiles.files.to_list()
    )

def _create_one_digest(actions, name, files, hash):
    output = actions.declare_file("%s.digest" % name)

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
        inputs = files,
        mnemonic = "Hash",
        outputs = [output],
        progress_message = "Creating digest %{output}",
        tools = [hash.files_to_run],
    )

    return output

def create_digest(actions, name, runfiles, hash):
    files = _runfiles_files(runfiles)

    if 200 <= len(files):
        new_files = []
        for i in range(0, len(files), 100):
            output = _create_one_digest(actions, "%s%s" % (name, i // 100), files[i:i + 100], hash)
            new_files.append(output)
        files = new_files

    return _create_one_digest(actions = actions, name = name, files = files, hash = hash)
