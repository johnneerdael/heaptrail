<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/johnneerdael/heaptrail/raw/HEAD/docs/assets/brand/heaptrail-readme-dark-1600x480.png">
    <img src="https://github.com/johnneerdael/heaptrail/raw/HEAD/docs/assets/brand/heaptrail-readme-light-1600x480.png" alt="HeapTrail. Find what is holding your memory." width="100%">
  </picture>
</p>

<p align="center">
  <a href="https://github.com/johnneerdael/heaptrail/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/johnneerdael/heaptrail?style=flat-square&color=F5A623&label=release"></a>
  <a href="https://github.com/johnneerdael/heaptrail/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/johnneerdael/heaptrail/ci.yml?branch=master&style=flat-square&label=CI"></a>
  <a href="https://crates.io/crates/heaptrail"><img alt="crates.io" src="https://img.shields.io/crates/v/heaptrail?style=flat-square&color=101820"></a>
  <a href="https://heaptrail.neerdael.nl/"><img alt="User guide" src="https://img.shields.io/badge/user%20guide-online-101820?style=flat-square"></a>
  <img alt="Platforms" src="https://img.shields.io/badge/Linux%20%C2%B7%20macOS%20%C2%B7%20Windows-101820?style=flat-square">
  <a href="LICENSE"><img alt="Apache-2.0 license" src="https://img.shields.io/badge/license-Apache--2.0-101820?style=flat-square"></a>
</p>

HeapTrail is a command-line analyzer for JVM and Android heap dumps. It ranks what takes the space, traces what keeps an object alive, and compares snapshots. Every investigation is one command that prints a report you can read, paste into a ticket, or parse as JSON.

It is a single binary with no runtime dependencies. Most modes stream the dump instead of loading it: a 224 MiB Android dump summarizes in about a fifth of a second on a laptop.

<p align="center">
  <a href="https://github.com/johnneerdael/heaptrail/releases/latest"><b>Download</b></a> &nbsp;·&nbsp;
  <a href="https://heaptrail.neerdael.nl/getting-started/install/"><b>Install</b></a> &nbsp;·&nbsp;
  <a href="https://heaptrail.neerdael.nl/"><b>User guide</b></a> &nbsp;·&nbsp;
  <a href="https://github.com/johnneerdael/heaptrail/issues"><b>Report an issue</b></a>
</p>

The [user guide](https://heaptrail.neerdael.nl/) has tutorials, how-tos, recipes, concepts and the full reference, with real output from real dumps. Its sources are in [`docs/user-guide/`](docs/user-guide/).

## Install

```bash
cargo install heaptrail
```

Or download a prebuilt binary for Linux, macOS or Windows (x86-64 and ARM64) from the [releases page](https://github.com/johnneerdael/heaptrail/releases/latest), and put it on your `PATH`. [Download and install](https://heaptrail.neerdael.nl/getting-started/install/) has the details, including building from source.

## First triage

```bash
# What is in the dump, and which classes take the space?
heaptrail -i heap.hprof

# What is wrong with it? (you do not know where to look yet)
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak

# What holds every instance of a class, looking through the arrays in between?
heaptrail -i heap.hprof --find-referrers com.example.Item --hops 2

# Prove one object is still reachable: the chain to a GC root
heaptrail -i heap.hprof --paths-from-id 1661812752

# What grew between two dumps?
heaptrail --diff-from before.hprof --diff-to after.hprof
```

[Your first triage](https://heaptrail.neerdael.nl/getting-started/first-triage/) walks through these on a real dump and explains each line of output.

## What it does

| You want to know | Use | Guide |
|---|---|---|
| Which classes take the space | the summary, `--preview-bytes`, `-l` | [Analyze](https://heaptrail.neerdael.nl/analyze/) |
| What an object keeps alive | `--retained-size` | [Retained size](https://heaptrail.neerdael.nl/analyze/retained-size/) |
| Where to start looking | `--leak-suspects` | [Leak suspects](https://heaptrail.neerdael.nl/analyze/leak-suspects/) |
| What holds an object, and whether it is reachable | `--find-referrers`, `--target-glob`, `--paths-from-id`, `--merge-paths` | [Trace holders](https://heaptrail.neerdael.nl/holders/) |
| What changed between snapshots | `--diff-from` and `--diff-to`, `--diff-series` | [Compare](https://heaptrail.neerdael.nl/compare/) |
| Real names in a release build | `--mapping`, `--auto-mapping` | [Android](https://heaptrail.neerdael.nl/android/) |
| A dump from a device, with checks | `android-capture` | [Capture](https://heaptrail.neerdael.nl/capture/) |
| Output for scripts and CI | `--json` | [Automate](https://heaptrail.neerdael.nl/automate/) |

Not sure which mode fits? [Choose the right mode](https://heaptrail.neerdael.nl/getting-started/choose-a-mode/) starts from your question.

HeapTrail has no window to click through. For interactive graph browsing, an OQL query language, or HTML reports, use [Eclipse MAT](https://www.eclipse.org/mat/) after HeapTrail has narrowed the question. A retained object is not automatically a leak, and [Limitations](https://heaptrail.neerdael.nl/reference/limitations/) lists what HeapTrail does not do and where a result can mislead.

## Capture a dump

On a JVM, take it with `jmap` or `jcmd`:

```bash
jmap -dump:live,format=b,file=heap.hprof <pid>
```

On Android, `heaptrail android-capture --package <app> --out dumps` takes the dump, checks that it finished, and pulls it. [Capture](https://heaptrail.neerdael.nl/capture/) covers both, a series of dumps, and handling dumps safely.

## Use it from Claude Code

This repository is also a [Claude Code](https://claude.com/claude-code) plugin marketplace. The plugin adds a skill that runs `heaptrail` for you when you mention a heap dump:

```
/plugin marketplace add johnneerdael/heaptrail
/plugin install analysing-heap-dumps@analysing-heap-dumps
```

[The Claude Code plugin](https://heaptrail.neerdael.nl/automate/claude-code-plugin/) explains what it does, and how to update or remove it.

## Formats

`JAVA PROFILE 1.0.1`, `1.0.2` (the JVM default) and `1.0.3` (Android, with its extension tags), with 4-byte and 8-byte identifiers. [HPROF formats](https://heaptrail.neerdael.nl/reference/hprof-formats/) has the detail, and [Performance](https://heaptrail.neerdael.nl/reference/performance/) has measured time and memory for each mode.

## Contributing

Issues and pull requests are welcome. Before you open one:

```bash
cargo fmt --all -- --check
cargo test
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

When a change touches a feature, run it against both reference dumps, `JAVA_PROFILE_1.0.2.hprof` and `JAVA_PROFILE_1.0.3.hprof`, because they exercise different format variants. The user guide is built with MkDocs, and every block of command output in it is generated from a real run. [About](https://heaptrail.neerdael.nl/help/about/#working-on-this-guide) explains how to work on it.

## Credits

HeapTrail is a fork of [agourlay/hprof-slurp](https://github.com/agourlay/hprof-slurp) by Arnaud Gourlay, which contributes the streaming parser. The design of that parser is described in [his blog series](https://agourlay.github.io/tags/hprof-slurp/). The HPROF format is documented in the [OpenJDK heap dumper source](https://hg.openjdk.java.net/jdk/jdk/file/ee1d592a9f53/src/hotspot/share/services/heapDumper.cpp#l62). These parsers were useful while researching it:

- [monoid/hprof_dump_parser](https://github.com/monoid/hprof_dump_parser)
- [eaftan/hprof-parser](https://github.com/eaftan/hprof-parser)

## License

[Apache-2.0](LICENSE).
