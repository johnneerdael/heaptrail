# Troubleshooting

Find your symptom, read the cause, apply the fix. Messages are quoted as heaptrail prints them. For the full list, see [Errors and exit codes](../reference/errors-and-exit-codes.md).

## The dump

### `input hprof is 0 bytes`

The capture failed and left an empty file. Do not analyze it. Capture again. With `android-capture`, check the transcript and `adb logcat` around `dumpheap`. See [android-capture](../capture/android-capture.md#when-it-fails).

### `invalid Hprof file - "Incomplete(Unknown)"` or `input hprof appears truncated`

The file is not a complete HPROF dump: it is too short for a header, or it was cut off. Compare its size with what the device or JVM reported, and capture again.

### A panic, `Results can't be empty`, or exit status 101

A short, cut-off dump can end in a panic, because the file has a header and a class table but no objects. Check the file size, and capture again. A longer partial dump may analyze without any error and give a partial report. heaptrail does not check
that a dump is complete.

### A panic, `failed printing to stdout: Broken pipe`

You piped heaptrail into a command that closed early, such as `head`. Redirect to a file (`heaptrail … > out.txt`) and read the file, or give `-t` a small value.

### A panic, `class id must have a class definition`

You are on heaptrail 1.1.0 or older, which crashed on modern Android dumps that reference classes the dumper left out. Upgrade to 1.1.1 or newer. See [Download and install](../getting-started/install.md#upgrade-and-uninstall).

### `warning: N class id(s) referenced without a ClassDump/LoadClass record`

The dump references classes it does not define, which is common on recent Android. heaptrail counted those instances at the bare header size, so class totals are a lower bound. It is a warning, and not a failure.

## Names

### Class names look like `a3.t` or `zh.l1`

The build is obfuscated. Add `--mapping <mapping.txt>`, or `--auto-mapping`. The mapping must come from the exact build. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

### `target class not found in dump: …`

The name is not in the dump. Check these:

- Names are dotted and case-sensitive, with `$` for inner classes: `java.util.LinkedHashMap$LinkedHashMapEntry`. The slash form is not accepted.
- On an obfuscated build, the target must be the name *in the dump* (`p1.j`), not the real name, even with `--mapping`.
- Primitive arrays such as `byte[]` cannot be targets. Use an object id.
- In a shell, quote globs, so `*` and `$` reach heaptrail: `'com.example.**'`, `'**$Itr'`.

### `--auto-mapping` finds no mapping

Read the message after `mapping discovery failed:`. The usual causes are no `--package`, no device with `adb`, a project that is not called `app`, or no local build with the installed version. See [Auto-mapping](../android/auto-mapping.md#when-it-picks-the-wrong-thing-or-nothing).

## Reading a result

### A path ends in `orphan`

The walker does not follow class static fields. Ask `--find-referrers id:<last id> --hops 1`: it lists statics. If it finds nothing, the object is unreachable garbage. See [Paths to a GC root](../holders/paths-to-root.md#orphans).

### A path repeats the same two ids

The objects hold each other, and the walker goes round until `--max-depth`. Ask `--find-referrers` about one of the repeated ids. See [Paths to a GC root](../holders/paths-to-root.md#cycles).

### A suspect shows more than 100 %

The dump has garbage that no root reaches, and heaptrail ranks it. The path ends in `orphan`. On a JVM, take the dump with `jmap -dump:live`. See [Leak suspects](../analyze/leak-suspects.md#more-than-100-and-orphans).

### The first holders are all `WeakReference`

Add `--exclude-soft-weak`. See [Exclude weak references](../holders/exclude-soft-weak.md).

### `--bitmaps` says the class is not loaded, but the summary lists `android.graphics.Bitmap`

The dump has bitmap instances, but heaptrail cannot size them because the class has no `mWidth`, `mHeight` and `mConfig` fields. See [Bitmaps](../analyze/bitmaps.md#when-it-fails).

### My numbers differ from the summary, or from MAT

Different code paths and different options. See [Why do my numbers differ from Eclipse MAT's](faq.md#why-do-my-numbers-differ-from-eclipse-mats).

### `-l` shows no URLs or tokens

`-l` lists the string table (names), not the contents of strings. Use `-l --preview-bytes 200` for the arrays. See [List strings and arrays](../analyze/list-strings.md).

## Errors from the command line

### `conflicting modes: pick exactly one of …`

Two modes at once, or a flag whose mode is missing: `--diff-from` without `--diff-to`, or `--group-holders` without a referrer mode. See [Mode compatibility](../reference/mode-compatibility.md).

### `the following required arguments were not provided: --json`

`--json-out` needs `--json`.

### `error: invalid value '6' for '--hops <HOPS>': 6 is not in 1..=5`

`--hops` takes 1 to 5, and heaptrail reports at most three hops.

### `--diff-series requires at least 3 HProf files`

Pass three or more dumps. For two, use `--diff-from` and `--diff-to`.

## Cost

### `--leak-suspects` or `--retained-size` runs out of memory

They keep the whole object graph, about 5 to 7.5 times the dump's size. Run them on a bigger machine, or use the summary and `--find-referrers`. See [Performance](../reference/performance.md).

### `--merge-paths` never finishes

It walks every instance of the class, one pass per hop. Use a class with few instances, and lower `--max-depth`. See [Merge paths](../holders/merge-paths.md#what-it-costs).

### A path takes many seconds

Each hop reads the file once. Lower `--max-depth`, or use `--find-referrers id:<id> --hops 2` for a wider view at a similar cost.

## Android capture

### `pidof returned no pid for package …`

The app is not running, or the name is wrong. Start it, and check the name with `adb shell pm list packages`. A newer `adb` may report this as `adb command failed` with status 1.

### `adb command failed … stderr: …` with a security error

`am dumpheap` is refused for an app that is neither debuggable nor `profileable` for the shell. Use a debug or profileable build, or a rooted or userdebug device.

### `device hprof size did not change for 60s …`

The device stopped writing the dump. Read `adb logcat` for `dumpheap` or `hprof`, and try again. Do not analyze the file. See [android-capture](../capture/android-capture.md#when-it-fails).

### `standard I/O error (No such file or directory (os error 2))`

`adb` is not on your `PATH`, or `--json-out` points into a folder that does not exist.

### `allocation-tracked dump unsupported/failed on this device`

Allocation tracking did not work. Capture without `--allocation-sites`, and use suspects, diffs and referrers. See [Allocation tracking](../capture/allocation-tracking.md#when-it-does-not-work).

## Still stuck

Open an issue on [GitHub](https://github.com/johnneerdael/heaptrail/issues) with `heaptrail --version`, your operating system, the exact command and the error. Check the dump for secrets before you attach it.

## Related

- [Errors and exit codes](../reference/errors-and-exit-codes.md) lists every message.
- [Limitations](../reference/limitations.md) lists known quirks.
- [FAQ](faq.md) answers common questions.
