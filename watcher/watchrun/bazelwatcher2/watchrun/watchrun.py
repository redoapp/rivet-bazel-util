import json
import os
import subprocess
import sys
import time
from bazelwatcher2 import ibazel_notifications
from rules_python.python.runfiles import runfiles

r = runfiles.Create()


def run(args):
    if not args.targets:
        while True:
            time.sleep(60)

    executables_process = subprocess.run(
        [
            "bazel",
            "cquery",
            "--output=starlark",
            "--starlark:expr=target.files_to_run.executable.path",
        ]
        + args.bazel_args
        + [" + ".join(args.targets)],
        capture_output=True,
        encoding="utf-8",
    )
    if executables_process.returncode:
        sys.exit(f"Could not resolve executables: {executables_process.stderr}")
    executables = executables_process.stdout.strip().split("\n")

    pipe_read, pipe_write = os.pipe()

    process = subprocess.Popen(
        [
            r.Rlocation("bazel_watcher/ibazel/ibazel_/ibazel"),
            f"-profile_dev=/dev/fd/{pipe_write}",
        ]
        + args.ibazel_args
        + ["build"]
        + args.bazel_args
        + args.targets,
        pass_fds=[pipe_write],
    )
    os.close(pipe_write)

    processes = []

    def start():
        env = dict(os.environ)
        env.pop("RUNFILES_DIR", None)
        env.pop("RUNFILES_MANIFEST_FILE", None)

        for executable in executables:
            process = subprocess.Popen(
                [executable], env=env, stdin=subprocess.PIPE, encoding="utf-8"
            )
            processes.append(process)

    with os.fdopen(pipe_read, "r") as profile:
        for line in profile:
            event = json.loads(line)
            if event["type"] == "BUILD_DONE":
                if not processes:
                    start()
                    continue
                for process in processes:
                    notification = ibazel_notifications.BuildCompleted(
                        ibazel_notifications.BuildStatus.SUCCESS
                    )
                    ibazel_notifications.write_one(process.stdin, notification)
            elif event["type"] == "BUILD_FAILED":
                for process in processes:
                    notification = ibazel_notifications.BuildCompleted(
                        ibazel_notifications.BuildStatus.SUCCESS
                    )
                    ibazel_notifications.write_one(process.stdin, notification)
            elif event["type"] == "BUILD_START":
                for process in processes:
                    notification = ibazel_notifications.BuildStarted()
                    ibazel_notifications.write_one(process.stdin, notification)
