# Allocation sites

A holder chain tells you *why* an object is still alive. An allocation site tells you *where in the code* it was created. `--allocation-sites` ranks the
call sites that allocated the most bytes, with the stack trace of each, so you can skip the grep through your source for whoever builds that class.

```bash
heaptrail -i heap.hprof --allocation-sites --top 20
```

This works only on a dump that was captured with [allocation tracking](../capture/allocation-tracking.md). Ordinary dumps do not carry the data, and the mode says so.

## Does the dump have them?

The summary always tells you:

```bash
heaptrail -i heap.hprof -t 1
```

<!-- output: alloc-hint-none.txt from="AllocationSites:" head="1" -->
```text
AllocationSites: not present (capture with `am profile start <pid>`)
```

and the mode refuses, with the same hint, when there is nothing to show:

<!-- output: alloc-err.txt from="error:" -->
```text
error: no AllocationSites records in this dump (capture with `am profile start <pid>`)
```

The exit status is 1, so a script can detect it and fall back to [suspects, referrers and diffs](leak-suspects.md).

## The report

The only dump in the repository that carries allocation sites is the small 32-bit JVM fixture `test-heap-dumps/hprof-32.bin`. Its summary line reads:

```bash
heaptrail -i test-heap-dumps/hprof-32.bin -t 2
```

<!-- output: fix32-alloc-hint.txt from="AllocationSites:" head="1" -->
```text
AllocationSites: 464 sites across 1 records (run with --allocation-sites for stack traces)
```

and the report looks like this:

```bash
heaptrail -i test-heap-dumps/hprof-32.bin --allocation-sites --top 5
```

<!-- output: fix32-alloc.txt from="Top 5 allocation" -->
```text
Top 5 allocation sites by bytes_allocated (of 464 total):

  ─   62.01KiB  /         692 instances  char[]#<init>

  ─   24.76KiB  /           9 instances  byte[]#<init>

  ─   16.81KiB  /         702 instances  java.lang.String#<init>

  ─   12.15KiB  /         304 instances  java.lang.Object[]#<init>

  ─    2.21KiB  /          51 instances  java.lang.String[]#<init>
```

Each site is one line:

| Part | Meaning |
|---|---|
| `62.01KiB` | Bytes allocated at this site. The list is sorted by this number. |
| `692 instances` | How many objects were allocated there. |
| `char[]#<init>` | The class allocated. The `#<init>` suffix is always printed. |

Under each line, HeapTrail prints the stack that led to the allocation, one frame per line. The records in this old dump carry no stack frames, so
nothing follows each row here. In a dump captured on Android with tracking, each site is followed by its frames, in this form:

```text
  ─    1.21GiB  /     4812000 instances  com.example.app.Catalog#<init>
        at com.example.app.Catalog.<init>(Catalog.kt:41)
        at com.example.app.Repository.parse(Repository.kt:87)
```

(The frames above are an illustration of the layout, not output from a dump.)

## Options and JSON

| Flag | Effect |
|---|---|
| `-t`, `--top N` | The number of sites to print. |
| `--mapping`, `--auto-mapping` | Restore real class names in the allocated class and in each frame. |
| `--json`, `--json-out` | Write the sites as JSON: `total_sites` and `top`, with `class_name`, `bytes_allocated`, `instances_allocated`, `bytes_alive`, `instances_alive` and `stack_trace` for each. |

The text report shows only the bytes and instances *allocated*. The JSON also carries the bytes and instances still alive.

## Gotchas

- **You cannot add allocation data afterwards.** If the summary says `not present`, the dump has none. Capture again with tracking on.
- **Tracking is opportunistic on Android.** It can fail or yield an empty dump on a given device. See [Allocation tracking](../capture/allocation-tracking.md#when-it-does-not-work).
- **Numbers are per site.** A site that allocates a lot is not necessarily a leak. Many allocations are short-lived. Pair it with a [diff](../compare/diff.md) or a retained-size view to find what survives.

## Related

- [Allocation tracking](../capture/allocation-tracking.md) is how to capture a dump that has sites.
- [Leak suspects](leak-suspects.md) is the fallback when a device cannot track allocations.
- [Android](../android/index.md) for restoring names in frames.
