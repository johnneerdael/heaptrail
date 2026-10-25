# What is different about Android dumps

heaptrail reads Android and JVM dumps with the same modes. A few things differ, and knowing them saves you from reading a quirk as a finding.

## Format and ids

- **Object ids are 4 bytes.** Android uses 32-bit ids, most JVMs use 64-bit. heaptrail reads both, and prints plain decimal numbers either way. Ids on Android dumps are smaller, such as `1661812752`.
- **The format is `JAVA PROFILE 1.0.3`** on current Android (`am dumpheap`). Older JVM dumps are `1.0.1` or `1.0.2`. The summary's first line says which you have.
- **Android adds extra root kinds** and a few record types. heaptrail parses them all, and keeps the roots as their own kinds on a path, such as `RootVmInternal` and `RootJniMonitor`. [HPROF formats](../reference/hprof-formats.md) lists them.

### Converted dumps

Some tools convert an Android dump to the standard format. `hprof-conv`, which exists for very old Dalvik dumps, folds Android's extra root kinds into `RootUnknown`. You do not need it for a modern dump. The effect is visible in
the summary's root counts. The 224 MiB dump used in this guide shows the signature of such a conversion, and a raw one from the same app does not:

| Dump | `..GC root unknown` |
|---|---|
| `heap.hprof` (converted, `JAVA PROFILE 1.0.2`) | 237,445 |
| `heap-b.hprof` (raw, `JAVA PROFILE 1.0.3`) | 8 |

Class totals and referrers come out the same either way. Root kinds on a path are less specific in the converted file.

## Names

- **Array classes print with an extra pair of brackets** in class tables and referrer rows: `java.lang.Object[][]` is an `Object[]`. On a JVM dump the same array prints as `java.lang.Object[]`. In JSON, the single-bracket name is used.
- **Release builds are obfuscated.** Class names such as `a3.t` need a mapping. See [Deobfuscate release builds](deobfuscate-release-builds.md).
- **Kotlin and Compose names are long.** Lambdas appear as `MainActivity$onCreate$6$2$1$1$17$1`, coroutine state machines as `…$1.L$0`, and generated holders such as `SlotTable.slots`. They are real classes, and most are noise for a leak hunt.

## What the dump does not contain

- **Native memory.** Decoded bitmap pixels (from Android 8), graphics buffers, the GL cache, `malloc` allocations and code are outside the Java heap. A dump can look healthy while the app's memory is not. Pair a dump with
  `dumpsys meminfo` and `--native-context`. See [Native context](../compare/native-context.md).
- **Thread names and stacks, most of the time.** The summary usually reports `Found 0 threads with stacktraces`, so a path that ends at a thread root prints raw thread serials instead of a name. See [Paths to a GC root](../holders/paths-to-root.md#how-it-ends).
- **Allocation sites**, unless you captured with tracking. See [Allocation tracking](../capture/allocation-tracking.md).
- **Some classes.** Dumps from recent Android versions can reference classes that the dumper left out, such as zygote-shared classes. heaptrail counts those instances at the bare header size, calls the class `<unknown class #id>`, and
  warns once on stderr. The class totals are then a lower bound. This was a crash before 1.1.1.

## Noise to expect

- **Weak references.** LeakCanary's `KeyedWeakReference`, the framework's `WeakReference<Activity>`, and the collector's own reference lists crowd paths. Use `--exclude-soft-weak`. See [Exclude weak references](../holders/exclude-soft-weak.md).
- **Views hold their context.** An `Activity` is held by every `View` through `mContext`. That is expected. See [Who holds an activity](../holders/recipes/who-holds-an-activity.md).
- **Singletons from dependency injection.** Hilt and Dagger components hold providers, and providers point back. Paths through them can go in circles. See [Paths to a GC root](../holders/paths-to-root.md#cycles).
- **Static caches.** `SharedPreferences`, image loaders and framework caches are held by static fields. A path ends in `orphan`, and find-referrers shows the static. See [Find the static that holds a cache](../holders/recipes/find-the-static-that-holds-a-cache.md).

## Getting a dump

`am dumpheap` works for a debuggable app, or for an app marked `profileable` for the shell (Android 10 and later). On a production device with a normal release build, it fails with a security error. Use a debuggable or profileable
build, or a rooted or userdebug device. [android-capture](../capture/android-capture.md) wraps the steps.

## Related

- [Capture](../capture/index.md) for getting a dump.
- [Bitmaps](../analyze/bitmaps.md) for pixel memory.
- [HPROF formats](../reference/hprof-formats.md) for the file format.
