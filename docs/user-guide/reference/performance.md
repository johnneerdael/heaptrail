# Performance

How long each mode takes, and how much memory it needs. These are measurements from one machine on real Android dumps, not guarantees. Use them to plan, then measure on your own dump.

## How these were measured

- **Machine:** an Apple silicon Mac running macOS, HeapTrail 1.4.0 built with `cargo build --release`.
- **Dumps:** a 224 MiB Android dump (2.6 million instances, 1.4 million primitive arrays), a 186 MiB one, and an 80 MiB one.
- **Method:** each command run once, with the dump already in the operating system's file cache. A first read from a cold disk is slower.
- **Memory** is the *peak resident set size* reported by `/usr/bin/time -l` (macOS). On Linux, `/usr/bin/time -v` reports it as "Maximum resident set size".

To measure your own dump:

```bash
/usr/bin/time -l heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak > /dev/null
```

## Time and memory by mode

On the 224 MiB dump:

| Mode | Wall time | Peak memory |
|---|---|---|
| Summary | 0.17 s | 533 MiB |
| Summary with `--preview-bytes 200` | 0.16 s | 598 MiB |
| Summary with `-l` | 0.17 s | 483 MiB |
| Summary with `--retained-size` | 1.7 s | 1,390 MiB |
| `--find-referrers <class> --hops 1` | 0.51 s | 137 MiB |
| `--find-referrers <class> --hops 2` | 0.71 s | 161 MiB |
| `--find-referrers <class> --hops 3` | 0.93 s | 151 MiB |
| `--find-referrers id:<n> --hops 1` | 0.36 s | 108 MiB |
| `--find-referrers --retained-size` | 1.9 s | 1,308 MiB |
| `--paths-from-id` (9 hops) | 2.8 s | 162 MiB |
| `--paths-from-id --retained-size` | 4.3 s | 1,422 MiB |
| `--leak-suspects --top 1` | 3.7 s | 1,507 MiB |
| `--leak-suspects --top 3` | 5.9 s | 1,687 MiB |
| `--paths-from-id --merge-paths` (5 instances, depth 12) | 15 s | 263 MiB |
| `--diff-from` and `--diff-to` (224 MiB and 186 MiB) | 0.30 s | 558 MiB |
| `--diff-series` (three dumps of about 80 MiB) | 0.27 s | 377 MiB |

Reading speed is about 1.3 GiB per second for the summary on this machine.

## How it scales with the dump

| Mode | 79 MiB | 186 MiB | 224 MiB |
|---|---|---|---|
| Summary, peak memory | 268 MiB | 526 MiB | 533 MiB |
| `--retained-size`, peak memory | 426 MiB | 913 MiB | 1,390 MiB |
| `--leak-suspects --top 3`, peak memory | 540 MiB | 954 MiB | 1,687 MiB |
| `--find-referrers <class> --hops 2`, peak memory | 96 MiB | 119 MiB | 161 MiB |
| `--leak-suspects --top 3`, wall time | 2.7 s | 5.6 s | 5.9 s |

Rules of thumb from these runs:

- **The summary** reaches about 0.5 GiB and was flat between the 186 MiB and 224 MiB dumps. Its read buffers are fixed at 64 MiB each.
- **Referrers and paths** stay small, 100 to 160 MiB, because they hold an index and a set of ids, not the object graph.
- **Retained size and leak suspects** keep the whole graph. Plan for about **5 to 7.5 times the dump's size** in RAM. The multiple depends on the number of objects, more than on the file size.
- **A path costs one pass per hop,** about 0.3 s per hop here. Referrers cost one pass per hop beyond the first, about 0.2 s.
- **`--merge-paths` costs instances × hops × one pass.** It has no cap on the number of instances.

These runs were not repeated on dumps larger than 224 MiB, on Linux or on Windows.

## What affects the time

| Factor | Effect |
|---|---|
| Number of objects | Retained size and suspects scale with it. The summary scales with the file size. |
| CPU cores | The parser reads, parses and records on separate threads. Four or more cores help. |
| Disk | A cold file is read at disk speed. Later runs on the same file hit the cache. |
| `--max-depth` | Paths and merged paths cost one pass per hop. |
| `--hops` | Each extra hop costs one more pass. |
| `--preview-bytes` | Adds a pass that keeps up to N bytes per primitive array. Small for a small N. |

## Reducing the cost

- **Use the summary and referrers first.** They are the cheap modes. Reach for retained size and suspects when the question needs them.
- **Lower `--max-depth`** to the depth you need.
- **Pick a class with few instances for `--merge-paths`.** A class with tens of instances, not thousands.
- **Run the heavy modes on a bigger machine.** At 5 to 7.5 times the file size, a 400 MiB dump would need 2 to 3 GiB for suspects, which is tight on a 4 GiB runner. That is an extrapolation from the numbers above, not a measurement.
- **Capture smaller dumps.** A dump taken at the right moment, from a smaller process, costs less than a large one.

## Related

- [How HeapTrail reads a dump](../concepts/how-heaptrail-reads-a-dump.md) explains where the time and memory go.
- [Limitations](limitations.md) lists what was not measured.
- [Gate a build on a leak threshold](../automate/ci-gates.md) for sizing a CI job.
