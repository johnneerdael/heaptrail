# Errors and exit codes

heaptrail prints errors on standard error as `error: <message>` and sets an exit status. This page lists each message, what causes it, and what to do. Every message below was produced by a real run.

## Exit codes

| Status | Meaning | Source |
|---|---|---|
| `0` | The command succeeded. | |
| `1` | heaptrail reported an error: a missing file, a bad combination of modes, a failed capture, a mapping problem. | heaptrail |
| `2` | The command line could not be parsed: an unknown flag, a missing value, an invalid value, a conflict between flags. | The argument parser |
| `101` | heaptrail panicked. | The Rust runtime |

A panic prints `thread 'main' panicked at …` and is a bug or an input heaptrail cannot handle. Keep the dump and the command, and [report it](https://github.com/johnneerdael/heaptrail/issues).

## Input errors

<!-- output: err-no-input.txt from="error:" cmd -->
```console
$ heaptrail
error: missing required `--inputFile <path>` for the selected mode
```

`-i` is missing, and the mode needs it. Add `-i <dump>`.

<!-- output: err-missing-file.txt from="error:" cmd -->
```console
$ heaptrail -i nope.hprof
error: input file `"nope.hprof"` not found
```

The path is wrong, or is a folder. Note that the quotes in the message belong to the path.

<!-- output: err-empty.txt from="error:" cmd -->
```console
$ heaptrail -i empty.hprof
error: input hprof is 0 bytes: empty.hprof
```

The file has 0 bytes. This is a failed capture. Do not analyze it. See [Capture](../capture/index.md).

<!-- output: err-garbage.txt from="error:" cmd -->
```console
$ heaptrail -i meminfo.txt
error: invalid Hprof file - "Incomplete(Unknown)"
```

The file is not an HPROF dump, or is too short to hold a header. Check that you passed the right file.

<!-- output: err-truncated-small.txt cmd -->
```console
$ heaptrail -i truncated-5mb.hprof
Processing 4.77MiB binary hprof file in 'JAVA PROFILE 1.0.2' format.

thread 'main' (76088808) panicked at src/rendered_result.rs:507:14:
Results can't be empty
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

A dump that was cut off early can end in a panic rather than a clear error. This is a 4.77 MiB prefix of a 224 MiB dump: the file has a valid header and class table but no heap contents, so
there is nothing to report and heaptrail stops with status 101. A longer prefix of a dump that holds some objects can produce a partial report with exit status 0, because heaptrail does not check that a dump is complete. Compare
the file size with what the device or JVM reported.

## Mode and argument errors

<!-- output: conflict.txt from="error:" cmd -->
```console
$ heaptrail -i heap.hprof --find-referrers java.util.ArrayList --paths-from-id 1
error: conflicting modes: pick exactly one of `--find-referrers`, `--paths-from-id`, or `--diff-from`/`--diff-to`
```

Two modes at once. Give one. The same message appears when a flag needs a mode that is missing, such as `--diff-from` alone, or `--group-holders` without a referrer mode:

<!-- output: diff-only-from.txt from="error:" cmd -->
```console
$ heaptrail --diff-from before.hprof
error: conflicting modes: pick exactly one of `--find-referrers`, `--paths-from-id`, or `--diff-from`/`--diff-to`
```

<!-- output: err-top-zero.txt from="error:" cmd -->
```console
$ heaptrail -i heap.hprof -t 0
error: invalid argument `top` - the value should be strictly positive
```

<!-- output: err-hops.txt from="error:" cmd -->
```console
$ heaptrail -i heap.hprof --find-referrers java.util.ArrayList --hops 6
error: invalid value '6' for '--hops <HOPS>': 6 is not in 1..=5

For more information, try '--help'.
```

<!-- output: err-json-out.txt from="error:" cmd -->
```console
$ heaptrail -i heap.hprof --json-out x.json
error: the following required arguments were not provided:
  --json

Usage: heaptrail --json --inputFile <INPUT_FILE> --json-out <PATH>

For more information, try '--help'.
```

`--json-out` needs `--json`. The usage line that follows the message is the argument parser's, and shows the flags it would accept.

`error: invalid Hprof file - "--diff-series requires at least 3 HProf files"` is the message when `--diff-series` has fewer than three dumps.

## Target and mode errors

| Message | Cause | What to do |
|---|---|---|
| `target class not found in dump: `<name>`` | The class name is not in the dump, or is spelled wrong. Names are dotted and case-sensitive. | Check the name in the [summary](../analyze/summary.md). Primitive array types such as `byte[]` cannot be targets. |
| `target class not found in dump: `glob '<pattern>' matched no classes; …`` | The glob matched nothing. | Check the pattern and the case. See [Target glob](../holders/target-glob.md). |
| `not yet implemented: object id not found in dump (--merge-paths)` | The id is not an instance of a class: it is a primitive array, or not in the dump. | Pick an instance id. See [Merge paths](../holders/merge-paths.md). |
| `no AllocationSites records in this dump (capture with `am profile start <pid>`)` | The dump has no allocation sites. | See [Allocation tracking](../capture/allocation-tracking.md). |
| `android.graphics.Bitmap class is not loaded in this dump; bitmap accounting has nothing to report. …` | The dump has no sizable `Bitmap`: no instances, or no `mWidth`, `mHeight` and `mConfig` fields. | See [Bitmaps](../analyze/bitmaps.md#when-it-fails). |

## Mapping errors

| Message | Cause |
|---|---|
| `mapping file not found: <path>` | `--mapping` points at a missing file. |
| `invalid mapping file <path> at line N: …` | The file is not an R8 mapping. |
| `mapping discovery failed: …` | `--auto-mapping` could not find a matching mapping. See [Auto-mapping](../android/auto-mapping.md#when-it-picks-the-wrong-thing-or-nothing). |

## Capture errors

| Message | Cause |
|---|---|
| `android capture failed: pidof returned no pid for package …` | The app is not running, or the name is wrong. |
| `android capture failed: device hprof size did not change for 60s …` | The device stopped writing the dump. |
| `android capture failed: captured hprof is 0 bytes: …` | The pull produced an empty file. |
| `android capture failed: allocation-tracked dump unsupported/failed on this device: …` | Allocation tracking did not work on this device. |
| `android capture failed: --series must be 1 or at least 3` | `--series` was 0 or 2. |
| `adb command failed: <command>`, `status: N`, `stderr: …` | `adb` ran and the device refused the command. |
| `standard I/O error (No such file or directory (os error 2))` | `adb` is not on the `PATH`, or `--json-out` points into a folder that does not exist. |

See [android-capture](../capture/android-capture.md#when-it-fails) for what to do about each.

## Warnings

These go to standard error and do not change the exit status.

| Warning | Meaning |
|---|---|
| `warning: N class id(s) referenced without a ClassDump/LoadClass record; …` | The dump references classes it does not define. Those instances were counted at the bare header size. Class totals are a lower bound. |
| `warning: mapping discovery failed: …` | `--auto-mapping optional` found no mapping and went on without one. |

## Reading a panic

If a message starts with `thread 'main' panicked`, heaptrail hit a case it did not handle. Besides the truncated dump above, closing the output early panics too: piping a long report into `head` ends with `failed printing to
stdout: Broken pipe` and exit status 101. Redirect to a file, or give `-t` a small value.

## Related

- [Troubleshooting](../help/troubleshooting.md) starts from the symptom.
- [Command line](command-line.md) for the valid values of each flag.
- [Limitations](limitations.md) lists what heaptrail cannot do.
