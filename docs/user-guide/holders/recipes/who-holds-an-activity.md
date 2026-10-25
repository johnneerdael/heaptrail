# Who holds an activity

<div class="recipe-meta" markdown>
<span><strong>Uses</strong> `--find-referrers`, `--merge-paths`, `--exclude-soft-weak`</span>
<span><strong>Works on</strong> Android dumps</span>
<span><strong>Time</strong> five minutes</span>
<span><strong>Undo</strong> nothing to undo: every step only reads the dump</span>
</div>

## The problem

An `Activity` is supposed to disappear when the user leaves it. If a static, a singleton, a long-running coroutine or an image request still holds it, the whole view tree and everything it references stays in memory.
A leak shows up as **more instances of the activity than the screen needs**, and a holder that outlives the screen.

## The solution

1. Count the instances. If there is one, there is no activity leak yet. If there are more than the screens you have open, continue.

    ```bash
    heaptrail -i heap.hprof --find-referrers com.example.MainActivity --hops 2 --exclude-soft-weak
    ```

    The first line says how many instances were found: `Found 1 target instance(s)` or `Found 3 …`.

2. Read the holders. A real dump of an Android TV app has one `MainActivity`, held by many things:

    ```bash
    heaptrail -i heap-b.hprof --find-referrers com.nexio.tv.MainActivity --hops 2
    ```

    <!-- output: ref-activity.txt from="Found 1" -->
    ```text
    Found 1 target instance(s) for com.nexio.tv.MainActivity

    === Direct referrers (1-hop) ===
      holder.field (or class[] for arrays)                                                     ref count
      androidx.compose.ui.graphics.layer.ViewLayer.mContext                                          122
      java.lang.Object[][]                                                                            82
      coil.request.ImageRequest.context                                                               47
      coil.size.DisplaySizeResolver.context                                                           14
      android.widget.ImageButton.mContext                                                             12
      com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernCarouselCard$2$1$1.$context                  8
      android.widget.LinearLayout.mContext                                                             7
      androidx.compose.foundation.AndroidEdgeEffectOverscrollFactory.context                           6
      android.widget.FrameLayout.mContext                                                              4
      com.nexio.tv.ui.screens.home.ModernHomeContentKt$ModernHomeContent$10$1.$lifecycleOwner          4
      android.widget.TextView.mContext                                                                 4
      java.util.LinkedHashMap$LinkedHashMapEntry.value                                                 4
      com.nexio.tv.MainActivity$onCreate$6$2$1$1$17$1.this$0                                           4
      com.nexio.tv.MainActivity$onCreate$6$2$1$1$19$1.this$0                                           4
      com.nexio.tv.ui.screens.home.ModernHomeRowsKt$ModernRowSection$1$5$1.$context                    3
      com.android.internal.policy.PhoneLayoutInflater.mContext                                         3
      androidx.compose.foundation.EdgeEffectWrapper.context                                            3
      androidx.compose.runtime.StaticValueHolder.value                                                 3
      com.nexio.tv.MainActivity$onCreate$6$2$1$1$13$1.this$0                                           3
      android.view.View.mContext                                                                       3

    === 2-hop referrers (X holds Object[] which holds target) ===
      holder.field (or class[] for arrays)       ref count
      androidx.compose.runtime.SlotWriter.slots         12
      androidx.compose.runtime.SlotTable.slots          12
      android.util.SparseArray.mValues                   1
    ```

3. Sort the holders into two groups.
    - **Part of the UI.** `View.mContext`, `ImageButton.mContext`, `TextView.mContext`, `LinearLayout.mContext`, `PhoneLayoutInflater.mContext`. Every view keeps its context. These are expected, and they die with the views.
    - **Not part of the UI.** `coil.request.ImageRequest.context` (47) and `coil.size.DisplaySizeResolver.context` (14) belong to an image-loading library, `StaticValueHolder.value` to Compose, and the
      `MainActivity$onCreate$…` lambdas hold `this$0`. These are the ones that could outlive the screen. Ask whether each should.

4. If there are several instances, find what they share. Take any instance id and fold the paths:

    ```bash
    heaptrail -i heap.hprof --paths-from-id <activity-id> --merge-paths --retained-size --exclude-soft-weak --max-depth 8
    ```

    The first hops that show `[N×]` with `N` equal to the instance count are the common holder: an event bus, a static map, an application-scoped object. See [Merge paths](../merge-paths.md).

## How it works

An activity has many legitimate holders, so the question is never "is it held?" but "is it held by something that outlives it?". The referrer table shows every holder at once. The path or the merged
tree shows the chain from the holder to a GC root, so you can judge its lifetime.

## Variations

- **Always add `--exclude-soft-weak` on Android.** LeakCanary's `KeyedWeakReference` and the framework's `WeakReference<Activity>` otherwise sit at the top of every path.
- **The holder is a lambda.** A name like `MainActivity$onCreate$6$2$1$1$17$1.this$0` is a Kotlin lambda that captured the activity. Trace the lambda with `--paths-from-id` to see who keeps the lambda.
- **There are no instances.** If `Found 0 target instance(s)` appears, the activity is not in the dump: it was not loaded, or the name is obfuscated. Add `--mapping` for a release build.
- **The holder is a coroutine.** Rows such as `…$1.L$0` are fields of generated coroutine state machines. They hold what a suspended function captured, so check whether the coroutine's scope outlives the screen.

## Related

- [Find referrers](../find-referrers.md) explains every column.
- [Merge paths](../merge-paths.md) folds the paths of several instances.
- [Exclude weak references](../exclude-soft-weak.md) for the Android noise.
