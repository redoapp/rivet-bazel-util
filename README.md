# Bazel Watcher 2

Similar to https://github.com/bazelbuild/bazel-watcher.

## Install

```sh
bazel build watcher/watchrun:tar
rm -fr /opt/watchrun
mkdir /opt/watchrun
tar xf bazel-bin/watcher/watchrun/tar.tar -C /opt/watchrun
printf '#!/bin/sh -e\nexec /opt/watchrun/watchrun "$@"\n' > /usr/local/bin/watchrun
chmod +x /usr/local/bin/watchrun
```
