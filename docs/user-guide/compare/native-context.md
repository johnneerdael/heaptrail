# Native context

A Java heap dump covers Java objects and nothing else. On Android, a lot of an app's memory is *not* in the Java heap: native allocations, decoded images, graphics buffers, the GL cache, code. A series
can show a flat Java heap while the app's memory climbs, and then the dumps alone cannot explain it.

`--native-context` adds the totals from `adb shell dumpsys meminfo` to a [diff series](diff-series.md), so you can read both side by side.

```bash
adb shell dumpsys meminfo com.example.myapp > meminfo.txt
heaptrail --diff-series launch.hprof play.hprof soak.hprof --diff-by bytes --top 8 --native-context meminfo.txt
```

`--native-context` is a modifier of `--diff-series`. It takes the path of a text file.

## What it reads

HeapTrail looks for five rows in the **App Summary** block of the file. To print that block:

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

| Row | Shown as |
|---|---|
| `Java Heap:` | Java Heap |
| `Native Heap:` | Native Heap |
| `Graphics:` | Graphics |
| `GL:` | GL |
| `TOTAL:` | TOTAL |

The values are PSS in KiB, as `dumpsys meminfo` prints them. PSS (proportional set size) splits shared pages between the processes that share them, so the numbers add up across the system.

## The output

<!-- output: series-native.txt from="Native context" -->
```text
Native context (dumpsys meminfo, PSS KiB):
  Java Heap:   43152 KiB
  Native Heap: 88852 KiB
  Graphics:    0 KiB
  TOTAL:       186892 KiB
  warning: missing meminfo row: GL
```

Rows that are in the file appear in order. A row that is missing is reported, not guessed: this device printed no `GL:` row, so the report says `warning: missing meminfo row: GL`. It does not make the command fail.

Read it next to the series. In the example the Java heap is 43,152 KiB and the native heap is 88,852 KiB, so the native part is about twice the Java part. A leak that lives in native memory would show up here and not in
any dump.

## What it does not do

- **It does not change the Java numbers.** `--native-context` only adds the block. Class deltas, totals and growth candidates are computed from the dumps as usual.
- **It is one snapshot.** The file is a single `dumpsys meminfo`, so you get one set of totals, not one per dump. Capture it right after the series, or take one per dump and read them yourself.
- **It is not parsed for other rows.** Code, Stack and Private Other are in the file but not in the report.
- **It only applies to a series.** Other modes ignore `--native-context`.

## In JSON

With `--json`, the same totals appear under `native_context`: `java_heap_kb`, `native_heap_kb`, `graphics_kb`, `gl_kb` and `total_pss_kb`, plus a `warnings` list. A row that was not found is left out of the object.

## Capture the file

`dumpsys meminfo` needs the package name or the process id:

```bash
adb shell dumpsys meminfo com.example.myapp > meminfo.txt
```

Take it while the app is in the state you captured the dumps in. For a series from [`android-capture`](../capture/capture-a-series.md), run it straight after the helper finishes. Use `adb -s <serial>` if more than one device is connected.

## Related

- [Diff a series](diff-series.md) is the report this block is attached to.
- [Capture a series](../capture/capture-a-series.md) takes the dumps and the meminfo together.
- [Bitmaps](../analyze/bitmaps.md) for graphics memory on Android.
