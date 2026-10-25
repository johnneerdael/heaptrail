# Shallow and retained size

**Why does a class whose instances are 8 KiB in total keep 15 MiB alive?** Because there are
two different ways to measure how big an object is, and heaptrail's default view shows only the
smaller one.

## Shallow size

An object's **shallow size** is the memory the object occupies itself: its header and its
own fields, or for an array, its elements. It does not include anything the object points to.
A `java.util.ArrayList` is 24 bytes shallow, however many items it holds, because the items live
in a separate `Object[]`.

The default [summary](../analyze/summary.md) ranks classes by shallow size. It is cheap to compute,
because it needs only the size of each record in the file. It is also blind to ownership: a tiny
object that anchors a huge subgraph looks harmless.

## Retained size

An object's **retained size** is the memory the runtime would free if that object were
collected: its own shallow size plus everything that is reachable *only* through it.

Two objects are involved in that definition. Object A **dominates** object B when every path from a GC
root to B goes through A. The retained size of A is the shallow size of A plus the shallow size of everything A
dominates. If B is also reachable another way, freeing A does not free B, so A does not retain it.

--8<-- "diagram-retained.html"

heaptrail computes this with a dominator tree (the Lengauer–Tarjan algorithm) over an in-memory graph
of every object. Add `--retained-size` to the [summary](../analyze/retained-size.md), to a path walk or to
referrers, or use [`--leak-suspects`](../analyze/leak-suspects.md), which always computes it.

A real case from the small JVM dump in the repository:

| Class | Instances | Shallow | Retained |
|---|---|---|---|
| `java.lang.ref.Finalizer` | 40 | 2.50 KiB | 149.52 KiB |

Forty small bookkeeping objects are 2.50 KiB. They keep 149.52 KiB alive, about 60 times their own
size. Each `Finalizer` points at an object that has a finalizer, and whatever those objects hold counts too.
Ranked by shallow size, `Finalizer` is nowhere near the top. Ranked by retained size, it is third.

## What the retained column in a class table means

In a class table, the **Retained** column is the sum of the retained sizes of every instance of that class.
When instances sit inside each other, such as lists that contain lists, the same bytes are counted once per
enclosing instance.

- Do not add up the column. The rows overlap.
- Do not compare a row to the heap total. In the first-triage dump, the leak-suspects report puts the whole
  object graph at 141.81 MiB, while the retained-size table gives `java.util.ArrayList` 126.84 MiB.
- Use the column to *rank* classes, and use the **Largest retained instances** list when you need the
  size of one object.

## Total, reachable and unreachable

A dump can hold objects that no root reaches: garbage the collector has not freed yet. heaptrail keeps them in its
graph, but counts them differently.

- The summary's **raw shallow heap** counts every object in the dump.
- A leak-suspects report prints two figures: `total` (every object in heaptrail's graph) and
  `retained-reachable` (what the GC roots can reach). Suspect percentages are computed against the
  **retained-reachable** figure.
- The summary's total and the suspects report's `total` come from different code paths and are not the
  same number. In the first-triage dump they are 171.21 MiB and 141.81 MiB. Compare figures within one report.
- An unreachable object's retained size is its shallow size, since nothing keeps it alive.

Class static fields are treated as roots when the graph is built, so an object held only by a static
field counts as reachable.

## Weak references change the answer

A strong reference keeps an object alive. A weak, soft or phantom reference does not, or not for long. By default heaptrail
counts all of them, which is the strict graph definition. Eclipse MAT's leak-hunting view leaves them out. Add
`--exclude-soft-weak` to match. See [Reference strength](reference-strength.md).

## What it costs

Retained size needs the whole object graph in memory. On the Android dumps measured for this guide, that was about
5 to 7.5 times the file size, and 1 to 6 seconds. See [Performance](../reference/performance.md).

## Related

- [Retained size](../analyze/retained-size.md) shows the flag in use.
- [Leak suspects](../analyze/leak-suspects.md) ranks dominators for you.
- [GC roots and paths](gc-roots-and-paths.md) explains what keeps an object reachable.
