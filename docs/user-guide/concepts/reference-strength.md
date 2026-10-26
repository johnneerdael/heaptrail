# Reference strength

**Why does every path in my Android dump run through `WeakReference` and LeakCanary?** Because the
dump records every reference, and the strength of a reference is not stored as part of the path.
This page explains what the strengths are, and what `--exclude-soft-weak` does about them.

## Four strengths

Java has four kinds of reference. They differ in whether they keep their target alive.

| Kind | Keeps the target alive? | Typical use |
|---|---|---|
| Strong (an ordinary field or array slot) | Yes, as long as the holder is reachable. | Almost everything. |
| `SoftReference` | Only until memory runs low. | Memory-sensitive caches. |
| `WeakReference` | No. The collector may clear it at the next collection. | Maps that must not keep keys alive, and leak detectors. |
| `PhantomReference` | No. | Cleanup after an object is gone. |

A leak is a *strong* path from a root to an object you no longer need. Weak, soft and phantom references
cannot be the reason an object stays alive. But they appear in the dump as ordinary references, and a path walk
that follows them finds chains no leak depends on.

## Why they get in the way on Android

[LeakCanary](https://square.github.io/leakcanary/) watches objects through `KeyedWeakReference`. The Android
framework holds activities and views through `WeakReference`, and the collector chains reference objects together
through the `discovered` field of `java.lang.ref.Reference`. When you trace a suspect object, the first holder
HeapTrail meets can be one of those, and the real strong holder sits underneath a dozen hops of reference machinery.

## What `--exclude-soft-weak` does

`--exclude-soft-weak` ignores every object whose class is a subclass of `SoftReference`, `WeakReference` or
`PhantomReference`, including app classes such as LeakCanary's `KeyedWeakReference`. The base class
`java.lang.ref.Reference` itself is not in that set. The flag works differently in each mode.

| Mode | What changes |
|---|---|
| `--retained-size`, `--leak-suspects` | A reference object no longer points at its referent when HeapTrail builds the graph, so it takes no part in who owns what. |
| `--paths-from-id`, `--merge-paths` | A holder that is a reference object is skipped, and the walk keeps looking for a strong holder. If every holder it finds is weak, the path ends with `orphan [soft/weak/phantom — excluded]`. |
| `--find-referrers`, `--target-glob` | Reference objects are left out of the holder rows. Arrays that hold the target are still listed. |

The retained-size change is not one-directional. Take the class table of the first-triage dump, and compare
three rows without the flag and with it. The columns are shallow size, instances, retained size and largest instance.

```bash
heaptrail -i heap.hprof --retained-size -t 3000
```

<!-- output: sw-retained-plain.txt -->
```text
|     51.09KiB | 1308 | 57.49KiB | 40.00bytes | sun.misc.Cleaner |
|  768.00bytes | 32 | 5.84KiB | 24.00bytes | kotlin.reflect.jvm.internal.KTypeImpl |
|      1.37KiB | 35 | 3.41KiB | 40.00bytes | java.util.WeakHashMap$Entry |
```

```bash
heaptrail -i heap.hprof --retained-size --exclude-soft-weak -t 3000
```

<!-- output: sw-retained-flag.txt -->
```text
|  768.00bytes | 32 | 709.45KiB | 24.00bytes | kotlin.reflect.jvm.internal.KTypeImpl |
|     51.09KiB | 1308 | 45.98KiB | 40.00bytes | sun.misc.Cleaner |
|      1.37KiB | 35 | 1.23KiB | 40.00bytes | java.util.WeakHashMap$Entry |
```

Objects that are held weakly lose retained bytes: `WeakHashMap$Entry` (weak keys) falls from 3.41 KiB to 1.23 KiB,
and `sun.misc.Cleaner` (a `PhantomReference`) from 57.49 KiB to 45.98 KiB. But `KTypeImpl` rises from 5.84 KiB to
709.45 KiB. That is what you expect when an object was reachable through both a strong path and a weak one: with
the weak path gone, the strong holder owns it alone, and its retained size grows. Do not read a rising number
as a leak, and do not read a falling one as a fix.

To find out whether something is held only weakly, trace it with `--paths-from-id <id> --exclude-soft-weak`.
If the path ends with `orphan [soft/weak/phantom — excluded]`, every holder HeapTrail found was a weak one.

## How it compares with MAT

Eclipse MAT's leak-hunting workflow excludes weak, soft and phantom references by default, so its retained sizes
are smaller than HeapTrail's default for objects reachable through them. `--exclude-soft-weak` brings HeapTrail in line.
MAT also has a separate option for finalizer references, and HeapTrail does not. Retained sizes can therefore
still differ slightly.

!!! tip "Default off, on purpose"
    Without the flag, HeapTrail reports the strict graph. That is the right answer to "what would be freed if this
    object disappeared?". It is the wrong answer to "what is leaking?", which is why the recommended
    leak-hunting command includes the flag.

## Related

- [Exclude weak references](../holders/exclude-soft-weak.md) shows the flag on a real dump.
- [Shallow and retained size](shallow-and-retained.md) explains the numbers the flag changes.
- [GC roots and paths](gc-roots-and-paths.md) describes how paths end.
