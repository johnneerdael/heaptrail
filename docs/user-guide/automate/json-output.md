# JSON output

Add `--json` to any mode and heaptrail writes the same result as a JSON file, in addition to the text report on standard output. Scripts read the file, people read the terminal.

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --json --json-out reports/suspects.json
```

## Choose the path { #choose-the-path }

Without `--json-out`, heaptrail picks a name for you: a prefix for the mode and the time in milliseconds, in the current directory. It prints the name:

```bash
heaptrail -i jvm.hprof -t 1 --json
```

<!-- output: j-default.txt -->
```text
Output JSON result file heaptrail-1792947497099.json
```

For anything a script has to find again, use `--json-out <path>`:

| Flag | Effect |
|---|---|
| `--json` | Write the JSON file. |
| `--json-out <PATH>` | Write it to exactly this path. Needs `--json`. |

`--json-out` without `--json` is an argument error. The parent folder of the path must already exist. heaptrail does not create it, and reports the file error if it is missing:

```bash
heaptrail -i jvm.hprof --json --json-out /no/such/dir/x.json
```

<!-- output: ci-json-out-dir.txt from="error:" -->
```text
error: standard I/O error (No such file or directory (os error 2))
```

### The default file names

| Mode | File name |
|---|---|
| Summary | `heaptrail-<ms>.json` |
| `--find-referrers`, `--target-glob` | `heaptrail-referrers-<ms>.json` |
| `--paths-from-id` | `heaptrail-paths-<ms>.json` |
| `--paths-from-id --merge-paths` | `heaptrail-merge-paths-<ms>.json` |
| `--diff-from`, `--diff-to` | `heaptrail-diff-<ms>.json` |
| `--diff-series` | `heaptrail-diff-series-<ms>.json` |
| `--leak-suspects` | `heaptrail-leak-suspects-<ms>.json` |
| `--allocation-sites` | `heaptrail-allocation-sites-<ms>.json` |
| `--bitmaps` | `heaptrail-bitmaps-<ms>.json` |

`<ms>` is the Unix time in milliseconds. These names are for a quick look. In a pipeline, use `--json-out`.

The files are compact: a single line, with no spaces. Pretty-print them with `jq .`:

```bash
heaptrail -i heap.hprof -t 1 --json --json-out reports/summary.json
head -c 180 reports/summary.json
```

<!-- output: j-pretty.txt -->
```text
{"top_allocated_classes":[{"class_name":"com.nexio.tv.domain.model.MetaPreview","instance_count":573552,"largest_allocation_bytes":104,"allocation_size_bytes":59649408}],"top_large
```

## What each mode writes

| Mode | Top level | Notes |
|---|---|---|
| Summary | `top_allocated_classes`, `top_largest_instances` | Two lists of classes. No header counts, no retained sizes, no previews. |
| Referrers | `target_label`, `target_instance_count`, `matched_classes`, `hop1`, `hop2`, `hop3`, and `grouped_holders` with `--group-holders` | Each hop is a list of `holder_class`, `field_name` (`null` for an array slot) and `ref_count`. |
| Paths | `start_object_id`, `steps`, `terminated_at_root`, `root_kind`, `root_thread_name`, `root_frame`, `max_depth_reached`, `depth` | One object per hop in `steps`. |
| Merged paths | `target_label`, `instance_count`, `root`, `graph_verified` | `root` is a nested tree. |
| Diff | An array | One object per class. |
| Diff series | `snapshots`, `steps`, `classes`, `monotonic_growth`, `native_context` | Complete: `--top` does not shorten it. |
| Leak suspects | `total_heap_bytes`, `retained_reachable_bytes`, `threshold_pct`, `suspects` | Each suspect has its `path_to_root`. |
| Allocation sites | `total_sites`, `top` | Each site has its `stack_trace`. |
| Bitmaps | `entries`, `total_pixel_bytes` | |

[JSON schemas](../reference/json-schemas.md) lists every field.

A few things the JSON does *not* contain:

- **Text-only parts of the summary:** the header counts, the thread stacks and the array previews. The one place a preview appears is `--leak-suspects`: `preview_snippet`.
- **Retained sizes in the summary and in referrers.** Use the suspects JSON for retained data.
- **`--top` limits** apply to most lists. A diff series is the exception.

## Query it with jq { #query-it-with-jq }

A table of the biggest classes, as tab-separated values:

```bash
heaptrail -i heap.hprof -t 5 --json --json-out reports/summary.json
jq -r '.top_allocated_classes[] | [.class_name, .instance_count, .allocation_size_bytes] | @tsv' reports/summary.json
```

<!-- output: j-top.txt -->
```text
com.nexio.tv.domain.model.MetaPreview	573552	59649408
byte[]	940474	26541296
char[]	372795	22639616
java.lang.String	908414	21801936
java.lang.Object[][]	227587	11292768
```

The biggest changes between two dumps, as CSV:

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --top 5 --json --json-out reports/diff.json
jq -r '.[] | [.class_name, .delta_count, .delta_bytes] | @csv' reports/diff.json
```

<!-- output: j-diff-csv.txt -->
```text
"java.util.TreeMap$TreeMapEntry",32284,1033088
"com.google.gson.reflect.TypeToken",31615,758760
"com.nexio.tv.domain.model.ProviderIds",17537,841776
"java.util.LinkedHashMap$LinkedHashMapEntry",4349,139168
"com.nexio.tv.core.metadata.router.MetadataLocalizationRejectedCandidate",3140,75360
```

More one-liners, each using fields from the tables above. Assume the file names from the earlier examples.

```bash
# The classes of every suspect
jq -r '.suspects[].dominator_class' suspects.json

# The share of the biggest suspect
jq '.suspects[0].heap_share_pct' suspects.json

# Only the suspects that clear the threshold
jq '.suspects[] | select(.below_threshold | not)' suspects.json

# Every holder class in a referrer report
jq -r '.hop1[].holder_class' referrers.json

# How a path ended
jq '{terminated_at_root, root_kind, max_depth_reached}' path.json

# Classes that never shrink across a series
jq -r '.monotonic_growth[].class_name' series.json

# The Java and native totals of a series
jq '.native_context' series.json
```

## With a mapping

On a release build, `--mapping` restores class names in the JSON as well. Summary, diff and series files keep the original name in `obfuscated_class_name`. See
[Deobfuscate release builds](../android/deobfuscate-release-builds.md#in-json).

## Gotchas

- **The text report still prints.** `--json` adds a file, it does not replace the report. Redirect or ignore standard output if you only want the file.
- **A second run does not overwrite a default-named file,** because the name has a timestamp. A `--json-out` path is overwritten.
- **Do not rely on row order among equal values.** Gate on values, not on which row came first.
- **Read fields by name.** The JSON has no schema version. Ignore fields you do not know, and treat optional fields as possibly absent: heaptrail leaves out some fields when they have no value, such as `obfuscated_class_name` and `preview_snippet`.

## Related

- [Gate a build on a leak threshold](ci-gates.md) uses these files in CI.
- [JSON schemas](../reference/json-schemas.md) has every field.
- [Command line reference](../reference/command-line.md) for `--json` and `--json-out`.
