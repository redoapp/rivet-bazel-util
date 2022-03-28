# Bazel Util

## Features

- `bazel-mrun` - Build and run multiple targets in parallel.
- `bazel-watchrun` Build and run multiple targets, restarting them after
  changes.

## Install

```sh
bazel build bazel:tar

rm -fr /opt/rivet-bazel-util
mkdir /opt/rivet-bazel-util
tar xf bazel-bin/bazel/tar.tar -C /opt/rivet-bazel-util

printf '#!/bin/sh -e\nexec /opt/rivet-bazel-util/mrun "$@"\n' > /usr/local/bin/bazel-mrun
chmod +x /usr/local/bin/bazel-mrun
printf '#!/bin/sh -e\nexec /opt/rivet-bazel-util/watchrun "$@"\n' > /usr/local/bin/bazel-watchrun
chmod +x /usr/local/bin/bazel-watchrun
```
