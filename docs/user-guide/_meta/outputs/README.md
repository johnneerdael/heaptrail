# Captured output

Every block of command output in the user guide is quoted from a file in this folder. Nothing is typed by hand, so a page cannot show output that heaptrail did not print.

Each `<name>.txt` is one real run:

```text
$ heaptrail -i heap.hprof -t 5      <- the command, as written in captures.txt
# exit 0                            <- its exit status
Found a total of ...                <- everything it printed (stdout and stderr)
```

These files are committed. `scripts/docs-check.py` reads them, so CI can verify the guide without the large dumps that produced them.

## The loop

```bash
cargo build --release                                  # the binary the guide describes
scripts/docs-workdir.sh /tmp/ht-work                   # short dump names -> the real files
scripts/docs-capture.sh /tmp/ht-work                   # run every command in captures.txt
python3 scripts/docs-embed.py                          # rewrite the output blocks in the pages
python3 scripts/docs-check.py                          # quotes, flags, commands, nav, voice
.venv/bin/mkdocs build --strict                        # links, anchors
```

`scripts/docs-capture.sh <workdir> <filter>` runs only the captures whose name contains the filter, which is what you want while writing one page.

### `captures.txt`

One line per capture, `name|max-lines|command`:

```text
first-summary|0|heaptrail -i heap.hprof -t 5
```

- `name` becomes `outputs/<name>.txt`.
- `max-lines` keeps the first N lines of output (`0` keeps all).
- A command that starts with `heaptrail` runs the binary you built. Any other command (`jq`, `sed`) runs as written, so a pipeline can quote its own result.
- Comment lines start with `#`.

### In a page

````markdown
<!-- output: first-summary.txt from="Found a total" until="Top 5 largest" -->
```text
...written by scripts/docs-embed.py...
```
````

The marker is followed by a fenced block, and `docs-embed.py` rewrites that block. The options are listed at the top of `scripts/docs-embed.py`: `from`, `until`, `through`, `head`, `keep` (do not rewrite, only verify; for blocks with `...` elisions) and `cmd` (start the block with the command, for a `console` fence).

`docs-check.py` then checks that every line in the block exists in the capture, that every `--flag` is real, and that the command that produced the capture is shown in a `bash`, `sh` or `console` block on the same page.

### Capture names with a suffix

| Suffix | Effect |
|---|---|
| `-stall` | The fake device never finishes writing the dump (a timeout path). |
| `-noproc` | The fake device reports that the app is not running. |
| `-noadb` | Runs with no `adb` on the `PATH` at all. |

## What the work directory holds

`scripts/docs-workdir.sh` links these names to real files. Only the last two rows are small enough to commit.

| Name in the guide | File |
|---|---|
| `heap.hprof`, `before.hprof` | `JAVA_PROFILE_1.0.2.hprof` in the repository root |
| `heap-b.hprof`, `after.hprof` | `JAVA_PROFILE_1.0.3.hprof` in the repository root |
| `launch.hprof`, `play.hprof`, `soak.hprof`, `meminfo.txt` | The three-snapshot series in `artifacts/` |
| `jvm.hprof`, `test-heap-dumps/` | `test-heap-dumps/` in the repository |
| `demo.hprof` | Unpacked from `assets/downloads/shop-demo.hprof.gz` |

The large dumps are real app dumps and are not committed (`*.hprof` is ignored). A fresh clone can run the checker and the site build, and cannot regenerate these captures.

## The fake device

`android-capture` and `--auto-mapping` talk to `adb`. So that they can run without a phone, `docs-capture.sh` puts `_meta/fixtures/fake-adb/adb` first on the `PATH`. It answers only the commands heaptrail sends (`pidof`, `monkey`, `dumpsys window`, `dumpsys package`, `am dumpheap`, `ls`, `rm`, `pull`, and the clean-up of old dumps) and copies a real dump when asked to "write" one.

What this means for the pages:

- The text heaptrail prints is genuine heaptrail output. It is the device's replies that are simulated: the process id, the focused activity, the app's version and the transfer speed.
- The package in those captures is `com.example.myapp`, and the mapping is the demo project in `_meta/fixtures/myapp/`. The class names in that mapping are invented.

## The JVM demo dump

`assets/downloads/shop-demo.hprof.gz` is a heap dump of the small program in `_meta/fixtures/jvm-demo/`, which keeps a deliberate leak. The guide quotes its output, including **object ids**, and an object id changes on every run of the program.

The dump is therefore committed, and it must not be rebuilt by accident. `scripts/docs-make-jvm-dump.sh` rebuilds it, and if you do, every id that comes from the demo has to be updated, in `captures.txt` and on the pages (the six `jvm-summary` to `jvm-paths` captures), then the loop above run again.

## Output that varies

A few lines differ between runs and are not worth pinning:

- The `File successfully processed in ...` timing line, which is never quoted.
- The order of rows with equal counts or sizes. Do not quote a block where the order of such rows is the point.

If a capture changes after a re-run and you did not change the tool, read the diff before you accept it. A changed number on a page is either a real change in heaptrail or a mistake in the page.
