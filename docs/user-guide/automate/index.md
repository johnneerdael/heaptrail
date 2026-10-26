# Automate

HeapTrail's reports are plain text for people. Every mode can also write the same result as JSON, so a script, a CI job or an agent can read it. This section covers the machine-readable side:
the files HeapTrail writes, how to gate a build on a result, and how to hand the whole investigation to Claude Code.

## Start here

1. [JSON output](json-output.md) shows `--json` and `--json-out`, what each mode writes, and `jq` recipes.
2. [Gate a build on a leak threshold](ci-gates.md) turns a report into a pass or fail.
3. [The Claude Code plugin](claude-code-plugin.md) lets an agent run `heaptrail` for you.

## Your goal, and the page

| Your goal | Page |
|---|---|
| Write a report to a file with a name I choose | [JSON output](json-output.md#choose-the-path) |
| Pull one number out of a report | [JSON output](json-output.md#query-it-with-jq) |
| Fail a build when memory use crosses a line | [Gate a build on a leak threshold](ci-gates.md) |
| Know which exit status means what | [Errors and exit codes](../reference/errors-and-exit-codes.md) |
| Let Claude run the triage | [The Claude Code plugin](claude-code-plugin.md) |
| See every field of every JSON file | [JSON schemas](../reference/json-schemas.md) |

## Why HeapTrail suits automation

- **It is a single binary with no runtime.** A CI job downloads it and runs it. See [Install](../getting-started/install.md).
- **Output is deterministic in shape.** The same command on the same dump prints the same fields. Row order among equal counts can vary, so gate on values, not on positions.
- **Exit status says what happened.** `0` for success, `1` for a HeapTrail error, `2` for a bad command line, `101` for a panic.
- **JSON paths are yours to choose,** with `--json-out`.

## Related

- [Command line reference](../reference/command-line.md) lists every flag.
- [Capture](../capture/index.md) for producing the dumps a job analyzes.
- [Handle dumps safely](../capture/handle-dumps-safely.md) before you upload a dump as a build artifact.
