#!/usr/bin/env bash
# Build the work directory that scripts/docs-capture.sh runs in.
#
# The guide's examples use short dump names. This links them to the real files:
#
#   heap.hprof, before.hprof      JAVA_PROFILE_1.0.2.hprof   (header JAVA PROFILE 1.0.2, repo root)
#   heap-b.hprof, after.hprof     JAVA_PROFILE_1.0.3.hprof   (header JAVA PROFILE 1.0.3, repo root)
#   launch/play/soak.hprof        series-a/b/c.hprof         (the nexio series in artifacts/)
#   meminfo.txt                   meminfo-after-series.txt   (same series)
#   jvm.hprof, test-heap-dumps/   the small fixtures committed to the repository
#   empty.hprof, truncated-5mb.hprof   made here, for the error captures
#
# None of the large dumps are committed (`*.hprof` is ignored), so a fresh clone cannot
# regenerate the captures. The captures themselves are committed in
# docs/user-guide/_meta/outputs/, which is all that scripts/docs-check.py needs.
#
# usage: scripts/docs-workdir.sh <workdir>
#   HEAPTRAIL_SERIES=/path/to/folder   folder with series-a/b/c.hprof and meminfo-after-series.txt
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
work=${1:?usage: scripts/docs-workdir.sh <workdir>}
series=${HEAPTRAIL_SERIES:-$root/artifacts/heaptrail-1.3.0-nexio-192.168.50.98}

mkdir -p "$work/reports"
missing=0
link() {
  if [ -e "$2" ]; then
    ln -sfn "$2" "$work/$1"
  else
    echo "missing: $2" >&2
    missing=1
  fi
}

link heap.hprof "$root/JAVA_PROFILE_1.0.2.hprof"
link before.hprof "$root/JAVA_PROFILE_1.0.2.hprof"
link heap-b.hprof "$root/JAVA_PROFILE_1.0.3.hprof"
link after.hprof "$root/JAVA_PROFILE_1.0.3.hprof"
link launch.hprof "$series/series-a.hprof"
link play.hprof "$series/series-b.hprof"
link soak.hprof "$series/series-c.hprof"
link meminfo.txt "$series/meminfo-after-series.txt"
link jvm.hprof "$root/test-heap-dumps/hprof-64.bin"
link test-heap-dumps "$root/test-heap-dumps"

# Inputs for the error captures (err-empty, err-truncated-small): a file with no bytes, and
# the first 5,000,000 bytes of a real dump, which ends in the middle of a record.
: >"$work/empty.hprof"
if [ -e "$root/JAVA_PROFILE_1.0.2.hprof" ]; then
  head -c 5000000 "$root/JAVA_PROFILE_1.0.2.hprof" >"$work/truncated-5mb.hprof"
fi

[ "$missing" -eq 0 ] || { echo "some inputs are missing; captures that need them will fail" >&2; exit 1; }
echo "work directory ready: $work"
