# GC roots and paths

A garbage collector keeps an object alive if it can reach it by following references from a **GC root**.
A **path to a GC root** is one such chain, and it is the proof that something is still holding an object.

## GC roots

A GC root is a place the runtime treats as always reachable, without asking who points at it. The kinds
heaptrail reports are:

| Kind | What it is |
|---|---|
| `RootStickyClass` | A system class that is always loaded, with its static fields. |
| `RootJavaFrame` | A local variable or parameter in a running method. |
| `RootThreadObject` | A live `Thread` object. |
| `RootJniGlobal`, `RootJniLocal` | A reference held by native code. |
| `RootMonitorUsed` | An object used as a lock. |
| `RootNativeStack`, `RootThreadBlock` | Objects referenced from a native stack or a thread block. |
| `RootUnknown` | A root the dumper did not classify. |

Android dumps add a few more, such as `RootInternedString`, `RootVmInternal` and `RootJniMonitor`.
[GC root kinds](../reference/gc-root-kinds.md) lists them all with what each means.

## A path

A path starts at an object and lists, one hop at a time, the object that holds it, and the field or array slot
the hold goes through. It ends at a root.

--8<-- "diagram-path.html"

This is the text heaptrail prints for a path, read from the object up toward the root:

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --preview-bytes 200
```

<!-- output: first-paths.txt keep -->
```text
Path from object_id=1661812752 (depth 9 step(s)):
  start  ── id=1661812752
  hop 1 ── id=1661812736  (via java.lang.String.value)
  hop 2 ── id=364312776  (via java.util.HashMap$Node.value)
```

Each `hop` is a holder object, and `via` names the field that holds the object one line above it. A hop through
an array shows the slot, such as `java.lang.Object[][13]`.

To free an object you break one hop of the path. Which hop? The one that should not exist: a view model kept
alive by a back stack, a listener never unregistered, a cache with no size limit. heaptrail tells you where the
hops are. You decide which one is the mistake.

## How heaptrail finds a path

heaptrail finds one holder at a time. For each hop it scans the dump for the **first** object, in file order,
that has a field or an array slot pointing at the current object. It then repeats for that holder.

That has three consequences.

- **It is a path, not the shortest path and not the only path.** An object can be held in several ways.
  The walker reports the first it meets. [Merge paths](../holders/merge-paths.md) and
  [find referrers](../holders/find-referrers.md) show the others.
- **It can go in circles.** If two objects hold each other, the walker follows the loop until it reaches
  `--max-depth`. Repeated ids in a path are the sign.
- **It does not look at class static fields.** A path that really ends in a static field ends with
  `orphan: no holder found in dump`. Ask [find referrers](../holders/find-referrers.md) about the last id: it does
  include statics.

The retained-size graph behaves differently on that last point. It treats every object-typed static field as a
root, so [leak suspects](../analyze/leak-suspects.md) see statics as reachable.

## How a path ends

| Last line | Meaning |
|---|---|
| `→ reached GC root: <kind>` | The chain ended at a root. For a thread-owned root, heaptrail adds the thread name and, for a Java frame, the top stack frame. |
| `→ stopped at --max-depth (chain may continue)` | The depth limit (12 by default) ran out first. Raise `--max-depth` if the hops are still informative. |
| `→ orphan: no holder found in dump` | No instance field or array slot points at the last object. It may be held by a static field, or it may be unreachable. |
| `→ orphan [soft/weak/phantom — excluded]` | The only holder found was a weak, soft or phantom reference, and `--exclude-soft-weak` is on. |

When a dump has no thread names or frames, a thread-owned root prints the raw `thread_serial` and
`frame_index` instead, with the note `(thread name/frame metadata not in dump)`.

## Related

- [Paths to a GC root](../holders/paths-to-root.md) is the how-to for `--paths-from-id`.
- [Reference strength](reference-strength.md) explains why weak references clutter paths.
- [GC root kinds](../reference/gc-root-kinds.md) lists every root kind.
