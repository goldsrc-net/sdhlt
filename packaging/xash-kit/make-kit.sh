#!/usr/bin/env bash
# Build the Xash kit: a release's compilers, a mod's delta.lst with its origins widened and its liblist.gam with
# edicts "4096", and this folder's README.
#
#   packaging/xash-kit/make-kit.sh <sdhlt-<tag>.zip> <mod folder> <out.zip>
#
# <mod folder> holds the mod's own delta.lst and liblist.gam (TS 3.0's for The Specialists). They are the mod's
# files, so they go into the zip only, never into this repository. Re-running replaces <out.zip>.
set -euo pipefail
RELEASE=${1:?release zip}; MOD=${2:?mod folder}; OUT=${3:?out.zip}
HERE=$(cd "$(dirname "$0")" && pwd)
NAME=$(basename "$MOD")
for f in "$RELEASE" "$MOD/delta.lst" "$MOD/liblist.gam"; do [ -f "$f" ] || { echo "no $f" >&2; exit 1; }; done
WORK=$(mktemp -d)
trap 'rm -rf "${WORK:?}"' EXIT
unzip -q "$RELEASE" -d "$WORK"
mkdir -p "$WORK/$NAME"
python3 "$HERE/patch-delta.py" "$MOD/delta.lst" "$WORK/$NAME/delta.lst"
cp "$MOD/liblist.gam" "$WORK/$NAME/liblist.gam"
if ! grep -qi '^[[:space:]]*edicts[[:space:]]' "$WORK/$NAME/liblist.gam"; then
  # the file's own line ending, so that it stays CRLF when it was
  if grep -q $'\r' "$WORK/$NAME/liblist.gam"; then printf 'edicts "4096"\r\n'; else printf 'edicts "4096"\n'; fi >> "$WORK/$NAME/liblist.gam"
fi
cp "$HERE/README.md" "$WORK/README.md"
OUT=$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT")
rm -f "$OUT"
(cd "$WORK" && zip -qr "$OUT" .)
unzip -l "$OUT" | tail -n +4 | awk '{print $4}' | grep -v '^$' | sed 's/^/  /'
echo "$OUT"
