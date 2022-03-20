import argparse

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

from bazelwatcher2.restart import restart

restart.run(args)
