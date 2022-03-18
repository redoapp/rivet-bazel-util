import atexit
import argparse
import io
import os
import signal
import sys
import typing
from bazelwatcher2 import ibazel_notifications

parser = argparse.ArgumentParser(
    description="Run the command, restarting it when the digest changes",
    prog="bazel-runner",
)
parser.add_argument("--digest", help="Digest file path", required=True)
parser.add_argument(
    "--pass-events", action="store_true", help="Pass events to executable via stdin"
)
parser.add_argument("--no-pass-events", action="store_false", dest="pass_events")
parser.add_argument("command", help="Command")
parser.add_argument("arguments", help="Arguments", nargs="*")

args = parser.parse_args()


class Runner:
    digest_path: str
    command: str
    arguments: typing.List[str]
    pass_events: bool
    _pipe: typing.Optional[io.TextIOWrapper]
    _digest: typing.Optional[bytes]
    _pid: typing.Optional[int]

    def __init__(
        self,
        digest_path: str,
        command: str,
        arguments: typing.List[str],
        pass_events: bool,
    ):
        self.digest_path = digest_path
        self.command = command
        self.arguments = arguments
        self.pass_events = pass_events
        self._pipe = None
        self._digest = None
        self._pid = None

    def notify(self, notification):
        if notification == ibazel_notifications.BuildCompleted(
            ibazel_notifications.BuildStatus.SUCCESS
        ):
            with open(args.digest, "rb") as f:
                new_digest = f.read()

            if self._digest != new_digest:
                self.stop()
                self._digest = new_digest
                self._start()
                return

        if self._pipe:
            ibazel_notifications.write_one(self._pipe, notification)

    def _start(self):
        if self.pass_events:
            pipe_read, pipe_write = os.pipe()
        self._pid = os.fork()
        if self._pid == 0:
            os.setpgid(0, 0)
            if self.pass_events:
                os.close(pipe_write)
                stdin = sys.stdin.fileno()
                sys.stdin.close()
                os.dup2(pipe_read, stdin)
            else:
                sys.stdin.close()
            try:
                os.execvp(args.command, [args.command] + args.arguments)
            except FileNotFoundError:
                sys.exit(f"Executable does not exist: {args.executable}")
        if self.pass_events:
            os.close(pipe_read)
            self._pipe = os.fdopen(pipe_write, "w")

    def stop(self, sig=signal.SIGTERM):
        self._digest = None
        if self._pid:
            try:
                os.killpg(self._pid, sig)
            except ProcessLookupError:
                pass
            while True:
                try:
                    os.wait()
                except ChildProcessError:
                    break
            self._pid = None


runner = Runner(
    arguments=args.arguments,
    command=args.command,
    digest_path=args.digest,
    pass_events=args.pass_events,
)


def stop(sig):
    runner.stop(sig)


def receive_signal(sig, frame):
    stop(sig)
    sys.exit(0)


signal.signal(signal.SIGINT, receive_signal)
signal.signal(signal.SIGTERM, receive_signal)
atexit.register(stop, signal.SIGTERM)

runner.notify(
    ibazel_notifications.BuildCompleted(ibazel_notifications.BuildStatus.SUCCESS)
)

for notification in ibazel_notifications.read(sys.stdin):
    runner.notify(notification)
