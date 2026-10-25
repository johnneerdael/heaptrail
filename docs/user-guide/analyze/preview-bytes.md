# Content previews

A class name tells you what an object *is*. For a `char[]` or `byte[]` that is not enough: a 5 MiB `char[]` could be a JSON
document, an XML preferences file, a log buffer or a pile of zeros, and each of those has a different fix. `--preview-bytes N` shows the first
N bytes of every large primitive array in the report, decoded as text or as a hex dump, with a label for what it looks like.

```bash
heaptrail -i heap.hprof -t 3 --preview-bytes 200
```

Use `200` as a default. It is long enough to recognize most content, and short enough to keep the report readable.

## Where previews appear

`--preview-bytes` is a modifier. It adds a preview wherever the report names a primitive array:

| Mode | Where the preview appears |
|---|---|
| Summary | Under each entry in *Largest array instances object ids*. |
| `-l` | In the *Standalone large arrays* list. See [List strings and arrays](list-strings.md). |
| `--paths-from-id` | Under the start object, and under any hop that is a primitive array. |
| `--find-referrers id:<id>` | Under the `Found 1 target instance` line, when the target is a primitive array. |
| `--leak-suspects` | As the `preview:` line, when the dominator is a primitive array. |

Modes that do not name arrays, such as diffs, ignore the flag.

## Read a preview

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

Each preview starts with a `content:` label.

- **Text.** The first array is a `char[]`. heaptrail decoded it, labeled it `JSON`, and printed the start of it on one line. Newlines and tabs
  appear as `\n` and `\t`, and other control characters as `\xNN`, so one array never breaks the report across many lines. A trailing `...` means more follows.
- **Binary.** The `int[]` has no text in it. heaptrail labels it `unknown binary` and prints a hex dump: an offset, 16 bytes in hex,
  and the same bytes as ASCII between `|` bars. The header says how big the array is in total, here 428,688 bytes.

The same preview in a trace shows what the object at the end of a path is, without a second command:

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

## What the labels mean

| Label | How heaptrail decides |
|---|---|
| `JSON` | The text starts with `{` or `[` and contains JSON punctuation such as `"` or `}`. |
| `XML` | The text starts with `<?xml`, or with `<` followed by a letter, `_` or `:`. |
| `UTF-8 text`, `UTF-16 text` | Valid text, at least 90 % printable characters, and neither JSON nor XML. `byte[]` is read as UTF-8, `char[]` as UTF-16. |
| `PNG image`, `JPEG image`, `GIF image`, `WebP image` | The bytes start with that format's signature. |
| `gzip compressed`, `ZIP archive` | The bytes start with the gzip or ZIP signature. |
| `binary/repeated-fill` | At least 16 bytes, all the same byte or the same two-byte pair. A buffer full of zeros, for example. |
| `protobuf-like binary` | At least 8 bytes, and at least a quarter of them are plausible protobuf tag bytes. |
| `unknown binary` | Anything else. |

The labels are heuristics. They name the *shape* of the content and never guess an application format: heaptrail will say `JSON`, not "your catalog cache".

A `byte[]` that starts with an image or archive signature is shown as hex, even if some of its bytes would also decode as text.

## How arrays are decoded

| Array type | Decoded as |
|---|---|
| `char[]` | UTF-16, the encoding of Java strings. Shown as text when it reads as text, as hex otherwise. |
| `byte[]` | UTF-8 when it is valid text, as hex otherwise or when a signature matches. |
| `int[]`, `long[]`, `short[]`, `float[]`, `double[]`, `bool[]` | Always hex. |
| Object arrays | Not previewed. |

A `char[]` uses two bytes per character, so `--preview-bytes 200` shows up to 100 characters of one. The text on screen is cut to 140
characters in the summary, paths and referrer output, to 120 in leak suspects, and to 80 in the `-l` list.

## What it costs

`--preview-bytes N` makes one extra pass over the file and keeps at most N bytes of every primitive array. On the 224 MiB Android dump, with N = 200, the summary
took the same 0.2 seconds and peaked at about 600 MiB instead of 530. The cost grows with the number of arrays in the dump, not with N.

## Gotchas

- **Previews are real data.** They can show tokens, personal data and URLs. See [Handle dumps safely](../capture/handle-dumps-safely.md). Leave the flag off, which is the default, for output you will share.
- **A preview is the start only.** The array may change character after the first 200 bytes. For a larger sample, raise N, but read the label first.
- **Strings are not arrays here.** A `java.lang.String` is an object that points at a `char[]` or `byte[]`. The preview is of that array. Trace
  the array's holder to see which string owns it: `String.value`.
- **Only large arrays are listed.** The summary names only the biggest arrays. To see every array above a size, use [`-l`](list-strings.md).

## Related

- [Identify a giant array](recipes/identify-a-giant-array.md) uses a preview to find out what an array is.
- [Find duplicate payloads](recipes/find-duplicate-payloads.md) uses previews to spot repeated content.
- [List strings and arrays](list-strings.md) previews every standalone array above a size.
