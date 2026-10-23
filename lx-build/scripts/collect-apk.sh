#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
mapfile -t APKS < <(find "$ROOT/source/android/app/build/outputs/apk/release" -maxdepth 1 -type f -name '*-arm64-v8a.apk')
[[ ${#APKS[@]} == 1 ]] || { echo "Expected one ARM64 APK, found ${#APKS[@]}" >&2; exit 2; }
SDK="${ANDROID_HOME:?}"
"$SDK/build-tools/35.0.0/apksigner" verify "${APKS[0]}"
BADGING="$("$SDK/build-tools/35.0.0/aapt2" dump badging "${APKS[0]}")"
grep -q "package: name='com.luna.music' versionCode='85003'" <<< "$BADGING"
grep -q "native-code: 'arm64-v8a'" <<< "$BADGING"
mkdir -p "$ROOT/apk-artifact"
cp "${APKS[0]}" "$ROOT/apk-artifact/LX-v1.9.1-originos-arm64-TEMP-SIGNED.apk"
cd "$ROOT/apk-artifact"
sha256sum ./*.apk > SHA256SUMS.txt
