#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
APK="$SCRIPT_DIR/app/build/outputs/apk/debug/app-debug.apk"

if [ -x "$ROOT_DIR/.tools/android-sdk/platform-tools/adb" ]; then
  ADB="$ROOT_DIR/.tools/android-sdk/platform-tools/adb"
elif [ -n "${ANDROID_HOME:-}" ] && [ -x "$ANDROID_HOME/platform-tools/adb" ]; then
  ADB="$ANDROID_HOME/platform-tools/adb"
else
  ADB="$(command -v adb)"
fi

if [ ! -f "$APK" ]; then
  "$SCRIPT_DIR/build-local.sh" assembleDebug
fi

"$ADB" install -r "$APK"
