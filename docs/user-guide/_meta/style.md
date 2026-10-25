# heaptrail user guide: style guide

For anyone who writes or edits the guide. This file is not published (`exclude_docs` in `mkdocs.yml`).

## Who the guide is for

Someone with a heap dump and a question: "what is using the memory?", "what is holding this?", "what grew between these two?". They know their language and their app. They may never have read a heap dump. Write for that person, and assume nothing about the dominator tree.

The guide does three jobs, and each page does one of them:

| Page type | Job | Where | Shape |
|---|---|---|---|
| Tutorial | Get a first result, in order | `getting-started/` | Numbered steps, real output after each, ends with **What you learned**. |
| How-to | Do one task with one feature | `capture/`, `analyze/`, `holders/`, `compare/`, `android/`, `automate/` | One command up front, then **Read the result**, variations, **Related**. |
| Recipe | Solve a named problem from end to end | `*/recipes/` | The `recipe-meta` box, **The problem**, **The solution**, **How it works**, **Variations**, **Related**. |
| Concept | Explain an idea, with no commands to run | `concepts/` | A definition first, a diagram where it earns its place, **Related**. |
| Reference | Be complete and exact | `reference/` | Tables. No story. Each row says what to do when it matters. |

If a page tries to be two of these, split it.

## Voice

- Plain, direct, second person: "you", "run", "check". Short sentences. One idea per paragraph.
- Say what happens, then why. Lead with the result, not the history.
- Name things as heaptrail prints them: `ref count`, `retained`, `orphan`. Bold a term once, where it is defined. Link to the glossary after that, not a second definition.
- Be exact about limits. If a flag does nothing, or a number is only measured on one machine, say so on the page. Do not soften it and do not hide it in a footnote. `reference/limitations.md` is where each known quirk lives, and the page that meets the quirk links there.
- Do not sell. No "powerful", "seamless", "blazing", "robust", "easy", "simply", "just", "leverage", "utilize". `scripts/docs-check.py` warns on these.
- Do not compare heaptrail with another tool to win. Say what it is not (see `reference/limitations.md`) and when to use Eclipse MAT instead.
- No emoji in prose. No exclamation marks.
- Spell out abbreviations once in `_snippets/abbreviations.md` and let the tooltip do the work. Add an entry there instead of explaining in the text.

## Numbers and claims

- Every number in prose comes from a capture in `_meta/outputs/` or from a measurement written down on `reference/performance.md`. Do not round a figure up, and do not quote one from memory.
- Timings are for the machine that measured them (a Mac, dumps up to 224 MiB). Say "on a laptop" or give the figure, never "fast".
- If a result differs between runs (tie order, timing lines), do not quote the part that varies.

## Examples

- **Real output only.** Output blocks are written by `scripts/docs-embed.py` from `_meta/outputs/`, so they cannot drift. Never paste output by hand. See `_meta/outputs/README.md`.
- Name the dumps as the guide does: `heap.hprof` (the working example), `heap-b.hprof` (a second dump, where a command was run on it), `before.hprof` and `after.hprof` (diffs), `launch.hprof`, `play.hprof` and `soak.hprof` (series), `jvm.hprof` (the small JVM fixture), `demo.hprof` (the JVM demo).
- The app package in prose is `com.example.myapp`. Output from real dumps keeps the real class names, because changing them would make it untrue.
- Use a `bash` fence for a command you want copied, a `text` fence for output, and a `console` fence with the `cmd` option for a session that shows both.
- Show a command before its output, and name the thing to look at after it. Do not paste output and leave the reader to find the point.
- Keep a block short enough to read. Use `from=`, `until=`, `through=` or `head=` on the embed marker, and `...` on its own line for a deliberate gap.

## Page layout

- One `#` title per page, in sentence case, matching the nav label. Sections are `##`. Go to `###` only when a section has real parts.
- Open with what the feature does and when to use it, in two or three sentences. Put the command next.
- End with **Related** (links), **Next steps** (a path through the guide) or **What you learned** (tutorials). The checker warns when a page has none.
- Link with relative paths to the `.md` file, and to an anchor when the point is in a section. `mkdocs build --strict` fails on a broken link or anchor.
- Tables for facts that have the same shape. Lists for steps and for parts. Prose for reasoning.
- Admonitions are rare, and never two in a row. `!!! note` is for something that surprises, `!!! tip` for a shortcut, `!!! warning` for something that costs time, and `!!! danger` for something that gives a wrong answer or loses data.
  Use `??? example` (collapsed) for a long block the reader may not need, such as a full transcript or the whole `--help` text.

## Diagrams

Diagrams are inline SVG in `_snippets/`, included with `--8<--`. They take their colors from the page (classes in `stylesheets/heaptrail.css`), so they work in light and dark. Draw one only where a picture explains the mechanism better than text: retained size and the path to a root are the two so far. Give each an accessible `<title>` and `<desc>`, keep `max-width` near 30 rem for a vertical one, and test at 390 px wide.

## Brand

| Token | Value | Use |
|---|---|---|
| Ink | `#0E1A2B` | Header, hero terminal, text on teal |
| Teal | `#19C3A1` | Accents, rules, primary buttons (with the gradient) |
| Amber | `#FFB020` | The one thing to look at: a highlight, a target node |
| Deep teal | `#0A7C69` | Links on light backgrounds |

The mark is `assets/brand/mark.svg`: three stacked bars (a heap) and a trail of dots to the one object that matters. Do not recolor it.

## Before you commit

```bash
python3 scripts/docs-embed.py --check   # no output block is stale
python3 scripts/docs-check.py           # quotes, flags, commands, nav, voice
.venv/bin/mkdocs build --strict         # links, anchors, nav
```

All three must pass. When a change touches a feature, run it against both reference dumps (`JAVA_PROFILE_1.0.2.hprof` and `JAVA_PROFILE_1.0.3.hprof`) before you describe it.
