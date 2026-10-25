# Retained size

The summary ranks classes by **shallow** size: the bytes each object occupies itself. `--retained-size` ranks them by
**retained** size: the bytes that would be freed if the objects were gone, including everything only they keep alive. It answers
the question the summary cannot: is this class small, or does it merely *look* small because it owns a big subgraph?

```bash
heaptrail -i heap.hprof --retained-size -t 10
```

Read [Shallow and retained size](../concepts/shallow-and-retained.md) first if the two terms are new.

## The retained class table

With the flag, the class table gains a **Retained** column and is sorted by it.

<!-- output: ret-table.txt from="Top 10 classes by retained" until="Top 10 largest" -->
```text
Top 10 classes by retained heap (dominator tree):

+-------------+-----------+-----------+-------------+-----------------------------------------------+
|     Shallow | Instances |  Retained |     Largest | Class name                                    |
+-------------+-----------+-----------+-------------+-----------------------------------------------+
|     2.80MiB |    122154 | 126.84MiB |  24.00bytes | java.util.ArrayList                           |
|     1.53MiB |     28697 |  58.58MiB |  56.00bytes | com.nexio.tv.domain.model.CatalogRow          |
|    56.89MiB |    573552 |  57.37MiB | 104.00bytes | com.nexio.tv.domain.model.MetaPreview         |
|    20.79MiB |    908414 |  30.65MiB |  24.00bytes | java.lang.String                              |
|    21.59MiB |    372795 |  16.37MiB |     5.64MiB | char[]                                        |
|     8.13KiB |       347 |  15.17MiB |  24.00bytes | kotlin.SynchronizedLazyImpl                   |
|  80.00bytes |         2 |  14.94MiB |  40.00bytes | com.nexio.tv.core.anime.AnimeIdMapAsset       |
|  16.00bytes |         1 |  14.94MiB |  16.00bytes | com.nexio.tv.core.anime.AnimeIdMappingService |
| 480.00bytes |        10 |  14.94MiB |  48.00bytes | com.squareup.moshi.LinkedHashTreeMap          |
|     3.68MiB |     80397 |  14.21MiB |  48.00bytes | com.squareup.moshi.LinkedHashTreeMap$Node     |
+-------------+-----------+-----------+-------------+-----------------------------------------------+
```

In this Android dump, `java.util.ArrayList` is 2.80 MiB shallow and 126.84 MiB retained. The lists are small. What they hold is not.
`com.nexio.tv.domain.model.CatalogRow` is 1.53 MiB shallow and 58.58 MiB retained. And 347 `kotlin.SynchronizedLazyImpl` wrappers, 8 KiB in total,
keep 15 MiB alive. Sorted by shallow size, none of the three would make the first page.

!!! warning "The rows overlap"
    Retained sizes are summed per class over every instance, and instances often contain each other. Do not add the column up, and do not
    compare one row with the total heap. Use it to rank. [Why the column overlaps](../concepts/shallow-and-retained.md#what-the-retained-column-in-a-class-table-means).

## The largest retained objects

The report ends with the single biggest objects by retained size, with their ids:

<!-- output: ret-table.txt from="Largest retained instances" -->
```text
Largest retained instances object ids:
    27.98MiB object_id=361762400 java.util.ArrayList
    27.98MiB object_id=320977512 java.lang.Object[]
    27.98MiB object_id=361760560 java.util.ArrayList
    27.98MiB object_id=320797680 java.lang.Object[]
    14.94MiB object_id=329824280 com.nexio.tv.core.anime.AnimeIdMappingService
    14.94MiB object_id=338604528 kotlin.SynchronizedLazyImpl
    14.94MiB object_id=338604792 com.nexio.tv.core.anime.AnimeIdMapAsset
     7.41MiB object_id=338605000 com.nexio.tv.core.anime.AnimeIdMapIndexes
     6.79MiB object_id=369633368 android.util.ArrayMap
     6.79MiB object_id=529946720 java.lang.Object[]
```

These ids feed the tracing modes. `object_id=361762400` is the `ArrayList` that [leak suspects](leak-suspects.md) names as the first suspect, and
the `Object[]` on the second line is the array inside it. Objects nest, so the biggest few often tell one story.

## On other modes

`--retained-size` also works on two tracing modes:

- **`--paths-from-id`** prints the retained size of each hop. It tells you how much freeing one reference would reclaim.
- **`--find-referrers`** adds a `class retained` column to each holder row.

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --max-depth 12 --retained-size --preview-bytes 200
```

<!-- output: paths-ret.txt from="Path from object_id" through="hop 9" -->
```text
Path from object_id=1661812752 (depth 9 step(s)):
  start  ── id=1661812752 (retained=5.64MiB)
         content: JSON
         {"schemaVersion":4,"languageEpoch":0,"languageTag":"en","posterProviderToken":"RPDB:-958971387","cat...
  hop 1 ── id=1661812736 (retained=5.64MiB)  (via java.lang.String.value)
  hop 2 ── id=364312776 (retained=5.64MiB)  (via java.util.HashMap$Node.value)
  hop 3 ── id=364312696 (retained=5.64MiB)  (via java.util.HashMap$Node[][10])
  hop 4 ── id=364312512 (retained=5.64MiB)  (via java.util.HashMap.table)
  hop 5 ── id=364312344 (retained=5.64MiB)  (via android.app.SharedPreferencesImpl.mMap)
  hop 6 ── id=529946832 (retained=6.79MiB)  (via java.lang.Object[][13])
  hop 7 ── id=529946800 (retained=6.79MiB)  (via android.util.ArrayMap.mArray)
  hop 8 ── id=529946720 (retained=6.79MiB)  (via java.lang.Object[][1])
  hop 9 ── id=369633368 (retained=6.79MiB)  (via android.util.ArrayMap.mArray)
```

```bash
heaptrail -i heap.hprof --find-referrers java.util.ArrayList --hops 1 --top 6 --retained-size
```

<!-- output: ref-ret.txt from="Found 122154" -->
```text
Found 122154 target instance(s) for java.util.ArrayList

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                     ref count  class retained
  com.nexio.tv.domain.model.MetaPreview.genres                573412        57.37MiB
  com.nexio.tv.domain.model.CatalogRow.items                   28697        58.58MiB
  com.squareup.moshi.LinkedHashTreeMap$Node.value              13743        14.21MiB
  com.nexio.tv.core.anime.AnimeIdMapRecord.evidence            12960         5.76MiB
  java.util.Collections$UnmodifiableRandomAccessList.c          7613         3.64MiB
  java.util.Collections$UnmodifiableRandomAccessList.list       7613         3.64MiB
```

[`--leak-suspects`](leak-suspects.md) turns retained size on by itself.

## Weak references

By default heaptrail counts weak, soft and phantom references like any other, which is the strict definition and is not what Eclipse MAT
shows. Add `--exclude-soft-weak` to match MAT's leak-hunting view. See [Reference strength](../concepts/reference-strength.md).

## What it costs

Retained size needs the whole graph in memory. On the 224 MiB Android dump, a run took 1.7 seconds and peaked at about 1.4 GiB. On a
186 MiB dump the peak was 0.9 GiB. Plan for roughly five to seven and a half times the file size. [Performance](../reference/performance.md) has the
numbers and how they were measured.

## Gotchas

- **Class statics count as roots.** An object held only by a static field is reachable in this graph, even though
  [`--paths-from-id`](../holders/paths-to-root.md) cannot see static fields.
- **The JSON summary has no retained column.** `--json` with `--retained-size` writes the same two lists as without it.
  For retained data in a file, use [`--leak-suspects --json`](leak-suspects.md#json).
- **Shallow sizes can differ from the summary's.** The retained-size graph sizes objects with its own code, so its totals are not the
  summary's `raw shallow heap`. Compare within one report.

## Related

- [Leak suspects](leak-suspects.md) ranks dominators and explains each one.
- [Concepts: shallow and retained size](../concepts/shallow-and-retained.md) defines the terms.
- [Paths to a GC root](../holders/paths-to-root.md) shows the per-hop retained sizes in context.
