---
hide:
  - navigation
  - toc
---

# heaptrail user guide { .md-visually-hidden }

<div class="ht-hero" markdown>

<div markdown>

![](assets/brand/mark.svg){ .ht-hero__mark }

## Find what is holding your memory

heaptrail reads JVM and Android heap dumps from the command line. It ranks what
takes the space, traces what keeps an object alive, and compares snapshots. Most
modes stream the file instead of loading it, so a 224 MiB Android dump takes about
a fifth of a second on a laptop. Output is plain text, with JSON for scripts and CI.

[Start your first triage](getting-started/first-triage.md){ .md-button .md-button--primary }
[Install heaptrail](getting-started/install.md){ .md-button }

</div>

<div class="ht-terminal">
<div class="ht-terminal__bar"><i></i><i></i><i></i><b>heaptrail</b></div>
<pre><code><span class="p">$</span> heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 1

<span class="hl">Suspect 1 — 27.98MiB (26.2 % of heap)</span>
  dominator: java.util.ArrayList (object_id=361762400)
  accumulating: 262517 instances of <span class="hl">com.nexio.tv.domain.model.MetaPreview</span>, total 26.04MiB
  path to GC root:

  Path from object_id=361762400 (depth 12 step(s)):
    start  ── id=361762400
    <span class="d">...</span>
    hop 3 ── id=361760584  (via <span class="hl">com.nexio.tv.ui.screens.home.HomeViewModel.fullCatalogRows</span>)
    <span class="d">...</span>
    hop 6 ── id=327606088  (via androidx.lifecycle.ViewModelStore.map)
    <span class="d">...</span>
    hop 9 ── id=327605632  (via androidx.navigation.NavControllerViewModel.viewModelStores)</code></pre>
</div>

</div>

!!! note "A command-line tool"
    heaptrail has no window to click through. Each investigation is one command that prints a
    report you can read in a terminal, paste into a ticket, or parse with `jq`. For
    interactive graph browsing, [use Eclipse MAT after heaptrail has narrowed the question](help/faq.md#when-should-i-use-eclipse-mat-instead).

## What do you want to do?

<div class="grid cards" markdown>

-   :material-cellphone-arrow-down:{ .lg .middle } **Get a heap dump**

    ---

    Capture from an Android device with one command, or from a running JVM with
    `jmap`. Check that the file is whole before you analyze it.

    [:octicons-arrow-right-24: Capture](capture/index.md)

    Popular: [android-capture](capture/android-capture.md) · [JVM dumps](capture/jvm.md)

-   :material-chart-bar:{ .lg .middle } **See what is using memory**

    ---

    Rank classes by size, find the objects that keep the most alive, and let
    heaptrail name the likely leak suspects.

    [:octicons-arrow-right-24: Analyze](analyze/index.md)

    Popular: [Summary](analyze/summary.md) · [Leak suspects](analyze/leak-suspects.md)

-   :material-source-branch:{ .lg .middle } **Find what holds an object**

    ---

    Follow a class or a single object back to the field, array or static that keeps
    it alive, all the way to a GC root.

    [:octicons-arrow-right-24: Trace holders](holders/index.md)

    Popular: [Find referrers](holders/find-referrers.md) · [Paths to a GC root](holders/paths-to-root.md)

-   :material-chart-timeline-variant:{ .lg .middle } **Check whether memory grows**

    ---

    Compare two snapshots, or a whole timeline of three or more, and pick out the
    classes that only ever get bigger.

    [:octicons-arrow-right-24: Compare](compare/index.md)

    Popular: [Snapshot diff](compare/diff.md) · [Diff a series](compare/diff-series.md)

-   :material-android:{ .lg .middle } **Read an Android release build**

    ---

    Turn names like `a3.t` back into real class names with your R8 mapping file,
    chosen by hand or matched to the installed app.

    [:octicons-arrow-right-24: Android](android/index.md)

    Popular: [Deobfuscate](android/deobfuscate-release-builds.md) · [Auto-mapping](android/auto-mapping.md)

-   :material-text-search:{ .lg .middle } **Look inside big arrays**

    ---

    A 5 MiB `char[]` is not a diagnosis. Preview what it holds: JSON, XML, an
    image, or a buffer full of zeros.

    [:octicons-arrow-right-24: Content previews](analyze/preview-bytes.md)

    Popular: [Identify a giant array](analyze/recipes/identify-a-giant-array.md) · [Find duplicate payloads](analyze/recipes/find-duplicate-payloads.md)

-   :material-robot-outline:{ .lg .middle } **Script it or hand it to an agent**

    ---

    Write stable JSON files, gate a build on a leak threshold, or let Claude Code
    run the whole triage for you.

    [:octicons-arrow-right-24: Automate](automate/index.md)

    Popular: [JSON output](automate/json-output.md) · [CI gates](automate/ci-gates.md)

-   :material-lightbulb-on-outline:{ .lg .middle } **Understand the numbers**

    ---

    Shallow versus retained size, GC roots, weak references and object ids,
    explained once and linked from everywhere else.

    [:octicons-arrow-right-24: Concepts](concepts/index.md)

    Popular: [Shallow and retained size](concepts/shallow-and-retained.md) · [GC roots and paths](concepts/gc-roots-and-paths.md)

-   :material-book-open-variant:{ .lg .middle } **Look something up**

    ---

    Every flag, which flags combine, the JSON fields, error messages and exit
    codes, and how fast each mode runs.

    [:octicons-arrow-right-24: Reference](reference/index.md)

    Popular: [Command line](reference/command-line.md) · [Errors and exit codes](reference/errors-and-exit-codes.md)

</div>

## New here?

1. [Install heaptrail](getting-started/install.md) with `cargo install heaptrail` or a
   prebuilt binary.
2. Work through [Your first triage](getting-started/first-triage.md), a real investigation
   from the first summary to the field that causes the leak.
3. Keep [Choose the right mode](getting-started/choose-a-mode.md) open: it maps the
   question you have to the command that answers it.

No heap dump of your own yet? [Follow along with the files in the repository](getting-started/follow-along.md).

## When to use heaptrail, and when not to

| Reach for heaptrail when… | Reach for Eclipse MAT or VisualVM when… |
|---|---|
| You want a first answer in seconds, from a terminal or a script. | You want to click through references and pivot as you go. |
| The dump is large, or the machine is a CI runner or a remote box. | You need OQL, or an HTML report for people who will not open a terminal. |
| An agent or a pipeline should read the result. | You are doing an open-ended, exploratory session. |

The two work well together. [Use heaptrail to narrow the question, then open the dump
in MAT](help/faq.md#when-should-i-use-eclipse-mat-instead) if you need a graph session.

Use the search box (press ++s++ or ++slash++) to find a flag, an error message or a class name.

## Get help and follow changes

Read what changed in each release in [What's new](getting-started/whats-new.md), or on the
[GitHub releases page](https://github.com/johnneerdael/heaptrail/releases). If a step in this
guide differs from your build, [report it on GitHub](https://github.com/johnneerdael/heaptrail/issues)
with your heaptrail version (`heaptrail --version`), your operating system and the command you ran.
