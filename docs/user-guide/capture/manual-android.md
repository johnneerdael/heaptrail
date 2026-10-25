# Capture by hand on Android

Use these methods when [`android-capture`](android-capture.md) is not an option: you have no `adb` on this machine, you
want a profile from Android Studio, or you need a feature the helper does not offer. The result is the same kind of
`.hprof` file, and every heaptrail mode reads it.

## With adb

This is what `android-capture` automates. Do it yourself like this:

```bash
# 1. Find the process id.
adb shell pidof com.example.myapp

# 2. Clear old dumps so /data does not fill up.
adb shell rm -f /data/local/tmp/*.hprof

# 3. Dump the heap.
adb shell am dumpheap 29481 /data/local/tmp/heap.hprof

# 4. Wait until the file stops growing (see below), then pull it.
adb shell ls -l /data/local/tmp/heap.hprof
adb pull /data/local/tmp/heap.hprof

# 5. Remove it from the device.
adb shell rm -f /data/local/tmp/heap.hprof
```

Replace `29481` with the id from step 1.

!!! warning "Wait for the file"
    On some devices `am dumpheap` returns before the file is complete. If you pull too early you get a short file,
    or a 0-byte one. Run the `ls -l` in step 4 until the size is nonzero and has not changed for a few seconds. If the
    size stays the same for a minute or more, stop and read `adb logcat` for lines about `dumpheap` or `hprof`.
    Do not analyze an empty file.

The file uses 4-byte object ids and the `JAVA PROFILE 1.0.3` format on current Android. heaptrail reads both
id sizes and all three format versions. You do not need `hprof-conv`, which exists only to convert very old Dalvik dumps.

For two dumps around an action, repeat steps 3 to 5 with a different file name each time:

```bash
adb shell rm -f /data/local/tmp/*.hprof
adb shell am dumpheap 29481 /data/local/tmp/before.hprof
# ... perform the action you suspect ...
adb shell am dumpheap 29481 /data/local/tmp/after.hprof
adb pull /data/local/tmp/before.hprof
adb pull /data/local/tmp/after.hprof
adb shell rm -f /data/local/tmp/before.hprof /data/local/tmp/after.hprof
```

Then run `heaptrail --diff-from before.hprof --diff-to after.hprof`. See [Snapshot diff](../compare/diff.md).

## Android Studio { #android-studio }

1. Run the app with **Run → Profile 'app'**.
2. In the **Memory** tool window, choose **Capture heap dump**.
3. Right-click the capture in the timeline and choose **Export…** to save it as an `.hprof` file.

If you turn on **Record memory allocations** before you capture, the dump also carries allocation sites, which
[`--allocation-sites`](../analyze/allocation-sites.md) can print.

## Perfetto

Perfetto's *Java heap dump* data source writes a heap dump in a compatible format. Follow Perfetto's
[Java heap dump guide](https://perfetto.dev/docs/data-sources/java-heap-dumps), then give the resulting file to
heaptrail as it is.

## Related

- [android-capture](android-capture.md) does all of this and writes a transcript.
- [Allocation tracking](allocation-tracking.md) for dumps that carry stack traces.
- [Handle dumps safely](handle-dumps-safely.md) before you share what you pulled.
