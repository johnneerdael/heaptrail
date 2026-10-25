# Find the static that holds a cache

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `--leak-suspects`, `--paths-from-id`, `--find-referrers id:`</span>
<span><strong>Works on</strong> JVM and Android dumps</span>
<span><strong>Time</strong> two minutes</span>
<span><strong>Undo</strong> nothing to undo: every step only reads the dump</span>
</div>

## The problem

A suspect report names a collection that retains most of the heap, and its path to a GC root says `orphan`. Nothing in the path points at a root, but a collection that big
did not appear from nowhere. Something holds it, and the path walker cannot see what.

## The solution

This recipe uses the demo dump from the repository: a JVM program with a session cache that never evicts anything.
Download it from [Capture: JVM dumps](../../capture/jvm.md#try-it-a-demo-with-a-deliberate-leak) and unpack it as `demo.hprof`.

1. Run the suspects report.

    ```bash
    heaptrail -i demo.hprof --leak-suspects --exclude-soft-weak --top 1
    ```

    <!-- output: jvm-suspects.txt from="Heap:" -->
    ```text
    Heap: 16.97MiB total, 16.68MiB retained-reachable.
    Threshold: 5.0 % retained share. Showing 1 suspect(s) (1 above threshold).

    Suspect 1 — 15.79MiB (94.7 % of heap)
      dominator: java.util.HashMap (object_id=34095644696)
      accumulating: 4000 instances of byte[], total 15.65MiB
      path to GC root:

      Path from object_id=34095644696 (depth 0 step(s)):
        start  ── id=34095644696
        → orphan: no holder found in dump
    ```

    One `HashMap` retains 94.7 % of the reachable heap, mostly `byte[]`. Its path is empty: `orphan`.

2. Confirm the path by hand, and note that it also ends at once:

    ```bash
    heaptrail -i demo.hprof --paths-from-id 34095644696
    ```

    <!-- output: jvm-paths.txt from="Path from" -->
    ```text
    Path from object_id=34095644696 (depth 0 step(s)):
      start  ── id=34095644696
      → orphan: no holder found in dump
    ```

3. Ask find-referrers who holds the map. Unlike the path walker, it includes class static fields.

    ```bash
    heaptrail -i demo.hprof --find-referrers id:34095644696 --hops 1
    ```

    <!-- output: jvm-holder.txt from="Found 1" -->
    ```text
    Found 1 target instance(s) for id:34095644696

    === Direct referrers (1-hop) ===
      holder.field (or class[] for arrays)  ref count
      shop.SessionCache.BY_ID                       1
    ```

    `shop.SessionCache.BY_ID` is a static field. The map is a field of the class, so it lives as long as the class does, which is as long as the process.

4. See what is in it. Ask who holds the entries:

    ```bash
    heaptrail -i demo.hprof --find-referrers shop.Session --hops 2
    ```

    <!-- output: jvm-referrers.txt from="Found 2000" -->
    ```text
    Found 2000 target instance(s) for shop.Session

    === Direct referrers (1-hop) ===
      holder.field (or class[] for arrays)  ref count
      java.util.HashMap$Node.value               2000
    ```

    There are 2,000 `Session` objects, each held as a `HashMap$Node.value`: one map entry each.

## How it works

The path walker follows instance fields and array slots. A class static field is not an instance field, so a path that ends at a static ends in `orphan`, as if nothing held the object. The referrer mode scans the
statics as well, which is why it finds the owner in one step. The retained-size graph treats statics as roots, so a suspect report finds the map even though its own path section cannot explain it.

The fix lives in the code, not in heaptrail: the cache needs a limit. Bound it by size or age (an LRU map, or a weak or soft reference to the values), or remove entries when sessions end.

## Variations

- **No static, no root, no referrer.** If find-referrers reports `(none)` and the path says `orphan`, the object is not reachable. It is garbage that the runtime has not collected yet. See [Find duplicate payloads](../../analyze/recipes/find-duplicate-payloads.md).
- **The static is a singleton.** On Android, the holder is often `Companion` or `INSTANCE` of a Kotlin object, or a Dagger or Hilt component. The answer is the same: a long-lived owner. Check what it should be allowed to keep.
- **The path loops instead of ending.** Repeated ids mean a cycle. Ask find-referrers about one of them. See [Paths to a GC root](../paths-to-root.md#cycles).
- **Obfuscated names.** Add `--mapping` so the static reads as a real class and field.

## Related

- [Find referrers](../find-referrers.md) lists statics among the holders.
- [Paths to a GC root](../paths-to-root.md#orphans) explains orphans.
- [Leak suspects](../../analyze/leak-suspects.md) finds the collection in the first place.
