# Concepts

Heap analysis has a small vocabulary that every report leans on: shallow and retained size,
GC roots, reference strength, object ids. These pages explain each idea once, with a
real example from HeapTrail's output, so the how-to pages can link here instead of
repeating themselves.

You do not need to read them before you start. Read one when a number in a report surprises you.

## Which page answers your question

| Your question | Page |
|---|---|
| Why does a class with 8 KiB of objects keep 15 MiB alive? | [Shallow and retained size](shallow-and-retained.md) |
| What is a GC root, and what does a path to one mean? | [GC roots and paths](gc-roots-and-paths.md) |
| Why do I see `WeakReference` all through my paths? | [Reference strength](reference-strength.md) |
| Where do I get an object id, and what can I do with it? | [Object ids](object-ids.md) |
| Why does one mode take 0.2 seconds and another take 6? | [How HeapTrail reads a dump](how-heaptrail-reads-a-dump.md) |

## A heap dump in one paragraph

A heap dump is a snapshot of every object a program had in memory at one instant, the classes
they belong to, and the references between them. It also records the **GC roots**: the places
the runtime treats as always alive, such as static fields and the local variables of running
threads. Anything the garbage collector can reach from a root stays alive. Everything else is
garbage. A memory leak is an object you no longer need that is still reachable from a root.
Finding a leak means finding the path from a root to that object and deciding which hop in it
should not exist.

## Related

- [Choose the right mode](../getting-started/choose-a-mode.md) maps questions to commands.
- [Glossary](../reference/glossary.md) defines every term in one line.
- [Your first triage](../getting-started/first-triage.md) puts the ideas to work.
