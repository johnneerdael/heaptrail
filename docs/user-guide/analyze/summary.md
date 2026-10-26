# Summary

The summary is what HeapTrail prints when you give it a dump and no mode flag. It reads the file once and reports what the
dump contains: record counts, GC roots, and which classes take the most space. It is the fastest mode, and the right
first command on any dump.

```bash
heaptrail -i heap.hprof -t 10
```

`-i` names the dump, and `-t` (`--top`) limits each table to N rows (default 20). A 224 MiB Android dump takes about 0.2 seconds.

## What it prints

The output has five parts.

### 1. The file header and record counts

<!-- output: sum-full.txt from="Processing" until="AllocationSites:" -->
```text
Processing 224.34MiB binary hprof file in 'JAVA PROFILE 1.0.2' format.

File content summary:

UTF-8 Strings: 109331
Classes loaded: 30744
Classes unloaded: 0
Stack traces: 1
Stack frames: 0
Start threads: 0
Allocation sites: 0
End threads: 0
Control settings: 0
CPU samples: 0
Heap summaries: 0
54063 heap dumps containing in total 4572970 segments:
..GC root unknown: 237445
..GC root thread objects: 47
..GC root JNI global: 612
..GC root JNI local: 41
..GC root Java frame: 1381
..GC root native stack: 82
..GC root sticky class: 10847
..GC root thread block: 0
..GC root monitor used: 0
..GC primitive array dump: 1356562
..GC object array dump: 359794
..GC class dump: 30744
..GC instance dump: 2575415
```

- The first line names the file size and the HPROF format. [HPROF formats](../reference/hprof-formats.md) explains `1.0.1`, `1.0.2` and `1.0.3`.
- `UTF-8 Strings`, `Classes loaded`, `Stack traces` and the lines under them count the records of each type. They tell you whether the dump
  carries thread stacks (`Stack traces`) or allocation sites (`Allocation sites`).
- `N heap dumps containing in total M segments` counts the heap-dump records and the object-level records inside them.
- The `..GC root` lines count GC roots by kind. This dump reports 237,445 `unknown` roots, which is typical of an Android
  dump that was converted with `hprof-conv`, because that tool folds Android's extra root kinds into `unknown`. A raw dump
  from the same app reports 8. See [GC root kinds](../reference/gc-root-kinds.md).
- `..GC instance dump`, `..GC primitive array dump` and `..GC object array dump` count the objects, which is a good sense
  of scale before you run anything heavier.

### 2. Allocation sites and threads

<!-- output: sum-full.txt from="AllocationSites:" until="Found a total" -->
```text
AllocationSites: not present (capture with `am profile start <pid>`)

Found 0 threads with stacktraces:
```

The `AllocationSites:` line says whether the dump was captured under [allocation tracking](../capture/allocation-tracking.md). When the
dump has thread stack traces, they are listed here, one block per thread.

### 3. The class table

<!-- output: sum-full.txt from="Found a total" until="Top 10 largest" -->
```text
Found a total of 171.21MiB of raw shallow heap objects in the dump.

Top 10 raw shallow heap classes:

+------------+-----------+-------------+-----------------------------------------------------------------------------------------------------------------------+
| Total size | Instances |     Largest | Class name                                                                                                            |
+------------+-----------+-------------+-----------------------------------------------------------------------------------------------------------------------+
|   56.89MiB |    573552 | 104.00bytes | com.nexio.tv.domain.model.MetaPreview                                                                                 |
|   25.31MiB |    940474 |    28.63KiB | byte[]                                                                                                                |
|   21.59MiB |    372795 |     5.64MiB | char[]                                                                                                                |
|   20.79MiB |    908414 |  24.00bytes | java.lang.String                                                                                                      |
|   10.77MiB |    227587 |   123.52KiB | java.lang.Object[][]                                                                                                  |
|    3.68MiB |     80397 |  48.00bytes | com.squareup.moshi.LinkedHashTreeMap$Node                                                                             |
|    3.11MiB |    204027 |  16.00bytes | java.lang.StringBuilder                                                                                               |
|    2.87MiB |     75290 |  40.00bytes | androidx.compose.runtime.external.kotlinx.collections.immutable.implementations.immutableMap.PersistentHashMapBuilder |
|    2.80MiB |    122154 |  24.00bytes | java.util.ArrayList                                                                                                   |
|    2.09MiB |     40545 |   418.64KiB | int[]                                                                                                                 |
+------------+-----------+-------------+-----------------------------------------------------------------------------------------------------------------------+
```

`Found a total of … raw shallow heap objects` is the sum of the shallow sizes of every object in the dump. Each row of the table is a
class, ranked by the space its instances take:

| Column | Meaning |
|---|---|
| **Total size** | The shallow bytes of all instances of the class. |
| **Instances** | How many objects of exactly that class there are. |
| **Largest** | The biggest single instance. For `char[]`, `5.64MiB` means one array is 5.64 MiB. |
| **Class name** | Dotted, with `$` for inner classes. Primitive arrays are `byte[]`, `char[]` and so on. |

Sizes use binary units: 1 KiB is 1,024 bytes, 1 MiB is 1,048,576.

!!! note "Array names on Android dumps"
    On a JVM dump, an array of objects prints as `java.lang.Object[]`. On Android dumps HeapTrail prints it with a second pair
    of brackets, as in the table above: `java.lang.Object[][]` is an `Object[]`, and `java.util.HashMap$Node[][]` is a
    `HashMap$Node[]`. Read the extra `[]` as a quirk of the label, not as a second dimension.

### 4. The largest instances

<!-- output: sum-full.txt from="Top 10 largest" until="Largest array instances" -->
```text
Top 10 largest instances:

+------------+-----------+-----------+-------------------------------------------------+
| Total size | Instances |   Largest | Class name                                      |
+------------+-----------+-----------+-------------------------------------------------+
|   21.59MiB |    372795 |   5.64MiB | char[]                                          |
|    2.09MiB |     40545 | 418.64KiB | int[]                                           |
|  752.16KiB |        10 | 128.02KiB | com.squareup.moshi.LinkedHashTreeMap$Node[][]   |
|   10.77MiB |    227587 | 123.52KiB | java.lang.Object[][]                            |
|  161.81KiB |      2084 |  50.07KiB | long[]                                          |
|   25.31MiB |    940474 |  28.63KiB | byte[]                                          |
|  243.08KiB |      1440 |  16.02KiB | java.util.HashMap$Node[][]                      |
|   41.41KiB |       167 |   8.02KiB | java.util.concurrent.ConcurrentHashMap$Node[][] |
|    6.77KiB |        77 |   4.02KiB | int[][][]                                       |
|    4.02KiB |         1 |   4.02KiB | org.apache.xpath.objects.XObject[][]            |
+------------+-----------+-----------+-------------------------------------------------+
```

The same shape, but ranked by the biggest *single* instance. A class can be high in the first table because it has many small
objects, and high in this one because it has one big object. Both are worth a look.

### 5. Object ids of the largest arrays

<!-- output: sum-full.txt from="Largest array instances" -->
```text
Largest array instances object ids (for retainer tracing):
     5.64MiB object_id=1661812752 char[]
   418.64KiB object_id=2595270656 int[]
   128.02KiB object_id=342360064 com.squareup.moshi.LinkedHashTreeMap$Node[][]
   123.52KiB object_id=518041528 java.lang.Object[][]
    50.07KiB object_id=2743599104 long[]
    28.63KiB object_id=1717379088 byte[]
    16.02KiB object_id=1871562064 java.util.HashMap$Node[][]
     8.02KiB object_id=1940013040 java.util.concurrent.ConcurrentHashMap$Node[][]
     4.02KiB object_id=1871836952 int[][][]
     4.02KiB object_id=1870481760 org.apache.xpath.objects.XObject[][]
```

This list is the hand-off to the other modes. Each `object_id` goes straight into
[`--paths-from-id`](../holders/paths-to-root.md) or [`--find-referrers id:<id>`](../holders/find-referrers.md). See
[Object ids](../concepts/object-ids.md).

## Options that change the summary

| Flag | Effect |
|---|---|
| `-t N`, `--top N` | Rows per table. Must be at least 1. |
| `--retained-size` | Adds a retained-bytes column and re-sorts the class table. See [Retained size](retained-size.md). |
| `--preview-bytes N` | Prints the start of each large array under its id. See [Content previews](preview-bytes.md). |
| `-l`, `--listStrings` | Lists every string in the dump, and with `--preview-bytes`, large arrays. See [List strings and arrays](list-strings.md). |
| `--mapping`, `--auto-mapping` | Restores real class names in an R8-obfuscated dump. See [Android](../android/index.md). |
| `--json`, `--json-out` | Also writes the two tables as JSON. |
| `-d`, `--debug` | Prints one line for every record in the file. It is for HeapTrail's own development and produces more than a hundred thousand lines. |

## JSON

Add `--json` to also write the class tables as a file. With `--json-out <path>` you choose where. The file has two lists:

```bash
heaptrail -i heap.hprof -t 3 --json --json-out reports/summary.json
```

<!-- output: sum-json.txt from="top_allocated_classes" -->
```text
["top_allocated_classes","top_largest_instances"]
{"class_name":"com.nexio.tv.domain.model.MetaPreview","instance_count":573552,"largest_allocation_bytes":104,"allocation_size_bytes":59649408}
```

The first object of `top_allocated_classes` has the class, `instance_count`, `largest_allocation_bytes` and `allocation_size_bytes`. Arrays
also carry `largest_object_id`. The JSON does not contain the header counts, the retained column or the previews. See
[JSON output](../automate/json-output.md).

## Gotchas

- **The total is shallow.** A class that tops this table is big in its own bytes. It may not be the one keeping the most
  alive. Use [`--retained-size`](retained-size.md) or [`--leak-suspects`](leak-suspects.md) for that.
- **One dump shows now, not growth.** For growth, [compare dumps](../compare/index.md).
- **Missing classes.** If a modern Android dump references classes the dumper left out, those objects are counted at the bare
  header size, their class prints as `<unknown class #id>`, and one warning appears on stderr. The totals for those classes are a
  lower bound.
- **Ties.** Rows with equal sizes can come out in a different order on different runs.
- **Redirecting.** If you pipe the output into `head`, HeapTrail can end with a `Broken pipe` panic. Redirect to a file, or give `-t` a small value.

## Related

- [Leak suspects](leak-suspects.md) ranks what to look at, without prior knowledge.
- [Concepts: shallow and retained size](../concepts/shallow-and-retained.md) explains why the first table can mislead.
- [Choose the right mode](../getting-started/choose-a-mode.md) for the next step.
