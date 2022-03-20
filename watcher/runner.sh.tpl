#!/usr/bin/env sh
set -e

if [ -z "${RUNFILES_DIR-}" ]; then
  if [ ! -z "${RUNFILES_MANIFEST_FILE-}" ]; then
    export RUNFILES_DIR="${RUNFILES_MANIFEST_FILE%.runfiles_manifest}.runfiles"
  else
    export RUNFILES_DIR="$0.runfiles"
  fi
fi

exec "$RUNFILES_DIR"/bazel_watcher_2/watcher/restart/bin \
  --digest "$RUNFILES_DIR"/%{digest} \
  %{flags} \
  "$RUNFILES_DIR"/%{bin}
