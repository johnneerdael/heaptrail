# JVM dumps

Any HotSpot-based JVM can write a heap dump in HPROF format, and HeapTrail reads it. You can take one from a
running process with `jmap` or `jcmd`, or have the JVM write one at the moment it runs out of memory.

The commands below were checked on OpenJDK 21. Other JDKs spell some options differently, so check your
JDK's documentation for `jmap` and `jcmd` if a flag is rejected.

## From a running process

Find the process id with `jps` or `jcmd` (with no arguments, `jcmd` lists the JVMs it can see), then pick one of these.

=== "jmap"

    ```bash
    jmap -dump:live,format=b,file=heap.hprof <pid>
    ```

    `live` dumps only objects that are still reachable, and the JVM runs a full garbage collection first.
    Leave it out to dump every object, including garbage that has not been collected yet:

    ```bash
    jmap -dump:format=b,file=heap.hprof <pid>
    ```

=== "jcmd"

    ```bash
    jcmd <pid> GC.heap_dump heap.hprof
    ```

Either command prints the size when it is done:

```text
Dumping heap to heap.hprof ...
Heap dump file created [20782533 bytes in 0.021 secs]
```

Run the command as the same user that owns the process, on the machine the process runs on. The file is written
by the *target* JVM, so give an absolute path it can write to, not a path relative to your shell.

!!! tip "Which one for a leak?"
    Use `live`. Garbage that is waiting for collection only adds noise to a leak investigation, and the full collection
    gives you a stable picture. For a question about allocation churn, the unreachable objects matter, and you want a dump
    without `live`.

## When the JVM runs out of memory { #dump-on-outofmemoryerror }

Start the JVM with these options and it writes a dump at the moment it throws `OutOfMemoryError`:

```bash
java -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/var/dumps/ -jar app.jar
```

`HeapDumpPath` can be a directory or a file name. Make sure the disk has room for a file as large as the heap. The
JVM prints this as it goes:

```text
java.lang.OutOfMemoryError: Java heap space
Dumping heap to /var/dumps/java_pid4711.hprof ...
Heap dump file created [34778745 bytes in 0.018 secs]
```

This is the best dump for an `OutOfMemoryError` investigation, because it is taken at the failure and not after.
Start with [`--leak-suspects`](../analyze/leak-suspects.md).

## Try it: a demo with a deliberate leak

The repository includes a small program with a leak: a session cache that never evicts anything. Its dump is committed
as [`shop-demo.hprof.gz`](../assets/downloads/shop-demo.hprof.gz) (1.2 MB), so you can follow
the examples without running a JVM. Unpack it, then run `heaptrail` on it:

```bash
gunzip -c docs/user-guide/assets/downloads/shop-demo.hprof.gz > demo.hprof
heaptrail -i demo.hprof --leak-suspects --exclude-soft-weak --top 1
```

<!-- output: jvm-suspects.txt from="Heap:" -->
```text
Heap: 16.97MiB total, 16.68MiB retained-reachable.
Threshold: 5.0 % retained share. Showing 1 suspect(s) (1 above threshold).

Suspect 1 — 15.79MiB (94.7 % of heap)
  dominator: java.util.HashMap (object_id=34095644696)
  accumulating: 4000 instances of byte[], total 15.65MiB
  path to GC root:

  Path from object_id=34095644696 (depth 0 step(s)):
    start  ── id=34095644696
    → orphan: no holder found in dump
```

One `HashMap` keeps 94.7 % of the reachable heap alive, almost all of it `byte[]`. The path ends in `orphan` because the walker does
not look at static fields. [Find the static that holds a cache](../holders/recipes/find-the-static-that-holds-a-cache.md)
finishes this investigation.

The program's source is in `docs/user-guide/_meta/fixtures/jvm-demo/`. It stores 2,000 `Session` objects, each with an
8 KiB buffer, in a static `HashMap`.

## Format notes

- A JVM dump is `JAVA PROFILE 1.0.1` or `1.0.2` with 8-byte object ids. This demo dump, from a current JDK, is 1.0.2. See
  [HPROF formats](../reference/hprof-formats.md).
- The dump contains a stack trace for each thread, so the summary lists them. It does not contain allocation sites. See
  [Allocation tracking](allocation-tracking.md).
- Android dumps have a different flavor, with 4-byte ids and some extra root kinds. See [Android](../android/index.md).

## Related

- [Handle dumps safely](handle-dumps-safely.md) because a JVM dump contains every secret the process held.
- [Your first triage](../getting-started/first-triage.md) runs the same modes on an Android dump.
- [Leak suspects](../analyze/leak-suspects.md) is the best first command for an OOM dump.
