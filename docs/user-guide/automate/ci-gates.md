# Gate a build on a leak threshold

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `--leak-suspects`, `--diff-from`, `--json-out`, `jq`</span>
<span><strong>Works on</strong> any dump</span>
<span><strong>Time</strong> seconds to a minute per dump</span>
<span><strong>Undo</strong> nothing to undo: it reads dumps</span>
</div>

## The problem

You run a soak test or a UI test and capture a heap dump at the end. You want the build to fail when one object keeps too much of the heap alive, or when a class that should not grow has grown, instead of finding out from a user.

## The solution

heaptrail writes the result as JSON, and `jq -e` turns a condition on that JSON into an exit status: `0` if the expression is true, `1` if it is false.

### Fail when one suspect retains too much

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 1 --json --json-out reports/suspects.json
jq -e '.suspects[0].heap_share_pct < 30' reports/suspects.json
```

In this dump the biggest suspect keeps 26.2 % of the reachable heap, so a threshold of 30 passes:

<!-- output: ci-pass.txt from="true" -->
```text
true
```

A stricter threshold of 20 fails, and `jq -e` exits with status 1:

<!-- output: ci-fail.txt from="false" -->
```text
false
```

The same shape works on bytes: `jq -e '.suspects[0].retained_bytes < 50000000'`. A percentage follows the size of the heap, and bytes follow the app. Pick the one that matches what you want to catch.

### Fail when a class grew

Compare the dump with a baseline you keep, and test the delta of the classes you care about. Ask for many rows so the class is certainly in the list:

```bash
heaptrail --diff-from before.hprof --diff-to after.hprof --top 100000 --json --json-out reports/diff.json
jq -e '(map(select(.class_name == "com.nexio.tv.domain.model.MetaPreview")) | first) as $c | $c.delta_count <= 1000' reports/diff.json
```

Here `MetaPreview` shrank between the two dumps, so the gate passes:

<!-- output: ci-diff-pass.txt from="true" -->
```text
true
```

Swap the two dumps, so the same change reads as growth of 450,170 instances, and it fails:

```bash
heaptrail --diff-from after.hprof --diff-to before.hprof --top 100000 --json --json-out reports/diff.json
jq -e '(map(select(.class_name == "com.nexio.tv.domain.model.MetaPreview")) | first) as $c | $c.delta_count <= 1000' reports/diff.json
```

<!-- output: ci-diff-fail.txt from="false" -->
```text
false
```

If the class is not in the report at all, `first` returns `null`, and in jq `null <= 1000` is true, so the gate passes without saying so. Make that explicit by naming the default: `first // {delta_count: 0}`. For a test such as `>= 1000`, a missing class would fail instead, so decide what "missing" should mean before you rely on it.

### A script that keeps the two kinds of failure apart

A gate that fails the build must not confuse "the threshold was crossed" with "heaptrail could not read the dump". The exit statuses differ, so check each:

```bash
#!/usr/bin/env bash
set -uo pipefail

heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak --top 1 \
  --json --json-out reports/suspects.json > reports/suspects.txt
status=$?
if [ "$status" -ne 0 ]; then
  echo "heaptrail failed with status $status" >&2   # 1 error, 2 bad arguments, 101 panic
  tail -n 5 reports/suspects.txt >&2
  exit 2
fi

if ! jq -e '.suspects[0].heap_share_pct < 30' reports/suspects.json > /dev/null; then
  echo "A single object retains more than 30 % of the heap" >&2
  cat reports/suspects.txt
  exit 1
fi
```

The text report is kept in `reports/suspects.txt`, so a failed gate leaves the evidence in the job log. Upload `reports/` as a build artifact, and do not upload the dump unless you have decided to. See
[Handle dumps safely](../capture/handle-dumps-safely.md).

## How it works

`--json` writes the same numbers as the text report. `jq -e` evaluates a condition and sets the exit status from the result. That is all a gate needs: the numbers, a comparison, and an exit status. The comparison
lives in your pipeline, where it is simple to change, and not in heaptrail.

## Variations

- **Gate on a percentage and on bytes.** Combine them: `jq -e '.suspects[0].heap_share_pct < 30 and .suspects[0].retained_bytes < 50000000'`.
- **Gate on the dominating class.** `jq -e '.suspects[0].accumulating_class != "com.example.Cache"'` fails when a known cache is the biggest thing in the heap.
- **Gate a series.** `jq -e '.monotonic_growth | length < 5'` with `--diff-series` fails when too many classes only grow.
- **Obfuscated builds.** Add `--mapping`, so the class names in your conditions are real.
- **Avoid noisy baselines.** A heap changes between runs, so leave a margin, and compare against a dump from the same build.

## Gotchas

- **A runner needs the RAM.** `--leak-suspects` keeps the whole graph in memory, about five to seven and a half times the dump size. Plan the runner for that. See [Performance](../reference/performance.md).
- **Garbage can rank.** On a JVM, use `jmap -dump:live` so an unreachable object does not become the suspect. See [Leak suspects](../analyze/leak-suspects.md#more-than-100-and-orphans).
- **The threshold is yours.** A cache that is meant to hold 30 % of the heap will trip a 30 % gate every time. Gate on what should be small.
- **`jq` is not part of heaptrail.** Install it in the job.

## Related

- [JSON output](json-output.md) explains the files.
- [Errors and exit codes](../reference/errors-and-exit-codes.md) lists every status.
- [Leak suspects](../analyze/leak-suspects.md) explains the numbers you are gating on.
