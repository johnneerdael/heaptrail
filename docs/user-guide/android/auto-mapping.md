# Auto-mapping

Choosing the right `mapping.txt` by hand is error-prone: several builds sit in your Gradle output folder, and the wrong one gives plausible but wrong names. `--auto-mapping` asks the device which version of the app is installed,
matches it to your local Gradle build output, and uses the mapping file of that exact build.

```bash
heaptrail -i launch.hprof --auto-mapping --package com.example.myapp --project-root myapp -t 12
```

## What you need

- `adb` on your `PATH` and the device connected. Add `--serial <SERIAL>` if more than one device is attached.
- The Android project on this machine, built with Gradle, with the release variant you installed.
- `--package <PACKAGE>`: the application id. It is required.

`--project-root <DIR>` points at the project. If you leave it out, heaptrail uses the current directory, so you can run the command from the project root.

## What it does

1. Runs `adb shell dumpsys package <package>` and reads the installed `versionCode` and `versionName`.
2. Looks for every `output-metadata.json` under `<project-root>/app/build/outputs/apk/`.
3. Keeps the ones whose `applicationId` is your package and whose first element has the same `versionCode` and `versionName` as the device.
4. For each match, takes `<project-root>/app/build/outputs/mapping/<variantName>/mapping.txt`, and keeps the matches whose mapping file exists.
5. If one remains, uses it. If several remain, it prefers the one variant whose name contains `universal`. Otherwise it stops and lists the candidates.

It then prints which file it used, and why:

<!-- output: map-auto.txt from="Using mapping" until="File content summary" -->
```text
Using mapping: myapp/app/build/outputs/mapping/universalRelease/mapping.txt
Matched package com.example.myapp versionCode=214 versionName=2.7.1 variant=universalRelease
Processing 78.90MiB binary hprof file in 'JAVA PROFILE 1.0.3' format.
```

The second line, `Matched package … versionCode=… versionName=… variant=…`, is the evidence that the mapping is the one for the installed build.

## strict and optional

`--auto-mapping` takes an optional mode.

| Mode | When no mapping can be found |
|---|---|
| `strict` (default) | The command fails. Use it when a mapped report is a requirement. |
| `optional` | heaptrail prints a warning and analyzes the dump without names restored. |

```bash
heaptrail -i launch.hprof --auto-mapping --package com.example.myapp --project-root /nonexistent -t 3
```

<!-- output: map-auto-fail.txt from="error:" -->
```text
error: mapping discovery failed: no Gradle output metadata matched installed app version with an existing mapping file
```

```bash
heaptrail -i launch.hprof --auto-mapping optional --package com.example.myapp --project-root /nonexistent -t 3
```

<!-- output: map-auto-optional.txt from="warning:" head="1" -->
```text
warning: mapping discovery failed: no Gradle output metadata matched installed app version with an existing mapping file
```

With `optional`, the analysis goes ahead after the warning, unmapped.

## When it picks the wrong thing, or nothing

| Message | Cause | What to do |
|---|---|---|
| `mapping discovery failed: --auto-mapping requires --package` | `--package` is missing. | Add it. |
| `mapping discovery failed: adb dumpsys package failed: …` | `adb` could not reach the device, or the package is not installed. | Check `adb devices` and the package name. |
| `mapping discovery failed: could not parse versionCode from dumpsys package output` | The device printed no `versionCode=` line. | Check the package name. |
| `mapping discovery failed: no Gradle output metadata matched installed app version with an existing mapping file` | No local build has the installed version, or its mapping file is gone. | Build that version, or point `--project-root` at the right project. Or give `--mapping` directly. |
| `mapping discovery failed: multiple Gradle outputs matched installed app version; use --mapping explicitly: …` | Several variants match and none is a single `universal` one. | Pick one and pass it with `--mapping`. |

```bash
heaptrail -i heap.hprof --auto-mapping
```

<!-- output: map-auto-nopkg.txt from="error:" -->
```text
error: mapping discovery failed: --auto-mapping requires --package
```

## Limits

- **The module must be called `app`.** heaptrail looks under `<project-root>/app/build/outputs/`. A project with another module name needs `--mapping`.
- **Only Gradle's `output-metadata.json` layout** is read, and only the first element of each file. Builds with several APK outputs per variant may not match.
- **It needs the device.** It reads the *installed* version. If you analyze a dump that is older than the installed build, use `--mapping` with the mapping of the build that made the dump.
- **It does not check the mapping against the dump.** It trusts the version. Install the build you captured from before you rely on it.

## In android-capture

`heaptrail android-capture --auto-mapping` runs the same discovery *before* it captures, so a missing mapping stops a doomed capture early, and records the result in the transcript. See
[android-capture](../capture/android-capture.md#mapping).

## Related

- [Deobfuscate release builds](deobfuscate-release-builds.md) explains what a mapping restores.
- [android-capture](../capture/android-capture.md) can record the mapping during capture.
- [Command line reference](../reference/command-line.md) lists `--package`, `--serial` and `--project-root`.
