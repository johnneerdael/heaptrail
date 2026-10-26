# Android

Android heap dumps are the same HPROF files as JVM dumps, with a few differences that matter when you read them: release builds are obfuscated, the format has extra root kinds, some memory is not in the Java heap at all, and
`adb` is the way to get a dump. This section covers the parts that are specific to Android.

## Start here

- Class names look like `a3.t`? [Deobfuscate release builds](deobfuscate-release-builds.md) with your R8 mapping file.
- Let HeapTrail pick the mapping file for the app on your device: [Auto-mapping](auto-mapping.md).
- Wondering why an Android dump looks different from a JVM one? [What is different about Android dumps](android-heaps.md).

## Your goal, and the page

| Your goal | Page |
|---|---|
| Turn `a3.t` into a real class name | [Deobfuscate release builds](deobfuscate-release-builds.md) |
| Pick the right `mapping.txt` automatically | [Auto-mapping](auto-mapping.md) |
| Understand Android-specific dump features | [What is different about Android dumps](android-heaps.md) |
| Capture a dump from a device | [android-capture](../capture/android-capture.md) |
| Capture by hand, or in Android Studio | [Capture by hand on Android](../capture/manual-android.md) |
| See pixel memory of bitmaps | [Bitmaps](../analyze/bitmaps.md) |
| Compare Java and native memory | [Native context](../compare/native-context.md) |
| Cut weak-reference noise from LeakCanary and the framework | [Exclude weak references](../holders/exclude-soft-weak.md) |

## A checklist for a release-build investigation

1. Keep the `mapping.txt` of every build you ship. The dump is only readable with the mapping of *its own* build.
2. Capture with [`android-capture --auto-mapping`](../capture/android-capture.md#mapping) so the transcript records which mapping belongs to the dump.
3. Add `--mapping <path>` (or `--auto-mapping`) to every `heaptrail` command. A report with names like `a3.t` means the mapping was left off.
4. Use `--leak-suspects --exclude-soft-weak --preview-bytes 200` as the first pass.
5. For growth over time, take a series and a `dumpsys meminfo`. See [Capture a series](../capture/capture-a-series.md).

## Related

- [Capture](../capture/index.md) covers getting the dump.
- [Analyze](../analyze/index.md) and [Trace holders](../holders/index.md) work the same on Android as anywhere.
- [HPROF formats](../reference/hprof-formats.md) lists the Android extension tags.
