# Capture a heap dump

heaptrail analyzes a heap dump; it does not attach to a running process. This section covers
getting a good dump: from an Android device, from a JVM, and in a series for timeline work.
The quality of the dump limits everything that follows.

## Start here

- On Android, use [`android-capture`](android-capture.md). It runs the `adb` steps for you, waits for the file to be complete,
  and writes a transcript.
- On a JVM, use [`jmap` or `jcmd`](jvm.md), or let the JVM write a dump when it runs out of memory.
- To see growth over time, capture [a series](capture-a-series.md).

## Which method fits

| You have | Use | Page |
|---|---|---|
| An Android device or emulator, and `adb` | `heaptrail android-capture` | [android-capture](android-capture.md) |
| An Android device, and you want to type the commands | `adb shell am dumpheap` | [Capture by hand on Android](manual-android.md) |
| Android Studio | The Memory profiler, then **Export** | [Capture by hand on Android](manual-android.md#android-studio) |
| A running JVM | `jmap -dump` or `jcmd GC.heap_dump` | [JVM dumps](jvm.md) |
| A JVM that crashes with `OutOfMemoryError` | `-XX:+HeapDumpOnOutOfMemoryError` | [JVM dumps](jvm.md#dump-on-outofmemoryerror) |
| Three or more states of one app | `android-capture --series 3` | [Capture a series](capture-a-series.md) |
| A need to know *which line* allocated an object | Allocation tracking | [Allocation tracking](allocation-tracking.md) |

## What a good dump looks like

Check these before you spend time analyzing:

- [ ] The file is not empty. heaptrail refuses a 0-byte file with `input hprof is 0 bytes`.
- [ ] The file is complete. heaptrail does not verify that, and a cut-off file can give a partial report. Compare its size with what the device or JVM reported.
- [ ] It was taken in the state you care about. A dump of an app on its profile picker answers questions about the picker.
- [ ] You know which build it came from. For a release build, keep the matching R8 mapping file, so class names can be [restored](../android/index.md).
- [ ] `heaptrail -i dump.hprof` runs and prints a sensible `Processing … binary hprof file` line.

## What a dump costs the app

Taking a dump pauses the process while the runtime walks its heap, and the file can be as large as the heap.
On a JVM, `jmap -dump:live` also forces a full garbage collection first. Do this on a test device or a canary, not
in the middle of a production traffic spike.

## Handle dumps like secrets

A heap dump contains everything the process held in memory: tokens, cookies, user data, file contents. See
[Handle dumps safely](handle-dumps-safely.md) before you attach one to a ticket.

## All pages in this section

| Your goal | Page |
|---|---|
| Capture and validate a dump over `adb` | [android-capture](android-capture.md) |
| Capture three or more dumps for a timeline | [Capture a series](capture-a-series.md) |
| Run the `adb` commands yourself, or use Android Studio or Perfetto | [Capture by hand on Android](manual-android.md) |
| Record where objects were allocated | [Allocation tracking](allocation-tracking.md) |
| Dump a JVM | [JVM dumps](jvm.md) |
| Share a dump without leaking secrets | [Handle dumps safely](handle-dumps-safely.md) |

## Related

- [Analyze](../analyze/index.md) is what to do with the file.
- [HPROF formats](../reference/hprof-formats.md) lists the dump formats heaptrail reads.
- [Troubleshooting](../help/troubleshooting.md) covers empty, truncated and unreadable dumps.
