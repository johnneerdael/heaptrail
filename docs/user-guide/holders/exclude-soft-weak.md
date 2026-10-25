# Exclude weak references

On an Android dump, the first holder of almost any object can be a `WeakReference`, a LeakCanary watcher or one of the collector's own reference lists, and the real strong holder hides
underneath. `--exclude-soft-weak` tells heaptrail to ignore weak, soft and phantom references, so the holders that actually keep objects alive show through.

It is a modifier. Add it to the mode you are already using:

```bash
heaptrail -i heap.hprof --leak-suspects --exclude-soft-weak
heaptrail -i heap.hprof --find-referrers <class> --exclude-soft-weak
heaptrail -i heap.hprof --paths-from-id <id> --exclude-soft-weak
heaptrail -i heap.hprof --retained-size --exclude-soft-weak
```

Read [Reference strength](../concepts/reference-strength.md) first if the difference between strong, soft, weak and phantom is new.

## What it removes

The flag ignores every object whose class is a subclass of `java.lang.ref.SoftReference`, `WeakReference` or `PhantomReference`, including classes your app or its libraries define, such as
LeakCanary's `KeyedWeakReference`. The abstract base `java.lang.ref.Reference` is not in the set. How it acts depends on the mode:

| Mode | Behavior |
|---|---|
| `--find-referrers`, `--target-glob` | Reference objects are left out of the holder rows. |
| `--paths-from-id`, `--merge-paths` | A reference object is skipped as a holder, and the walk keeps looking for a strong one. If all it finds are weak, the path ends with `orphan [soft/weak/phantom — excluded]`. |
| `--retained-size`, `--leak-suspects` | A reference object no longer points at its referent in the graph. |

## An example in referrers

Referrers of `java.lang.ref.WeakReference` itself. Without the flag, one holder is another reference object: the `pendingNext` field of a `WeakReference`, which links reference objects to each other:

```bash
heaptrail -i heap-b.hprof --find-referrers java.lang.ref.WeakReference --hops 1 --top 3
```

<!-- output: ref-weak-obj.txt from="Found 333" -->
```text
Found 333 target instance(s) for java.lang.ref.WeakReference

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                ref count
  java.lang.Object[][]                                      124
  java.lang.ref.WeakReference.pendingNext                    46
  android.graphics.drawable.VectorDrawable.mCallback         43
```

With the flag, that row is gone and the next holder takes its place:

```bash
heaptrail -i heap-b.hprof --find-referrers java.lang.ref.WeakReference --hops 1 --top 3 --exclude-soft-weak
```

<!-- output: ref-weak-obj-sw.txt from="Found 333" -->
```text
Found 333 target instance(s) for java.lang.ref.WeakReference

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                ref count
  java.lang.Object[][]                                      124
  android.graphics.drawable.VectorDrawable.mCallback         43
  android.graphics.drawable.ColorDrawable.mCallback          28
```

`WeakReference.pendingNext` had 46 references. All of them came from reference objects, so none of them can be the reason anything stays alive.

## An example in retained sizes

With the flag, retained sizes move in both directions. See the three rows compared in [Reference strength](../concepts/reference-strength.md#what-exclude-soft-weak-does).

## Recommended use

- **Android leak hunting:** always. The default command is `--leak-suspects --exclude-soft-weak --preview-bytes 200`.
- **To check whether an object is held only weakly:** trace it with `--paths-from-id <id> --exclude-soft-weak`. If the path ends in `orphan [soft/weak/phantom — excluded]`, only weak holders were found.
- **To answer "what would be freed if this disappeared?":** leave the flag off. The strict graph is the right answer to that question.

## Differences from Eclipse MAT

MAT's leak-hunting view excludes weak, soft and phantom references by default. `--exclude-soft-weak` is the same idea. MAT also has a separate option for finalizer references (`java.lang.ref.FinalReference` and its
subclasses). heaptrail does not exclude those, so retained sizes can still differ slightly.

## Gotchas

- **It is off by default.** Without it you get the strict graph.
- **It changes numbers.** Retained sizes and shares are not the same with and without it. Say which you used when you report one.
- **Summary alone ignores it.** In the default summary the flag does nothing. It acts on the summary only when `--retained-size` is also set.

## Related

- [Concepts: reference strength](../concepts/reference-strength.md) explains the four strengths.
- [Leak suspects](../analyze/leak-suspects.md) is the mode that most needs this flag.
- [Paths to a GC root](paths-to-root.md) for how paths end.
