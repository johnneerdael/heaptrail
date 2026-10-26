# Mode compatibility

Each mode reads only some flags. A flag that a mode does not use is accepted and ignored, without a warning. This page shows which flags each mode reads, taken from the way HeapTrail builds each mode from the command line.

## Choosing a mode

You select a mode with one of these flags (or none, for the summary). Give at most one.

| Selects | Flag |
|---|---|
| Referrers | `--find-referrers` or `--target-glob` |
| Paths | `--paths-from-id` |
| Diff | `--diff-from` with `--diff-to` |
| Diff series | `--diff-series` |
| Allocation sites | `--allocation-sites` |
| Leak suspects | `--leak-suspects` |
| Bitmaps | `--bitmaps` |
| Summary | none of the above |

If you give two, HeapTrail stops:

<!-- output: conflict.txt from="error:" cmd -->
```console
$ heaptrail -i heap.hprof --find-referrers java.util.ArrayList --paths-from-id 1
error: conflicting modes: pick exactly one of `--find-referrers`, `--paths-from-id`, or `--diff-from`/`--diff-to`
```

The check also fires when a flag needs a mode that is missing. `--group-holders` without a referrer mode, and `--diff-from` without `--diff-to` (or the reverse), both print this same `conflicting modes` message.
`--find-referrers` and `--target-glob` together are rejected earlier, by the argument parser.

## Which flags each mode reads

A tick means the mode uses the flag. A dash means it ignores it.

| Flag | Summary | Referrers | Paths | Diff | Series | Suspects | Alloc sites | Bitmaps |
|---|---|---|---|---|---|---|---|---|
| `-i`, `--inputFile` | ✓ | ✓ | ✓ | – | – | ✓ | ✓ | ✓ |
| `-t`, `--top` | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ |
| `-d`, `--debug` | ✓ | ✓ | ✓ | – | – | ✓ | ✓ | ✓ |
| `--json`, `--json-out` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `--mapping`, `--auto-mapping` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `--preview-bytes` | ✓ | id targets | ✓ | – | – | ✓ | – | – |
| `-l`, `--list-arrays-min-bytes` | ✓ | – | – | – | – | – | – | – |
| `--retained-size` | ✓ | ✓ | ✓ | – | – | always on | – | – |
| `--exclude-soft-weak` | with `--retained-size` | ✓ | ✓ | – | – | ✓ | – | – |
| `--hops`, `--group-holders` | – | ✓ | – | – | – | – | – | – |
| `--max-depth`, `--merge-paths` | – | – | ✓ | – | – | – | – | – |
| `--diff-by` | – | – | – | ✓ | ✓ | – | – | – |
| `--native-context` | – | – | – | – | ✓ | – | – | – |

Notes:

- **`--top` in referrers** limits the rows of each hop section. In suspects it limits the number of suspects. In a series it limits every table of the text report, but not the JSON.
- **`--preview-bytes` in referrers** shows a preview only when the target is a primitive array given by id.
- **`--exclude-soft-weak` in the summary** does something only when `--retained-size` is also set. `--merge-paths` is read as part of the paths mode, so the paths flags apply.
- **`--mapping` in bitmaps** has nothing to restore, because the report names no classes.
- **`--include-statics`** is accepted by the referrer mode and has no effect: statics are always listed.

## What a mode needs

| Mode | Requires |
|---|---|
| Summary, referrers, paths, suspects, allocation sites, bitmaps | `-i <dump>` |
| Diff | Both `--diff-from` and `--diff-to` |
| Diff series | At least three paths |
| `--group-holders` | `--find-referrers` or `--target-glob` |
| `--json-out` | `--json` |
| `--project-root`, `--package` | `--auto-mapping` |

`--mapping` and `--auto-mapping` cannot be used together, and `--find-referrers` and `--target-glob` cannot be used together. `--merge-paths` without `--paths-from-id` is ignored.

## Related

- [Command line](command-line.md) lists every flag and its default.
- [Choose the right mode](../getting-started/choose-a-mode.md) starts from the question.
- [Errors and exit codes](errors-and-exit-codes.md) lists the messages above.
