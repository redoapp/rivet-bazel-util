import argparse

parser = argparse.ArgumentParser(
    prog="watchrun", description="Build and run Bazel executables."
)
parser.add_argument(
    "--run",
    action="append",
    default=[],
    dest="runs",
    help="path to executable",
    metavar="RUN",
)
parser.add_argument("args", metavar="arg", nargs="*", help="ibazel args")

if __name__ == "__main__":
    try:
        args = parser.parse_args()
        from bazelwatcher2.watchrun import watchrun

        watchrun.run(args)
    except KeyboardInterrupt:
        pass
