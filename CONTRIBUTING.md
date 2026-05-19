# Contributing

Thanks for helping improve Codex Quota Coach Lite.

## Development Setup

Python backend:

```bash
python3 -m unittest discover -s tests
python3 -m quota_coach collect
```

Android widget:

```bash
cd android
./gradlew assembleDebug
```

If you keep the optional local toolchain under `.tools/`, `android/build-local.sh` will pick it up automatically.

## Pull Request Checklist

- Keep secrets, tokens, local snapshots, and build outputs out of commits.
- Run `python3 -B -m unittest discover -s tests`.
- If Android files changed, run `cd android && ./gradlew assembleDebug` or build in Android Studio.
- Update docs when changing setup, API shape, or deployment behavior.

## Scope

This project intentionally stays small:

- collect local Codex quota snapshots
- expose the latest snapshot through Quota Hub
- show it on Android home screen widgets

Task recommendation engines, account systems, and general analytics dashboards are out of scope for the Lite project.
