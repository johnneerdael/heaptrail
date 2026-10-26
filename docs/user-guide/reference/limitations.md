# Limitations

What HeapTrail does not do, and where it is liable to be misread. Each row says what to do instead. The list comes from using the tool on real dumps for this guide, so it includes behaviors that are quirks
and not design choices.

## What it is not

| Not offered | Use instead |
|---|---|
| Interactive graph browsing, clicking through references | Eclipse MAT or VisualVM. See [the FAQ](../help/faq.md#when-should-i-use-eclipse-mat-instead). |
| A query language such as OQL | MAT. HeapTrail has fixed flags by design. |
| HTML reports for people who will not use a terminal | MAT's report exporter. |
| Native heap attribution | A native profiler. `--native-context` records totals only. |
| Redacting secrets from a dump or a report | Share reports, not dumps. See [Handle dumps safely](../capture/handle-dumps-safely.md). |
| Listing the instances of a class | Take ids from [retained size](../analyze/retained-size.md), [suspects](../analyze/leak-suspects.md) or [`-l`](../analyze/list-strings.md). |

## Where a result can mislead

| Behavior | Detail | What to do |
|---|---|---|
| A path ending in `orphan` | The walker follows instance fields and array slots, not class statics. A static holder is invisible to it. | Ask [`--find-referrers id:<id>`](../holders/find-referrers.md) about the last id. |
| A path that loops | The walker takes the first holder it finds, so cycles run to `--max-depth`. | Ask find-referrers about a repeated id. |
| `--leak-suspects` ranks garbage | Unreachable objects are ranked too, and can show over 100 %. | Use a `live` JVM dump. |
| Nested suspects | Suspects inside suspects tell one story. | Read the group as one finding. |
| Class retained overlaps | The column sums each instance's retained size, so nested instances count more than once. | Rank with it, do not add it up. |
| Two different totals | The summary's raw total and the suspects report's `total` come from different code paths. | Compare within one report. |
| `--bitmaps` on newer Android | It needs `mWidth`, `mHeight` and `mConfig`, and reports "class is not loaded" when they are missing, even if instances exist. | See [Bitmaps](../analyze/bitmaps.md#when-it-fails). |
| `--bitmaps` config and holders | The config is always reported as `ARGB_8888`, and the holder summary is always empty. | Trace with `--paths-from-id`. |
| `-l` is not string contents | It lists the dump's string table (names), not `java.lang.String` values. | Use `--preview-bytes` on the arrays. |
| `--hops` above 3 | `4` and `5` are accepted, and three hops are reported. | Trace the last holder by id. |
| `--include-statics` | Accepted, and has no effect. Statics are always listed. | |
| An unknown id in referrers | `id:<n>` for an object that is not in the dump still prints `Found 1 target instance(s)` and `(none)`. | Check the id. |
| Array names on Android | Class tables and referrer rows add a pair of brackets: `Object[][]` means `Object[]`. JSON does not. | Read it as a label quirk. |
| Unknown classes | Instances of a class the dump does not define are counted at the bare header size and named `<unknown class #id>`. | Treat class totals as a lower bound. |
| Row order | Rows with equal counts or sizes can come out in a different order on different runs. | Do not depend on position. |

## Mapping

| Behavior | Detail |
|---|---|
| Only classes and fields are restored | Method names, including those in stack frames, stay as they are. |
| Targets use the dump's names | `--find-referrers` and `--target-glob` match the names in the dump, so use the obfuscated name as the target. |
| `--auto-mapping` assumptions | It needs `adb`, an `app` module, Gradle's `output-metadata.json`, and reads the first element of each. |
| The mapping is trusted | HeapTrail does not check that a mapping belongs to the dump. |

## Cost

| Behavior | Detail |
|---|---|
| Retained size and suspects keep the whole graph | About 5 to 7.5 times the dump's size in memory on the dumps measured. |
| `--merge-paths` has no instance cap | The time is instances × hops × one pass. |
| Paths cost a pass per hop | A deep path on a large dump takes many seconds. |
| Larger dumps were not measured | The numbers in [Performance](performance.md) stop at 224 MiB. |

## Input and output

| Behavior | Detail |
|---|---|
| Completeness is not checked | A truncated dump can give a partial report, or a panic with status 101. |
| A closed pipe panics | Piping a long report into `head` ends with `Broken pipe` and status 101. Redirect to a file. |
| Some errors are generic | `conflicting modes` also covers a missing `--diff-to` and `--group-holders` without a referrer mode. `not yet implemented: object id not found in dump (--merge-paths)` means the id is not an instance. |
| Thread names are rare | Most Android dumps carry no thread records. Roots print raw serial numbers instead. |
| Allocation sites need tracking | They cannot be added after the fact, and tracking is opportunistic on Android. |
| The JSON has no schema version | Read fields by name. See [JSON schemas](json-schemas.md). |
| The summary JSON is small | It has the two class lists, and no header counts, retained sizes or previews. |
| A diff compares class names and shallow bytes | It does not follow objects, and obfuscated names change between builds. |
| A finalizer-reference option is not offered | MAT has a separate exclusion for finalizer references. HeapTrail has only `--exclude-soft-weak`. |

## Related

- [Errors and exit codes](errors-and-exit-codes.md) lists the messages.
- [Troubleshooting](../help/troubleshooting.md) starts from a symptom.
- [Performance](performance.md) has the measurements.
