#!/usr/bin/env bash
# Download a day of traces into this repository's ignored adsb/ directory.
set -euo pipefail
if [[ ${1:-} != ????\.??\.?? ]]; then echo 'Usage: scripts/get.sh YYYY.MM.DD' >&2; exit 1; fi
d=$1
root=$(cd "$(dirname "$0")/.." && pwd)
tag="v$d-planes-readsb-prod-0"
out="$root/adsb/$d"
base="https://github.com/adsblol/globe_history_${d:0:4}/releases/download/$tag/$tag.tar"
mkdir -p "$out"
# Save both chunks before extracting, so a failed download cannot look successful.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
curl --fail --show-error --location "$base.aa" --output "$tmp/a"
curl --fail --show-error --location "$base.ab" --output "$tmp/b"
cat "$tmp/a" "$tmp/b" > "$tmp/archive.tar"
python3 - "$tmp/archive.tar" "$out" <<'PY'
import sys,tarfile,pathlib
allowed={'aa3b5a','a783b4','aaec64','a06bba','ad9518','a2ca97'}
with tarfile.open(sys.argv[1]) as archive:
    for member in archive:
        name=pathlib.PurePosixPath(member.name).name
        if member.isfile() and name in {f'trace_full_{code}.json' for code in allowed}:
            with archive.extractfile(member) as source:
                (pathlib.Path(sys.argv[2])/name).write_bytes(source.read())
PY
