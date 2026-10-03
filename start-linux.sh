#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if ! command -v python3 >/dev/null 2>&1; then
    printf '%s\n' 'Python 3.10 or newer is required. Install python3 using your distribution package manager.' >&2
    exit 1
fi
exec python3 "$script_dir/remote_ai.py" "$@"
