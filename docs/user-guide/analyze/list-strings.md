# List strings and arrays

`-l` (`--listStrings`) adds two lists to the summary:

- **List of Strings**, the dump's string table: every class, field, method and file name the dump refers to.
- **Standalone large arrays**, when you also pass `--preview-bytes`: a content preview of every primitive array above a size.

```bash
heaptrail -i heap.hprof -l > strings.txt
```

!!! warning "Redirect it to a file"
    `-l` prints one line per name, more than 100,000 lines on an Android dump. Redirect it. If you pipe the output into `head`, HeapTrail ends with a
    `Broken pipe` panic and exit status 101 once the pipe closes.

## The string table

HPROF stores every identifier once, in a string table: the names of classes, fields and methods, and source file names. HeapTrail's `UTF-8 Strings` count in the summary is the size of that table.
`-l` prints it. These are *names*, not the contents of `java.lang.String` objects that live in the heap. To read what a `String` holds, look at the array behind it with
[`--preview-bytes`](preview-bytes.md).

```bash
heaptrail -i heap-b.hprof -l | sed -n '/List of Strings/,+12p'
```

<!-- output: list-head.txt from="List of Strings" head="8" -->
```text
List of Strings
$$INSTANCE
$$changed
$$changed1
$$default
$$delegate_0
$$delegatedProperties
$$this$LaunchedEffect
```

Use it to answer small questions about the dump:

- Does a class or field exist at all? `grep -c 'AnimeIdMapAsset' strings.txt`
- Which source files does the code come from? `grep '\.kt$' strings.txt`
- What does an obfuscated build look like? Short names such as `a3.t` are the sign that you need a [mapping](../android/deobfuscate-release-builds.md).

A name in this table does not mean an *object* of that class exists. A dump can name a class it holds no instance of. Use the summary's class table to see instances.

## Standalone large arrays

Add `--preview-bytes N` to `-l` and a second list follows the first: every primitive array of at least `--list-arrays-min-bytes` bytes (1,024 by default), biggest first, each with its
object id, type and a preview.

```bash
heaptrail -i heap-b.hprof -l --preview-bytes 120 --list-arrays-min-bytes 100000 | sed -n '/Standalone large arrays/,$p'
```

<!-- output: list-arrays.txt head="8" -->
```text
Standalone large arrays (>= 100000 bytes, sorted by size):
   544.01KiB  object_id=1723142144      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1722261504      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1720037376      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1718874112      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1714692096      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1712033792      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
   544.01KiB  object_id=1710886912      char[]     content: JSON  {"0019187198e2cd05a629f3ee787deb7c8b44dd45ab66e9559b94a9f397...
```

The threshold applies to the array's total size in bytes, not to the preview. It takes effect only when `-l` and `--preview-bytes` are both set. Each preview is cut to 80 characters in this list.

### Spot repeated content

The list is sorted by size and shows the start of every array, so copies of one payload sit next to each other, and the previews show whether they match. In this
186 MiB dump, raising the threshold to 500,000 bytes and trimming each line to 100 characters shows the same 544 KiB array again and again:

```bash
heaptrail -i heap-b.hprof -l --preview-bytes 40 --list-arrays-min-bytes 500000 | sed -n '/Standalone large arrays/,$p' | cut -c1-100
```

<!-- output: list-count.txt head="6" -->
```text
Standalone large arrays (>= 500000 bytes, sorted by size):
   544.01KiB  object_id=1723142144      char[]     content: JSON  {"0019187198e2cd05a6...
   544.01KiB  object_id=1722261504      char[]     content: JSON  {"0019187198e2cd05a6...
   544.01KiB  object_id=1720037376      char[]     content: JSON  {"0019187198e2cd05a6...
   544.01KiB  object_id=1718874112      char[]     content: JSON  {"0019187198e2cd05a6...
   544.01KiB  object_id=1714692096      char[]     content: JSON  {"0019187198e2cd05a6...
```

[Find duplicate payloads](recipes/find-duplicate-payloads.md) turns that into a diagnosis.

## Options

| Flag | Default | Effect |
|---|---|---|
| `-l`, `--listStrings` | off | Print the string table. |
| `--preview-bytes N` | 0 | With `-l`, also list large arrays with a preview. |
| `--list-arrays-min-bytes N` | 1024 | The smallest array, in bytes, that the second list includes. |

## Gotchas

- **It is only for the summary.** `-l` belongs to the default mode. Other modes ignore it.
- **The list is long.** Search it with `grep`, and keep it out of chat windows and tickets.
- **Arrays, not strings.** Content such as JSON bodies and tokens shows up in the second list, not the first.
- **Contents are sensitive.** The array list prints data from memory. See [Handle dumps safely](../capture/handle-dumps-safely.md).

## Related

- [Content previews](preview-bytes.md) explains the labels and decoding.
- [Summary](summary.md) shows the sections that `-l` extends.
- [Find duplicate payloads](recipes/find-duplicate-payloads.md) is the recipe that uses the array list.
