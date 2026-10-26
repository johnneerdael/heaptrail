# Object ids

Every object in a heap dump has an **object id**: a number the dumper assigns to it. HeapTrail
prints ids in its reports and takes them as input, so you can pick an object out of one report and
follow it in another.

```text
5.64MiB object_id=1661812752 char[]
```

## What an id is, and is not

- It is a decimal number. HPROF stores it in 4 bytes on Android and in 8 bytes on most JVMs. HeapTrail
  reads both and always prints a plain number.
- It identifies one object *in one dump*. Do not expect the same object to have the same id in another
  dump. That is why [diffs](../compare/diff.md) compare classes, not objects.
- It is not a count, a size or an address you can look up elsewhere. Treat it as a handle.

## Where to get an id

HeapTrail never asks you to guess one. Reports hand them out:

| Report | Ids it shows |
|---|---|
| [Summary](../analyze/summary.md) | The largest array of each kind, under *Largest array instances object ids*. |
| [Retained size](../analyze/retained-size.md) (`--retained-size`) | The biggest objects by retained bytes, under *Largest retained instances object ids*. |
| [Leak suspects](../analyze/leak-suspects.md) | The dominator of every suspect, and every hop on its path. |
| [List strings and arrays](../analyze/list-strings.md) (`-l --preview-bytes`) | Every standalone large array. |
| [Paths](../holders/paths-to-root.md) | The holder at every hop. |
| [JSON output](../automate/json-output.md) | `largest_object_id`, `dominator_id`, `holder_object_id` and so on. |

## What you can do with an id

| Command | What it answers |
|---|---|
| `--paths-from-id <id>` | What holds this object, all the way to a GC root? |
| `--find-referrers id:<id>` | Which fields and arrays hold this object, including class statics? |
| `--paths-from-id <id> --merge-paths` | Do all objects of this one's class share a holder? The id only picks the class. |
| `--preview-bytes N` with either of the first two | What is inside it, if it is a primitive array? |

For `--find-referrers`, write the id as `id:1661812752` or as bare digits, `1661812752`. Digits alone are
always read as an id, never as a class name.

## What you cannot do

There is no flag that lists the instances of a class. If you know a class and need one of its ids, take it from a
report that already names it: the retained-size hot list, a leak suspect, or a `-l` listing. To learn who holds
*all* instances of a class, you do not need an id at all: use
[`--find-referrers <class>`](../holders/find-referrers.md).

## Related

- [GC roots and paths](gc-roots-and-paths.md) explains what a path from an id shows.
- [Find referrers](../holders/find-referrers.md) accepts a class name or an id.
- [Identify a giant array](../analyze/recipes/identify-a-giant-array.md) walks through id to diagnosis.
