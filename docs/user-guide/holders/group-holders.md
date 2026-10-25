# Group holders

A referrer table for a big family of classes can run to hundreds of rows, most of them the same few owners seen through different fields. `--group-holders` merges the rows into
one table of **owners**: by package family, holder class and field.

```bash
heaptrail -i heap.hprof --target-glob 'com.nexio.tv.domain.model.*' --hops 2 --top 8 --group-holders
```

It works with `--find-referrers` and `--target-glob`. With any other mode it fails (see [Gotchas](#gotchas)).

## Read the grouped table

The grouped table is printed before the usual hop sections:

<!-- output: glob-grouped.txt from="=== Grouped holders ===" until="=== Direct referrers" -->
```text
=== Grouped holders ===
  owner family                 holder class                                         field                        ref count
  java.lang                    java.lang.Object[]                                   []                              689620
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                posterShape                     573552
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                firstPaintSource                573552
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                type                            573552
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                firstPaintStableIds             573552
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                firstPaintSourceProvider        573440
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                firstPaintRailSource            573440
  com.nexio.tv                 com.nexio.tv.domain.model.MetaPreview                ratingSource                    573432
  java.util                    java.util.ArrayList                                  elementData                      29105
  kotlinx.coroutines.flow      kotlinx.coroutines.flow.internal.CombineKt$combin... L$0                                 25
  kotlin.enums                 kotlin.enums.EnumEntriesList                         entries                             24
  androidx.compose.runtime     androidx.compose.runtime.SlotTable                   slots                               15
  androidx.compose.runtime     androidx.compose.runtime.SlotWriter                  slots                               15
  java.util                    java.util.LinkedHashMap$LinkedHashMapEntry           value                                9
  java.util                    java.util.Arrays$ArrayList                           a                                    3
```

| Column | Meaning |
|---|---|
| **owner family** | The first three package segments of the holder class (`com.nexio.tv`). For classes in `java` and `kotlin`, the first two (`java.util`). A name without a package is its own family. |
| **holder class** | The class that holds the target. Long names are cut with `...`. |
| **field** | The field, or `[]` for an array slot. |
| **ref count** | References through that field, from all hops combined, biggest first. |

The grouping merges *all* hops into one list, so `java.util.ArrayList.elementData` from hop 2 sits among the direct holders. The usual 1-hop and 2-hop sections still follow, unchanged.

## When it helps

- **Subsystems with many classes.** A glob over `androidx.media3.**` can produce hundreds of holder rows. Grouped by family, you see which *library or layer* holds the objects.
- **Playback and cache ownership.** One field repeated across many classes collapses into a single row.
- **Reports to share.** The owner-family column makes a table readable at a glance.

## Options

| Flag | Effect |
|---|---|
| `--group-holders` | Print the grouped table. Requires `--find-referrers` or `--target-glob`. |
| `--retained-size` | Adds each holder class's retained size to the grouped rows in the JSON (`retained_bytes`). The text table does not show it. |
| `--mapping` | Grouping happens after names are restored, so families use the real package names. |
| `--json` | The grouped rows appear in the JSON as `grouped_holders`, with `owner_family`, `holder_class`, `field_label` and `ref_count`, plus `retained_bytes` when `--retained-size` is set. |

## Gotchas

- **Only for referrer modes.** `--group-holders` with the plain summary fails with `conflicting modes`. That message is generic. The real problem is that grouping needs a referrer mode.

  ```bash
  heaptrail -i heap.hprof --group-holders
  ```

  <!-- output: group-no-ref.txt from="error:" -->
  ```text
  error: conflicting modes: pick exactly one of `--find-referrers`, `--paths-from-id`, or `--diff-from`/`--diff-to`
  ```

- **Families are a convention, not an ownership proof.** `com.nexio.tv` means "the first three segments". Code in one package can belong to a team, a library or a generated class.
- **Counts are still slots.** See [Find referrers](find-referrers.md#read-the-result).

## Related

- [Target glob](target-glob.md) is the usual source of a table that needs grouping.
- [Find referrers](find-referrers.md) explains every row.
- [Playback growth](../compare/recipes/playback-growth.md) uses grouped holders on a media app.
