# Triage an unfamiliar dump

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> the summary, `--leak-suspects`, `--find-referrers`, `--paths-from-id`</span>
<span><strong>Works on</strong> any dump</span>
<span><strong>Time</strong> ten minutes</span>
<span><strong>Undo</strong> nothing to undo: every step only reads the dump</span>
</div>

## The problem

Someone hands you a heap dump from an app you did not write, with a note that says "it ran out of memory". You do not know the classes,
you cannot ask the author, and you want a first answer in minutes.

## The solution

Work through these steps in order. Stop as soon as you know enough to ask a good question.

1. **Check what you have.** Run the summary and read the first line and the tables.

    ```bash
    heaptrail -i heap.hprof -t 10 --preview-bytes 200
    ```

    - Does the first line name a format and a size you expect? An empty or cut-off file fails here.
    - Do class names look like `a3.t`? Then the build is obfuscated. Find the matching mapping file first and add `--mapping` to every command below.
      See [Deobfuscate release builds](../../android/deobfuscate-release-builds.md).
    - Is `AllocationSites:` `present`? If so, [`--allocation-sites`](../allocation-sites.md) can show where objects were allocated.

2. **Ask for suspects.** This is the step that needs no prior knowledge.

    ```bash
    heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 3
    ```

    Here is that step on the small JVM demo from the repository, which has one planted leak:

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

    `HashMap` keeps 94.7 % of the reachable heap alive, and almost all of it is `byte[]`.

3. **Follow the dominator.** Take the dominator's id, and ask who holds it. If the suspect's path ended in `orphan`, ask referrers, which also sees static fields:

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

    `shop.SessionCache.BY_ID` is a static field. That is the owner. [Find the static that holds a cache](../../holders/recipes/find-the-static-that-holds-a-cache.md) goes through this case in full.

4. **Check what is inside.** If the dominator or a top class is a primitive array, the preview already told you what it holds. If it is a collection, ask what class its
   items are: the suspect's `accumulating:` line says so.

5. **Decide whether it is growing.** One dump shows what is alive, not what is growing. Compare it with another dump from the same app, or take a series. See
   [Compare snapshots](../../compare/index.md).

6. **Write it down.** Save the evidence where others can read it:

    ```bash
    heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --json --json-out reports/suspects.json
    ```

## How it works

The summary gives the shape and the ids. Suspects turn a heap of millions of objects into a short list of owners, ranked by what they keep alive. The tracing modes then explain why each owner exists.
Each step uses the output of the one before, so you never need to guess a class name.

## Variations

| If you find | Do this instead |
|---|---|
| Many leaked instances of one class (activities, view models) | [`--merge-paths`](../../holders/merge-paths.md) on one of them, to see the holder they share. |
| A giant array and no suspect | [Identify a giant array](identify-a-giant-array.md). |
| A package of your own code with many classes in the summary | [`--target-glob 'com.example.**' --group-holders`](../../holders/target-glob.md). |
| An OOM from a JVM | Start with `jmap -dump:live` or `-XX:+HeapDumpOnOutOfMemoryError`, then step 2. See [JVM dumps](../../capture/jvm.md). |
| A dump that is too big for the memory you have | Use the summary and `--find-referrers` only. Retained size and suspects need the whole graph in memory. See [Performance](../../reference/performance.md). |

## Related

- [Your first triage](../../getting-started/first-triage.md) walks through the same steps on an Android dump.
- [Leak suspects](../leak-suspects.md) explains every part of the report.
- [Choose the right mode](../../getting-started/choose-a-mode.md) for the other questions.
