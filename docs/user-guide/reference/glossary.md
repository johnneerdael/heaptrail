# Glossary

One-line definitions of the terms this guide uses. Terms link to the page that explains them in depth.

## A

**accumulating class.** In a [leak suspect](../analyze/leak-suspects.md), the class with the most instances inside the dominated subtree.

**allocation site.** A call site, with its stack trace, where a batch of objects was created. Only in dumps captured with [allocation tracking](../capture/allocation-tracking.md).

**ART.** The Android Runtime, which runs apps on Android 5 and later and writes Android's heap dumps.

## D

**dominator.** Object A dominates object B when every path from a GC root to B goes through A. A suspect is a dominator that retains a lot. See [Shallow and retained size](../concepts/shallow-and-retained.md).

**dominator tree.** The tree of immediate dominators over the whole object graph. HeapTrail builds it with the Lengauer–Tarjan algorithm to compute retained sizes.

## G

**GC root.** A place the runtime treats as always alive, such as a static field or a thread's local variable. See [GC roots and paths](../concepts/gc-roots-and-paths.md).

## H

**heap dump.** A snapshot of every object in a process's heap, the classes, and the references between them. Also called a dump, or an `.hprof` file.

**holder.** An object, field or array slot that points at another object. Also called a *referrer*.

**hop.** One link in a chain of holders. A path is made of hops.

**HPROF.** The binary format of heap dumps. See [HPROF formats](hprof-formats.md).

## I

**instance.** An object that is an instance of a class, as opposed to an array.

## J

**JNI.** The Java Native Interface. Native code holds references to Java objects through it, and those become roots.

## M

**mapping file.** The `mapping.txt` that R8 writes, recording what each obfuscated name stands for. See [Deobfuscate release builds](../android/deobfuscate-release-builds.md).

**monotonic growth candidate.** In a [series](../compare/diff-series.md), a class whose value never decreases between neighboring dumps and ends higher than it started.

## N

**native memory.** Memory outside the Java heap: native allocations, decoded images, graphics buffers. Not in a heap dump. See [Native context](../compare/native-context.md).

## O

**object id.** The number a dump assigns to an object. Valid within one dump only. See [Object ids](../concepts/object-ids.md).

**orphan.** A path that ends because no instance field or array slot points at the last object. It may be held by a static field, or be unreachable. See [Paths to a GC root](../holders/paths-to-root.md#orphans).

## P

**path.** A chain of holders from an object up to a GC root. See [Paths to a GC root](../holders/paths-to-root.md).

**phantom reference.** A reference that does not keep its target alive and is used for cleanup after the target is gone.

**PSS.** Proportional set size: a process's memory with shared pages split between the processes that share them. `dumpsys meminfo` reports it.

**preview.** The first bytes of a primitive array, decoded as text or shown as hex. See [Content previews](../analyze/preview-bytes.md).

## R

**R8.** The Android tool that shrinks and obfuscates code, and replaced ProGuard.

**referrer.** The same as a holder. The `--find-referrers` mode lists them.

**retained size.** The memory freed if an object were collected: its own size plus everything only it keeps alive. See [Shallow and retained size](../concepts/shallow-and-retained.md).

**retained-reachable.** In a suspects report, the bytes the GC roots can reach. Suspect shares are relative to it.

## S

**series.** Three or more dumps of one process, in order, compared by `--diff-series`.

**shallow size.** The memory an object occupies itself, without what it points to.

**soft reference.** A reference that keeps its target alive until memory runs low.

**static field.** A field that belongs to a class and not to an instance. It lives as long as the class does, so it is a common holder of caches.

**string table.** The dump's list of identifier names (classes, fields, methods, files). `-l` prints it.

**suspect.** An object that retains a large share of the heap, reported by `--leak-suspects`. A lead, not a verdict.

## T

**transcript.** The text file `android-capture` writes beside a dump, recording every `adb` command and the evidence of what was on screen.

## W

**weak reference.** A reference that does not keep its target alive. The collector may clear it at the next collection. See [Reference strength](../concepts/reference-strength.md).

## Related

- [Concepts](../concepts/index.md) explains the ideas behind these terms.
- [Command line](command-line.md) for flag names.
- [HPROF formats](hprof-formats.md) for the file format.
