import json
import os
import subprocess
import sys
from bazelwatcher2 import ibazel_notifications


def run(args):
    pipe_read, pipe_write = os.pipe()

    process = subprocess.Popen(
        [args.ibazel, f"-profile_dev=/dev/fd/{pipe_write}"] + args.args,
        pass_fds=[pipe_write],
    )
    os.close(pipe_write)

    processes = []

    def start():
        env = dict(os.environ)
        env.pop("RUNFILES_DIR", None)
        env.pop("RUNFILES_MANIFEST_FILE", None)

        for run in args.runs:
            process = subprocess.Popen(
                [run], env=env, stdin=subprocess.PIPE, encoding="utf-8"
            )
            processes.append(process)

    with os.fdopen(pipe_read, "r") as f:
        for line in f:
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
