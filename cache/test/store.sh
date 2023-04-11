#!/usr/bin/env bash
mkdir -p ~/.test
file=~/.test/"${1//[^A-Za-z0-9._-]/_}"
if [ -f "$file" ]; then
    cat > /dev/null
    exec cat "$file"
fi
exec tee "$file"
