# How heaptrail reads a dump

**Why does one mode finish in 0.2 seconds and another take 6, and why does one need 100 MiB of memory and
another 1.7 GiB?** The answer is how many times each mode reads the file, and what it keeps in memory between reads.

## What is in the file

An HPROF file is a header followed by a stream of records. The header names the format (`JAVA PROFILE 1.0.1`,
`1.0.2` or `1.0.3`), the size of an object id (4 or 8 bytes) and a timestamp. The records include:

- the **strings** the dump refers to, such as class and field names;
- the **loaded classes**, with their fields and static values;
- stack traces and threads, when the dumper recorded them;
- one record per **object**: instances, object arrays and primitive arrays;
- the **GC roots**, and, if allocation tracking was on, the allocation sites.

Nothing in the file says "this object holds that one". References are numbers inside object records, and heaptrail has to read
them out and match them against object ids.

## The summary: one streaming pass

The default mode reads the file front to back exactly once, on three threads:

1. a **prefetch** thread reads the file in 64 MiB buffers;
2. a **parser** thread turns the bytes into records;
3. a **recorder** thread adds each record to per-class counters.

No object graph is built. The recorder keeps one counter per class and a few extras: the largest instance, the
largest arrays and, if you ask, the text of every string. A 224 MiB Android dump takes about 0.2 seconds on a recent laptop.
In a terminal, a progress bar draws on stderr while this runs and disappears when it finishes.

## Investigation modes: an index, then targeted passes

Questions about *who holds what* need more than counts. Those modes first read the file once to build a small
**index**: classes and their field layouts, threads, stack frames, GC roots and class static fields. Then they read the file again
for the question they answer.

| Mode | Extra reads | Why |
|---|---|---|
| `--find-referrers` | One per hop | Each hop scans every object for references to the objects found by the previous hop. |
| `--paths-from-id` | One per hop | Each hop scans for the first object that holds the current one. A 12-hop path reads the file 12 times. |
| `--merge-paths` | Instances × hops | The path walk runs once per instance of the class. |
| `--retained-size`, `--leak-suspects` | One to build the whole graph | The dominator tree needs every reference in memory at once. |
| `--preview-bytes` | One extra | It keeps up to N bytes of every primitive array. |
| `--diff-from`, `--diff-to` | One summary pass per file | The two files are read one after the other. |
| `--diff-series` | One summary pass per file | Same as the diff. |

That table is also a cost model. On a 224 MiB dump, `--find-referrers` took 0.51 s for one hop, 0.71 s for two and
0.93 s for three: about 0.2 s per extra hop. `--paths-from-id` over nine hops took 2.8 s, about 0.3 s per hop.

## Memory

Memory is the other half of the cost.

- **Summary, diff, series.** The read buffers dominate: a few 64 MiB buffers plus the counters. On the dumps measured,
  the peak was about 0.5 GiB, and it was flat between a 186 MiB and a 224 MiB dump.
- **Referrers and paths.** Small: 100 to 160 MiB. They hold the index and a set of ids, not the object graph.
- **Retained size and leak suspects.** These keep the whole graph. Peak memory was 5 to 7.5 times the file size on the
  Android dumps measured.

[Performance](../reference/performance.md) has the measured numbers. They come from one machine, so run
`/usr/bin/time -l heaptrail …` (macOS) or `/usr/bin/time -v heaptrail …` (Linux) on your own dump before you plan a CI job around them.

!!! warning "A full graph needs RAM"
    `--retained-size` and `--leak-suspects` keep every reference in memory at once, so the graph has to fit. On a small CI
    runner, run them on a bigger machine, or use the summary and referrers there. Dumps larger than a few hundred MiB
    were not measured for this guide.

## What heaptrail does when a dump is unusual

- **A class is missing.** Modern Android dumps can reference classes the dumper left out. heaptrail counts those instances at the
  bare object-header size, calls the class `<unknown class #id>`, and prints one warning on stderr at the end.
  Class totals are then a lower bound for those classes.
- **A file is empty.** heaptrail stops with `input hprof is 0 bytes`.
- **A file is cut short.** heaptrail does not check that a dump is complete. A truncated file can produce a partial report, or
  fail with a different error. Compare the file size with what the device or the JVM reported.
- **Ties.** Rows with equal counts or sizes can appear in a different order from one run to the next.

## Related

- [Performance](../reference/performance.md) lists wall time and memory per mode.
- [HPROF formats](../reference/hprof-formats.md) describes the header and record tags.
- [Choose the right mode](../getting-started/choose-a-mode.md) helps you pick by question.
