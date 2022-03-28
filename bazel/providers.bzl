def runfiles_files(runfiles):
    return depset(
        [entry.target_file for entry in runfiles.symlinks.to_list()] +
        [entry.target_file for entry in runfiles.root_symlinks.to_list()],
        transitive = [runfiles.files],
    )
