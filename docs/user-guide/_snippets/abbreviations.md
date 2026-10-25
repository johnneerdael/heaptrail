*[HPROF]: The binary heap dump format written by the JVM and by Android's ART runtime (files end in .hprof)
*[GC]: Garbage collector: the part of the runtime that frees objects nothing can reach
*[GC root]: A place the runtime treats as always reachable: a static field, a thread, a JNI reference. Everything the GC keeps alive is reachable from a root
*[ART]: The Android Runtime, which runs apps on Android 5 and later
*[ADB]: Android Debug Bridge, the command-line tool that talks to a device or emulator
*[JNI]: Java Native Interface: how Java code and native (C/C++) code hold references to each other
*[R8]: The Android code shrinker and obfuscator that replaced ProGuard in Android Gradle builds
*[ProGuard]: The older shrinker and obfuscator whose mapping file format R8 also writes
*[MAT]: Eclipse Memory Analyzer, a graphical heap dump analyzer
*[OOM]: Out of memory: the runtime could not allocate and gave up
*[PSS]: Proportional set size: a process's memory counted so shared pages are split between the processes that share them
*[JSON]: JavaScript Object Notation, a plain-text format scripts can read
*[CI]: Continuous integration: a server that builds and tests every change
*[MiB]: Mebibyte: 1,048,576 bytes
*[KiB]: Kibibyte: 1,024 bytes
*[LRU]: Least recently used: a cache that drops the entry nobody has touched for the longest time
*[UTF-8]: The most common Unicode text encoding
*[UTF-16]: The text encoding Java strings use in memory
*[CSR]: Compressed sparse row: a compact way to store a graph's edges in memory
