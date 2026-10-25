# Follow along with the bundled files

The repository ships two small JVM heap dumps in `test-heap-dumps/`. They are enough to
try every basic mode in a few milliseconds each, without capturing anything. The
examples elsewhere in this guide use bigger Android dumps that are not published, so this
page is the one place where you can run the commands and get exactly the output shown.

You need a clone of the repository and a heaptrail build. Run every command from the
repository root.

```bash
git clone https://github.com/johnneerdael/heaptrail
cd heaptrail
cargo build --release
export PATH="$PWD/target/release:$PATH"
```

| File | What it is |
|---|---|
| `test-heap-dumps/hprof-64.bin` | A 3 MiB dump with 8-byte object ids, from the NetBeans profiler tests. |
| `test-heap-dumps/hprof-32.bin` | A 275 KiB dump with 4-byte ids, from the JDK 8 `jhat` tests. It also holds allocation-site records. |

Both files use the `JAVA PROFILE 1.0.1` format. Android dumps from `am dumpheap` use 1.0.3.
heaptrail reads all three; see [HPROF formats](../reference/hprof-formats.md).

## 1. The summary

```bash
heaptrail -i test-heap-dumps/hprof-64.bin -t 5
```

<!-- output: fix-summary.txt from="Found a total" until="Top 5 largest" -->
```text
Found a total of 2.51MiB of raw shallow heap objects in the dump.

Top 5 raw shallow heap classes:

+------------+-----------+------------+--------------------+
| Total size | Instances |    Largest | Class name         |
+------------+-----------+------------+--------------------+
|    1.99MiB |       436 |  634.78KiB | int[]              |
|  194.89KiB |      1991 |   16.02KiB | char[]             |
|   85.23KiB |       443 |    8.02KiB | byte[]             |
|   47.38KiB |      1516 | 32.00bytes | java.lang.String   |
|   45.42KiB |       560 |    8.02KiB | java.lang.Object[] |
+------------+-----------+------------+--------------------+
```

Above the tables, the summary prints the file format, record counts, GC root counts and a stack
trace for each thread that has one. This dump has 436 `int[]` arrays that together take 1.99 MiB,
and the biggest is 634.78 KiB. On a JVM dump, object arrays print as `java.lang.Object[]`.

<!-- output: fix-summary.txt from="Largest array instances" -->
```text
Largest array instances object ids (for retainer tracing):
   634.78KiB object_id=3607227400 int[]
    16.02KiB object_id=3606712464 char[]
     8.02KiB object_id=3606691640 byte[]
     8.02KiB object_id=3606636656 java.lang.Object[]
     2.02KiB object_id=3606990376 java.util.HashMap$Node[]
```

The last block lists the largest arrays with their object ids. Those ids are what you hand to the
tracing modes below.

## 2. Retained size

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --retained-size -t 5
```

<!-- output: fix-retained.txt from="Top 5 classes by retained" until="Top 5 largest" -->
```text
Top 5 classes by retained heap (dominator tree):

+-----------+-----------+-----------+------------+-------------------------+
|   Shallow | Instances |  Retained |    Largest | Class name              |
+-----------+-----------+-----------+------------+-------------------------+
|   1.99MiB |       436 |   1.99MiB |  634.78KiB | int[]                   |
| 194.89KiB |      1991 | 158.22KiB |   16.02KiB | char[]                  |
|   2.50KiB |        40 | 149.52KiB | 64.00bytes | java.lang.ref.Finalizer |
|  85.23KiB |       443 |  76.60KiB |    8.02KiB | byte[]                  |
|  47.38KiB |      1516 |  52.87KiB | 32.00bytes | java.lang.String        |
+-----------+-----------+-----------+------------+-------------------------+
```

`java.lang.ref.Finalizer` is the row to look at. Its 40 instances are 2.50 KiB shallow, but they keep
149.52 KiB alive, about 60 times more. A small wrapper that anchors a large subgraph is what retained
size exists to find. [Shallow and retained size](../concepts/shallow-and-retained.md) explains why.

The report ends with the largest retained objects and their ids.

<!-- output: fix-retained.txt from="Largest retained instances" -->
```text
Largest retained instances object ids:
   634.77KiB object_id=3607227400 int[]
   634.73KiB object_id=3608528056 int[]
   630.43KiB object_id=3607881976 int[]
   130.83KiB object_id=3607093296 int[]
    43.71KiB object_id=3606861808 sun.misc.Launcher$AppClassLoader
```

## 3. Who holds a class?

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --find-referrers java.util.LinkedList --hops 2
```

<!-- output: fix-referrers.txt from="Found 190" -->
```text
Found 190 target instance(s) for java.util.LinkedList

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  java.util.HashMap$Node.value                190
```

All 190 lists are values in a `HashMap`. Each row of the table is a field that holds the target, with
the number of references through it. There is no second-hop section here because no list is held by an
`Object[]`.

## 4. A path to a GC root

In the list above, `sun.misc.Launcher$AppClassLoader` has object id `3606861808`. Trace it.

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --paths-from-id 3606861808
```

<!-- output: fix-paths-root.txt -->
```text
Path from object_id=3606861808 (depth 1 step(s)):
  start  ── id=3606861808
  hop 1 ── id=3606600864  (via java.lang.Thread.contextClassLoader)
  → reached GC root: RootThreadObject
        root metadata: thread_serial=9 stack_trace_serial=10 thread_object_id=3606600864
        (thread name/frame metadata not in dump)
```

The class loader is held by a `Thread` through its `contextClassLoader` field, and that thread object
is itself a GC root (`RootThreadObject`). The chain ends because it reached something the runtime
always keeps alive. The `root metadata` line is what heaptrail knows about the thread when the dump has no
thread name.

## 5. A path that goes in circles

Not every path ends cleanly. Try the 16 KiB `char[]` from the summary.

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --paths-from-id 3606712464 --preview-bytes 80
```

<!-- output: fix-paths-cycle.txt -->
```text
Path from object_id=3606712464 (depth 12 step(s)):
  start  ── id=3606712464
         content: binary/repeated-fill, 16384 bytes total
         00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
         00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00 |................|
  hop 1 ── id=3606712424  (via java.io.BufferedWriter.cb)
  hop 2 ── id=3606700208  (via java.io.PrintStream.textOut)
  hop 3 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 4 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 5 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 6 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 7 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop 8 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop 9 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop10 ── id=3606700208  (via java.io.PrintStream.charOut)
  hop11 ── id=3606700936  (via java.io.OutputStreamWriter.lock)
  hop12 ── id=3606700208  (via java.io.PrintStream.charOut)
  → stopped at --max-depth (chain may continue)
```

The same two ids repeat: `3606700208` holds `3606700936` through `PrintStream.charOut`, and
`3606700936` holds `3606700208` through `OutputStreamWriter.lock`. The two objects hold each other. The
walker follows the first holder it finds on every hop, so it goes round and round until it hits
`--max-depth` (12 by default). The preview tells you why it is not worth chasing: the array is 16 KiB of
repeated-fill bytes, and the first rows are all zeros.

When ids repeat, stop reading the path and ask find-referrers about one of them. It lists every holder, not
only the first one it meets, and it includes class static fields.

```bash
heaptrail -i test-heap-dumps/hprof-64.bin --find-referrers id:3606700208 --hops 1
```

<!-- output: fix-cycle-referrers.txt from="Found 1" -->
```text
Found 1 target instance(s) for id:3606700208

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)  ref count
  java.io.OutputStreamWriter.lock               1
  sun.nio.cs.StreamEncoder.out                  1
  java.lang.System.out                          1
```

`java.lang.System.out` is the holder the walk never found. It is a static field, so it is the reason this
`PrintStream` lives as long as the JVM does. [Paths to a GC root](../holders/paths-to-root.md#cycles)
explains why paths skip statics and referrers do not.

## 6. Allocation sites

The 32-bit file was captured with allocation tracking on, which most dumps are not. The summary says so:

```bash
heaptrail -i test-heap-dumps/hprof-32.bin -t 2
```

<!-- output: fix32-alloc-hint.txt from="AllocationSites:" head="1" -->
```text
AllocationSites: 464 sites across 1 records (run with --allocation-sites for stack traces)
```

```bash
heaptrail -i test-heap-dumps/hprof-32.bin --allocation-sites --top 5
```

<!-- output: fix32-alloc.txt from="Top 5 allocation" -->
```text
Top 5 allocation sites by bytes_allocated (of 464 total):

  ─   62.01KiB  /         692 instances  char[]#<init>

  ─   24.76KiB  /           9 instances  byte[]#<init>

  ─   16.81KiB  /         702 instances  java.lang.String#<init>

  ─   12.15KiB  /         304 instances  java.lang.Object[]#<init>

  ─    2.21KiB  /          51 instances  java.lang.String[]#<init>
```

Each row is a call site, ranked by the bytes it allocated. The records in this old file carry no stack
frames, so none print under the rows. In a dump captured on Android with allocation tracking, each row
is followed by the `at` lines of the stack that allocated it. See [Allocation sites](../analyze/allocation-sites.md).

## What you learned

- Every mode takes the dump with `-i` and prints a plain-text report; `-t N` limits the rows.
- `--retained-size` ranks classes by what they keep alive, not by what they are.
- `--find-referrers` names every field that holds a class or an object, and includes statics.
- `--paths-from-id` follows one chain to a GC root, and repeated ids mean it is going in circles.
- `--preview-bytes` shows what is inside a primitive array.

## Next steps

- [Your first triage](first-triage.md) uses the same modes on a real Android dump, with a real leak at the end.
- [Choose the right mode](choose-a-mode.md) maps your question to the command.
- [Capture a heap dump](../capture/index.md) of your own app.
