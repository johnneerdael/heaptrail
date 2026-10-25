#!/usr/bin/env bash
# Rebuild docs/user-guide/assets/downloads/shop-demo.hprof.gz: build the demo program in
# docs/user-guide/_meta/fixtures/jvm-demo, run it, and take a heap dump with jmap.
#
# The guide quotes heaptrail's output on this dump, including object ids, and ids change
# with every run. Only rebuild it on purpose: afterwards, run scripts/docs-capture.sh,
# scripts/docs-embed.py, and fix the ids that the pages and captures.txt mention.
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
src=$root/docs/user-guide/_meta/fixtures/jvm-demo
out=$root/docs/user-guide/assets/downloads/shop-demo.hprof.gz
tmp=$(mktemp -d)
trap 'kill "${pid:-0}" 2>/dev/null || true; rm -rf "$tmp"' EXIT

javac -d "$tmp" "$src"/shop/*.java
java -Xmx256m -cp "$tmp" shop.Main 2000 >"$tmp/out.txt" &
pid=$!
for _ in $(seq 1 50); do grep -q sessions "$tmp/out.txt" && break; sleep 0.2; done
jmap -dump:live,format=b,file="$tmp/shop-demo.hprof" "$pid"
mkdir -p "$(dirname "$out")"
gzip -9 -c "$tmp/shop-demo.hprof" >"$out"
echo "wrote $out ($(wc -c <"$out" | tr -d ' ') bytes; the dump is $(wc -c <"$tmp/shop-demo.hprof" | tr -d ' ') bytes)"
