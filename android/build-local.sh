#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -z "${JAVA_HOME:-}" ] && [ -d "$ROOT_DIR/.tools/jdk" ]; then
  JAVA_HOME="$(find "$ROOT_DIR/.tools/jdk" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
  export JAVA_HOME
fi

if [ -z "${ANDROID_HOME:-}" ] && [ -d "$ROOT_DIR/.tools/android-sdk" ]; then
  export ANDROID_HOME="$ROOT_DIR/.tools/android-sdk"
fi

if [ -n "${ANDROID_HOME:-}" ] && [ -z "${ANDROID_SDK_ROOT:-}" ]; then
  export ANDROID_SDK_ROOT="$ANDROID_HOME"
fi

if [ -d "$ROOT_DIR/.tools/gradle-home" ]; then
  export GRADLE_USER_HOME="${GRADLE_USER_HOME:-$ROOT_DIR/.tools/gradle-home}"
fi

if [ "$#" -eq 0 ]; then
  set -- assembleDebug
fi

cd "$SCRIPT_DIR"

if [ -x "$ROOT_DIR/.tools/gradle/gradle-8.9/bin/gradle" ]; then
  "$ROOT_DIR/.tools/gradle/gradle-8.9/bin/gradle" --no-daemon "$@"
else
  ./gradlew --no-daemon "$@"
fi
