#!/usr/bin/env bash
set -euo pipefail
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
[[ -n "$SDK" && -d "$SDK" ]] || { echo 'Runner Android SDK is missing.' >&2; exit 2; }
SDKMANAGER="$SDK/cmdline-tools/latest/bin/sdkmanager"
[[ -x "$SDKMANAGER" ]] || SDKMANAGER="$(command -v sdkmanager)"
MISSING=()
[[ -f "$SDK/platforms/android-36/android.jar" ]] || MISSING+=("platforms;android-36")
[[ -x "$SDK/build-tools/35.0.0/aapt2" ]] || MISSING+=("build-tools;35.0.0")
[[ -f "$SDK/ndk/26.1.10909125/source.properties" ]] || MISSING+=("ndk;26.1.10909125")
[[ -x "$SDK/cmake/3.22.1/bin/cmake" ]] || MISSING+=("cmake;3.22.1")
if (( ${#MISSING[@]} )); then
  # User has explicitly accepted Google's Android SDK agreement for this build.
  set +e
  yes | "$SDKMANAGER" --sdk_root="$SDK" "${MISSING[@]}"
  LICENSE_STATUS=${PIPESTATUS[1]}
  set -e
  [[ "$LICENSE_STATUS" == 0 ]] || exit "$LICENSE_STATUS"
fi
printf 'ANDROID_HOME=%s\nANDROID_SDK_ROOT=%s\n' "$SDK" "$SDK" >> "$GITHUB_ENV"
