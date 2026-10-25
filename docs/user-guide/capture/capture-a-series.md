# Capture a series

One heap dump shows what is alive at one instant. It cannot tell you what is *growing*. For a leak that
builds up over time, such as media playback, screen navigation or a long soak, take three or more dumps at known
points and compare them.

This tutorial takes about 10 minutes plus the time your scenario needs. You will capture a series, capture
the matching memory totals, and read the timeline.

- [ ] An app running on a device or emulator that `adb` can reach.
- [ ] [`android-capture`](android-capture.md) works for that app (try one capture first).
- [ ] The action you suspect is something you can repeat while the helper waits.

## 1. Choose the points in time

Three dumps are the minimum. A good set brackets the action:

| Dump | State | Why |
|---|---|---|
| 1 | Settled, before the action | The baseline. |
| 2 | After the action once | The first cost. |
| 3 | After the action again, or after a wait | If growth continues, it is not a one-time cost. |

For a playback problem the points might be launch, home screen loaded, playback started, playback stopped and a soak.
Name the files after the states so the report says so.

## 2. Capture the dumps

```bash
heaptrail android-capture --package com.example.myapp --out dumps --foreground --series 3 --series-delay-seconds 10
```

The helper takes three dumps, waiting ten seconds between them. Use that gap to perform the action. When it
finishes, it prints the dumps and the command to run next:

<!-- output: cap-series.txt from="Captured heap dump series" until="Dump size" -->
```text
Captured heap dump series:
  dumps/com-example-myapp-20261025-165514-01.hprof
  dumps/com-example-myapp-20261025-165514-02.hprof
  dumps/com-example-myapp-20261025-165514-03.hprof
Diff-series command: heaptrail --diff-series dumps/com-example-myapp-20261025-165514-01.hprof dumps/com-example-myapp-20261025-165514-02.hprof dumps/com-example-myapp-20261025-165514-03.hprof --diff-by bytes
```

`Dump size` is the total of all three dumps. The helper validates each dump the same way it does a single capture.

If you need to drive the app by hand between dumps, take them one at a time with `--series 1` (the default), and
name each file yourself. The series count is only for hands-off captures: it must be `1` or at least `3`.

## 3. Capture memory totals beside it

A Java heap dump does not show native memory, graphics buffers or the GL cache. Capture `dumpsys meminfo` right
after the series, so you can tell a Java-heap leak from a native one:

```bash
adb shell dumpsys meminfo com.example.myapp > meminfo.txt
```

heaptrail reads the *App Summary* block of that file. These are the rows it uses:

```bash
sed -n '/App Summary/,/TOTAL:/p' meminfo.txt
```

<!-- output: series-meminfo.txt -->
```text
 App Summary
                       Pss(KB)
                        ------
           Java Heap:    43152
         Native Heap:    88852
                Code:    29688
               Stack:      224
            Graphics:        0
       Private Other:    18536
              System:     6440

               TOTAL:   186892       TOTAL SWAP PSS:       45
```

## 4. Compare the series

Rename the files after the states, then hand all of them to `--diff-series`, in the order you took them. Add the
meminfo file with `--native-context`.

```bash
heaptrail --diff-series launch.hprof play.hprof soak.hprof --diff-by bytes --top 8 --native-context meminfo.txt
```

The report has four parts: the snapshots, the biggest changes between each adjacent pair, the totals from first to
last, and the classes that grew in every step.

<!-- output: series-native.txt from="Diff series snapshots" until="Step 0 -> 1" -->
```text
Diff series snapshots:
  [0] launch.hprof - 6918 classes, 54.28MiB shallow
  [1] play.hprof - 6918 classes, 58.54MiB shallow
  [2] soak.hprof - 6921 classes, 58.43MiB shallow
```

<!-- output: series-native.txt from="Monotonic growth candidates" until="Native context" -->
```text
Monotonic growth candidates (top 8):
     +336232 bytes        6951 count  int[]
     +205200 bytes        5130 count  p1.j
      +82560 bytes        5160 count  s1.l
      +62720 bytes        2240 count  char[]
      +58552 bytes         563 count  d1.q2
      +47208 bytes        1967 count  java.lang.String
      +46144 bytes         824 count  z1.z
      +38688 bytes        2418 count  f1.g
```

The **monotonic growth candidates** are the shortlist. A class that grows from dump 1 to 2 and again from 2 to 3 is more
interesting than one that jumped once. The native totals from `meminfo.txt` follow the timeline:

<!-- output: series-native.txt from="Native context" -->
```text
Native context (dumpsys meminfo, PSS KiB):
  Java Heap:   43152 KiB
  Native Heap: 88852 KiB
  Graphics:    0 KiB
  TOTAL:       186892 KiB
  warning: missing meminfo row: GL
```

`--native-context` does not change any Java number. It adds the totals for correlation. Here the Java heap is
43,152 KiB and the native heap is 88,852 KiB, about twice as large, so a native-memory leak would not appear in the dumps at
all. The warning says the file had no `GL:` row; heaptrail reports what it cannot find instead of guessing.

## 5. Follow the candidates

Each candidate class is a lead, not a verdict. Take the most interesting one into the tracing modes:

```bash
heaptrail -i soak.hprof --find-referrers <class> --hops 2 --group-holders
heaptrail -i soak.hprof --leak-suspects --exclude-soft-weak
```

If the names look like `a3.t`, add `--mapping` first. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

## What you learned

- A series shows growth; one dump cannot.
- `android-capture --series 3 --series-delay-seconds 10` takes validated dumps and prints the diff command.
- `dumpsys meminfo` captured beside the dumps tells you whether memory grows in the Java heap at all.
- `--diff-series` reports step deltas, first-to-last totals and the classes that grow in every step.

## Next steps

- [Diff a series](../compare/diff-series.md) explains every section of that report.
- [Playback growth](../compare/recipes/playback-growth.md) is the full workflow from the first dump to the owner of the leak.
- [Native context](../compare/native-context.md) lists the meminfo rows heaptrail reads.
