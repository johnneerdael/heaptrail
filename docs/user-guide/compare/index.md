# Compare snapshots

One heap dump shows what is alive at one moment. It cannot say whether a number is growing, because it has no "before". These modes compare dumps of the same process: a pair for a clear
before-and-after, or a series of three or more for a timeline.

## Start here

- Two dumps around one action: [Snapshot diff](diff.md).
- Three or more, in order: [Diff a series](diff-series.md). It finds the classes that never shrink.
- Android memory that does not live in the Java heap: [Native context](native-context.md).

## Your goal, and the page

| Your goal | Command | Page |
|---|---|---|
| What changed between two dumps? | `--diff-from a.hprof --diff-to b.hprof` | [Snapshot diff](diff.md) |
| What keeps growing across a timeline? | `--diff-series a.hprof b.hprof c.hprof` | [Diff a series](diff-series.md) |
| Is it Java heap growth or native? | `--native-context meminfo.txt` | [Native context](native-context.md) |
| Capture the dumps | `android-capture --series 3` | [Capture a series](../capture/capture-a-series.md) |

## Recipes

| Your problem | Recipe |
|---|---|
| Memory grows while media plays | [Playback growth](recipes/playback-growth.md) |
| I want to know what one screen or action costs | [Before and after an interaction](recipes/before-and-after-an-interaction.md) |

## What a comparison can and cannot tell you

- **It compares classes, not objects.** Object ids are not stable between dumps, so HeapTrail counts instances and shallow bytes per class name, and compares those totals.
- **It is shallow.** A diff shows growth in the bytes objects occupy themselves. Use [`--retained-size`](../analyze/retained-size.md) on one dump to see what the growth keeps alive.
- **It needs the same build.** Obfuscated names change between builds, so compare dumps of one build, or restore names with `--mapping` first.
- **A diff is a signal, not a proof.** Growth between two dumps taken seconds apart may be warm-up. Capture around a deliberate, repeatable action, and prefer a series.

## Related

- [Capture a series](../capture/capture-a-series.md) takes the dumps.
- [Analyze](../analyze/index.md) for what to do with one dump.
- [Trace holders](../holders/index.md) for what to do with a class a diff points at.
