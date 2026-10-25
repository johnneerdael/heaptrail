# Reference

Complete, exact and for looking things up. Every table here is checked against the code: flags against `--help`, errors against real runs, output against captures.

## Pages

| You need | Page |
|---|---|
| Every flag, its default and its range | [Command line](command-line.md) |
| Which flags work with which mode | [Mode compatibility](mode-compatibility.md) |
| Every field of every JSON file | [JSON schemas](json-schemas.md) |
| The meaning of a GC root kind | [GC root kinds](gc-root-kinds.md) |
| Which dump formats heaptrail reads | [HPROF formats](hprof-formats.md) |
| An error message, and what to do | [Errors and exit codes](errors-and-exit-codes.md) |
| How long a mode takes and how much memory it needs | [Performance](performance.md) |
| What heaptrail cannot do | [Limitations](limitations.md) |
| A term in one line | [Glossary](glossary.md) |

## The command in one glance

```text
heaptrail [OPTIONS]                       analyze a dump (one mode per command)
heaptrail android-capture [OPTIONS]       capture a dump over adb
```

With no mode flag, `heaptrail -i <dump>` prints the [summary](../analyze/summary.md). Pick at most one of the modes: `--find-referrers` (or `--target-glob`), `--paths-from-id`, `--diff-from` with `--diff-to`, `--diff-series`,
`--allocation-sites`, `--leak-suspects` and `--bitmaps`.

## Related

- [Choose the right mode](../getting-started/choose-a-mode.md) maps a question to a command.
- [Concepts](../concepts/index.md) explains the ideas behind the numbers.
- [Help](../help/faq.md) for questions and troubleshooting.
