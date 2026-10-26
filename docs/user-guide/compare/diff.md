# Snapshot diff

`--diff-from` and `--diff-to` compare two dumps class by class: how many instances each class had in each dump, how many shallow bytes, and the difference. It is the quickest way to see what grew
between two moments.

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --top 10
```

`--diff-from` is the baseline (the earlier dump) and `--diff-to` the later one. You give both, and you do not use `-i`.

## Read the result

<!-- output: diff-count.txt from="Processing" -->
```text
Processing 224.34MiB binary hprof file in 'JAVA PROFILE 1.0.2' format.
Processing 186.08MiB binary hprof file in 'JAVA PROFILE 1.0.3' format.

Class deltas (sorted, top 10 shown):
        Δcount       Δbytes   count(a→b)   bytes(a→b)  class
        +32284     +1033088    621→32905 19.41KiB→1.00MiB  java.util.TreeMap$TreeMapEntry
        +31615      +758760    657→32272 15.40KiB→756.38KiB  com.google.gson.reflect.TypeToken
        +17537      +841776    547→18084 25.64KiB→847.69KiB  com.nexio.tv.domain.model.ProviderIds
         +4349      +139168  13508→17857 422.12KiB→558.03KiB  java.util.LinkedHashMap$LinkedHashMapEntry
         +3140       +75360       0→3140 0.00bytes→73.59KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationRejectedCandidate
         +2059       +32944    4409→6468 68.89KiB→101.06KiB  java.lang.Integer
         +1571       +50272       2→1573 64.00bytes→49.16KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationFieldTrace
         +1393      +100296       0→1393 0.00bytes→97.95KiB  com.nexio.tv.core.tvdb.TvEpisodeMetadata
          +967       +15472     244→1211 3.81KiB→18.92KiB  kotlin.Pair
          +880       +49280     961→1841 52.55KiB→100.68KiB  java.util.LinkedHashMap
```

The first two lines show the two files being read, in order. Each row of the table is a class:

| Column | Meaning |
|---|---|
| **Δcount** | Instances in the later dump minus instances in the earlier one. Positive means more. |
| **Δbytes** | The same difference in shallow bytes. |
| **count(a→b)** | The instance counts, earlier then later. |
| **bytes(a→b)** | The shallow sizes, earlier then later. |
| **class** | The class name. |

A class that is not in the earlier dump starts at `0`, as `MetadataLocalizationRejectedCandidate` does here (`0→3140`). Classes whose count and bytes are both unchanged are left out.

Both numbers are shown because they can disagree. Look at `char[]` in the [byte-sorted table](#sorting-and-direction) below: it has 197,372 *fewer* arrays in the later dump, but 26 MB *more* bytes, so the arrays that remain are bigger.

## Sorting and direction

Rows are sorted by the signed delta, **largest growth first**. Classes that shrank sort to the bottom. With `--top 10` you see only what grew, so to see what shrank, either ask for a lot of rows
and look at the end, or swap the arguments.

For the two dumps above, the biggest change is a shrink. The last rows of the full table, with `--top 3000`, are:

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --top 3000 | tail -4
```

<!-- output: diff-shrunk.txt -->
```text
       -197372    +25990448 372795→175423 21.59MiB→46.38MiB  char[]
       -450170    -46817680 573552→123382 56.89MiB→12.24MiB  com.nexio.tv.domain.model.MetaPreview
```

Or swap the arguments, and the same change reads as growth. `MetaPreview` goes from 123,382 instances to 573,552:

```bash
heaptrail --diff-from after.hprof --diff-to before.hprof --top 6
```

<!-- output: diff-swapped.txt from="Class deltas" until="  +108545" -->
```text
Class deltas (sorted, top 6 shown):
        Δcount       Δbytes   count(a→b)   bytes(a→b)  class
       +450170    +46817680 123382→573552 12.24MiB→56.89MiB  com.nexio.tv.domain.model.MetaPreview
       +197372    -25990448 175423→372795 46.38MiB→21.59MiB  char[]
```

`--diff-by` chooses the sort key. Sorted by bytes, the same two dumps tell a different story, led by `char[]` and `byte[]`:

| Flag | Sorts by | Use it for |
|---|---|---|
| `--diff-by count` (default) | Δcount | Churn: many objects created, such as iterators, wrappers and events. |
| `--diff-by bytes` | Δbytes | Payload growth: a few large objects, such as caches, buffers and images. |

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --diff-by bytes --top 10
```

<!-- output: diff-bytes.txt from="Class deltas" until="  +1393" -->
```text
Class deltas (sorted, top 10 shown):
        Δcount       Δbytes   count(a→b)   bytes(a→b)  class
       -197372    +25990448 372795→175423 21.59MiB→46.38MiB  char[]
        -46441     +5574248 940474→894033 25.31MiB→30.63MiB  byte[]
        +32284     +1033088    621→32905 19.41KiB→1.00MiB  java.util.TreeMap$TreeMapEntry
        +17537      +841776    547→18084 25.64KiB→847.69KiB  com.nexio.tv.domain.model.ProviderIds
        +31615      +758760    657→32272 15.40KiB→756.38KiB  com.google.gson.reflect.TypeToken
         +4349      +139168  13508→17857 422.12KiB→558.03KiB  java.util.LinkedHashMap$LinkedHashMapEntry
```

## A dump against itself

A diff of a file with itself finds nothing, which makes a handy sanity check:

```bash
heaptrail --diff-from heap.hprof --diff-to heap.hprof
```

<!-- output: diff-self.txt from="No per-class" -->
```text
No per-class deltas — the two snapshots match.
```

## Obfuscated builds

Class names in a release build are short and change between builds. Compare two dumps of the same build, and add `--mapping` so the names are readable. Rows whose names were restored keep the raw name in the
JSON as `obfuscated_class_name`. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

## JSON

`--json` writes the rows as a list. `--json-out` chooses the path. Each entry has the class and both sides of the difference:

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --top 3 --json --json-out reports/diff.json
```

The fields are `class_name`, `count_a`, `count_b`, `delta_count`, `bytes_a`, `bytes_b` and `delta_bytes`, plus `obfuscated_class_name` when a name was restored. See
[JSON schemas](../reference/json-schemas.md).

## Options

| Flag | Default | Effect |
|---|---|---|
| `--diff-from <PATH>` | | The earlier dump. |
| `--diff-to <PATH>` | | The later dump. Needs `--diff-from`. |
| `--diff-by <KEY>` | `count` | The sort key. `KEY` is `count` or `bytes`. |
| `-t`, `--top <N>` | 20 | Rows to show. |
| `--mapping`, `--auto-mapping` | off | Restore class names in both dumps. |
| `--json`, `--json-out` | off | Write the rows as JSON. |

## Gotchas

- **Giving only one of the two flags fails** with the generic `conflicting modes` message. Always pass both.
- **Time order matters to the reader, not to HeapTrail.** It subtracts the first from the second. If your "before" is really the later dump, the signs flip.
- **Shallow, not retained.** A class that did not grow in bytes can still keep more alive. Check a suspect with [`--retained-size`](../analyze/retained-size.md).
- **Short intervals mislead.** Two dumps seconds apart show warm-up and caches filling. Compare around a repeatable action.
- **Both files are read in full,** one after the other, about 0.3 seconds for the two dumps above.

## Related

- [Diff a series](diff-series.md) for three or more dumps.
- [Before and after an interaction](recipes/before-and-after-an-interaction.md) is the workflow for one action.
- [Trace holders](../holders/index.md) for the class a diff points at.
