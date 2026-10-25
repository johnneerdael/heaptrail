# Command line

```text
heaptrail [OPTIONS] [COMMAND]
```

heaptrail has one default mode, the summary, and selects every other mode with a flag. The only subcommand is `android-capture`. Run `heaptrail --help` for the version of this table that matches your build.

??? example "Full `--help` output of this version"

    <!-- output: help-main.txt cmd -->
    ```console
    $ heaptrail --help
    JVM/Android heap dump (hprof) analyzer

    Usage: heaptrail [OPTIONS] [COMMAND]

    Commands:
      android-capture  Capture and validate an Android heap dump via adb
      help             Print this message or the help of the given subcommand(s)

    Options:
      -i, --inputFile <INPUT_FILE>
              Binary hprof input file. Required for summary, --find-referrers, and --paths-from-id modes. Not used in diff mode (see --diff-from/--diff-to)
      -t, --top <TOP>
              The top N results to display [default: 20]
      -d, --debug
              Debug info
      -l, --listStrings
              List all Strings found (summary mode)
          --json
              Additional JSON output
          --json-out <PATH>
              Write JSON output to this exact path. Requires --json. When omitted, --json keeps the current timestamped/default sidecar behavior
          --native-context <PATH>
              Optional Android dumpsys meminfo text to annotate diff-series reports
          --mapping <PATH>
              R8/ProGuard mapping file used to deobfuscate class and holder field names
          --auto-mapping [<MODE>]
              Discover the mapping file from a local Android Gradle project and an installed app version [possible values: strict, optional]
          --project-root <DIR>
              Android project root for --auto-mapping
          --package <PACKAGE>
              Android package/application id for --auto-mapping
          --serial <SERIAL>
              adb serial/device id for --auto-mapping
          --preview-bytes <N>
              Show first N bytes/chars of primitive arrays in summary, paths, find-referrers id:N, and (with -l) the standalone-array list. Default 0 (off); recommended 200. UTF-8 / UTF-16 BE auto-detect with control-char escaping; falls back to xxd-style hex on binary content. See "Content previews" in the user guide [default: 0]
          --list-arrays-min-bytes <LIST_ARRAYS_MIN_BYTES>
              Minimum total byte size for a standalone primitive array to appear in `-l` output. Effective only when both `-l` and `--preview-bytes` are set. Default 1024 [default: 1024]
          --find-referrers <TARGET>
              Find direct + N-hop referrers of a target. Accepts an FQ class name (e.g. `java.util.ArrayList`) or `id:<u64>` / a bare `<u64>` for a specific object id
          --target-glob <PATTERN>
              Find direct + N-hop referrers of every class matching this glob. Mutually exclusive with `--find-referrers`. Glob syntax: `*` matches within a package level, `**` crosses package levels, `?` matches one character, `[abc]` is a class. See "Target glob" in the user guide
          --hops <HOPS>
              Number of hops for referrer tracing. 1 = direct only, 2 = also through Object[] arrays, 3 = three-link chain [default: 2]
          --include-statics
              Include class statics as candidate referrers
          --group-holders
              Group referrer rows by owner family, holder class, and field label
          --paths-from-id <ID>
              Trace holder chain from this object id toward a GC root
          --max-depth <MAX_DEPTH>
              Maximum chain depth before giving up (paths mode) [default: 12]
          --diff-from <PATH>
              Baseline (older) hprof for diff
          --diff-to <PATH>
              Comparison (newer) hprof for diff
          --diff-series <PATH>...
              Ordered HProf snapshots for series diff. Requires at least 3 files
          --diff-by <DIFF_BY>
              Diff sort key (count = delta instances, bytes = delta shallow size) [default: count] [possible values: count, bytes]
          --allocation-sites
              Show per-class allocation sites with stack traces. Requires the dump to have been captured under allocation tracking (Android: `am profile start <pid>` before `am dumpheap`)
          --retained-size
              Compute and surface retained sizes via Lengauer–Tarjan dominator tree. Annotates summary's class table (re-sorted by retained), `--paths-from-id` hops, and `--find-referrers` holders. Adds ~250 MiB working memory and ~1–3 s wall time on a 200 MiB Android dump. Includes weak/soft/phantom-reference edges (graph-theoretic dominator-tree definition); pair with `--exclude-soft-weak` for MAT-style leak hunting. Default off
          --exclude-soft-weak
              Drop outgoing edges from java.lang.ref.{Soft,Weak,Phantom}Reference subclasses across path walks and the retained-size graph build. MAT's default leak-hunting filter; required on Android dumps where LeakCanary watchers and framework weak-refs would otherwise bury the real strong reference. Default off
          --leak-suspects [<THRESHOLD>]
              Auto-rank dominators with retained share ≥ THRESHOLD; emit narrative + path-to-root + content preview per suspect. Implies --retained-size. Top-N suspects bounded by --top. Always shows at least top-3 (flagged "below threshold" if applicable). Default threshold 0.05 (5%)
          --merge-paths
              Modifier on `--paths-from-id`. Fold paths-to-root for all instances of the start id's class into a single tree with branch counts. Pair with `--retained-size` for graph-verified convergence; otherwise textual prefix matching with a banner
          --bitmaps
              List top-N android.graphics.Bitmap instances by pixel-byte size. Reports width × height × config and pixel bytes; Java-heap or native location; one-line holder summary. Android dumps only
      -h, --help
              Print help
      -V, --version
              Print version
    ```

## Input and output

| Flag | Default | Meaning |
|---|---|---|
| `-i`, `--inputFile <INPUT_FILE>` | | The dump to analyze. Required by every mode except `--diff-from`/`--diff-to`, `--diff-series` and `android-capture`. Note the camelCase spelling. |
| `-t`, `--top <TOP>` | `20` | Rows to show. Must be at least 1. See [Mode compatibility](mode-compatibility.md) for the modes it applies to. |
| `--json` | off | Also write the result as a JSON file. |
| `--json-out <PATH>` | | Write the JSON to exactly this path. Needs `--json`. The folder must exist. |
| `-d`, `--debug` | off | Print every record's tag while parsing. For heaptrail development; the output runs to more than a hundred thousand lines. |
| `-h`, `--help` | | Print help. |
| `-V`, `--version` | | Print the version, as `heaptrail <version>`. |

## Modes

Pick at most one. Giving two fails with `conflicting modes`.

| Flag | Value | Meaning | Page |
|---|---|---|---|
| (none) | | The summary. | [Summary](../analyze/summary.md) |
| `--find-referrers <TARGET>` | A class name, `id:<n>`, or digits | Holders of a class or object. | [Find referrers](../holders/find-referrers.md) |
| `--target-glob <PATTERN>` | A glob over dotted class names | Holders of every matching class. Conflicts with `--find-referrers`. | [Target glob](../holders/target-glob.md) |
| `--paths-from-id <ID>` | An object id (unsigned 64-bit) | Path from an object to a GC root. | [Paths to a GC root](../holders/paths-to-root.md) |
| `--diff-from <PATH>` with `--diff-to <PATH>` | Two dumps | Per-class difference between two dumps. | [Snapshot diff](../compare/diff.md) |
| `--diff-series <PATH>...` | Three or more dumps | Timeline across dumps. | [Diff a series](../compare/diff-series.md) |
| `--allocation-sites` | | Top allocation sites with stack traces. | [Allocation sites](../analyze/allocation-sites.md) |
| `--leak-suspects [<THRESHOLD>]` | A fraction, default `0.05` | Ranked suspects with paths. Implies `--retained-size`. | [Leak suspects](../analyze/leak-suspects.md) |
| `--bitmaps` | | Top `android.graphics.Bitmap` by pixel bytes. | [Bitmaps](../analyze/bitmaps.md) |

Write the threshold with `=`: `--leak-suspects=0.10`. A space (`--leak-suspects 0.10`) also works, but `=` cannot be confused with the next argument.

## Modifiers

| Flag | Default | Applies to | Meaning |
|---|---|---|---|
| `--retained-size` | off | Summary, referrers, paths | Compute retained sizes with a dominator tree. |
| `--exclude-soft-weak` | off | Retained size, referrers, paths, merged paths, suspects | Ignore weak, soft and phantom references. |
| `--preview-bytes <N>` | `0` | Summary, `-l`, paths, referrers by id, suspects | Show the first N bytes of primitive arrays. |
| `-l`, `--listStrings` | off | Summary | List the string table; with `--preview-bytes`, also large arrays. |
| `--list-arrays-min-bytes <N>` | `1024` | `-l` with `--preview-bytes` | The smallest array to list. |
| `--hops <HOPS>` | `2` | Referrers | Links to look through. `1` to `5`; at most three are reported. |
| `--include-statics` | on | Referrers | Accepted, and has no effect: class statics are always included. |
| `--group-holders` | off | Referrers | Group holder rows by owner. Fails without a referrer mode. |
| `--max-depth <N>` | `12` | Paths | The most hops to follow. `0` to `255`. |
| `--merge-paths` | off | Paths | Fold the paths of every instance of the object's class. |
| `--diff-by <KEY>` | `count` | Diff, series | The sort key: `count` or `bytes`. |
| `--native-context <PATH>` | | Series | Add `dumpsys meminfo` totals. |

## Android and mapping

| Flag | Default | Meaning |
|---|---|---|
| `--mapping <PATH>` | | An R8 or ProGuard mapping file. Conflicts with `--auto-mapping`. |
| `--auto-mapping [<MODE>]` | | Find the mapping from the installed app and a local Gradle build. `MODE` is `strict` (the default when given without a value) or `optional`. |
| `--project-root <DIR>` | current directory | The Android project for `--auto-mapping`. Needs `--auto-mapping`. |
| `--package <PACKAGE>` | | The application id for `--auto-mapping`. Needs `--auto-mapping`. |
| `--serial <SERIAL>` | adb's default | The device for `--auto-mapping`. |

## android-capture

```text
heaptrail android-capture --package <PACKAGE> --out <DIR> [OPTIONS]
```

<!-- output: help-capture.txt from="Usage:" cmd -->
```console
$ heaptrail android-capture --help
Usage: heaptrail android-capture [OPTIONS] --package <PACKAGE> --out <DIR>

Options:
      --serial <SERIAL>                 adb serial/device id. When omitted, adb's default target is used
      --package <PACKAGE>               Android application package name to capture
      --out <DIR>                       Local output directory for the pulled hprof and transcript
      --allocation-sites                Attempt allocation tracking setup before dump capture
      --foreground                      Bring the package to foreground with `monkey -p <package> 1`
      --series <COUNT>                  Number of validated HProf captures to collect for a diff-series run [default: 1]
      --series-delay-seconds <SECONDS>  Seconds to wait between captures when --series is greater than 1 [default: 0]
      --auto-mapping [<MODE>]           Discover the matching R8 mapping from a local Android Gradle project [possible values: strict, optional]
      --project-root <DIR>              Android project root for capture transcript mapping metadata
  -h, --help                            Print help
```

| Flag | Default | Meaning |
|---|---|---|
| `--package <PACKAGE>` | (required) | The application id to dump. |
| `--out <DIR>` | (required) | Folder for the dump and the transcript. |
| `--serial <SERIAL>` | adb's default | The device to use. |
| `--foreground` | off | Bring the app to the front first. |
| `--series <COUNT>` | `1` | Dumps to take. `1` or at least `3`. |
| `--series-delay-seconds <SECONDS>` | `0` | Wait between the dumps of a series. |
| `--allocation-sites` | off | Turn on allocation tracking around the dump. |
| `--auto-mapping [<MODE>]` | | Record the mapping for the installed build. |
| `--project-root <DIR>` | current directory | The project to search. Needs `--auto-mapping`. |

See [android-capture](../capture/android-capture.md).

## Value rules

- **`--top`** must be at least 1.
- **`--hops`** must be 1 to 5. Anything else is rejected before heaptrail starts.
- **`--paths-from-id`** takes digits only. An id that is not in the dump gives an empty path, not an error.
- **`--leak-suspects`** takes a fraction, normally between 0 and 1. heaptrail does not check the range, and uses what you give it: `2.0` prints `Threshold: 200.0 %`.
- **`--diff-by`** is `count` or `bytes`.
- **File arguments** must exist, and must not be empty.

## Related

- [Mode compatibility](mode-compatibility.md) shows which modifiers each mode uses.
- [Errors and exit codes](errors-and-exit-codes.md) lists every message.
- [Choose the right mode](../getting-started/choose-a-mode.md) for the flag to use.
