# Playback growth

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `android-capture --series`, `--diff-series`, `--native-context`, `--find-referrers`</span>
<span><strong>Works on</strong> Android apps</span>
<span><strong>Time</strong> twenty minutes</span>
<span><strong>Undo</strong> nothing to undo: it reads dumps</span>
</div>

## The problem

A media app's memory climbs while it plays, or after repeated starts and stops, and settles somewhere higher than where it began. A single dump cannot say what grew. You need a timeline,
and a way to tell Java-heap growth from native growth, and then a way from a growing class to the object that owns it.

## The solution

1. **Capture a series and the native totals.** Take three dumps while you play, and the meminfo straight after. Add `--auto-mapping` if you have a release build, so the transcript records which mapping file belongs to the dumps.

    ```bash
    heaptrail android-capture --package com.example.myapp --out dumps --foreground --series 3 --series-delay-seconds 10
    adb shell dumpsys meminfo com.example.myapp > meminfo.txt
    ```

2. **Read the timeline.** Rename the dumps after their state, then run:

    ```bash
    heaptrail --diff-series launch.hprof play.hprof soak.hprof --diff-by bytes --top 8 --native-context meminfo.txt
    ```

    <!-- output: series-native.txt from="Monotonic growth candidates" -->
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

    Native context (dumpsys meminfo, PSS KiB):
      Java Heap:   43152 KiB
      Native Heap: 88852 KiB
      Graphics:    0 KiB
      TOTAL:       186892 KiB
      warning: missing meminfo row: GL
    ```

    Two things matter. The **monotonic growth candidates** at the top are your shortlist. The **native context** at the bottom shows that the Java heap is about 42 MiB and native about 87 MiB, so the Java heap is not the whole story.

3. **Restore names.** If the candidates read like `p1.j`, run again with `--mapping` (or `--auto-mapping`). The shortlist then names real classes. The mapping file in these examples is a small demonstration file with invented class names. See [Deobfuscate release builds](../../android/deobfuscate-release-builds.md).

4. **Trace the candidate in the last dump.** Take a class from the list and ask who holds it. Targets are matched against the names *in the dump*, so give the name as the dump prints it:

    ```bash
    heaptrail -i soak.hprof --find-referrers p1.j --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt --hops 1 --top 4
    ```

    <!-- output: pg-referrers.txt from="Found" -->
    ```text
    Found 11382 target instance(s) for com.example.myapp.player.PlaybackState

    === Direct referrers (1-hop) ===
      holder.field (or class[] for arrays)  ref count
      p1.b.j                                     1238
      p1.b.a                                     1238
      p1.b0.j                                     276
      p1.b0.a                                     276
    ```

    The target is restored to `PlaybackState` in the first line. The holder rows come back as `p1.b.j`, `p1.b.a`, `p1.b0.j`: more obfuscated names. Add the mapping for those classes too, or trace further with `--paths-from-id`. For a family of classes in one package,
    collapse the table with `--target-glob 'androidx.media3.**' --hops 2 --group-holders`. See [Group holders](../../holders/group-holders.md).

5. **Confirm it is held, not garbage.** Use `--leak-suspects --exclude-soft-weak` on the last dump. A class that grows *and* ranks as a suspect is held. A class that grows but is unreachable is allocation churn. See
   [Leak suspects](../../analyze/leak-suspects.md).

## How it works

The series isolates the classes that only grow, the meminfo says whether the Java heap is where the growth lives, and the tracing modes name the owner. Each step narrows the question: *which classes*, *which memory*,
*which holder*.

## Variations

- **Only two dumps.** Use [`--diff-from` and `--diff-to`](../diff.md). With two you cannot tell a steady climb from a single jump.
- **Native memory is the growth.** If the Java heap is flat and native grows, no dump will find it. Look at Graphics and the native heap in meminfo, check [bitmaps](../../analyze/bitmaps.md), and use a native profiler.
- **Allocation stacks.** If a class grows and you need the code that creates it, capture one more dump with [allocation tracking](../../capture/allocation-tracking.md).
- **Compose and view-heavy apps.** Candidates such as snapshot sets, slot tables and semantics nodes often rank high after many recompositions. Check whether they are still reachable before you treat them as a leak.

## Related

- [Diff a series](../diff-series.md) explains each part of the report.
- [Capture a series](../../capture/capture-a-series.md) takes the dumps.
- [Android](../../android/index.md) for names in release builds.
