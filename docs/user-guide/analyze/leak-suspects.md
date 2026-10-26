# Leak suspects

`--leak-suspects` answers "what is wrong with this dump?" when you do not know which class to look at. It ranks every object by the
memory it keeps alive, takes the biggest ones, and prints, for each, what it holds, which class dominates inside it, and the chain of
holders that keeps it reachable.

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak
```

This is the command to run first on an unfamiliar Android dump. It is the same idea as the *Leak Suspects* report in Eclipse MAT, printed as
text, with a content preview built in.

## Read a report

<!-- output: first-suspects.txt from="Heap:" until="Suspect 2" -->
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
```

**The two header lines**

- `Heap: 141.81MiB total, 106.60MiB retained-reachable.` The first figure is every object in HeapTrail's graph. The second is what the GC
  roots can reach. Percentages are relative to the *second* figure. See [Shallow and retained size](../concepts/shallow-and-retained.md#total-reachable-and-unreachable).
- `Threshold: 5.0 % retained share. Showing 3 suspect(s) (3 above threshold).` A suspect has to retain at least this share of the reachable heap to
  count as above the threshold.

**One suspect**

| Line | Meaning |
|---|---|
| `Suspect 1 — 27.98MiB (26.2 % of heap)` | The retained size of the dominator, and its share of the reachable heap. |
| `dominator: java.util.ArrayList (object_id=…)` | The object that, if freed, would free the whole subtree. Its id goes into [`--paths-from-id`](../holders/paths-to-root.md). |
| `accumulating: 262517 instances of …MetaPreview, total 26.04MiB` | The class with the *most instances* inside the dominated subtree, with their count and combined shallow size. It tells you what the memory is made of. |
| `preview: …` | For a dominator that is a primitive array, the start of its content. Needs `--preview-bytes`. |
| `path to GC root:` | The chain of holders from the dominator up toward a root, up to 12 hops, as [`--paths-from-id`](../holders/paths-to-root.md) prints it. |

## Nested suspects { #nested-suspects }

Suspects are ranked by retained size, and the objects inside a big subtree are retained too. So the top suspects are often one story told
at different levels. In the first-triage dump, the three suspects are 27.98 MiB each:

- Suspect 1 is an `ArrayList`.
- Suspect 2 is the `Object[]` inside that list. Its first hop reads `via java.util.ArrayList.elementData`.
- Suspect 3 is a second `ArrayList` with almost the same contents (262,497 `MetaPreview` against 262,517), held directly by a Java frame.

Read the group as one finding, and follow the path of the outermost one. [Your first triage](../getting-started/first-triage.md) does exactly that.

## Options

| Flag | Default | Effect |
|---|---|---|
| `--leak-suspects[=THRESHOLD]` | `0.05` | The minimum retained share, as a fraction. `--leak-suspects=0.10` keeps only suspects of 10 % or more. Write the value with `=`. |
| `-t`, `--top N` | 20 | The most suspects to print. |
| `--exclude-soft-weak` | off | Ignore weak, soft and phantom references. Use it on Android. See [Reference strength](../concepts/reference-strength.md). |
| `--preview-bytes N` | 0 | Show the start of a suspect's content when it is a primitive array. |
| `--mapping`, `--auto-mapping` | off | Restore real class names. |
| `--json`, `--json-out` | off | Also write the report as JSON. |

`--leak-suspects` computes retained sizes by itself, so you do not add `--retained-size`.

### The threshold, and the top-three fallback

If no object clears the threshold, HeapTrail does not print an empty report. It falls back to the top three objects and labels each
`below threshold`:

```bash
heaptrail -i heap.hprof --leak-suspects=0.9 --top 3
```

<!-- output: sus-below.txt from="Heap:" until="  dominator:" -->
```text
Heap: 141.81MiB total, 106.65MiB retained-reachable.
Threshold: 90.0 % retained share. Showing 3 suspect(s) (0 above threshold).

Suspect 1 — 27.98MiB (26.2 % of heap, below threshold)
```

A threshold of `0.9` asks for objects that retain 90 % or more. None does here, so the three biggest are shown anyway.

## Reading a path that loops

The path section uses the same walker as `--paths-from-id`, so it can go in circles. In this second dump, the suspect's path repeats two ids until it hits the depth limit of 12:

```bash
heaptrail -i heap-b.hprof --leak-suspects --exclude-soft-weak --top 3
```

<!-- output: sus-103.txt from="Suspect 1" until="Suspect 2" -->
```text
Suspect 1 — 14.94MiB (28.4 % of heap)
  dominator: com.nexio.tv.core.anime.AnimeIdMappingService (object_id=333406600)
  accumulating: 318693 instances of byte[], total 2.05MiB
  path to GC root:

  Path from object_id=333406600 (depth 12 step(s)):
    start  ── id=333406600
    hop 1 ── id=317356280  (via dagger.internal.DoubleCheck.instance)
    hop 2 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.animeIdMappingServiceProvider)
    hop 3 ── id=317356072  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl$SwitchingProvider.singletonCImpl)
    hop 4 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.addonRepositoryImplProvider)
    hop 5 ── id=317356072  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl$SwitchingProvider.singletonCImpl)
    hop 6 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.addonRepositoryImplProvider)
    hop 7 ── id=317356072  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl$SwitchingProvider.singletonCImpl)
    hop 8 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.addonRepositoryImplProvider)
    hop 9 ── id=317356072  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl$SwitchingProvider.singletonCImpl)
    hop10 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.addonRepositoryImplProvider)
    hop11 ── id=317356072  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl$SwitchingProvider.singletonCImpl)
    hop12 ── id=330322432  (via com.nexio.tv.DaggerNexioApplication_HiltComponents_SingletonC$SingletonCImpl.addonRepositoryImplProvider)
    → stopped at --max-depth (chain may continue)
```

`SingletonCImpl$SwitchingProvider.singletonCImpl` and `SingletonCImpl.addonRepositoryImplProvider` hold each other: Dagger's generated component holds its providers, and
each provider points back at the component. The useful finding is in the first hops. A Dagger `DoubleCheck` provider inside the Hilt singleton component holds
`AnimeIdMappingService`, which retains 14.94 MiB. When ids repeat, stop following the path and ask [`--find-referrers id:<id>`](../holders/find-referrers.md) about one of them.

## More than 100 %, and orphans

A dump can contain garbage: objects the runtime has not freed yet. HeapTrail ranks those too. A suspect can then show more than 100 % of the reachable heap,
and its path ends with `orphan`, because nothing reaches it.

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --leak-suspects --top 2 --preview-bytes 100
```

<!-- output: sus-fixture.txt from="Heap:" until="Suspect 2" -->
```text
Heap: 2.37MiB total, 198.21KiB retained-reachable.
Threshold: 5.0 % retained share. Showing 2 suspect(s) (2 above threshold).

Suspect 1 — 634.77KiB (320.2 % of heap)
  dominator: int[] (object_id=3607227400)
  accumulating: 1 instances of int[], total 634.77KiB
  preview: content: binary/repeated-fill, binary, 650000 bytes
  path to GC root:

  Path from object_id=3607227400 (depth 0 step(s)):
    start  ── id=3607227400
    → orphan: no holder found in dump
```

This small JVM dump holds many unreachable objects: 198 KiB of its 2.37 MiB are reachable. So the large arrays that rank first are garbage, and the share of 320.2 % is the tell.
They are not leaks, because nothing keeps them alive. A JVM dump taken with `jmap -dump:live` would not contain them. See [JVM dumps](../capture/jvm.md).

An `orphan` on a *reachable* suspect is a different case: the object may be held by a static field, which the path walker does not follow. Ask
[find referrers](../holders/find-referrers.md) about the id. See [Find the static that holds a cache](../holders/recipes/find-the-static-that-holds-a-cache.md).

## JSON { #json }

`--json` writes the whole report as a file, with a `path_to_root` object for each suspect:

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 3 --json --json-out reports/suspects.json
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

The top level has `total_heap_bytes`, `retained_reachable_bytes`, `threshold_pct` and `suspects`. Each suspect has the fields above, plus `below_threshold`, and,
when previews are on and the dominator is a primitive array, `preview_snippet` and `preview_content_label`. See [JSON schemas](../reference/json-schemas.md) and
[Gate a build on a leak threshold](../automate/ci-gates.md).

## What to do with a suspect

| The report shows | Next |
|---|---|
| A class from your code as the accumulating class | [`--find-referrers <class> --hops 2`](../holders/find-referrers.md) to see every field that holds it. |
| A primitive array as the dominator or a big `byte[]` | [`--preview-bytes 200`](preview-bytes.md), then [identify the array](recipes/identify-a-giant-array.md). |
| A path that ends in `orphan` | Ask find-referrers about the last id: it may end in a static. |
| Many instances of one class on a shared path | [`--merge-paths`](../holders/merge-paths.md) to fold their paths. |
| Weak references all through the path | Add `--exclude-soft-weak`. |

## Gotchas

- **A suspect is retained memory, not a verdict.** A cache that is supposed to hold 30 MiB will appear. Decide whether the retention is intended.
- **The total can differ from the summary's.** The suspects report sizes objects in its own graph, so its `total` is not the summary's raw total.
- **Garbage can rank.** On a JVM, prefer a dump taken with `live`.
- **It costs memory.** The graph must fit in RAM: about 1.7 GiB for a 224 MiB dump, and 4 to 6 seconds. See [Performance](../reference/performance.md).

## Related

- [Retained size](retained-size.md) is the same engine without the narrative.
- [Paths to a GC root](../holders/paths-to-root.md) explains the path section in depth.
- [Triage an unfamiliar dump](recipes/triage-an-unfamiliar-dump.md) puts suspects in a complete workflow.
