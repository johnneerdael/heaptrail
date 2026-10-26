# JSON schemas

This page lists the fields of every JSON file HeapTrail writes with `--json`. Types are JSON types: *integer*, *number*, *string*, *boolean*, *array*, *object*, or `null`. A field marked *optional* is left out of the file when
it has no value. Read fields by name, and ignore any you do not know: the files carry no schema version.

See [JSON output](../automate/json-output.md) for how to write and query them.

## Summary

The file is an object with two lists of *class rows*.

| Field | Type | Meaning |
|---|---|---|
| `top_allocated_classes` | array of class row | The class table, ranked by total shallow size, limited by `--top`. |
| `top_largest_instances` | array of class row | The same classes ranked by the largest single instance. |

**Class row**

| Field | Type | Meaning |
|---|---|---|
| `class_name` | string | The class, with `[]` for arrays. |
| `obfuscated_class_name` | string, optional | The name in the dump, when `--mapping` changed it. |
| `instance_count` | integer | Number of instances. |
| `largest_allocation_bytes` | integer | Shallow bytes of the biggest instance. |
| `largest_object_id` | integer, optional | The id of that instance. Present for arrays. |
| `allocation_size_bytes` | integer | Shallow bytes of all instances. |

## Referrers

| Field | Type | Meaning |
|---|---|---|
| `target_label` | string | The class name, `id:<n>`, or `glob:<pattern>`. |
| `target_instance_count` | integer | How many instances were found. |
| `matched_classes` | array | For `--target-glob`: objects with `class_name` and `instance_count`. Empty otherwise. |
| `hop1`, `hop2`, `hop3` | array of holder row | The holders found at each hop. `hop3` is empty for fewer than three hops. |
| `grouped_holders` | array of grouped row, optional | With `--group-holders`. |

**Holder row:** `holder_class` (string), `field_name` (string, or `null` for an array slot), `ref_count` (integer).

**Grouped row:** `owner_family` (string), `holder_class` (string), `field_label` (string, `[]` for an array slot), `ref_count` (integer), `retained_bytes` (integer, optional, with `--retained-size`).

In JSON an array holder has a single-bracket class name (`java.lang.Object[]`), unlike the text table.

## Paths

| Field | Type | Meaning |
|---|---|---|
| `start_object_id` | integer | The object that was traced. |
| `steps` | array of step | One entry per hop. |
| `terminated_at_root` | boolean | Whether the chain reached a GC root. |
| `root_kind` | string or `null` | The root kind, such as `RootJavaFrame`. |
| `root_thread_name` | string or `null` | The thread that owns a thread root, when the dump records it. |
| `root_frame` | object or `null` | The top frame of that thread: `method`, `class`, `file`, `line`. |
| `root_metadata` | object, optional | The raw facts about a thread root: `object_id`, and, when present, `thread_serial`, `stack_trace_serial`, `frame_index` and `thread_object_id`. |
| `max_depth_reached` | boolean | Whether the walk stopped at `--max-depth`. |
| `depth` | integer | The number of hops taken. |

**Step:** `holder_object_id` (integer), `holder_class` (string), `via_field` (string, or `null` for an array), `array_index` (integer, or `null` for a field), `held_object_id` (integer).

## Merged paths

| Field | Type | Meaning |
|---|---|---|
| `target_label` | string | The class whose instances were merged. |
| `instance_count` | integer | How many instances. |
| `graph_verified` | boolean | `true` when `--retained-size` was set. |
| `root` | object | The tree. Its own `source_class` is empty. |

**Tree node:** `source_class` (string), `field_name` (string or `null`), `instance_count` (integer), `children` (array of tree node).

## Diff

The file is an array of *diff rows*, sorted by `--diff-by`, limited by `--top`.

| Field | Type | Meaning |
|---|---|---|
| `class_name` | string | The class. |
| `obfuscated_class_name` | string, optional | The name in the dumps, when `--mapping` changed it. |
| `count_a`, `count_b` | integer | Instances in the earlier and later dump. |
| `delta_count` | integer | `count_b - count_a`. May be negative. |
| `bytes_a`, `bytes_b` | integer | Shallow bytes in the earlier and later dump. |
| `delta_bytes` | integer | `bytes_b - bytes_a`. May be negative. |

## Diff series

`--top` does not shorten this file.

| Field | Type | Meaning |
|---|---|---|
| `snapshots` | array | One per dump, in order: `index`, `path`, `total_shallow_bytes`, `class_count`. |
| `steps` | array | One per neighbouring pair: `from_index`, `to_index`, and `deltas`, an array of diff rows. |
| `classes` | array of series row | Every class, with its value in every dump. |
| `monotonic_growth` | array of series row | The classes that never shrink and end higher. |
| `native_context` | object, optional | With `--native-context`. |

**Series row:** `class_name` (string), `obfuscated_class_name` (string, optional), `counts` (array of integer, one per dump), `bytes` (array of integer, one per dump), `total_delta_count` (integer), `total_delta_bytes` (integer).

**Native context:** `java_heap_kb`, `native_heap_kb`, `graphics_kb`, `gl_kb`, `total_pss_kb` (each integer, optional, in KiB) and `warnings` (array of string).

## Leak suspects

| Field | Type | Meaning |
|---|---|---|
| `total_heap_bytes` | integer | The sum of shallow sizes in HeapTrail's object graph. |
| `retained_reachable_bytes` | integer | What the GC roots can reach. Shares are relative to this. |
| `threshold_pct` | number | The threshold, as a percentage. |
| `suspects` | array of suspect | In rank order. |

**Suspect:** `dominator_id` (integer), `dominator_class` (string), `retained_bytes` (integer), `heap_share_pct` (number), `accumulating_class` (string), `accumulating_count` (integer), `accumulating_total_bytes` (integer),
`path_to_root` (a [paths](#paths) object without the per-hop retained sizes), `preview_snippet` (string, optional), `preview_content_label` (string, optional, in snake case: `json`, `xml`, `utf8_text`, `utf16_text`, `png_image`, `repeated_fill`, `unknown_binary` and so on), `below_threshold` (boolean).

## Allocation sites

| Field | Type | Meaning |
|---|---|---|
| `total_sites` | integer | All sites in the dump. |
| `top` | array of site | The biggest, limited by `--top`. |

**Site:** `class_name` (string), `bytes_allocated`, `instances_allocated`, `bytes_alive`, `instances_alive` (integers) and `stack_trace` (array of frame: `method`, `class`, `file`, `line`).

## Bitmaps

| Field | Type | Meaning |
|---|---|---|
| `entries` | array of entry | The biggest bitmaps. |
| `total_pixel_bytes` | integer | The sum over the entries shown. |

**Entry:** `object_id`, `width`, `height`, `bpp`, `pixel_bytes` (integers), `config` (string, always `ARGB_8888` in this version), `location` (`Java` or `Native`) and `holder_summary` (always `null`).

## Related

- [JSON output](../automate/json-output.md) shows how to write and query these files.
- [Leak suspects](../analyze/leak-suspects.md#json) and [Snapshot diff](../compare/diff.md#json) show them in use.
- [Command line](command-line.md) for `--json` and `--json-out`.
