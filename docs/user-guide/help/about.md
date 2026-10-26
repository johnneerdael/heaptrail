# About HeapTrail

## The project

HeapTrail is a free, open-source command-line analyzer for JVM and Android heap dumps. It is licensed under the [Apache License 2.0](https://github.com/johnneerdael/heaptrail/blob/master/LICENSE).

| | |
|---|---|
| Source | [github.com/johnneerdael/heaptrail](https://github.com/johnneerdael/heaptrail) |
| Releases and binaries | [GitHub releases](https://github.com/johnneerdael/heaptrail/releases) |
| Crate | [crates.io/crates/heaptrail](https://crates.io/crates/heaptrail) |
| Issues | [GitHub issues](https://github.com/johnneerdael/heaptrail/issues) |
| Authors | John Neerdael, and Arnaud Gourlay for the original parser |

## Where it comes from

HeapTrail is a fork of [hprof-slurp](https://github.com/agourlay/hprof-slurp) by Arnaud Gourlay. hprof-slurp contributes the streaming parser, which reads a dump in one pass and produces the summary. HeapTrail keeps that parser and adds the
investigation modes on top: referrers, paths to a GC root, snapshot diff and series, allocation sites, content previews, retained size, leak suspects, bitmaps, mapping support and Android capture. Release 0.7.0 was the rename. See
[What's new](../getting-started/whats-new.md).

The design of the parser is described in [Arnaud Gourlay's blog series](https://agourlay.github.io/tags/hprof-slurp/). The HPROF format is documented in the
[OpenJDK heap dumper source](https://hg.openjdk.java.net/jdk/jdk/file/ee1d592a9f53/src/hotspot/share/services/heapDumper.cpp#l62).

Other HPROF parsers were useful while researching the format:

- [monoid/hprof_dump_parser](https://github.com/monoid/hprof_dump_parser)
- [eaftan/hprof-parser](https://github.com/eaftan/hprof-parser)

HeapTrail is an independent project. It is not affiliated with Eclipse MAT, VisualVM, LeakCanary, Android Studio or Perfetto, which this guide names for comparison.

## What it is built with

HeapTrail is written in Rust. It uses `nom` for parsing, `clap` for the command line, `crossbeam-channel` for its reader, parser and recorder threads, `serde_json` for JSON, `globset` for class patterns, and
`indicatif` for the progress bar.

## Brand and typefaces

The HeapTrail name, mark and colours come from the HeapTrail brand kit. This guide is set in [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) for headings, [Inter](https://rsms.me/inter/) for text and [IBM Plex Mono](https://www.ibm.com/plex/) for commands and output. The site serves them itself, under the SIL Open Font License, and the licence notices are published with them: [Space Grotesk](../assets/fonts/SpaceGrotesk-OFL.txt), [Inter](../assets/fonts/Inter-OFL.txt) and [IBM Plex Mono](../assets/fonts/IBMPlexMono-OFL.txt).

## Test files

The repository ships two small JVM dumps in `test-heap-dumps/`, used in the tests and in [Follow along](../getting-started/follow-along.md):

- `hprof-64.bin` is from the [NetBeans profiler tests](https://github.com/apache/netbeans/tree/master/profiler/lib.profiler/test/unit/src/org/netbeans/lib/profiler/heap).
- `hprof-32.bin` is from the [jdk8u `jhat` tests](https://github.com/frohoff/jdk8u-jdk/tree/master/test/sun/tools/jhat).

The guide's other examples use real Android dumps that are not part of the repository, and a small [JVM demo](../capture/jvm.md#try-it-a-demo-with-a-deliberate-leak) that is.

## Contributing

Issues and pull requests are welcome. Before you open a pull request:

```bash
cargo fmt --all -- --check
cargo test
cargo clippy --workspace --all-targets --all-features -- -D warnings
```

CI runs the same three. The project's rule for a change to any feature is to run it against both reference Android dumps, one in `JAVA PROFILE 1.0.2` and one in `1.0.3`, because they exercise different format variants, and passing on one is not
enough. Those dumps are too large to commit.

### Working on this guide

The guide is built with [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) theme. Its sources are in `docs/user-guide/`, and the configuration is `mkdocs.yml`.

```bash
python3 -m venv .venv
.venv/bin/pip install -r docs/site-requirements.txt
.venv/bin/mkdocs serve          # live preview at http://127.0.0.1:8000
.venv/bin/mkdocs build --strict # what CI runs; must pass
python3 scripts/docs-check.py   # checks the pages against the tool
```

Every block of command output in the guide is generated from a real run, so it cannot drift from what HeapTrail prints:

1. `docs/user-guide/_meta/captures.txt` lists the commands. `scripts/docs-workdir.sh <workdir>` builds a folder where the dumps have the short names the guide uses, `scripts/docs-capture.sh <workdir>` runs the commands in it, and the output lands in `docs/user-guide/_meta/outputs/`.
2. A page marks a block with `<!-- output: name.txt -->`, and `scripts/docs-embed.py` writes the block from the capture.
3. `scripts/docs-check.py` verifies that every quoted line exists in a capture, that every flag is a real flag, that the command shown is the one that produced the output, and that the nav and the files agree.

The captures are committed, so the checks and the build run on a fresh clone. Regenerating them needs the real dumps, which are too large to commit. `docs/user-guide/_meta/outputs/README.md` describes the whole loop, including the stand-in for `adb` that lets `android-capture` run without a device. `docs/user-guide/_meta/style.md` is the style guide: voice, page types and templates. Neither is published.

## Related

- [FAQ](faq.md) answers common questions.
- [What's new](../getting-started/whats-new.md) lists the releases.
- [Limitations](../reference/limitations.md) lists what HeapTrail does not do.
