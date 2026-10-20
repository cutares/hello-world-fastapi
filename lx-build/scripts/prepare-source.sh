#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
test "$(git -C "$ROOT/source" rev-parse HEAD)" = fb8480728d875fa5e0da25eebd3a26bb71723aae
test "$(git -C "$ROOT/track-player" rev-parse HEAD)" = bfe33933793460e7588d4d8f38eddf7910806f29
git -C "$ROOT/source" apply --check "$ROOT/lx-build/patches/app-full.patch"
git -C "$ROOT/source" apply "$ROOT/lx-build/patches/app-full.patch"
git -C "$ROOT/track-player" apply --check "$ROOT/lx-build/patches/track-player-system-queue.patch"
git -C "$ROOT/track-player" apply "$ROOT/lx-build/patches/track-player-system-queue.patch"
node - "$ROOT/source" <<'JS'
const fs = require('fs');
const root = process.argv[2];
const pkg = JSON.parse(fs.readFileSync(root + '/package.json'));
const lock = JSON.parse(fs.readFileSync(root + '/package-lock.json'));
if (pkg.version !== '1.9.1' || pkg.versionCode !== 81) throw Error('Unexpected app version');
if (!lock.packages['node_modules/react-native-track-player'].resolved.endsWith('#bfe33933793460e7588d4d8f38eddf7910806f29')) throw Error('Unexpected track-player commit');
JS
