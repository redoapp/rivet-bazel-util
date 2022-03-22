import argparse
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)

parser = argparse.ArgumentParser(
    prog="watchrun", description="Build and run Bazel executables."
)
parser.add_argument(
    "--bazel-arg",
    action="append",
    default=[],
    dest="bazel_args",
    metavar="BAZEL_ARG",
    help="bazel argument",
)
parser.add_argument(
    "--ibazel-arg",
    action="append",
    default=[],
    dest="ibazel_args",
    metavar="IBAZEL_ARG",
    help="ibazel argument",
)
parser.add_argument(
    "targets",
    nargs="*",
    help="Targets to run",
    metavar="target",
)

try:
    args = parser.parse_args()
    from bazelwatcher2.watchrun import watchrun

    watchrun.run(args)
except KeyboardInterrupt:
    pass
