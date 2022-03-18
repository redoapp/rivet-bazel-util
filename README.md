# Bazel Watcher 2

Similar to https://github.com/bazelbuild/bazel-watcher.

## Install

```sh
bazel build watcher/watchrun:bin
rm -fr /usr/local/bin/watchrun /usr/local/bin/watchrun.runfiles
cp bazel-bin/watcher/watchrun/bin /usr/local/bin/watchrun
cp -r bazel-bin/watcher/watchrun/bin.runfiles /usr/local/bin/watchrun.runfiles
```
