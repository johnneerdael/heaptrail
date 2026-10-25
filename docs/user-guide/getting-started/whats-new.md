# What's new

This page lists what each release added, newest first. Dates are the day each release was
published. The [GitHub releases page](https://github.com/johnneerdael/heaptrail/releases) has the
original notes and the binaries.

To see which version you have, run `heaptrail --version`. To upgrade, see
[Download and install](install.md#upgrade-and-uninstall).

## Which version added what

| You want to use | You need |
|---|---|
| `--find-referrers`, `--paths-from-id`, `--diff-from` and `--diff-to`, `--hops`, 4-byte ids | 0.7.0 |
| Android `JAVA PROFILE 1.0.3` dumps | 0.7.1 |
| Thread names on paths, `--allocation-sites`, `--target-glob`, array slot numbers on paths | 0.8.0 |
| `--preview-bytes`, `-l` with standalone arrays, `--list-arrays-min-bytes` | 0.9.0 |
| `--retained-size` | 1.0.0 |
| `--exclude-soft-weak`, `--leak-suspects`, `--merge-paths`, `--bitmaps` | 1.1.0 |
| Android dumps with elided classes, without a panic | 1.1.1 |
| `--mapping`, `--auto-mapping`, `android-capture`, `--json-out`, `content:` labels on previews | 1.2.0 |
| `--diff-series`, `--group-holders`, `--native-context`, root metadata on paths | 1.3.0 |
| `android-capture --series`, stall detection while capturing | 1.3.1 |
| Cleanup of old dumps on the device | 1.4.0 |

## 1.4.1 — October 25, 2026

The user guide is now a site. Nothing about how heaptrail reads a dump changes.

- The guide you are reading replaces `USERGUIDE.md` and the long `README.md`. Every block of output in it comes from a real run.
- `README.md` is a short front door, `USERGUIDE.md` maps the old sections to the new pages, and the guide's [glossary](../reference/glossary.md) replaces `glossary.md`.
- `--help` for `--preview-bytes` and `--target-glob` names the guide page instead of a `USERGUIDE.md` section.
- The `analysing-heap-dumps` Claude Code plugin points at the guide. Update the plugin to get the new text.
- The crate links to the guide as its documentation, and its package no longer carries the guide sources.

## 1.4.0 — May 25, 2026

Repeated Android captures no longer fill the device's `/data` partition.

- `android-capture` deletes stale `/data/local/tmp/*.hprof` files before each run.
- It removes each device-side dump after pulling it.
- The cleanup commands appear in the capture transcript, so the provenance is complete.

See [android-capture](../capture/android-capture.md).

## 1.3.1 — May 24, 2026

More reliable live Android capture.

- `android-capture` waits for the device-side dump to be nonzero and stable before it pulls.
- It fails after 60 seconds of no change in the device-side file, instead of pulling empty dumps again and again.
- It always tries `am profile stop <pid>` after an allocation-tracked capture.
- A stalled allocation-tracked capture is reported as unsupported on that device, so you can fall back to suspects, diffs, holders and paths.
- New `--series <COUNT>` and `--series-delay-seconds <SECONDS>` collect a validated series for `--diff-series`.

## 1.3.0 — May 24, 2026

Primitives for media and playback leaks, where memory grows across state changes.

- `--diff-series` compares three or more ordered snapshots: step deltas, first-to-last totals and monotonic growth candidates.
- `--group-holders` groups referrer rows by owner family, holder class and field.
- `--paths-from-id` prints raw root metadata (thread serial, frame index) when thread names or frames are not in the dump.
- `--native-context <PATH>` adds a bounded block of `dumpsys meminfo` totals to a diff series.

See [Compare snapshots](../compare/index.md).

## 1.2.0 — May 24, 2026

Release-build Android heaps in readable names, and a capture helper.

- `--mapping <PATH>` deobfuscates class and field names with an R8 or ProGuard mapping file.
- `--auto-mapping` matches the installed app's version to your local Gradle outputs and picks the right file.
- `android-capture` captures and validates a dump over `adb`, and writes a transcript.
- `--json-out <PATH>` writes JSON to an exact path instead of a timestamped one.
- Previews gain a `content:` label such as `JSON`, `XML`, `PNG image` or `unknown binary`.

See [Android](../android/index.md).

## 1.1.1 — May 11, 2026

Modern Android dumps no longer crash heaptrail.

Version 1.1.0 panicked with `class id must have a class definition` on dumps that reference classes the
dumper left out, which is common for `am dumpheap` on recent Android. Now heaptrail counts those instances at
the bare object-header size, names the class `<unknown class #id>`, and prints a single warning at the end
of the run. Upgrade if you see that panic.

## 1.1.0 — May 10, 2026

Leak hunting in the style of Eclipse MAT.

- `--exclude-soft-weak` drops weak, soft and phantom reference edges, so the strong holder shows through.
- `--leak-suspects` ranks the objects that keep the most alive and prints a report for each.
- `--merge-paths` folds the paths of every instance of a class into one tree.
- `--bitmaps` ranks `android.graphics.Bitmap` instances by pixel bytes.

## 1.0.0 — May 10, 2026

- `--retained-size` computes retained sizes with a Lengauer–Tarjan dominator tree. It re-sorts the summary by retained bytes, annotates each path hop, and adds a retained column to referrer rows.

## 0.9.0 — May 9, 2026

- `--preview-bytes N` shows the first bytes of `char[]`, `byte[]` and other primitive arrays, decoded as UTF-8, UTF-16 or hex.
- With `-l`, the summary lists standalone large arrays. `--list-arrays-min-bytes` sets the size threshold.

## 0.8.0 — May 9, 2026

- A path that ends at a thread-owned root now names the thread and, for a Java frame, the top frame.
- `--allocation-sites` prints the top call sites with resolved stack traces for dumps captured under allocation tracking. The summary always says whether the dump has them.
- `--target-glob` finds referrers of every class that matches a glob.
- Path hops through an `Object[]` show the slot number, for example `java.lang.Object[][12]`.

## 0.7.1 — May 9, 2026

- Support for the Android extension tags of `JAVA PROFILE 1.0.3`. Version 0.7.0 panicked with `unhandled gc record tag 141` on dumps from modern `am dumpheap`. The extension roots are kept as their own kinds on paths, such as `RootVmInternal` and `RootJniMonitor`, instead of being lumped into `RootUnknown`. See [GC root kinds](../reference/gc-root-kinds.md).

## 0.7.0 — May 9, 2026

heaptrail begins as a rebrand of [hprof-slurp](https://github.com/agourlay/hprof-slurp), keeping its streaming summary parser and adding investigation modes on top.

- `--find-referrers` with `--hops 1`, `2` or `3`, for a class name or an object id.
- `--paths-from-id` with `--max-depth`.
- `--diff-from` and `--diff-to`, sorted with `--diff-by count` or `bytes`.
- 4-byte object ids, which Android uses.
- The [Claude Code plugin](../automate/claude-code-plugin.md).

## Related

- [Download and install](install.md) for the upgrade command.
- [Command line reference](../reference/command-line.md) for the current flags.
- [About heaptrail](../help/about.md) for the project's origin and license.
