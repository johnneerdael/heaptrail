# Allocation tracking

A normal dump tells you *what* is in memory and *who holds it*. It does not tell you *which line of code created it*.
A dump captured under **allocation tracking** also records the allocation sites: call sites with the stack that
allocated each batch of objects. [`--allocation-sites`](../analyze/allocation-sites.md) prints them.

Use it when you already know which class is too big and need the code that creates it. If you do not
know the class yet, start with [leak suspects](../analyze/leak-suspects.md).

## You must ask before the dump

Allocation sites cannot be recovered from a dump that was taken without tracking. Tracking has to be on while the
objects are allocated, then the dump taken. If you are not sure whether your dump has them, ask the summary:

```bash
heaptrail -i heap.hprof -t 1
```

<!-- output: alloc-hint-none.txt from="AllocationSites:" head="1" -->
```text
AllocationSites: not present (capture with `am profile start <pid>`)
```

That line says `not present` for most dumps. When a dump does hold them, it reads
`AllocationSites: N sites across M records (run with --allocation-sites for stack traces)`.

## Capture with the helper

```bash
heaptrail android-capture --package com.example.myapp --out dumps --allocation-sites
```

The helper turns tracking on with `am profile start`, takes the dump, and turns tracking off again, even if the dump
failed. It then checks the pulled file for allocation sites, and records the answer in the transcript as
`allocation_sites_present`.

<!-- output: cap-alloc.txt from="$ adb shell am profile start" until="$ adb shell ls -l" -->
```text
$ adb shell am profile start 4242 /data/local/tmp/heaptrail-alloc.trace
status: 0

$ adb shell am dumpheap 4242 /data/local/tmp/com-example-myapp-20261025-165536.hprof
status: 0

$ adb shell am profile stop 4242
status: 0
```

## Capture by hand

```bash
adb shell rm -f /data/local/tmp/*.hprof /data/local/tmp/heaptrail-alloc.trace
adb shell am profile start 29481 /data/local/tmp/heaptrail-alloc.trace
# ... run the workload you want to attribute ...
adb shell am dumpheap 29481 /data/local/tmp/heap.hprof
adb shell am profile stop 29481
adb shell ls -l /data/local/tmp/heap.hprof
adb pull /data/local/tmp/heap.hprof
adb shell rm -f /data/local/tmp/heap.hprof
```

Always run `am profile stop`, even if the dump failed. Tracking slows the app down.

In Android Studio, tick **Record memory allocations** in the Memory profiler before you capture. The exported dump then
carries the sites.

## When it does not work { #when-it-does-not-work }

Treat allocation tracking on Android as *opportunistic*. `am profile start` returning success means only that
tracking was requested. It does not guarantee that the runtime writes allocation records into the next dump on that
device or build.

In heaptrail's own testing on rooted Android TV hardware, `am profile start` succeeded but the tracked dump stayed 0 bytes,
while ordinary dumps worked. The helper then fails with:

```text
error: android capture failed: allocation-tracked dump unsupported/failed on this device: …
```

When that happens, do not keep retrying. Use what does not depend on tracking:

- [Leak suspects](../analyze/leak-suspects.md) for the objects that keep the most alive.
- [Diff a series](../compare/diff-series.md) for what grows.
- [Find referrers](../holders/find-referrers.md) and [paths](../holders/paths-to-root.md) for who holds it.

Tracking also changes the app's timing, so use it for a targeted reproduction, not for every baseline capture.

## JVM dumps

The JVM's standard heap dump (`jmap`, `jcmd`, `-XX:+HeapDumpOnOutOfMemoryError`) does not include allocation sites. For
those, use a profiler that can export an HPROF with them, or an allocation profiler such as Java Flight Recorder.

## Related

- [Allocation sites](../analyze/allocation-sites.md) shows how to read the report.
- [android-capture](android-capture.md) lists every flag.
- [Capture by hand on Android](manual-android.md) for the plain flow.
