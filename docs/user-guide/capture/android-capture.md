# android-capture

`heaptrail android-capture` takes a heap dump of an app on an Android device or emulator over `adb`. It
does what you would do by hand, but it waits until the dump is complete, rejects an empty file,
cleans up after itself, and writes a transcript that shows exactly how the dump was made.

Use it when you want a dump you can trust and explain later. If you cannot use it, the manual steps are in
[Capture by hand on Android](manual-android.md).

## What you need

- `adb` on your `PATH`, and a device or emulator it can reach (`adb devices` lists it).
- An app that Android lets the shell dump. On Android 10 and later that means a debuggable build, an app marked
  `profileable` for the shell, or a rooted or userdebug device. Otherwise `am dumpheap` fails with a security error.
- The app running. `android-capture` finds it by package name.

## Run it

```bash
heaptrail android-capture --package com.example.myapp --out dumps --foreground
```

`--package` and `--out` are required. `--out` is a local folder, created if it does not exist. `--foreground` brings
the app to the front first, which matters when the leak depends on what is on screen.

<!-- output: cap-single.txt from="Processing" until="heaptrail android-capture transcript" -->
```text
Processing 3.07MiB binary hprof file in 'JAVA PROFILE 1.0.1' format.
Captured heap dump: dumps/com-example-myapp-20261025-165513.hprof
Dump size: 3214090 bytes
AllocationSites present: false
Transcript: dumps/com-example-myapp-20261025-165513-transcript.txt
```

The `Processing …` line is a quick summary pass that HeapTrail runs on the pulled file. It checks that the dump
parses and whether it holds allocation sites. The last line names the transcript.

## What it does

1. Looks up the process id: `adb shell pidof <package>`. If nothing is running, it stops here.
2. With `--foreground`, runs `adb shell monkey -p <package> 1`, which brings the app to the front.
3. Reads `adb shell dumpsys window` and keeps the focus lines (`mCurrentFocus`, `mFocusedApp`,
   `topResumedActivity`) as proof of what was on screen.
4. Deletes every `*.hprof` in `/data/local/tmp` on the device, and the allocation trace file `heaptrail-alloc.trace`.
5. Runs `adb shell am dumpheap <pid> /data/local/tmp/<name>.hprof`.
6. Polls `adb shell ls -l` on that file every half second until its size is nonzero and has stopped changing.
7. Pulls the file with `adb pull`, then deletes it from the device.
8. Checks that the local file is not empty, and runs the summary pass on it.
9. Writes `<package>-<timestamp>-transcript.txt` next to the dump.

!!! warning "It deletes other `.hprof` files"
    Step 4 removes *every* `*.hprof` in `/data/local/tmp`, not only HeapTrail's own. Move anything you want to keep.
    The cleanup stops dumps from piling up on the device and filling `/data`.

## The transcript

The transcript is a plain-text record of one capture: which package and device, which process, the focus evidence,
the local file and its size, the mapping file if you asked for one, and every `adb` command with its status and output.
It is as useful as the dump when someone else has to judge later whether the dump is trustworthy.

<!-- output: cap-single.txt from="heaptrail android-capture transcript" until="commands:" -->
```text
heaptrail android-capture transcript

package: com.example.myapp
serial: (adb default)
pid: 4242
foreground_requested: true
allocation_sites_requested: false
local_hprof: dumps/com-example-myapp-20261025-165513.hprof
dump_size_bytes: 3214090
allocation_sites_present: false
mapping_path: (none)

foreground_evidence:
  mCurrentFocus=Window{4f2a9c1 u0 com.example.myapp/com.example.myapp.MainActivity}
  mFocusedApp=ActivityRecord{8d31e77 u0 com.example.myapp/.MainActivity t112}
```

??? example "Every adb command in the transcript"

    <!-- output: cap-single.txt from="commands:" -->
    ```text
    commands:
    $ adb shell pidof com.example.myapp
    status: 0
    stdout:
    4242

    $ adb shell monkey -p com.example.myapp 1
    status: 0
    stdout:
    Events injected: 1
    ## Network stats: elapsed time=12ms (0ms mobile, 0ms wifi, 12ms not connected)

    $ adb shell dumpsys window
    status: 0
    stdout:
      mCurrentFocus=Window{4f2a9c1 u0 com.example.myapp/com.example.myapp.MainActivity}
      mFocusedApp=ActivityRecord{8d31e77 u0 com.example.myapp/.MainActivity t112}

    $ adb shell sh -c rm -f /data/local/tmp/*.hprof /data/local/tmp/heaptrail-alloc.trace
    status: 0

    $ adb shell am dumpheap 4242 /data/local/tmp/com-example-myapp-20261025-165513.hprof
    status: 0

    $ adb shell ls -l /data/local/tmp/com-example-myapp-20261025-165513.hprof
    status: 0
    stdout:
    -rw------- 1 shell shell 3214090 2026-10-25 17:02 /data/local/tmp/com-example-myapp-20261025-165513.hprof

    $ adb shell ls -l /data/local/tmp/com-example-myapp-20261025-165513.hprof
    status: 0
    stdout:
    -rw------- 1 shell shell 3214090 2026-10-25 17:02 /data/local/tmp/com-example-myapp-20261025-165513.hprof

    $ adb pull /data/local/tmp/com-example-myapp-20261025-165513.hprof dumps/com-example-myapp-20261025-165513.hprof
    status: 0
    stdout:
    /data/local/tmp/com-example-myapp-20261025-165513.hprof: 1 file pulled, 0 skipped. 91.4 MB/s (3214090 bytes in 0.036s)

    $ adb shell rm -f /data/local/tmp/com-example-myapp-20261025-165513.hprof
    status: 0
    ```

## Options

| Flag | Default | What it does |
|---|---|---|
| `--package <PACKAGE>` | (required) | The application id to dump. |
| `--out <DIR>` | (required) | Local folder for the dump and the transcript. |
| `--serial <SERIAL>` | adb's default device | Which device to use, as `adb devices` shows it. For a network device, `192.168.1.20:5555`. |
| `--foreground` | off | Bring the app to the front first. |
| `--series <COUNT>` | `1` | Take this many dumps in a row. Must be `1` or at least `3`. See [Capture a series](capture-a-series.md). |
| `--series-delay-seconds <SECONDS>` | `0` | Wait this long between the dumps of a series. |
| `--allocation-sites` | off | Turn on allocation tracking around the dump. See [Allocation tracking](allocation-tracking.md). |
| `--auto-mapping [MODE]` | off | Find the R8 mapping file for the installed build and record it in the transcript. `MODE` is `strict`, the default when you give the flag without a value, or `optional`. |
| `--project-root <DIR>` | current directory | The Android project to search for the mapping. Needs `--auto-mapping`. |

### File names

A single capture is `<package>-<timestamp>.hprof`, where the package has every character that is not a letter, digit,
`-` or `_` replaced by `-`, and the timestamp is UTC: `com-example-myapp-20261025-161235.hprof`. A series adds
`-01`, `-02` and so on.

### Mapping

`--auto-mapping` runs *before* the capture. In `strict` mode, the command fails at once if no matching mapping is found,
so you do not capture a dump you cannot read. In `optional` mode it prints a warning and goes on. Either way the dump
itself is not changed. HeapTrail records the mapping path, how it was found, and its identifiers in the transcript, and you
apply the mapping later with `--mapping` or `--auto-mapping` on the analysis commands. See [Auto-mapping](../android/auto-mapping.md).

```bash
heaptrail android-capture --package com.example.myapp --out dumps --auto-mapping --project-root myapp
```

<!-- output: cap-auto.txt from="mapping_path:" through="pg_map_hash:" -->
```text
mapping_path: myapp/app/build/outputs/mapping/universalRelease/mapping.txt
mapping_source: auto
pg_map_id: 3c1f9a07be41d2c85e6a90b7d4f21e08
pg_map_hash: SHA-256 7d5be0c4a1f2936b88d0e5c7a4419f0236ab8c5d17e3f4a9b2c60d815e7f3a24
```

## When it fails

| Message | Cause | What to do |
|---|---|---|
| `android capture failed: pidof returned no pid for package …` | The app is not running, or the package name is wrong. A newer `adb` may report the same problem as `adb command failed: adb shell pidof …` with status 1. | Start the app, and check the name with `adb shell pm list packages`. |
| `adb command failed: …` with a status and stderr | `adb` ran and the device refused the command: a security error, an offline device, no permission. | Read the stderr that follows. Fix the permission, or reconnect the device. |
| `standard I/O error (No such file or directory …)` | `adb` is not on your `PATH`. | Install the Android platform tools, or add them to `PATH`. |
| `device hprof size did not change for 60s while waiting for dump to finish …` | The device stopped writing, or never started. The file stayed the same size for 60 seconds. | Look at `adb logcat` around `dumpheap` or `hprof`. Do not analyze the file. Try again, or capture by hand. |
| `captured hprof is 0 bytes: …` | The pull produced an empty file. | Check the transcript, then try again. |
| `allocation-tracked dump unsupported/failed on this device: …` | Allocation tracking is not supported by this device or build. | Capture without `--allocation-sites` and use [suspects, diffs and referrers](allocation-tracking.md#when-it-does-not-work). |
| `--series must be 1 or at least 3` | `--series` was `0` or `2`. | Use `1` for one dump or `3` or more for a series. |

<!-- output: cap-noproc.txt -->
```text
error: android capture failed: pidof returned no pid for package com.example.myapp
```

<!-- output: cap-stall.txt -->
```text
error: android capture failed: device hprof size did not change for 60s while waiting for dump to finish: /data/local/tmp/com-example-myapp-20261025-165538.hprof (last observed size: 0 bytes)
```

When a capture fails, HeapTrail still writes the transcript, so you can see which step stopped.

## Related

- [Capture a series](capture-a-series.md) takes several dumps in one command.
- [Capture by hand on Android](manual-android.md) is the same flow without the helper.
- [Allocation tracking](allocation-tracking.md) adds stack traces to a dump.
- [Troubleshooting](../help/troubleshooting.md) covers empty and cut-off dumps.
