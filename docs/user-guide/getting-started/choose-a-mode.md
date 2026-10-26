# Choose the right mode

HeapTrail has one default mode, the summary, and several modes you select with a flag. Pick
the row below that matches your question, then follow the link.

## By question

| You want to know | Run | Page |
|---|---|---|
| What is in this dump, and which classes take the space? | `heaptrail -i heap.hprof` | [Summary](../analyze/summary.md) |
| Which objects keep the most memory alive? | `heaptrail -i heap.hprof --retained-size` | [Retained size](../analyze/retained-size.md) |
| What is wrong with this dump? (you do not know where to look) | `heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak` | [Leak suspects](../analyze/leak-suspects.md) |
| What is inside that giant `char[]` or `byte[]`? | `heaptrail -i heap.hprof --preview-bytes 200` | [Content previews](../analyze/preview-bytes.md) |
| Where are all the big text arrays? | `heaptrail -i heap.hprof -l --preview-bytes 200` | [List strings and arrays](../analyze/list-strings.md) |
| Which bitmaps take the most memory? | `heaptrail -i heap.hprof --bitmaps` | [Bitmaps](../analyze/bitmaps.md) |
| Which line of code allocated this? | `heaptrail -i heap.hprof --allocation-sites` | [Allocation sites](../analyze/allocation-sites.md) |
| What holds every instance of a class? | `heaptrail -i heap.hprof --find-referrers <class> --hops 2` | [Find referrers](../holders/find-referrers.md) |
| What holds a whole package of classes? | `heaptrail -i heap.hprof --target-glob 'com.example.**'` | [Target glob](../holders/target-glob.md) |
| What holds this one object, and is it reachable? | `heaptrail -i heap.hprof --paths-from-id <id>` | [Paths to a GC root](../holders/paths-to-root.md) |
| Do all instances of a class hang off the same holder? | `heaptrail -i heap.hprof --paths-from-id <id> --merge-paths` | [Merge paths](../holders/merge-paths.md) |
| What changed between two dumps? | `heaptrail --diff-from a.hprof --diff-to b.hprof` | [Snapshot diff](../compare/diff.md) |
| What grew across three or more dumps? | `heaptrail --diff-series a.hprof b.hprof c.hprof` | [Diff a series](../compare/diff-series.md) |
| How do I get a dump from an Android device? | `heaptrail android-capture --package <app> --out dumps` | [android-capture](../capture/android-capture.md) |

## By situation

**"The app uses too much memory and I do not know why."** Start with the summary to see the
shape, then `--leak-suspects --exclude-soft-weak`. If a suspect names a class, trace it with
`--find-referrers`. This is [the loop from your first triage](first-triage.md).

**"One object looks huge."** Take its id from the summary's list of largest arrays, preview it with
`--preview-bytes 200`, then trace it with `--paths-from-id`. See
[Identify a giant array](../analyze/recipes/identify-a-giant-array.md).

**"I think something leaks over time."** One dump shows what is alive now, not what is growing.
Capture two or more dumps from the same process around the action you suspect, and compare them. With
three or more, use `--diff-series` and read the *monotonic growth* list. See
[Compare snapshots](../compare/index.md).

**"The class names look like `a3.t`."** The build is obfuscated. Add `--mapping` to every command, or let
`--auto-mapping` pick the file. See [Android](../android/index.md).

**"I want the result in a script."** Add `--json --json-out <path>` to any mode. See
[Automate](../automate/index.md).

## One mode at a time

You pick one of these per command:

`--find-referrers` (or `--target-glob`), `--paths-from-id`, `--diff-from` with `--diff-to`,
`--diff-series`, `--allocation-sites`, `--leak-suspects`, `--bitmaps`. With none of them, you get the summary.

Giving two modes at once fails with `conflicting modes`. `android-capture` is a separate subcommand with its own
flags. The other flags are modifiers: they change what a mode prints or how it computes, and a mode ignores the
modifiers it does not use.

| Modifier | Use it with |
|---|---|
| `-t`, `--top N` | Summary, referrers, diff, diff-series, suspects, bitmaps, allocation sites |
| `--retained-size` | Summary, referrers, paths |
| `--exclude-soft-weak` | Retained size, referrers, paths, merge paths, suspects |
| `--preview-bytes N` | Summary, `-l`, paths, referrers by id, suspects |
| `--mapping`, `--auto-mapping` | Every mode |
| `--json`, `--json-out` | Every mode |

[Mode compatibility](../reference/mode-compatibility.md) has the full table, checked against the code.

## Related

- [Command line reference](../reference/command-line.md) lists every flag with its default.
- [How HeapTrail reads a dump](../concepts/how-heaptrail-reads-a-dump.md) explains why some modes are fast and others need more memory.
- [Your first triage](first-triage.md) shows the loop in action.
