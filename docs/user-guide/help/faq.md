# Frequently asked questions

## What is HeapTrail?

A command-line analyzer for JVM and Android heap dumps. It ranks what takes the space, traces what holds an object, and compares snapshots, and it prints the result as text or JSON. It began as a fork of
[hprof-slurp](https://github.com/agourlay/hprof-slurp). See [About](about.md).

## When should I use Eclipse MAT instead? { #when-should-i-use-eclipse-mat-instead }

Use HeapTrail first, and MAT when the question needs a graph you can click through.

| Reach for HeapTrail when… | Reach for MAT or VisualVM when… |
|---|---|
| You want an answer in seconds from a terminal, a script or a CI job. | You want to click through references and pivot as you go. |
| The dump is large, or you are on a CI runner or a remote box. | You need OQL for an ad-hoc query. |
| An agent or a pipeline should read the result. | You need an HTML report for people who will not open a terminal. |
| The question is narrow and repeatable: who holds X, what changed, what dominates. | The question is open-ended, and you will explore. |

The two work together: HeapTrail is the cheap, scriptable first pass, and MAT is the right tool when the question turns into an interactive session. For live captures with allocation tracking, Android Studio's profiler
is the better fit, and Perfetto is for dumps correlated with a system trace.

## Do I need Java installed?

No. HeapTrail is a single binary. You need a JDK only to take a JVM dump (`jmap`, `jcmd`), and the Android platform tools to capture from a device.

## Does HeapTrail change my dump?

No. It only reads the file. It writes JSON files only when you ask for them.

## Can it analyze a running process?

No. It analyzes a dump file. Take the dump with [`android-capture`](../capture/android-capture.md), `jmap` or `jcmd`. See [Capture](../capture/index.md).

## Is a suspect a leak?

Not necessarily. A suspect is an object that keeps a lot of memory alive. A cache that is meant to hold 30 MiB is a suspect, and not a bug. A leak is an object you no longer need that is still reachable. HeapTrail finds the
retention and the chain that explains it. You decide whether it is intended. See [Leak suspects](../analyze/leak-suspects.md).

## Why does my path say `orphan`?

Because the path walker follows instance fields and array slots, and not class static fields. A cache held by a static field ends in `orphan`. Ask `--find-referrers id:<id>` about the last id: it includes statics. See
[Paths to a GC root](../holders/paths-to-root.md#orphans).

## Why do I see `java.lang.Object[][]`?

On Android dumps, HeapTrail's text tables add a pair of brackets to object array names. `java.lang.Object[][]` is an `Object[]`. JSON uses the single-bracket name. See [Summary](../analyze/summary.md#3-the-class-table).

## Why are class names like `a3.t`?

The build is obfuscated by R8. Add `--mapping <mapping.txt>`, or `--auto-mapping`. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

## Why do my numbers differ from Eclipse MAT's?

Several reasons, in order of how often they matter.

1. MAT excludes weak, soft and phantom references in its leak-hunting view. Add `--exclude-soft-weak`.
2. MAT also has a separate exclusion for finalizer references, which HeapTrail does not offer.
3. HeapTrail's class *retained* column sums each instance's retained size, so nested instances count more than once. See [Shallow and retained size](../concepts/shallow-and-retained.md).
4. The two tools size objects with their own code, so shallow sizes differ slightly.

## How big a dump can it handle?

It depends on the mode. On a 224 MiB Android dump, the summary peaks at about 0.5 GiB, referrers and paths at 100 to 160 MiB, and retained size and leak suspects at 1.4 to 1.7 GiB, about 5 to 7.5 times the file size. Larger dumps were not measured.
See [Performance](../reference/performance.md).

## Does it work on Windows, macOS and Linux?

There are prebuilt binaries for macOS (Apple silicon and Intel), Linux (x86-64 and ARM64) and Windows (x86-64 and ARM64). The measurements in this guide are from macOS. See [Download and install](../getting-started/install.md).

## Can I use it in CI?

Yes. Use `--json --json-out <path>` and gate on the result with `jq`. See [Gate a build on a leak threshold](../automate/ci-gates.md).

## Can an agent use it?

Yes. The [Claude Code plugin](../automate/claude-code-plugin.md) teaches Claude the workflow, and any agent can run the commands and read the JSON.

## Can I get a dump from a production Android device?

Only for a debuggable app, an app marked `profileable` for the shell (Android 10 and later), or on a rooted or userdebug device. Otherwise `am dumpheap` fails with a security error. See
[What is different about Android dumps](../android/android-heaps.md#getting-a-dump).

## Is the output format stable?

The text is for people and can change between versions. The JSON has no schema version, so read fields by name and ignore ones you do not know. See [JSON output](../automate/json-output.md).

## What license is it under?

Apache-2.0. See [About](about.md).

## How do I report a bug?

Open an issue on [GitHub](https://github.com/johnneerdael/heaptrail/issues) with the output of `heaptrail --version`, your operating system, the command you ran, and the error. Do not attach a dump unless you have
checked it for secrets. See [Handle dumps safely](../capture/handle-dumps-safely.md).

## Related

- [Troubleshooting](troubleshooting.md) starts from a symptom.
- [Limitations](../reference/limitations.md) lists what HeapTrail does not do.
- [Choose the right mode](../getting-started/choose-a-mode.md).
