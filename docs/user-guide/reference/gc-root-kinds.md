# GC root kinds

A **GC root** is a place the runtime treats as always alive. heaptrail names each root by the record that declared it. A path that reaches a root ends with `→ reached GC root: <kind>`, and the summary counts roots by kind.
See [GC roots and paths](../concepts/gc-roots-and-paths.md) for what a root proves.

## Standard kinds

These come from the HPROF specification and appear in JVM and Android dumps.

| Kind | Tag | What it is |
|---|---|---|
| `RootUnknown` | `0xFF` | A root the dumper did not classify. |
| `RootJniGlobal` | `0x01` | A global reference held by native (JNI) code. |
| `RootJniLocal` | `0x02` | A local reference held by native code during a call. |
| `RootJavaFrame` | `0x03` | A local variable or parameter in a Java stack frame, on a thread. |
| `RootNativeStack` | `0x04` | An object referenced from a native stack. |
| `RootStickyClass` | `0x05` | A system class that is never unloaded, and its static fields. |
| `RootThreadBlock` | `0x06` | An object referenced from a thread block. |
| `RootMonitorUsed` | `0x07` | An object used as a monitor (a lock). |
| `RootThreadObject` | `0x08` | A live `Thread` object. |

## Android extension kinds

`JAVA PROFILE 1.0.3` dumps from Android's runtime add kinds that the standard format lacks. heaptrail parses all of them and keeps each as its own kind, where converting the dump with `hprof-conv` would fold
them into `RootUnknown`.

| Kind | Tag | Status |
|---|---|---|
| `RootInternedString` | `0x89` | Active. |
| `RootFinalizing` | `0x8A` | Deprecated; older runtimes still emit it. |
| `RootDebugger` | `0x8B` | Active. |
| `RootReferenceCleanup` | `0x8C` | Deprecated. |
| `RootVmInternal` | `0x8D` | Active. Objects the runtime holds for itself. |
| `RootJniMonitor` | `0x8E` | Active. A monitor held through JNI. |

Android also adds three record types that are not roots: `Unreachable` (`0x90`, deprecated), `PrimitiveArrayNoDataDump` (`0xC3`, an array whose contents are not in the dump, such as a zygote-shared one) and `HeapDumpInfo` (`0xFE`, which
annotates a heap segment).

## Where kinds show up

- **The summary** counts the standard kinds under the `..GC root` lines.
- **A path** ends with the kind of the root it reached. For `RootJavaFrame`, `RootThreadObject`, `RootJniLocal` and `RootJniMonitor`, it also prints the owning thread and, for a Java frame, the top frame of its stack. When the
  dump has no thread records, it prints the raw serial numbers instead. See [Paths to a GC root](../holders/paths-to-root.md#how-it-ends).
- **The retained-size graph** treats every GC root, and every object-typed class static field, as reachable from a single virtual root.
- **JSON** has the kind as the string in `root_kind`. See [JSON schemas](json-schemas.md#paths).

## Related

- [Concepts: GC roots and paths](../concepts/gc-roots-and-paths.md) explains roots.
- [HPROF formats](hprof-formats.md) lists the record tags.
- [Android](../android/android-heaps.md) explains the Android differences.
