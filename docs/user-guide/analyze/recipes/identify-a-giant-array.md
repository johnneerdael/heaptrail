# Identify a giant array

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `--preview-bytes`, `--find-referrers id:`, `--paths-from-id`</span>
<span><strong>Works on</strong> any dump</span>
<span><strong>Time</strong> a few seconds per command</span>
<span><strong>Undo</strong> nothing to undo: every step only reads the dump</span>
</div>

## The problem

The summary shows one `char[]` of 544 KiB, or a `byte[]` of 154 KiB, near the top of the largest instances. The class name says nothing about
what is in it, and a different content needs a different fix: a cached JSON response, an image, a log buffer, or a block of zeros.

## The solution

1. Take the array's object id from the summary and preview it. This sample dump has a `char[]`, an `int[]` and a `byte[]` near the top:

    ```bash
    heaptrail -i heap-b.hprof -t 3 --preview-bytes 200
    ```

    <!-- output: prev-103.txt from="Largest array instances" -->
    ```text
    Largest array instances object ids (for retainer tracing):
       544.01KiB object_id=1723142144 char[]
                 content: JSON
                 {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397f16fc2":"https://artworks.thetvdb.com/ba...
       418.64KiB object_id=2595270656 int[]
                 content: unknown binary, 428688 bytes total
                 00000000  00 00 00 cb 00 00 00 00  00 00 00 00 00 00 00 00 |................|
                 00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
       154.16KiB object_id=1740406800 byte[]
                 content: JSON
                 {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397f16fc2":"https://artworks.thetvdb.com/banners/episodes/76733/213300.jpg","01a3fe...
    ```

2. Read the `content:` label. The `char[]` and the `byte[]` are JSON, and the `int[]` is `unknown binary`.
3. Find out who holds the array you care about. A `String` wraps most `char[]`s, so ask for the chain:

    ```bash
    heaptrail -i heap-b.hprof --paths-from-id 1723142144 --preview-bytes 100
    ```

    <!-- output: paths-103.txt from="Path from" through="orphan" -->
    ```text
    Path from object_id=1723142144 (depth 3 step(s)):
      start  ── id=1723142144
             content: JSON
             {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e955...
      hop 1 ── id=337740168  (via java.lang.StringBuffer.value)
      hop 2 ── id=337740144  (via java.io.StringWriter.buf)
      hop 3 ── id=337740240  (via com.google.gson.stream.JsonWriter.out)
      → orphan: no holder found in dump
    ```

4. Read the chain from the array up: a `StringBuffer`, inside a `StringWriter`, inside a Gson `JsonWriter`. These are the objects that build JSON text. The array is the
   output buffer of a serializer that was run on a large object. That is already a diagnosis the class name alone could not give.

## How it works

The summary tells you *that* an array is big, the preview tells you *what* is in it, and the path tells you *who owns it*. Together they replace a search through
the source for whoever builds such a string.

Match the label to a likely cause:

| Label | Often means | Look at |
|---|---|---|
| `JSON` | A cached or serialized response, or a serializer's output buffer. | Who builds the string: the path usually ends in a writer or a cache map. |
| `XML` | A preferences file, a layout or a config loaded whole. | `SharedPreferencesImpl.mMap` on Android. |
| `PNG image`, `JPEG image`, … | An encoded image held as bytes. | An image cache or a network layer buffering a body. |
| `binary/repeated-fill` | A buffer that was allocated and never filled. | A pool or buffer sized for a worst case. |
| `unknown binary` | A packed structure, a native handle table, an index. | The holder's class name. |

## Variations

- **The path ends in `orphan`.** The walker does not follow class static fields. Ask [`--find-referrers id:<last id>`](../../holders/find-referrers.md) about the last hop. See
  [Paths to a GC root](../../holders/paths-to-root.md#orphans).
- **There are many arrays of the same size.** Do not trace them one by one. See [Find duplicate payloads](find-duplicate-payloads.md).
- **You want the size of what the holder retains.** Add `--retained-size` to the path command.
- **The id is a `String`'s array and you want the string.** The preview is the string. Nothing else is needed.

## Related

- [Content previews](../preview-bytes.md) lists every label and how arrays are decoded.
- [Object ids](../../concepts/object-ids.md) explains where ids come from.
- [Paths to a GC root](../../holders/paths-to-root.md) shows how to read the chain.
