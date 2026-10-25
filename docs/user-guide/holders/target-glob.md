# Target glob

`--find-referrers` takes one class. When you want to know who holds a whole *family* of classes, such as every model class in a package or every iterator inner class, `--target-glob` does it in
one pass. It matches class names against a shell-style pattern and traces the holders of all of them together.

```bash
heaptrail -i heap.hprof --target-glob 'com.nexio.tv.domain.model.*' --hops 2 --top 8
```

Quote the pattern. Without quotes your shell expands `*` and `$` before heaptrail sees them.

## Read the result

Output begins with the classes that matched, most instances first, and then the same holder tables as [`--find-referrers`](find-referrers.md), now for all those instances together.

<!-- output: glob-model.txt from="Found 66" head="6" -->
```text
Found 66 classes matching glob:com.nexio.tv.domain.model.*:
  - com.nexio.tv.domain.model.MetaPreview                        (573552 instances)
  - com.nexio.tv.domain.model.CatalogRow                         (28697 instances)
  - com.nexio.tv.domain.model.HydratedHomeFieldTrace             (3938 instances)
  - com.nexio.tv.domain.model.ResolvedSlot                       (1248 instances)
  - com.nexio.tv.domain.model.ProviderIds                        (547 instances)
```

The list of matched classes is printed in full, whatever `--top` is. Here it is 66 lines long. The tables that follow are limited by `--top`:

<!-- output: glob-model.txt from="Found 610247" -->
```text
Found 610247 target instance(s) for glob:com.nexio.tv.domain.model.*

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                            ref count
  java.lang.Object[][]                                               689620
  com.nexio.tv.domain.model.MetaPreview.firstPaintSource             573552
  com.nexio.tv.domain.model.MetaPreview.type                         573552
  com.nexio.tv.domain.model.MetaPreview.firstPaintStableIds          573552
  com.nexio.tv.domain.model.MetaPreview.posterShape                  573552
  com.nexio.tv.domain.model.MetaPreview.firstPaintRailSource         573440
  com.nexio.tv.domain.model.MetaPreview.firstPaintSourceProvider     573440
  com.nexio.tv.domain.model.MetaPreview.ratingSource                 573432

=== 2-hop referrers (X holds Object[] which holds target) ===
  holder.field (or class[] for arrays)                              ref count
  java.util.ArrayList.elementData                                       29105
  kotlinx.coroutines.flow.internal.CombineKt$combineInternal$2.L$0         25
  kotlin.enums.EnumEntriesList.entries                                     24
  androidx.compose.runtime.SlotTable.slots                                 15
  androidx.compose.runtime.SlotWriter.slots                                15
  java.util.LinkedHashMap$LinkedHashMapEntry.value                          9
  java.util.Arrays$ArrayList.a                                              3
```

Every row is a holder of *some* class in the family. Here `MetaPreview.posterShape`, `.type` and `.firstPaintSource` each have 573,552 references, one per `MetaPreview`. They are fields of a class in the family that point
at other classes in the family.

## Pattern syntax

The pattern is matched against the whole dotted class name.

| Pattern | Matches |
|---|---|
| `*` | Any characters except a `.`: one package level. It does match `$`. |
| `**` | Anything, including `.`: any number of package levels. |
| `?` | Exactly one character. |
| `[abc]` | One of the listed characters. |

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --target-glob 'java.util.Linked*' --hops 1 --top 3
```

<!-- output: glob-linked.txt from="Found 3 classes" -->
```text
Found 3 classes matching glob:java.util.Linked*:
  - java.util.LinkedList$Node     (378 instances)
  - java.util.LinkedList          (190 instances)
  - java.util.LinkedHashMap$Entry (16 instances)

Found 584 target instance(s) for glob:java.util.Linked*

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  java.util.LinkedList.last                   190
  java.util.HashMap$Node.value                190
  java.util.LinkedList.first                  190
```

`java.util.Linked*` matched `LinkedList$Node`, an inner class, because `*` does not stop at `$`. Patterns are case-sensitive. To match inner classes of any class, use `**$Itr`:

```bash
heaptrail -i heap.hprof --target-glob '**$Itr' --hops 1 --top 8
```

<!-- output: glob-itr.txt from="Found 4 classes" -->
```text
Found 4 classes matching glob:**$Itr:
  - java.util.ArrayList$Itr                     (1938 instances)
  - java.util.AbstractList$Itr                  (8 instances)
  - com.google.common.collect.ImmutableList$Itr (2 instances)
  - kotlin.collections.builders.ListBuilder$Itr (1 instances)

Found 1949 target instance(s) for glob:**$Itr

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                                                            ref count
  com.nexio.tv.ui.screens.home.HomeViewModelPresentationPipelineKt$enrichHeroItemsPipeline$1.L$9          2
  kotlin.sequences.FilteringSequence$iterator$1.iterator                                                  1
  com.google.common.collect.ImmutableList.EMPTY_ITR                                                       1
  kotlin.sequences.FlatteningSequence$iterator$1.iterator                                                 1
  com.nexio.tv.core.metadata.router.ProviderPlanRunner$run$1.L$5                                          1
```

If nothing matches, heaptrail says so and suggests how to look up names:

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --target-glob 'nothing.matches.*'
```

<!-- output: glob-nomatch.txt from="error:" -->
```text
error: target class not found in dump: `glob 'nothing.matches.*' matched no classes; check available classes with: heaptrail -i <file> -t 1000`
```

## Options

`--target-glob` takes the same modifiers as `--find-referrers`: `--hops`, `--top`, `--retained-size`, `--exclude-soft-weak`, `--group-holders`, `--json`. It cannot be combined with `--find-referrers`; passing
both is an argument error.

```bash
heaptrail -i heap.hprof --find-referrers java.util.ArrayList --target-glob 'java.*'
```

<!-- output: glob-conflict.txt from="error:" -->
```text
error: the argument '--find-referrers <TARGET>' cannot be used with '--target-glob <PATTERN>'

Usage: heaptrail --inputFile <INPUT_FILE> --find-referrers <TARGET>

For more information, try '--help'.
```

## Gotchas

- **The matched list is long.** For a broad pattern, pipe through `sed -n '/Found .* target/,$p'` to skip it.
- **Family-wide counts hide the member.** A holder row says "points at something in the family". To see which member, trace that class with `--find-referrers`.
- **Primitive arrays cannot be matched.** Patterns apply to class names, and `byte[]` is not one.
- **Obfuscated builds match obfuscated names.** Apply `--mapping` and write the pattern with the real names.

## Related

- [Group holders](group-holders.md) collapses a long table into owners, which is the right companion for a glob.
- [Find referrers](find-referrers.md) for one class or one object.
- [Choose the right mode](../getting-started/choose-a-mode.md).
