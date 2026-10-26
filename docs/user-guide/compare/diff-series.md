# Diff a series

A pair of dumps shows one change. A **series** of three or more shows a trend: which classes grow at every step, which jump once, and which come back down. `--diff-series` reads the dumps in the order
you give them and reports each step, the total from the first to the last, and a shortlist of classes that never shrink.

```bash
heaptrail --diff-series launch.hprof play.hprof soak.hprof --diff-by bytes --top 8 --native-context meminfo.txt
```

List the dumps in the order you took them. At least three are required. [Capture a series](../capture/capture-a-series.md) shows how to take them with one command.

## The four parts of the report

### 1. The snapshots

<!-- output: series-native.txt from="Diff series snapshots" until="Step 0 -> 1" -->
```text
Diff series snapshots:
  [0] launch.hprof - 6918 classes, 54.28MiB shallow
  [1] play.hprof - 6918 classes, 58.54MiB shallow
  [2] soak.hprof - 6921 classes, 58.43MiB shallow
```

Each snapshot is numbered from 0 and shows the path you typed, the number of classes and the total shallow size. A heap that grows from 54.28 MiB to 58.54 MiB and then stays flat shows up here
before you read a single class.

### 2. The steps

<!-- output: series-native.txt from="Step 0 -> 1" until="Total first" -->
```text
Step 0 -> 1 top 8 deltas:

Class deltas (sorted, top 8 shown):
        Δcount       Δbytes   count(a→b)   bytes(a→b)  class
        +13984      +668848  66700→80684 3.79MiB→4.43MiB  java.lang.Object[][]
        +17152      +548864  22512→39664 703.50KiB→1.21MiB  a3.t
        +17914      +429936  57212→75126 1.31MiB→1.72MiB  java.util.ArrayList
         +7021      +329952  37934→44955 2.42MiB→2.74MiB  int[]
         +4800      +307200   6300→11100 393.75KiB→693.75KiB  f1.f
         +7642      +183408  10044→17686 235.41KiB→414.52KiB  i1.a
         +7552      +181248  10055→17607 235.66KiB→412.66KiB  y1.b
         +4697      +157584   9842→14539 438.30KiB→592.19KiB  long[]

Step 1 -> 2 top 8 deltas:

Class deltas (sorted, top 8 shown):
        Δcount       Δbytes   count(a→b)   bytes(a→b)  class
         +1463       +58520   9919→11382 387.46KiB→444.61KiB  p1.j
          +656       +18368    7503→8159 1.16MiB→1.18MiB  char[]
          +167       +17368    1116→1283 113.34KiB→130.30KiB  d1.q2
          +510       +12240 280970→281480 6.43MiB→6.44MiB  java.lang.String
          +730       +11680  12670→13400 197.97KiB→209.38KiB  s1.l
          +203       +11368    1752→1955 95.81KiB→106.91KiB  z1.z
          +702       +11232    4655→5357 72.73KiB→83.70KiB  f1.g
          +164       +10496    1074→1238 67.12KiB→77.38KiB  p1.b
```

One table for each pair of neighbours: step 0 → 1, then 1 → 2. They are the same table as a [snapshot diff](diff.md), sorted by `--diff-by` and limited to `--top` rows. The first step here is the larger one, likely warm-up, and the second is
small. The interesting classes are the ones that show up in both.

### 3. First to last

<!-- output: series-native.txt from="Total first" until="Monotonic" -->
```text
Total first -> last top 8 deltas:
     +611568 bytes       13482 count  java.lang.Object[][]
     +463104 bytes       14472 count  a3.t
     +367536 bytes       15314 count  java.util.ArrayList
     +336232 bytes        6951 count  int[]
     +259200 bytes        4050 count  f1.f
     +205200 bytes        5130 count  p1.j
     +154632 bytes        6443 count  i1.a
     +152928 bytes        6372 count  y1.b
```

The total change from the first dump to the last, for each class, sorted by `--diff-by`. It cannot tell a steady climb from one jump, which is what the next list is for.

### 4. Monotonic growth candidates

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

A class is a **monotonic growth candidate** when its value never goes down from one dump to the next and ends higher than it started. The value is the one `--diff-by` picks: bytes here, instances by default.
`int[]` and `p1.j` are on this list because they were bigger in the second dump than the first, and at least as big in the third. Use this list as the shortlist for [tracing](../holders/index.md).

!!! note "Not every class on the first-to-last list is on this one"
    `java.lang.Object[][]` has the largest total growth, but it is missing from the candidates: it fell slightly between the second and third dump. A class that rose and then fell is churn. One that only ever
    rises is a better lead for a leak.

### 5. Native context (optional)

<!-- output: series-native.txt from="Native context" -->
```text
Native context (dumpsys meminfo, PSS KiB):
  Java Heap:   43152 KiB
  Native Heap: 88852 KiB
  Graphics:    0 KiB
  TOTAL:       186892 KiB
  warning: missing meminfo row: GL
```

With `--native-context <meminfo.txt>`, HeapTrail adds the totals from `dumpsys meminfo`, so you can see whether the *Java* heap is the part that is growing. See [Native context](native-context.md).

## Mapped names

On an obfuscated build, add `--mapping` and the names in every part are restored. This is the same series with a small mapping file that covers three of the short names. (The file is a demonstration, with invented class names.)

```bash
heaptrail --diff-series launch.hprof play.hprof soak.hprof --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt --diff-by bytes --top 4
```

<!-- output: series-mapped.txt from="Total first" -->
```text
Total first -> last top 4 deltas:
     +611568 bytes       13482 count  java.lang.Object[][]
     +463104 bytes       14472 count  com.example.myapp.player.TrackQueue
     +367536 bytes       15314 count  java.util.ArrayList
     +336232 bytes        6951 count  int[]

Monotonic growth candidates (top 4):
     +336232 bytes        6951 count  int[]
     +205200 bytes        5130 count  com.example.myapp.player.PlaybackState
      +82560 bytes        5160 count  s1.l
      +62720 bytes        2240 count  char[]
```

`a3.t` and `p1.j` now read `TrackQueue` and `PlaybackState`. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

## Options

| Flag | Default | Effect |
|---|---|---|
| `--diff-series <PATH>...` | | Three or more dumps, in order. |
| `--diff-by <KEY>` | `count` | The sort key and the key for the growth test. `KEY` is `count` or `bytes`. |
| `-t`, `--top <N>` | 20 | Rows in every table of the text report. |
| `--native-context <PATH>` | | A `dumpsys meminfo` text file. |
| `--mapping`, `--auto-mapping` | off | Restore class names. |
| `--json`, `--json-out` | off | Write the full report as JSON. |

Fewer than three dumps fail:

```bash
heaptrail --diff-series launch.hprof play.hprof
```

<!-- output: series-two.txt from="error:" -->
```text
error: invalid Hprof file - "--diff-series requires at least 3 HProf files"
```

## JSON

The JSON holds the whole report, and `--top` does not shorten it. It has `snapshots` (index, path, total size, class count), `steps` (each with `from_index`, `to_index` and every class delta), `classes` (every class with an array of counts
and an array of bytes, one value per snapshot, plus the totals), `monotonic_growth` (the same rows, filtered), and `native_context` when you passed a meminfo file. The file can be large: the three dumps above produce about 930 KB. See [JSON schemas](../reference/json-schemas.md).

## Gotchas

- **Order is yours.** HeapTrail does not sort the files by time. The first path is snapshot 0.
- **Use the same build.** A new build changes obfuscated names, and every class then looks new.
- **The growth test follows `--diff-by`.** Counts and bytes can disagree about which classes qualify. Try both.
- **A short series is noisy.** Three dumps seconds apart show warm-up. Prefer dumps that bracket real work.
- **It compares classes, not objects.** To find what keeps a growing class alive, trace it in the last dump.

## Related

- [Capture a series](../capture/capture-a-series.md) takes the dumps.
- [Native context](native-context.md) explains the meminfo rows.
- [Playback growth](recipes/playback-growth.md) takes a candidate from the list to its owner.
