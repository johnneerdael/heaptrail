# Get started

heaptrail answers memory questions about a heap dump: what is big, what keeps it
alive, and what grew. You give it an `.hprof` file and one flag, and it prints a
report. This section gets it installed and walks you through a first investigation.

## Start here

1. [Install heaptrail](install.md). One `cargo install` or a prebuilt binary.
2. [Your first triage](first-triage.md). A real investigation, from the first
   summary to the field that causes the leak. About 15 minutes.
3. [Choose the right mode](choose-a-mode.md). Pick the command that answers the
   question you have.

No heap dump yet? [Follow along with the files in the repository](follow-along.md), or
[capture one](../capture/index.md) from a device or a JVM.

## The loop

Most investigations go through the same three steps. Each step has its own flag and
its own page.

| Step | Question | Command shape | Page |
|---|---|---|---|
| 1. See | What takes the space? | `heaptrail -i heap.hprof` | [Summary](../analyze/summary.md) |
| 2. Rank | What keeps the most alive, and which objects look like a leak? | `heaptrail -i heap.hprof --leak-suspects` | [Leak suspects](../analyze/leak-suspects.md) |
| 3. Trace | What holds this class or object? | `heaptrail -i heap.hprof --find-referrers <class>` | [Find referrers](../holders/find-referrers.md) |

When you have two or more dumps from the same process, [compare them](../compare/index.md)
to see what grew.

## All pages in this section

| Your goal | Page |
|---|---|
| Install or upgrade heaptrail | [Download and install](install.md) |
| Run a complete investigation once, end to end | [Your first triage](first-triage.md) |
| Try heaptrail with the small dumps in the repository | [Follow along with the bundled files](follow-along.md) |
| Decide which flag to use | [Choose the right mode](choose-a-mode.md) |
| See what changed in a release | [What's new](whats-new.md) |

## About the examples

Output in this guide is real: it was captured by running heaptrail, and the pages quote it verbatim. The files are named the same way everywhere.

| File | What it is |
|---|---|
| `heap.hprof` | A 224 MiB heap dump of an Android TV app (`JAVA PROFILE 1.0.2`, converted from an Android dump). The main example. |
| `heap-b.hprof` | A second dump of the same app: 186 MiB, raw `JAVA PROFILE 1.0.3` from `am dumpheap`. |
| `before.hprof`, `after.hprof` | The same two files, in the order they were captured, for the diff pages. |
| `launch.hprof`, `play.hprof`, `soak.hprof` | A series of three ~80 MiB dumps from an obfuscated release build, for the series pages. |
| `demo.hprof` | The JVM demo with a deliberate leak. It is in the repository, so you can run every command on it. |
| `test-heap-dumps/*.bin` | The two small JVM dumps in the repository. |

Your numbers will differ. Only the small JVM dumps ship with the repository, so on any other page treat the output as a picture of what your own dump will print.
The `android-capture` examples come from heaptrail's own code running against a stand-in for `adb`, so they show exactly what it prints without needing a device.

## Related

- [Capture a heap dump](../capture/index.md) if you do not have one yet.
- [Concepts](../concepts/index.md) explains shallow size, retained size and GC roots.
- [Reference](../reference/index.md) lists every flag.
