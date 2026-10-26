# HPROF formats

HeapTrail reads the binary heap dump format that the JVM and Android's runtime write, known as HPROF. This page lists what it accepts, and what it does with each part.

## Supported formats

| Format string | Typical source | Id size |
|---|---|---|
| `JAVA PROFILE 1.0.1` | Older JVMs, and the small fixtures in the repository. | 4 or 8 bytes |
| `JAVA PROFILE 1.0.2` | Current JVMs (`jmap`, `jcmd`, `-XX:+HeapDumpOnOutOfMemoryError`) and Android dumps converted to the standard format. | 4 or 8 bytes |
| `JAVA PROFILE 1.0.3` | Android's runtime (`am dumpheap`), with extension records. | 4 bytes in practice |

The summary's first line says which one you have: `Processing 224.34MiB binary hprof file in 'JAVA PROFILE 1.0.2' format.` HeapTrail uses the string as it finds it in the header. It does not check
the version against a list, so a dump is judged by whether its records parse, not by its label.

CI validates against a 64-bit and a 32-bit fixture, and the project tests both an Android `1.0.2` and a `1.0.3` dump before each release. See [About](../help/about.md).

## The header

Every dump starts with a header:

| Part | Size | Meaning |
|---|---|---|
| Format string | variable, ends with a zero byte | `JAVA PROFILE 1.0.x` |
| Identifier size | 4 bytes | `4` or `8`. Any other value fails with `invalid pointer size - the value should be either `4` or `8``. |
| Timestamp | 8 bytes | When the dump was taken, in milliseconds since 1970. |

The timestamp is a handy way to tell dumps apart. The two Android dumps used in this guide were taken about two hours apart, and a series from a device 15 seconds apart.

## Records

After the header comes a stream of records, each with a tag, a time, a length and a body. The summary's counts map to these tags:

| Tag | Record | Summary line |
|---|---|---|
| `0x01` | UTF-8 string | `UTF-8 Strings` |
| `0x02` | Load class | `Classes loaded` |
| `0x03` | Unload class | `Classes unloaded` |
| `0x04` | Stack frame | `Stack frames` |
| `0x05` | Stack trace | `Stack traces` |
| `0x06` | Allocation sites | `Allocation sites` |
| `0x07` | Heap summary | `Heap summaries` |
| `0x0A` | Start thread | `Start threads` |
| `0x0B` | End thread | `End threads` |
| `0x0C`, `0x1C` | Heap dump, heap dump segment | `heap dumps containing in total … segments` |
| `0x0D` | CPU samples | `CPU samples` |
| `0x0E` | Control settings | `Control settings` |
| `0x2C` | Heap dump end | |

Inside a heap dump, each sub-record is one of the [GC root kinds](gc-root-kinds.md), or one of:

| Tag | Sub-record | Summary line |
|---|---|---|
| `0x20` | Class dump | `..GC class dump` |
| `0x21` | Instance dump | `..GC instance dump` |
| `0x22` | Object array dump | `..GC object array dump` |
| `0x23` | Primitive array dump | `..GC primitive array dump` |

Android's `0xC3` (primitive array without data) and `0xFE` (heap dump info) are parsed as well.

## What HeapTrail does with them

- **Strings** form the string table that gives names to classes and fields. `-l` prints it.
- **Class dumps** give each class's fields, super class and static values. They let HeapTrail size instances and find references in them.
- **Instances and arrays** are the objects. The summary counts and sizes them, and the tracing modes read the references inside.
- **Roots** become [GC root kinds](gc-root-kinds.md).
- **Stack traces, frames and threads** give thread names and stack frames when present.
- **Allocation sites** feed [`--allocation-sites`](../analyze/allocation-sites.md).
- **Heap summary, CPU samples and control settings** are counted and not used further.

A class that an instance refers to, but that no record defines, is counted at the bare header size and named `<unknown class #id>`. See [How HeapTrail reads a dump](../concepts/how-heaptrail-reads-a-dump.md).

## Sizes

HeapTrail's **shallow** sizes are the sum of an object's field sizes and header, and of an array's elements. They are close to, and not identical to, what the runtime's own tools report. Compare sizes within one
HeapTrail report, and between HeapTrail reports. See [Shallow and retained size](../concepts/shallow-and-retained.md).

## Related

- [GC root kinds](gc-root-kinds.md) lists the roots.
- [Android](../android/android-heaps.md) explains the Android extensions.
- [Capture](../capture/index.md) for how dumps are made.
