# Find duplicate payloads

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `-l --preview-bytes`, `--paths-from-id`, `--find-referrers`</span>
<span><strong>Works on</strong> any dump</span>
<span><strong>Time</strong> a minute</span>
<span><strong>Undo</strong> nothing to undo: every step only reads the dump</span>
</div>

## The problem

Several large arrays near the top of the dump look like the same document: the same size, the same first characters. If they are separate
copies, you are paying for the same data many times. But copies that are *garbage* and copies that are *held* call for different fixes, so you need to know which you have.

## The solution

1. List every large array with a preview, and look for runs of the same size:

    ```bash
    heaptrail -i heap-b.hprof -l --preview-bytes 40 --list-arrays-min-bytes 500000 | sed -n '/Standalone large arrays/,$p' | cut -c1-110 | head -6
    ```

    <!-- output: dup-list.txt -->
    ```text
    Standalone large arrays (>= 500000 bytes, sorted by size):
       544.01KiB  object_id=1723142144      char[]     content: JSON  {"0019187198e2cd05a6...
       544.01KiB  object_id=1722261504      char[]     content: JSON  {"0019187198e2cd05a6...
       544.01KiB  object_id=1720037376      char[]     content: JSON  {"0019187198e2cd05a6...
       544.01KiB  object_id=1718874112      char[]     content: JSON  {"0019187198e2cd05a6...
       544.01KiB  object_id=1714692096      char[]     content: JSON  {"0019187198e2cd05a6...
    ```

    Count the copies:

    ```bash
    heaptrail -i heap-b.hprof -l --preview-bytes 40 --list-arrays-min-bytes 500000 | sed -n '/Standalone large arrays/,$p' | grep -c '544.01KiB'
    ```

    <!-- output: dup-count.txt -->
    ```text
    28
    ```

    There are 28 arrays of 544.01 KiB, all JSON, all starting with the same characters. That is about 15 MiB.

2. Trace two of them. If the chains have the same shape, the copies come from one place:

    ```bash
    heaptrail -i heap-b.hprof --paths-from-id 1722261504 --preview-bytes 60
    ```

    <!-- output: dup-paths.txt from="Path from" through="orphan" -->
    ```text
    Path from object_id=1722261504 (depth 3 step(s)):
      start  ── id=1722261504
             content: JSON
             {"0019187198e2cd05a629f3ee787d...
      hop 1 ── id=337883608  (via java.lang.StringBuffer.value)
      hop 2 ── id=337883584  (via java.io.StringWriter.buf)
      hop 3 ── id=337883680  (via com.google.gson.stream.JsonWriter.out)
      → orphan: no holder found in dump
    ```

    Each array is the buffer of a `StringBuffer`, inside a `StringWriter`, inside a Gson `JsonWriter`, and the chain stops at `orphan`.

3. Ask who holds the *writer*, since the path stopped there. There are 28 `JsonWriter` objects, one per array:

    ```bash
    heaptrail -i heap-b.hprof --find-referrers com.google.gson.stream.JsonWriter --hops 1
    ```

    <!-- output: dup-writer-holders.txt from="Found 28" -->
    ```text
    Found 28 target instance(s) for com.google.gson.stream.JsonWriter

    === Direct referrers (1-hop) ===
      (none)
    ```

    No field and no array points at any of them. And a path from one of the writers is empty:

    ```bash
    heaptrail -i heap-b.hprof --paths-from-id 337740240
    ```

    <!-- output: dup-writer-path.txt from="Path from" -->
    ```text
    Path from object_id=337740240 (depth 0 step(s)):
      start  ── id=337740240
      → orphan: no holder found in dump
    ```

4. Read the result. Nothing holds these writers, and none of them is a GC root. They are **unreachable**: garbage that the runtime has not collected yet. This is
   not a leak of live objects. It is a sign of allocation churn: the app appears to have serialized a 544 KiB document 28 times, and the buffers had not been collected when the dump was taken.

## How it works

Same size and the same first characters make copies likely, but they do not prove it. The decisive question is who holds them. A copy that is held lives for as long as its holder does. A copy
that nothing holds is waiting to be collected. The first is a retention bug, and the second is an allocation-rate problem.

## Variations

- **The copies are held.** A path that reaches a root, or a holder that is a map or a list, is a cache or a collection that stores the same value many times. Deduplicate at the
  point where the value enters it.
- **To fix the churn.** Serialize once and share the result. Or stream the output to its destination (`Gson.toJson(value, writer)` into a buffered writer or the
  response) so no 544 KiB string is built at all. To find the call site, take a dump with [allocation tracking](../../capture/allocation-tracking.md).
- **Smaller threshold.** Lower `--list-arrays-min-bytes` to catch smaller payloads. Expect a longer list.

## Related

- [List strings and arrays](../list-strings.md) explains the standalone array list.
- [Paths to a GC root](../../holders/paths-to-root.md) for how a path ends.
- [Find referrers](../../holders/find-referrers.md) for the holder question.
