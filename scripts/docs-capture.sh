#!/usr/bin/env bash
# Regenerate the command output that the user guide quotes.
#
# Every line of `docs/user-guide/_meta/captures.txt` is `name|max-lines|command`.
# The command runs in <workdir>, where the dumps have the short names the guide
# uses (heap.hprof, before.hprof, after.hprof, launch.hprof, play.hprof,
# soak.hprof, jvm.hprof, meminfo.txt, test-heap-dumps/). `demo.hprof` is unpacked
# from assets/downloads/shop-demo.hprof.gz when missing. The output lands in
# `docs/user-guide/_meta/outputs/<name>.txt`, and `scripts/docs-check.py` checks
# that the pages quote it faithfully. See `_meta/outputs/README.md`.
#
# `adb` is replaced by docs/user-guide/_meta/fixtures/fake-adb/adb for every
# capture, so `android-capture` and `--auto-mapping` run without a device. A capture
# named *-stall or *-noproc makes the fake device misbehave (see that script), and
# one named *-noadb runs with no adb on the PATH at all.
# `myapp/` in the work directory is the demo Gradle project in _meta/fixtures.
#
# usage: scripts/docs-capture.sh <workdir> [name-filter]
#   HEAPTRAIL=/path/to/heaptrail   binary to run (default: target/release/heaptrail)
set -uo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
work=${1:?usage: scripts/docs-capture.sh <workdir> [name-filter]}
only=${2:-}
bin=${HEAPTRAIL:-$root/target/release/heaptrail}
fixtures=$root/docs/user-guide/_meta/fixtures
list=$root/docs/user-guide/_meta/captures.txt
out=$root/docs/user-guide/_meta/outputs

[ -x "$bin" ] || { echo "heaptrail binary not found: $bin (run cargo build --release)" >&2; exit 2; }
[ -d "$work" ] || { echo "workdir not found: $work" >&2; exit 2; }
mkdir -p "$out"
# demo.hprof is the committed JVM dump from _meta/fixtures/jvm-demo.
[ -f "$work/demo.hprof" ] || gunzip -c "$root/docs/user-guide/assets/downloads/shop-demo.hprof.gz" >"$work/demo.hprof"

orig_path=$PATH
failed=0
while IFS='|' read -r name max cmd; do
  case "$name" in ''|'#'*) continue ;; esac
  if [ -n "$only" ] && [[ "$name" != *"$only"* ]]; then continue; fi
  tmp=$(mktemp)
  # Reset the fake device and the capture directory, so every capture starts clean.
  rm -rf "$work/dumps" "$work/.fake-adb"
  ln -sfn "$fixtures/myapp" "$work/myapp"
  mode=ok
  case "$name" in *-stall) mode=stall ;; *-noproc) mode=no-process ;; esac
  export PATH="$fixtures/fake-adb:$orig_path" FAKE_ADB_STATE="$work/.fake-adb" \
         FAKE_ADB_HPROF="$work/jvm.hprof" FAKE_ADB_MODE="$mode"
  case "$name" in *-noadb) export PATH=/usr/bin:/bin ;; esac
  # A command that starts with `heaptrail` runs the real binary; anything else (jq) runs as written.
  case "$cmd" in
    heaptrail*) run="\"$bin\"${cmd#heaptrail}" ;;
    *) run=$cmd ;;
  esac
  ( cd "$work" && eval "$run" ) >"$tmp" 2>&1
  rc=$?
  {
    printf '$ %s\n# exit %s\n' "$cmd" "$rc"
    if [ "${max:-0}" -gt 0 ]; then head -n "$max" "$tmp"; else cat "$tmp"; fi
  } >"$out/$name.txt"
  rm -f "$tmp"
  printf '%-34s exit %s\n' "$name" "$rc"
done <"$list"
exit $failed
