# Deobfuscate release builds

Release builds of an Android app are shrunk and renamed by R8 (or ProGuard) before they ship, so a heap dump from one is full of names such as `a3.t`, `p1.j` and `zh.l1`. The build also writes a
**mapping file** that records what each short name stands for. `--mapping` hands that file to HeapTrail, which then prints the real names.

```bash
heaptrail -i heap.hprof --mapping app/build/outputs/mapping/universalRelease/mapping.txt --leak-suspects --exclude-soft-weak
```

## Before and after

This is the top of the class table of a release-build dump, first as the dump has it:

```bash
heaptrail -i launch.hprof -t 12
```

<!-- output: map-raw.txt from="Top 12 raw shallow" until="Top 12 largest" -->
```text
Top 12 raw shallow heap classes:

+------------+-----------+------------+--------------------------------------------+
| Total size | Instances |    Largest | Class name                                 |
+------------+-----------+------------+--------------------------------------------+
|   17.53MiB |    301745 |    1.38MiB | byte[]                                     |
|    6.40MiB |    279513 | 24.00bytes | java.lang.String                           |
|    3.79MiB |     66700 |   42.16KiB | java.lang.Object[][]                       |
|    2.79MiB |     60844 | 48.00bytes | x7.k                                       |
|    2.42MiB |     37934 |  418.64KiB | int[]                                      |
|    1.31MiB |     57212 | 24.00bytes | java.util.ArrayList                        |
|    1.12MiB |      5919 |  117.41KiB | char[]                                     |
|  907.00KiB |     29024 | 32.00bytes | java.util.LinkedHashMap$LinkedHashMapEntry |
|  774.16KiB |     49546 | 16.00bytes | v7.t                                       |
|  703.50KiB |     22512 | 32.00bytes | a3.t                                       |
|  594.84KiB |      7614 | 80.00bytes | gg.s0                                      |
|  444.26KiB |     11373 | 40.00bytes | mg.a0                                      |
+------------+-----------+------------+--------------------------------------------+
```

Then with a mapping file:

```bash
heaptrail -i launch.hprof --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt -t 12
```

<!-- output: map-manual.txt from="Using mapping" until="File content summary" -->
```text
Using mapping: myapp/app/build/outputs/mapping/universalRelease/mapping.txt
Processing 78.90MiB binary hprof file in 'JAVA PROFILE 1.0.3' format.
```

<!-- output: map-manual.txt from="Top 12 raw shallow" until="Top 12 largest" -->
```text
Top 12 raw shallow heap classes:

+------------+-----------+------------+--------------------------------------------+
| Total size | Instances |    Largest | Class name                                 |
+------------+-----------+------------+--------------------------------------------+
|   17.53MiB |    301745 |    1.38MiB | byte[]                                     |
|    6.40MiB |    279513 | 24.00bytes | java.lang.String                           |
|    3.79MiB |     66700 |   42.16KiB | java.lang.Object[][]                       |
|    2.79MiB |     60844 | 48.00bytes | x7.k                                       |
|    2.42MiB |     37934 |  418.64KiB | int[]                                      |
|    1.31MiB |     57212 | 24.00bytes | java.util.ArrayList                        |
|    1.12MiB |      5919 |  117.41KiB | char[]                                     |
|  907.00KiB |     29024 | 32.00bytes | java.util.LinkedHashMap$LinkedHashMapEntry |
|  774.16KiB |     49546 | 16.00bytes | v7.t                                       |
|  703.50KiB |     22512 | 32.00bytes | com.example.myapp.player.TrackQueue        |
|  594.84KiB |      7614 | 80.00bytes | gg.s0                                      |
|  444.26KiB |     11373 | 40.00bytes | mg.a0                                      |
+------------+-----------+------------+--------------------------------------------+
```

`a3.t` became `com.example.myapp.player.TrackQueue`, and HeapTrail printed the file it used. The rows for `x7.k`, `v7.t` and the others did not change, because the mapping file in this example covers only three names. It
is a small demonstration file, with invented class names, not the app's real mapping. A real mapping covers every renamed class.

`Using mapping:` is the first line of the output, so a report that shows it is a report with a mapping applied.

## Find the mapping file

Gradle writes it when it builds a release variant with minification on:

```text
app/build/outputs/mapping/<variant>/mapping.txt
```

For a variant called `universalRelease`, that is `app/build/outputs/mapping/universalRelease/mapping.txt`. Keep this file for every release you ship, and upload it to your store console, so you can read a dump or a crash report from any build.

!!! danger "Use the mapping of the exact build"
    The mapping must come from the same build as the app that produced the dump. A mapping from another build, even a neighboring version, gives names that look plausible and are wrong. Check the
    version of the installed app against the build. [Auto-mapping](auto-mapping.md) does this for you.

## What gets restored

HeapTrail reads the class lines and the field lines of the mapping file. It restores:

- **Class names**, in every report, including array types such as `a3.t[]`.
- **Field names**, for holders in [referrers](../holders/find-referrers.md), [paths](../holders/paths-to-root.md) and merged paths: `p1.b.j` becomes the real field name when the mapping has it.
- **Class names in stack frames** of [allocation sites](../analyze/allocation-sites.md).

It does not restore method names. Lines for methods in the mapping file are skipped.

| Mode | Names restored |
|---|---|
| Summary, retained size | Class names. |
| `--find-referrers`, `--target-glob` | The target label, holder classes and field names. |
| `--paths-from-id`, `--merge-paths` | Holder classes and field names. |
| `--leak-suspects` | Dominator and accumulating classes, and the path. |
| `--diff-from`/`--diff-to`, `--diff-series` | Class names. |
| `--allocation-sites` | The allocated class, and the class of each frame. |
| `--bitmaps` | Nothing to restore. |

## Give targets by the name in the dump

The mapping changes what is *printed*. It does not change how targets are looked up: `--find-referrers` and `--target-glob` match against the names that are in the dump. So you must give the obfuscated name as the target,
and the output comes back with the real one:

```bash
heaptrail -i soak.hprof --find-referrers com.example.myapp.player.PlaybackState --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt
```

That command fails with `target class not found in dump`, because the dump knows the class as `p1.j`. The working form names the class as the dump does:

```bash
heaptrail -i soak.hprof --find-referrers p1.j --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt --hops 1 --top 4
```

<!-- output: pg-referrers.txt from="Found" -->
```text
Found 11382 target instance(s) for com.example.myapp.player.PlaybackState

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  p1.b.j                                     1238
  p1.b.a                                     1238
  p1.b0.j                                     276
  p1.b0.a                                     276
```

To find the dump's name for a class, look it up in `mapping.txt`: the line `com.example.myapp.player.PlaybackState -> p1.j:` says it. A glob over real package names, such as `com.example.myapp.**`, matches nothing for the same reason.

## In JSON

JSON from the summary, a diff and a series keeps the raw name next to the restored one, so a machine-readable report can still be traced back to the dump:

```bash
heaptrail -i launch.hprof --mapping myapp/app/build/outputs/mapping/universalRelease/mapping.txt -t 12 --json --json-out reports/mapped.json
jq -c '.top_allocated_classes[] | select(.obfuscated_class_name) | {class_name, obfuscated_class_name}' reports/mapped.json
```

<!-- output: map-json.txt from="obfuscated_class_name" -->
```text
{"class_name":"com.example.myapp.player.TrackQueue","obfuscated_class_name":"a3.t"}
```

JSON from referrers, paths, merged paths and suspects carries the restored names only.

## Errors

| Message | Cause |
|---|---|
| `mapping file not found: <path>` | The path is wrong, or is not a file. |
| `invalid mapping file <path> at line N: …` | A class line is not in the form `original -> obfuscated:`. The file may be truncated or not an R8 mapping. |

```bash
heaptrail -i heap.hprof --mapping /nope/mapping.txt
```

<!-- output: map-missing.txt from="error:" -->
```text
error: mapping file not found: /nope/mapping.txt
```

```bash
heaptrail -i jvm.hprof --mapping meminfo.txt
```

<!-- output: map-invalid.txt from="error:" -->
```text
error: invalid mapping file meminfo.txt at line 1: expected class mapping with ` -> `
```

`--mapping` and `--auto-mapping` cannot be used together. clap rejects the combination before HeapTrail reads anything.

## Gotchas

- **Methods are not restored.** Names of methods in stack frames stay as they are.
- **Names the mapping does not know stay raw.** Library classes that R8 kept (such as `java.lang.String`) were never renamed. Classes from a library you did not map stay short.
- **An old dump needs its old mapping.** Keep one mapping file per shipped build.
- **Without `--mapping`, nothing is wrong.** The report is in the dump's names. Use it to look names up in the mapping file by hand.

## Related

- [Auto-mapping](auto-mapping.md) finds the right file for the installed app.
- [android-capture](../capture/android-capture.md#mapping) records the mapping used during capture.
- [Playback growth](../compare/recipes/playback-growth.md) uses a mapping on a series.
