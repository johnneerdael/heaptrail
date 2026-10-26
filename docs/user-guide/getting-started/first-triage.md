# Your first triage

You will take a 224 MiB heap dump from "this app uses too much memory" to the field that
keeps 28 MiB alive. It takes about 15 minutes. Each step is one command, and each
command's output points to the next one.

Before you start:

- [ ] HeapTrail is [installed](install.md) (`heaptrail --version` prints a version).
- [ ] You have a heap dump. Use your own, or read along: every output below comes from
  a real dump of an Android TV app, so your numbers will differ. To run the commands
  yourself on a file from the repository, see [Follow along with the bundled files](follow-along.md).

The examples call the file `heap.hprof`. Replace it with your own path.

!!! note "Release builds show short names"
    If the class names in your output look like `a3.t` or `p1.j`, the dump is from an
    R8-obfuscated build. Add `--mapping <mapping.txt>` to every command in this tutorial.
    See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

## 1. See what takes the space

Start with the default mode. It reads the whole file once and prints what is in it.

```bash
heaptrail -i heap.hprof -t 5
```

`-t 5` limits each table to five rows. Here is the part to look at.

<!-- output: first-summary.txt from="Found a total" until="Top 5 largest" -->
```text
Found a total of 171.21MiB of raw shallow heap objects in the dump.

Top 5 raw shallow heap classes:

+------------+-----------+-------------+---------------------------------------+
| Total size | Instances |     Largest | Class name                            |
+------------+-----------+-------------+---------------------------------------+
|   56.89MiB |    573552 | 104.00bytes | com.nexio.tv.domain.model.MetaPreview |
|   25.31MiB |    940474 |    28.63KiB | byte[]                                |
|   21.59MiB |    372795 |     5.64MiB | char[]                                |
|   20.79MiB |    908414 |  24.00bytes | java.lang.String                      |
|   10.77MiB |    227587 |   123.52KiB | java.lang.Object[][]                  |
+------------+-----------+-------------+---------------------------------------+
```

Two rows stand out.

- `MetaPreview` is an app class, and there are 573,552 of them: 56.89 MiB, a third of the heap.
  Each one is only 104 bytes, so this is a count problem, not a size problem.
- One `char[]` is 5.64 MiB on its own (the **Largest** column).

The same output ends with a list of the largest arrays and their **object ids**. You will
use one of those ids in step 4.

!!! tip "What does shallow mean?"
    **Total size** counts only the bytes each object occupies itself, not what it points
    to. That is why this view cannot tell you what is *keeping* those objects alive. Steps
    2 and 3 do. [Shallow and retained size](../concepts/shallow-and-retained.md) explains the difference.

## 2. Ask for suspects

You do not need to know which class to look at. `--leak-suspects` ranks the objects that
keep the most memory alive and explains each one.

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 3
```

`--exclude-soft-weak` ignores weak, soft and phantom references. The collector can clear
those, so they are rarely the reason an object stays alive. Use it on Android, where
LeakCanary and the framework add many of them.
The report starts like this:

<!-- output: first-suspects.txt -->
```text
Heap: 141.81MiB total, 106.60MiB retained-reachable.
Threshold: 5.0 % retained share. Showing 3 suspect(s) (3 above threshold).

Suspect 1 — 27.98MiB (26.2 % of heap)
  dominator: java.util.ArrayList (object_id=361762400)
  accumulating: 262517 instances of com.nexio.tv.domain.model.MetaPreview, total 26.04MiB
  path to GC root:

  Path from object_id=361762400 (depth 12 step(s)):
    start  ── id=361762400
    hop 1 ── id=320784056  (via kotlinx.coroutines.flow.StateFlowImpl._state$volatile)
    hop 2 ── id=320788184  (via kotlinx.coroutines.flow.ReadonlyStateFlow.$$delegate_0)
    hop 3 ── id=361760584  (via com.nexio.tv.ui.screens.home.HomeViewModel.fullCatalogRows)
    hop 4 ── id=327606272  (via java.util.LinkedHashMap$LinkedHashMapEntry.value)
    hop 5 ── id=327606104  (via java.util.LinkedHashMap.tail)
    hop 6 ── id=327606088  (via androidx.lifecycle.ViewModelStore.map)
    hop 7 ── id=327606056  (via java.util.LinkedHashMap$LinkedHashMapEntry.value)
    hop 8 ── id=327605888  (via java.util.LinkedHashMap.tail)
    hop 9 ── id=327605632  (via androidx.navigation.NavControllerViewModel.viewModelStores)
    hop10 ── id=327600144  (via androidx.navigation.NavBackStackEntry.viewModelStoreProvider)
    hop11 ── id=327599744  (via androidx.compose.animation.core.SeekableTransitionState.composedTargetState)
    hop12 ── id=327599704  (via java.lang.Object[][5])
    → stopped at --max-depth (chain may continue)

Suspect 2 — 27.98MiB (26.2 % of heap)
  dominator: java.lang.Object[] (object_id=320977512)
  accumulating: 262517 instances of com.nexio.tv.domain.model.MetaPreview, total 26.04MiB
  path to GC root:

  Path from object_id=320977512 (depth 12 step(s)):
    start  ── id=320977512
    hop 1 ── id=361762400  (via java.util.ArrayList.elementData)
    hop 2 ── id=320784056  (via kotlinx.coroutines.flow.StateFlowImpl._state$volatile)
    hop 3 ── id=320788184  (via kotlinx.coroutines.flow.ReadonlyStateFlow.$$delegate_0)
    hop 4 ── id=361760584  (via com.nexio.tv.ui.screens.home.HomeViewModel.fullCatalogRows)
    hop 5 ── id=327606272  (via java.util.LinkedHashMap$LinkedHashMapEntry.value)
    hop 6 ── id=327606104  (via java.util.LinkedHashMap.tail)
    hop 7 ── id=327606088  (via androidx.lifecycle.ViewModelStore.map)
    hop 8 ── id=327606056  (via java.util.LinkedHashMap$LinkedHashMapEntry.value)
    hop 9 ── id=327605888  (via java.util.LinkedHashMap.tail)
    hop10 ── id=327605632  (via androidx.navigation.NavControllerViewModel.viewModelStores)
    hop11 ── id=327600144  (via androidx.navigation.NavBackStackEntry.viewModelStoreProvider)
    hop12 ── id=327599744  (via androidx.compose.animation.core.SeekableTransitionState.composedTargetState)
    → stopped at --max-depth (chain may continue)

Suspect 3 — 27.98MiB (26.2 % of heap)
  dominator: java.util.ArrayList (object_id=361760560)
  accumulating: 262497 instances of com.nexio.tv.domain.model.MetaPreview, total 26.04MiB
  path to GC root:

  Path from object_id=361760560 (depth 0 step(s)):
    start  ── id=361760560
    → reached GC root: RootJavaFrame
          root metadata: thread_serial=55 frame_index=4294967295
          (thread name/frame metadata not in dump)
```

Read suspect 1 from the top.

- **dominator.** One `ArrayList` is responsible for 27.98 MiB, 26.2 % of the reachable heap.
  If that list were freed, so would everything it keeps alive.
- **accumulating.** Inside that 28 MiB, the most common class is the one from step 1:
  262,517 `MetaPreview` objects.
- **path to GC root.** Each `hop` names the object that holds the one before it, and the
  field it holds it through. Read the chain from the start: the list is the value of a
  `StateFlow`; that flow is `HomeViewModel.fullCatalogRows`; the view model sits in a
  `ViewModelStore` owned by `NavControllerViewModel`, which belongs to the navigation back stack.

That is already a lead: a home-screen view model holds a catalog list, and the back stack keeps
the view model alive.

The report prints two more suspects. They are not separate problems. Suspect 2 is the
`Object[]` inside suspect 1's list: its first hop is `via java.util.ArrayList.elementData`.
Suspect 3 is a second list with almost the same contents (262,497 instances) that is a GC
root itself, held by a Java frame, meaning a local variable on a thread. Dominators nest
like this because the objects inside a retained subtree are retained too. See
[Leak suspects](../analyze/leak-suspects.md#nested-suspects).

## 3. See who else holds the class

Suspects find the biggest owner. Find referrers answers a narrower question: which fields
hold *any* instance of this class? Use it to check that you found the whole story.

```bash
heaptrail -i heap.hprof --find-referrers com.nexio.tv.domain.model.MetaPreview --hops 3 --top 10
```

`--hops 3` follows holders three links deep. Hop 1 is the direct holder, and each later hop
looks through the array in between.

<!-- output: first-referrers.txt -->
```text
Found 573552 target instance(s) for com.nexio.tv.domain.model.MetaPreview

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                                                             ref count
  java.lang.Object[][]                                                                                603715
  com.nexio.tv.ui.screens.home.ModernCarouselItem.metaPreview                                            249
  com.nexio.tv.ui.screens.home.CachedCarouselItem.source                                                 120
  com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernRowSection$1$6$2$1$6$2$1.$metaPreview                8
  com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernRowSection$1$6$2$1$6$1$1.$nextCatalogItem            8
  com.nexio.tv.ui.screens.home.HomeHydrationCoordinator$hydrate$1.L$0                                      3
  com.nexio.tv.ui.screens.home.HomeViewModelPresentationPipelineKt$enrichHeroItemsPipeline$1.L$12          2
  java.util.LinkedHashMap$LinkedHashMapEntry.value                                                         1

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

Hop 1 is almost useless on its own: 603,715 references come from `java.lang.Object[][]`, which is
the way this table prints "a slot in an `Object[]` array". Every `ArrayList` hides its items in
one. The next hops look through the array to the real owner:

- Hop 2: 28,681 `ArrayList.elementData` arrays hold the objects. That is a lot of lists.
- Hop 3: `CatalogRow.items` holds 28,673 of those lists. So at least 28,673 `CatalogRow`
  objects each carry their own list of `MetaPreview` items.

The counts are reference slots, not unique objects. A count of 249 means 249 fields pointed at a
`MetaPreview`. The story so far: the home screen builds catalog rows, each row holds a list of
previews, and a view model that outlives the screen keeps all of it.

## 4. Identify the biggest array

Back to the 5.64 MiB `char[]` from step 1. A class name tells you nothing about what is in an
array, so ask HeapTrail to show the first bytes.

```bash
heaptrail -i heap.hprof -t 3 --preview-bytes 200
```

<!-- output: first-preview.txt from="Largest array instances" -->
```text
Largest array instances object ids (for retainer tracing):
     5.64MiB object_id=1661812752 char[]
             content: JSON
             {"schemaVersion":4,"languageEpoch":0,"languageTag":"en","posterProviderToken":"RPDB:-958971387","cat...
   418.64KiB object_id=2595270656 int[]
             content: unknown binary, 428688 bytes total
             00000000  00 00 00 cb 00 00 00 00  00 00 00 00 00 00 00 00 |................|
             00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
   128.02KiB object_id=342360064 com.squareup.moshi.LinkedHashTreeMap$Node[][]
```

The big `char[]` is a JSON document: 5.64 MiB of text. Now find out who holds it, using the object id
as the starting point.

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --preview-bytes 200
```

<!-- output: first-paths.txt -->
```text
Path from object_id=1661812752 (depth 9 step(s)):
  start  ── id=1661812752
         content: JSON
         {"schemaVersion":4,"languageEpoch":0,"languageTag":"en","posterProviderToken":"RPDB:-958971387","cat...
  hop 1 ── id=1661812736  (via java.lang.String.value)
  hop 2 ── id=364312776  (via java.util.HashMap$Node.value)
  hop 3 ── id=364312696  (via java.util.HashMap$Node[][10])
  hop 4 ── id=364312512  (via java.util.HashMap.table)
  hop 5 ── id=364312344  (via android.app.SharedPreferencesImpl.mMap)
  hop 6 ── id=529946832  (via java.lang.Object[][13])
  hop 7 ── id=529946800  (via android.util.ArrayMap.mArray)
  hop 8 ── id=529946720  (via java.lang.Object[][1])
  hop 9 ── id=369633368  (via android.util.ArrayMap.mArray)
  → orphan: no holder found in dump
```

The chain says: the characters are a `String`, stored as a value in a `HashMap`, which is the
`mMap` of a `SharedPreferencesImpl`. The app keeps a 5.64 MiB JSON blob in `SharedPreferences`,
which Android loads into memory in full.

The last line, `orphan`, does not mean the object is unreachable. It means the path walker found no
more *instance fields or array slots* that point at `id=369633368`. The walker does not look at class
static fields. Ask find-referrers about that last id, which does:

```bash
heaptrail -i heap.hprof --find-referrers id:369633368 --hops 1
```

<!-- output: first-last-hop.txt -->
```text
Found 1 target instance(s) for id:369633368

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)       ref count
  android.app.ContextImpl.sSharedPrefsCache          1
```

A static field, `ContextImpl.sSharedPrefsCache`, holds the cache of every `SharedPreferences`
file. The blob lives for as long as the process does.

## 5. Keep the evidence

Add `--json` to any report to also write it as a file you can query or attach to a ticket.
`--json-out` chooses the path, so scripts always know where to look.

```bash
mkdir -p reports
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 3 --json --json-out reports/suspects.json
```

Then ask the file a question with `jq`:

```bash
jq '.suspects[0] | {dominator_class, retained_bytes, heap_share_pct, accumulating_class, accumulating_count}' reports/suspects.json
```

<!-- output: first-jq.txt -->
```json
{
  "dominator_class": "java.util.ArrayList",
  "retained_bytes": 29336318,
  "heap_share_pct": 26.24489,
  "accumulating_class": "com.nexio.tv.domain.model.MetaPreview",
  "accumulating_count": 262517
}
```

## What you learned

- `heaptrail -i heap.hprof` shows what takes space and prints object ids for the largest arrays.
- `--leak-suspects --exclude-soft-weak` finds the objects that keep the most alive and traces each to a GC root.
- `--find-referrers` shows every field that holds a class, and `--hops` looks through the arrays in between.
- `--preview-bytes` shows what is inside a big array, and `--paths-from-id` traces one object to its owner.
- A path that ends in `orphan` may end in a class static field. `--find-referrers id:<id>` finds it.
- `--json --json-out <path>` writes a report that scripts can read.

## Next steps

- [Choose the right mode](choose-a-mode.md) when your next question is not this one.
- [Leak suspects](../analyze/leak-suspects.md) explains every line of that report and what to do when it names nothing useful.
- [Compare snapshots](../compare/index.md) to find out whether the numbers grow over time.
- [Gate a build on a leak threshold](../automate/ci-gates.md) with the JSON from step 5.
