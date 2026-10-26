# Bitmaps

Bitmaps are often the biggest thing in an Android heap, and in a class table they look like any other big primitive array. `--bitmaps` ranks
`android.graphics.Bitmap` instances by pixel bytes, computed from each bitmap's width and height, so you can see a 4096 × 4096 image for what it is.

```bash
heaptrail -i heap.hprof --bitmaps -t 20
```

!!! warning "This mode does not run on either sample dump"
    `--bitmaps` reads the fields `mWidth`, `mHeight` and `mConfig` from each `android.graphics.Bitmap`. Some Android builds do not have those
    fields in the Java object, and then HeapTrail cannot size the bitmaps. **Neither of the two Android dumps used in this guide has them**, so the report below shows
    the layout with illustrative values, and the error is real. If the command fails on your dump, see [When it fails](#when-it-fails).

## The report

The report has one row per bitmap, biggest first, and a total. This is its layout, with illustrative numbers:

```text
Top 3 Bitmap instances by pixel bytes:

  pixel_bytes   dimensions    config        location object_id
    64.00MiB   4096×4096     ARGB_8888     native   4097812752
    12.00MiB   1024×3072     ARGB_8888     java     2097446928
     4.00MiB   1024×1024     ARGB_8888     java     1723142144

Total bitmap pixel bytes: 80.00MiB across 3 instances.
```

| Column | Meaning |
|---|---|
| `pixel_bytes` | `width × height × 4`, in binary units. |
| `dimensions` | The bitmap's `mWidth × mHeight`. |
| `config` | Always `ARGB_8888` in this version. HeapTrail does not read the real `Bitmap.Config`. |
| `location` | `java` if the bitmap has a `mBuffer` array on the Java heap (pre-Android 8), `native` otherwise. |
| `object_id` | The id to give to [`--paths-from-id`](../holders/paths-to-root.md). |

The total adds up only the rows shown, so it depends on `--top`.

### Java heap or native?

Before Android 8 (API 26), a bitmap's pixels lived in a Java `byte[]`, and that array is in the dump and counted in the heap totals. From Android 8 on, the pixels are in native memory. The
dump holds only a handle. For those bitmaps, HeapTrail *estimates* `width × height × 4`. Native memory is not part of the heap dump, so the number is an estimate, not
a measurement. A bitmap with a different pixel format, or with stride padding, takes a different amount.

## When it fails { #when-it-fails }

<!-- output: bitmaps-err.txt -->
```text
error: android.graphics.Bitmap class is not loaded in this dump; bitmap accounting has nothing to report. This can happen on Android dumps from screens that have not used Bitmap-backed images.
```

This message is misleading in one case. It says the class "is not loaded", but the real cause can be that its fields are not the ones HeapTrail expects. Check which it is:

- Run the plain summary and look for `android.graphics.Bitmap` in the class table. In the 186 MiB sample dump it lists 20 instances, and `--bitmaps` still fails.
  If the class is there, the dump has bitmaps but HeapTrail cannot size them.
- If the class is not there, the app had not used a bitmap when the dump was taken. Capture again after the images load.

When the dump has bitmaps HeapTrail cannot size, use these instead:

- `heaptrail -i heap.hprof --find-referrers android.graphics.Bitmap` to see who holds the bitmaps. On the 186 MiB sample dump, which has 20 of them, that
  shows an image-loading memory cache, `BitmapDrawable` state and Compose image wrappers:
```bash
heaptrail -i heap-b.hprof --find-referrers android.graphics.Bitmap --hops 1 --top 5
```

<!-- output: bitmaps-refs.txt from="Found 20" -->
```text
Found 20 target instance(s) for android.graphics.Bitmap

=== Direct referrers (1-hop) ===
  holder.field (or class[] for arrays)                          ref count
  sun.misc.Cleaner.referent                                            20
  coil.memory.RealStrongMemoryCache$InternalValue.bitmap               18
  android.graphics.drawable.BitmapDrawable$BitmapState.mBitmap         17
  androidx.compose.ui.graphics.AndroidImageBitmap.bitmap               16
  java.lang.ref.WeakReference.referent                                  1
```

- `adb shell dumpsys meminfo <package>` for the *Graphics* and native totals. Capture it with the dump, and attach it to a diff series with
  [`--native-context`](../compare/native-context.md).

## JSON

`--json` writes `heaptrail-bitmaps-<timestamp>.json`, or the path you give with `--json-out`. It has `entries` (each with `object_id`, `width`, `height`, `config`, `bpp`,
`pixel_bytes`, `location` and a `holder_summary` that is always null) and `total_pixel_bytes`.

## Gotchas

- **No capture flag.** `--bitmaps` analyzes a dump; it does not change how one is taken. Navigate to the image-heavy screen, wait for the images, capture, then run it.
- **Strings are not bitmaps.** The word `Bitmap` appears in the string table of many dumps ([`-l`](list-strings.md)) whether or not any instance exists.
- **No holder summary.** The report does not say who holds each bitmap. Trace the ids you care about.

## Related

- [Paths to a GC root](../holders/paths-to-root.md) finds what holds a bitmap.
- [Native context](../compare/native-context.md) records graphics and native totals beside a series.
- [Limitations](../reference/limitations.md) lists what each mode cannot do.
