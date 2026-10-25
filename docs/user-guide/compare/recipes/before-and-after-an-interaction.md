# Before and after an interaction

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `--diff-from`, `--diff-to`, `--diff-by`, `--find-referrers`</span>
<span><strong>Works on</strong> JVM and Android dumps</span>
<span><strong>Time</strong> ten minutes</span>
<span><strong>Undo</strong> nothing to undo: it reads dumps</span>
</div>

## The problem

You suspect that opening a screen, playing a clip, or running a job leaves something behind, and you want to know what and how much. A single dump cannot say. Two dumps around the action can, if you
take them so the difference means something.

## The solution

1. **Reach a steady state.** Start the app, let it finish loading, and leave it idle for a moment. Caches that fill once would otherwise look like growth.

2. **Capture the baseline.** On Android, `heaptrail android-capture --package com.example.myapp --out dumps --foreground`. On a JVM, `jmap -dump:live,format=b,file=before.hprof <pid>`. Name the file `before.hprof`.

3. **Do the action several times.** Open and close the screen five times, or run the job ten times. Do not do it once. A leak per iteration scales with the number of iterations, and a one-time cost does not. That difference is your clue.

4. **Capture again** as `after.hprof`, in the same way.

5. **Diff the two.** Look at both sort orders: counts for churn, bytes for payloads.

    ```bash
    heaptrail --diff-from before.hprof --diff-to after.hprof --top 10
    ```

    <!-- output: diff-count.txt from="Class deltas" -->
    ```text
    Class deltas (sorted, top 10 shown):
            Δcount       Δbytes   count(a→b)   bytes(a→b)  class
            +32284     +1033088    621→32905 19.41KiB→1.00MiB  java.util.TreeMap$TreeMapEntry
            +31615      +758760    657→32272 15.40KiB→756.38KiB  com.google.gson.reflect.TypeToken
            +17537      +841776    547→18084 25.64KiB→847.69KiB  com.nexio.tv.domain.model.ProviderIds
             +4349      +139168  13508→17857 422.12KiB→558.03KiB  java.util.LinkedHashMap$LinkedHashMapEntry
             +3140       +75360       0→3140 0.00bytes→73.59KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationRejectedCandidate
             +2059       +32944    4409→6468 68.89KiB→101.06KiB  java.lang.Integer
             +1571       +50272       2→1573 64.00bytes→49.16KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationFieldTrace
             +1393      +100296       0→1393 0.00bytes→97.95KiB  com.nexio.tv.core.tvdb.TvEpisodeMetadata
              +967       +15472     244→1211 3.81KiB→18.92KiB  kotlin.Pair
              +880       +49280     961→1841 52.55KiB→100.68KiB  java.util.LinkedHashMap
    ```

    ```bash
    heaptrail --diff-from before.hprof --diff-to after.hprof --diff-by bytes --top 10
    ```

    <!-- output: diff-bytes.txt from="Class deltas" -->
    ```text
    Class deltas (sorted, top 10 shown):
            Δcount       Δbytes   count(a→b)   bytes(a→b)  class
           -197372    +25990448 372795→175423 21.59MiB→46.38MiB  char[]
            -46441     +5574248 940474→894033 25.31MiB→30.63MiB  byte[]
            +32284     +1033088    621→32905 19.41KiB→1.00MiB  java.util.TreeMap$TreeMapEntry
            +17537      +841776    547→18084 25.64KiB→847.69KiB  com.nexio.tv.domain.model.ProviderIds
            +31615      +758760    657→32272 15.40KiB→756.38KiB  com.google.gson.reflect.TypeToken
             +4349      +139168  13508→17857 422.12KiB→558.03KiB  java.util.LinkedHashMap$LinkedHashMapEntry
             +1393      +100296       0→1393 0.00bytes→97.95KiB  com.nexio.tv.core.tvdb.TvEpisodeMetadata
              +868       +77792    1440→2308 243.08KiB→319.05KiB  java.util.HashMap$Node[][]
             +3140       +75360       0→3140 0.00bytes→73.59KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationRejectedCandidate
             +1571       +50272       2→1573 64.00bytes→49.16KiB  com.nexio.tv.core.metadata.router.MetadataLocalizationFieldTrace
    ```

    These two sample dumps differ in many classes at once, so they are a poor model of a clean experiment. In a real one, look for the signature of a leak: a delta that is a **multiple of the number of times you
    did the action**. If you opened the screen five times, a class that gained 5, 10 or 15 instances is a candidate. A class that gained one is a cache.

6. **Trace the candidate in the later dump.** Take a class that gained with the iterations and ask who holds it:

    ```bash
    heaptrail -i after.hprof --find-referrers <class> --hops 2 --exclude-soft-weak
    ```

    See [Find referrers](../../holders/find-referrers.md), and [Who holds an activity](../../holders/recipes/who-holds-an-activity.md) if the class is a screen.

## How it works

A diff compares class totals, so it is only as good as the experiment. Settling first removes warm-up. Repeating the action separates "costs a fixed amount once" from "costs more every time". Comparing the
count against the iteration count turns an ambiguous number into a test.

## Variations

- **Three or more dumps.** Capture after one, three and ten iterations and use [`--diff-series`](../diff-series.md). The *monotonic growth candidates* list does the comparison for you.
- **Obfuscated build.** Add `--mapping`, or the names will be `a3.t`. See [Deobfuscate release builds](../../android/deobfuscate-release-builds.md).
- **A diff shrinks.** If a class falls between the dumps, something was freed. Look at the bottom of the table (`--top 3000`) or swap the arguments. See [Snapshot diff](../diff.md#sorting-and-direction).
- **Count is flat but bytes grow.** Something got bigger, not more numerous: a cache, a buffer, a list. Sort by bytes and preview the large arrays with [`--preview-bytes`](../../analyze/preview-bytes.md).

## Related

- [Snapshot diff](../diff.md) explains every column.
- [Diff a series](../diff-series.md) for three or more dumps.
- [Playback growth](playback-growth.md) is the same idea for media apps.
