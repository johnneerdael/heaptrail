# Paths to a GC root

`--paths-from-id` takes one object and follows its holders upward, one hop at a time, until it reaches a GC root or gives up. The result is the chain that proves why the object is still in
memory, and each link is a field or an array slot you could cut.

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --max-depth 12
```

You need an object id. [Object ids](../concepts/object-ids.md) lists the reports that print them. Read [GC roots and paths](../concepts/gc-roots-and-paths.md) first if the terms are new.

## Read a path

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --preview-bytes 200
```

<!-- output: first-paths.txt from="Path from" -->
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

- `start` is the object you asked about. With `--preview-bytes`, a primitive array shows its content here.
- Each `hop N` is a *holder*. Its `id` is the holder object, and `via` names where the holder keeps the object on the line above: `String.value` is a field,
  and `java.util.HashMap$Node[][10]` is slot 10 of an array. The slot number lets you find the entry in a paged or sparse collection.
- The last line says how the path ended.

Read it bottom-up as a story: the character array is the `value` of a `String`, which is the value of a `HashMap` entry, in the `mMap` of a `SharedPreferencesImpl`, inside two `ArrayMap`s.

## How it ends

| Last line | Meaning |
|---|---|
| `→ reached GC root: <kind>` | The chain reached a root. The object is alive because of it. |
| `→ stopped at --max-depth (chain may continue)` | The depth limit ran out. Raise `--max-depth` if the hops are still informative. |
| `→ orphan: no holder found in dump` | No field or array slot points at the last object. See [Orphans](#orphans). |
| `→ orphan [soft/weak/phantom — excluded]` | Every holder found was a weak, soft or phantom reference, and `--exclude-soft-weak` is on. |

A path that reaches a root:

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --paths-from-id 3606861808
```

<!-- output: fix-paths-root.txt from="Path from" -->
```text
Path from object_id=3606861808 (depth 1 step(s)):
  start  ── id=3606861808
  hop 1 ── id=3606600864  (via java.lang.Thread.contextClassLoader)
  → reached GC root: RootThreadObject
        root metadata: thread_serial=9 stack_trace_serial=10 thread_object_id=3606600864
        (thread name/frame metadata not in dump)
```

The root kind (`RootThreadObject` here) says what kind of root it is. See [GC root kinds](../reference/gc-root-kinds.md). When a dump records thread names and stack frames, a path that ends at a
thread-owned root also names the thread and, for a Java frame, the method on top of its stack:

```text
  → reached GC root: RootJavaFrame
        thread "pool-7-thread-2"
        at android.app.SharedPreferencesImpl$EditorImpl.commitToMemory(SharedPreferencesImpl.java:478)
```

(That layout is from a dump that has thread records. Neither sample dump has them.) When it does not, HeapTrail prints the raw serial numbers it has, as above, with
`(thread name/frame metadata not in dump)`, so you can tell a gap in the dump from a gap in HeapTrail.

A path stopped by the depth limit:

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --max-depth 3
```

<!-- output: paths-short.txt from="Path from" -->
```text
Path from object_id=1661812752 (depth 3 step(s)):
  start  ── id=1661812752
  hop 1 ── id=1661812736  (via java.lang.String.value)
  hop 2 ── id=364312776  (via java.util.HashMap$Node.value)
  hop 3 ── id=364312696  (via java.util.HashMap$Node[][10])
  → stopped at --max-depth (chain may continue)
```

## Orphans { #orphans }

`orphan` means *the walker found no more instance fields or array slots that point at the last object*. It does not mean the object is unreachable. The walker does not look at **class static fields**, and a static is
the most common holder of a cache.

The first-triage path ends in an orphan. Ask find-referrers about the last id, because it does include statics:

```bash
heaptrail -i heap.hprof --find-referrers id:369633368 --hops 1
```

<!-- output: first-last-hop.txt from="Found 1" -->
```text
Found 1 target instance(s) for id:369633368

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)       ref count
  android.app.ContextImpl.sSharedPrefsCache          1
```

`android.app.ContextImpl.sSharedPrefsCache` is a static field. That is the root of the whole chain. An orphan can also mean the object really is unreachable: garbage that the runtime has not collected yet. Then no referrer
exists either. [Find the duplicates](../analyze/recipes/find-duplicate-payloads.md) shows that case.

## Cycles { #cycles }

At every hop the walker takes the first holder it finds. If two objects hold each other, it goes round the loop until it reaches `--max-depth`. Repeated ids are the sign. In this path
(from the small JVM fixture), `3606700208` and `3606700936` alternate:

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --paths-from-id 3606712464 --preview-bytes 80
```

<!-- output: fix-paths-cycle.txt from="Path from" -->
```text
Path from object_id=3606712464 (depth 12 step(s)):
  start  ── id=3606712464
         content: binary/repeated-fill, 16384 bytes total
         00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
         00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
  hop 1 ── id=3606712424  (via java.io.BufferedWriter.cb)
  hop 2 ── id=3606700208  (via java.io.PrintStream.textOut)
  hop 3 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 4 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 5 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 6 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 7 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 8 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 9 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop10 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop11 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop12 ── id=3606700208  (via java.io.PrintStream.charOut)
  → stopped at --max-depth (chain may continue)
```

Stop reading the path, and ask find-referrers about one of the repeated ids. It lists every holder, not the first one:

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --find-referrers id:3606700208 --hops 1
```

<!-- output: fix-cycle-referrers.txt from="Found 1" -->
```text
Found 1 target instance(s) for id:3606700208

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  java.io.OutputStreamWriter.lock               1
  sun.nio.cs.StreamEncoder.out                  1
  java.lang.System.out                          1
```

`java.lang.System.out` is the holder the walk never reached. [Find the static that holds a cache](recipes/find-the-static-that-holds-a-cache.md) does the same on a leaking cache.

## Add retained sizes

`--retained-size` appends `(retained=<size>)` to every hop. It shows how much memory each link keeps alive, so you can tell which link is worth cutting.

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --max-depth 12 --retained-size --preview-bytes 200
```

<!-- output: paths-ret.txt from="Path from" through="hop 9" -->
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

The retained size stays at 5.64 MiB up to the `SharedPreferencesImpl`, then rises to 6.79 MiB one hop later, at the array behind an `ArrayMap`, which also holds other entries. Cutting a hop above that point would free more than the blob.

## Options

| Flag | Default | Effect |
|---|---|---|
| `--paths-from-id <ID>` | | The object to trace. |
| `--max-depth <N>` | 12 | The most hops to follow. |
| `--retained-size` | off | Add the retained size of every hop. |
| `--exclude-soft-weak` | off | Skip weak, soft and phantom holders. See [Exclude weak references](exclude-soft-weak.md). |
| `--merge-paths` | off | Fold the paths of every instance of the object's class. See [Merge paths](merge-paths.md). |
| `--preview-bytes <N>` | 0 | Show content for primitive arrays on the path. |
| `--mapping`, `--auto-mapping` | off | Restore real names. |
| `--json`, `--json-out` | off | Write the path as JSON. |

`--top` does not apply to paths.

## Cost

Each hop reads the whole file once, so the time grows with the depth: 0.9 seconds for three hops and 2.8 seconds for nine, on a 224 MiB dump. Memory stays small, about 160 MiB. With
`--retained-size` it also builds the whole graph. See [Performance](../reference/performance.md).

## JSON

`--json` writes the path as `steps`, one object per hop, plus how it ended: `terminated_at_root`, `root_kind`, `root_thread_name`, `root_frame`, `max_depth_reached` and `depth`.

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --json --json-out reports/path.json
jq -r '.steps[] | "\(.holder_class) \(.via_field // ("[" + (.array_index|tostring) + "]"))"' reports/path.json
```

<!-- output: paths-jq.txt -->
```text
java.lang.String value
java.util.HashMap$Node value
java.util.HashMap$Node[] [10]
java.util.HashMap table
android.app.SharedPreferencesImpl mMap
java.lang.Object[] [13]
android.util.ArrayMap mArray
java.lang.Object[] [1]
android.util.ArrayMap mArray
```

In the JSON, array classes keep their single-bracket names (`java.lang.Object[]`), and a hop through an array has `via_field: null` and an `array_index`.

## Gotchas

- **It is a path, not the path.** The walker reports the first holder it meets. Other holders may exist. [Merge paths](merge-paths.md) and [find referrers](find-referrers.md) show them.
- **Statics are invisible to the walker.** Orphan does not mean unreachable.
- **A path through weak references is not a leak path.** Add `--exclude-soft-weak`.
- **An id that is not in the dump gives an empty path,** not an error.

## Related

- [Concepts: GC roots and paths](../concepts/gc-roots-and-paths.md) explains what a path proves.
- [Find referrers](find-referrers.md) lists all holders, including statics.
- [Merge paths](merge-paths.md) folds many instances into one tree.
