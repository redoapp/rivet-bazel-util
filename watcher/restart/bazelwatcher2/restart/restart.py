import io
import os
import pathlib
import signal
import sys
import typing
from bazelwatcher2 import ibazel_notifications


class _Runner:
    digest_path: pathlib.Path
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
            new_digest = self.digest_path.read_bytes()

            if self._digest != new_digest:
                self.stop()
                self._digest = new_digest
                self.start()
                return

        if self._pipe:
            try:
                ibazel_notifications.write_one(self._pipe, notification)
            except BrokenPipeError:
                pass

    def start(self):
        if self.pass_events:
            pipe_read, pipe_write = os.pipe()
        self._pid = os.fork()
        if self._pid == 0:
            os.setpgid(0, 0)
            if self.pass_events:
                os.close(pipe_write)
                os.dup2(pipe_read, sys.stdin.fileno())
            else:
                sys.stdin.close()
            try:
                os.execvp(self.command, [self.command] + self.arguments)
            except FileNotFoundError:
                sys.exit(f"Executable does not exist: {self.command}")
        if self.pass_events:
            os.close(pipe_read)
            self._pipe = os.fdopen(pipe_write, "w")

    def stop(self, sig=signal.SIGTERM):
        self._digest = None
        if self._pipe:
            self._pipe.close()
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


def run(args):
    runner = _Runner(
        arguments=args.arguments,
        command=args.command,
        digest_path=pathlib.Path(args.digest),
        pass_events=args.pass_events,
    )

    def receive_signal(sig, frame):
        runner.stop(sig)
        sys.exit()

    signal.signal(signal.SIGINT, receive_signal)
    signal.signal(signal.SIGTERM, receive_signal)

    try:
        runner.notify(
            ibazel_notifications.BuildCompleted(
                ibazel_notifications.BuildStatus.SUCCESS
            )
        )

        for notification in ibazel_notifications.read(sys.stdin):
            runner.notify(notification)
    finally:
        runner.stop(signal.SIGTERM)
