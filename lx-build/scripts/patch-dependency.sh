#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEP="$ROOT/source/node_modules/react-native-track-player"
PIN=bfe33933793460e7588d4d8f38eddf7910806f29
test "$(git -C "$ROOT/track-player" rev-parse HEAD)" = "$PIN"
# npm's Git package can omit src/tsconfig. Restore pristine pinned inputs, not
# the checkout's already-patched working tree, before checking the full patch.
git -C "$ROOT/track-player" archive "$PIN" src tsconfig.json | tar -x -C "$DEP"
patch --batch --forward --dry-run -d "$DEP" -p1 < "$ROOT/lx-build/patches/track-player-system-queue.patch"
patch --batch --forward -d "$DEP" -p1 < "$ROOT/lx-build/patches/track-player-system-queue.patch"
# Regenerate even if npm supplied lib: the patch also changes public TS types.
"$ROOT/source/node_modules/.bin/tsc" -p "$DEP"
