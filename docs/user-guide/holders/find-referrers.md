# Find referrers

`--find-referrers` answers "what holds this?" for a whole class or for one object. It lists the fields, array slots and static fields that point at the target, with how
many references each accounts for, and with `--hops` it looks through the arrays in between to the real owner.

```bash
heaptrail -i heap.hprof --find-referrers com.nexio.tv.domain.model.MetaPreview --hops 1 --top 5
```

## Read the result

<!-- output: ref-hops1.txt from="Found" -->
```text
Found 573552 target instance(s) for com.nexio.tv.domain.model.MetaPreview

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                                                           ref count
  java.lang.Object[][]                                                                              603715
  com.nexio.tv.ui.screens.home.ModernCarouselItem.metaPreview                                          249
  com.nexio.tv.ui.screens.home.CachedCarouselItem.source                                               120
  com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernRowSection$1$6$2$1$6$1$1.$nextCatalogItem          8
  com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernRowSection$1$6$2$1$6$2$1.$metaPreview              8
```

The first line says how many instances of the target were found. The table lists each *holder* and *field*, and a **ref count**:

- `com.nexio.tv.ui.screens.home.ModernCarouselItem.metaPreview` is a field. `249` is how many `ModernCarouselItem` objects point at a target through it.
- `java.lang.Object[][]` is an array slot, not a field. On Android dumps the table writes an array of objects with an extra pair of brackets, so read it as "an element of an `Object[]`". Here 603,715
  slots in `Object[]` arrays point at a target.
- A row like `android.app.ContextImpl.sSharedPrefsCache` is a **class static field**. Statics are always included.

The **ref count** is the number of reference slots, not the number of distinct objects. A field that appears once in each of 249 holder objects counts 249. One object can also be
referenced from several slots, so the count can exceed the instance count, as it does here.

Rows are sorted by count, highest first. `--top N` limits each section to N rows, and rows with equal counts can come out in a different order on different runs.

## Look through arrays with `--hops`

Hop 1 is often useless on its own: almost every list stores its items in an `Object[]`, so the direct holder is "an array". `--hops` follows the chain one step further each time.

| Hops | What the section shows |
|---|---|
| 1 | Direct holders of the target. |
| 2 | Holders of the `Object[]` arrays found at hop 1: `ArrayList.elementData`, `SlotTable.slots`. |
| 3 | Holders of those holders: `CatalogRow.items`, the object that owns the list. |

```bash
heaptrail -i heap.hprof --find-referrers com.nexio.tv.domain.model.MetaPreview --hops 3 --top 10
```

<!-- output: first-referrers.txt from="=== 2-hop" -->
```text
=== 2-hop referrers (X holds Object[] which holds target) ===
  holder.field (or class[] for arrays)       ref count
  java.util.ArrayList.elementData                28681
  androidx.compose.runtime.SlotTable.slots           8
  androidx.compose.runtime.SlotWriter.slots          8

=== 3-hop referrers (X holds Y which holds Object[] which holds target) ===
  holder.field (or class[] for arrays)                                                                      ref count
  com.nexio.tv.domain.model.CatalogRow.items                                                                    28673
  java.util.ArrayList$ListItr.this$0                                                                             2592
  java.util.ArrayList$Itr.this$0                                                                                 1918
  kotlin.collections.CollectionsKt___CollectionsKt$asSequence$$inlined$Sequence$1.$this_asSequence$inlined       1882
  androidx.compose.runtime.SlotReader.table                                                                        16
  androidx.compose.runtime.SlotWriter.table                                                                         8
  androidx.compose.runtime.CompositionImpl.slotTable                                                                8
  androidx.compose.runtime.ComposerImpl.slotTable                                                                   8
  com.nexio.tv.ui.screens.home.HomeUiState.heroItems                                                                4
  com.nexio.tv.ui.screens.home.HomeViewModelCatalogPipelineKt$updateCatalogRowsPipeline$2$4.$baseHeroItems          3
```

Here the 603,715 slots resolve to 28,681 `ArrayList.elementData` arrays, and to `CatalogRow.items` one hop later. Start with `--hops 2` for any class that lives in collections. Each extra hop costs one more pass over the
file, about 0.2 seconds on a 224 MiB dump.

`--hops` accepts 1 to 5, but heaptrail reports at most three hops. A value of 4 or 5 prints the same three sections as 3.

## Target an object { #target-an-object }

Pass an object id instead of a class, as `id:<number>` or as bare digits:

```bash
heaptrail -i heap.hprof --find-referrers id:1661812752 --hops 1 --preview-bytes 200
```

<!-- output: ref-id.txt from="Found 1" -->
```text
Found 1 target instance(s) for id:1661812752
  preview: content: JSON
    {"schemaVersion":4,"languageEpoch":0,"languageTag":"en","posterProviderToken":"RPDB:-958971387","cat...

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  java.lang.String.value                        1
```

For a primitive array the preview says what it holds, and the table says who owns it: here a `String` through `String.value`. See [Object ids](../concepts/object-ids.md) for where to get an id.

!!! warning "An id that is not in the dump still reports a hit"
    `--find-referrers id:99999999999` prints `Found 1 target instance(s)` and `(none)`, as if the object existed and nothing held it. If you get `(none)`, check the id, and
    check that it came from this dump.

    ```bash
    heaptrail -i test-heap-dumps/hprof-64.bin --find-referrers id:99999999999 --hops 1
    ```

    <!-- output: ref-bogus-id.txt from="Found 1" -->
    ```text
    Found 1 target instance(s) for id:99999999999

    === Direct referrers (1-hop) ===
      (none)
    ```

## Choose the target

| Form | Meaning | Example |
|---|---|---|
| Fully qualified class name | Every instance of that class | `java.util.ArrayList` |
| `id:<number>` | One object | `id:1661812752` |
| Digits only | The same as `id:`, always | `1661812752` |

Class names are dotted and case-sensitive, and inner classes use `$`: `java.util.LinkedHashMap$LinkedHashMapEntry`. The slash form (`java/util/ArrayList`) is not accepted. A name that is not in the dump
fails with `target class not found in dump`.

```bash
heaptrail -i heap.hprof --find-referrers com.example.Nope --hops 1
```

<!-- output: ref-unknown.txt from="error:" -->
```text
error: target class not found in dump: `com.example.Nope`
```

Primitive array types such as `byte[]` cannot be targeted by class name. Take the id of a specific array from the summary instead.

## Add retained sizes

`--retained-size` adds a **class retained** column: how much memory each holder *class* keeps alive. It tells you which holder matters most when counts are close.

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

## Options

| Flag | Default | Effect |
|---|---|---|
| `--find-referrers <TARGET>` | | The class or id to trace. Cannot be combined with `--target-glob`. |
| `--hops <N>` | 2 | How many links to look through. 1 to 5, at most 3 reported. |
| `-t`, `--top <N>` | 20 | Rows per section. |
| `--include-statics` | on | Class statics are always listed. The flag is accepted and changes nothing. |
| `--group-holders` | off | Group the rows by owner. See [Group holders](group-holders.md). |
| `--retained-size` | off | Add the `class retained` column. |
| `--exclude-soft-weak` | off | Leave weak, soft and phantom reference objects out of the holder rows. See [Exclude weak references](exclude-soft-weak.md). |
| `--preview-bytes <N>` | 0 | With an id that is a primitive array, show its content. |
| `--json`, `--json-out` | off | Write the result as JSON with `hop1`, `hop2` and `hop3` lists. |

## Gotchas

- **Counts are slots, not objects.** Read them as weights, not as a count of owners.
- **Hop 1 can say only "array".** Use `--hops 2`.
- **Holders that are views, listeners or iterators are not leaks.** A row with a high count is where to look first, not a verdict. Ask whether that holder should outlive the target.
- **Fields are named after the dump.** On an obfuscated build you see names like `a3.t`. Add `--mapping`.

## Related

- [Paths to a GC root](paths-to-root.md) follows one object all the way up.
- [Target glob](target-glob.md) traces a whole package in one pass.
- [Who holds an activity](recipes/who-holds-an-activity.md) uses referrers on a real Android dump.
