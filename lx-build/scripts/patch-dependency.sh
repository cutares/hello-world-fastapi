#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEP="$ROOT/source/node_modules/react-native-track-player"
patch --batch --forward --dry-run -d "$DEP" -p1 < "$ROOT/lx-build/patches/track-player-system-queue.patch"
patch --batch --forward -d "$DEP" -p1 < "$ROOT/lx-build/patches/track-player-system-queue.patch"
# Normally npm ci runs prepare. Recover generated JS if npm omitted Git prepare.
if [[ ! -f "$DEP/lib/index.js" ]]; then
  cp -R "$ROOT/track-player/src" "$DEP/"
  cp "$ROOT/track-player/tsconfig.json" "$DEP/"
  "$ROOT/source/node_modules/.bin/tsc" -p "$DEP"
fi
