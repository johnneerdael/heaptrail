# The Claude Code plugin

The repository doubles as a [Claude Code](https://claude.com/claude-code) plugin marketplace. Installing the plugin gives Claude a skill, `analysing-heap-dumps`, that switches on when you talk about heap dumps. Claude then runs
HeapTrail for you, installs it if it is missing, and works through the same loop you would: summary, suspects, referrers, paths, diff.

## Install it

In Claude Code, add the marketplace once, then install the plugin:

```text
/plugin marketplace add johnneerdael/heaptrail
/plugin install analysing-heap-dumps@analysing-heap-dumps
```

The plugin name and the marketplace name are both `analysing-heap-dumps`, which is why the identifier reads `analysing-heap-dumps@analysing-heap-dumps`. Check that it is installed:

```text
/plugin
```

`analysing-heap-dumps` should be in the list of installed plugins.

## Use it

Describe the problem in plain words:

```text
I have a 235 MB Android hprof at /tmp/heap.hprof. The app is using way more
memory than expected. What's going on?
```

The skill is triggered by things like a `.hprof` file in the conversation, `am dumpheap`, `jmap -dump`, "memory leak", "retained size", "OutOfMemoryError" and "what holds this object". Claude checks that HeapTrail is on your `PATH`, runs
`cargo install heaptrail` if it is not, and then follows the skill's workflow.

## What the skill tells Claude to do

The skill is a written set of defaults, so the agent does what an experienced user would. In short:

- **Restore names first.** For an Android release dump, use `--mapping` or `--auto-mapping` on every command, and say so when no mapping is available instead of analyzing obfuscated names silently.
- **Preview arrays on the first pass.** Use `--preview-bytes 200`, so a big `char[]` identifies itself.
- **Start with suspects for a vague Android leak:** `--leak-suspects --exclude-soft-weak --preview-bytes 200 --top 5`.
- **Use a series for growth.** Three or more ordered dumps and `--diff-series`, not repeated pair diffs, with `dumpsys meminfo` beside them for native memory.
- **Group noisy holders** with `--target-glob` and `--group-holders` for media and cache classes.
- **Capture with the helper.** Prefer `android-capture` over hand-typed `adb`, and treat a 0-byte dump as invalid.
- **Write machine-readable files.** `--json --json-out` to a path, not a timestamped sidecar.
- **Redirect long output.** `-l` goes to a file.
- **Do not reach for Eclipse MAT first,** and do not run `hprof-conv` on a modern Android dump.

The full text is in
[`plugins/analysing-heap-dumps/skills/analysing-heap-dumps/SKILL.md`](https://github.com/johnneerdael/heaptrail/blob/master/plugins/analysing-heap-dumps/skills/analysing-heap-dumps/SKILL.md). You can read it, fork it, or paste it into
another agent's instructions.

## Update and uninstall

```text
/plugin marketplace update johnneerdael/heaptrail
/plugin update analysing-heap-dumps@analysing-heap-dumps
```

```text
/plugin uninstall analysing-heap-dumps@analysing-heap-dumps
/plugin marketplace remove johnneerdael/heaptrail
```

## Working with an agent

Whichever agent runs `heaptrail`, a few habits make the result more useful:

- **Give it the dump path and the question.** "What holds `com.example.Foo`?" and "Is memory growing between these three dumps?" are answerable. "Fix my leak" is not.
- **Give it the mapping.** Without it, an agent reasons about `a3.t`.
- **Keep dumps private.** An agent that runs `-l` or `--preview-bytes` reads the contents of memory. See [Handle dumps safely](../capture/handle-dumps-safely.md).
- **Ask for evidence.** The JSON files and the transcript from `android-capture` let you check a conclusion.
- **Treat a suspect as a lead.** A report names a retention. Whether it is a bug is your decision.

## Related

- [Choose the right mode](../getting-started/choose-a-mode.md) is the same map the skill follows.
- [JSON output](json-output.md) for the files an agent should write.
- [Install HeapTrail](../getting-started/install.md) if you want it on your `PATH` without the plugin.
