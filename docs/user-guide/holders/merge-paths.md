# Merge paths

When 47 activities leak, they usually leak the same way: one cache, one listener, one static holds all of them. `--paths-from-id` follows one instance at a time, so you would run it 47 times
and compare by eye. `--merge-paths` does the comparison for you. It follows the path of *every instance of the object's class* and folds them into one tree, with a count on each hop.

```bash
heaptrail -i heap.hprof --paths-from-id 534941512 --merge-paths --retained-size --max-depth 12
```

The id picks the class. Any instance will do. Take it from the [largest retained instances](../analyze/retained-size.md), a [leak suspect](../analyze/leak-suspects.md), or any other report that
[names an id](../concepts/object-ids.md).

## Read the tree

<!-- output: merge-fold.txt from="Target:" head="22" -->
```text
Target: kotlin.reflect.jvm.internal.impl.serialization.deserialization.ProtoBasedClassDataFinder — 5 instance(s) merged.
(merge verified via dominator convergence)
  ↑ field classDataFinder in kotlin.reflect.jvm.internal.impl.serialization.deserialization.builtins.BuiltInsPackageFragmentImpl  [5×]
    ↑ field containingDeclaration in kotlin.reflect.jvm.internal.impl.serialization.deserialization.descriptors.DeserializedClassDescriptor  [3×]
      ↑ field this$0 in kotlin.reflect.jvm.internal.impl.serialization.deserialization.descriptors.DeserializedClassDescriptor$DeserializedClassTypeConstructor  [1×]
        ↑ field constructor in kotlin.reflect.jvm.internal.impl.types.SimpleTypeImpl  [1×]
          ↑ field outType in kotlin.reflect.jvm.internal.impl.descriptors.impl.ValueParameterDescriptorImpl  [1×]
            ↑ field referent in java.lang.ref.SoftReference  [1×]
              ↑ field value in kotlin.reflect.jvm.internal.ReflectProperties$LazySoftVal  [1×]
                ↑ field descriptor$delegate in kotlin.reflect.jvm.internal.KParameterImpl  [1×]
                  ↑ field parameter in com.squareup.moshi.kotlin.reflect.KotlinJsonAdapter$Binding  [1×]
                    ↑ java.lang.Object[][]  [1×]
                      ↑ field elementData in java.util.ArrayList  [1×]
                        ↑ field nonIgnoredBindings in com.squareup.moshi.kotlin.reflect.KotlinJsonAdapter  [1×]
      ↑ field referent in java.lang.ref.SoftReference  [2×]
        ↑ field value in kotlin.reflect.jvm.internal.ReflectProperties$LazySoftVal  [2×]
          ↑ field descriptor$delegate in kotlin.reflect.jvm.internal.KClassImpl$Data  [2×]
            ↑ field _value in kotlin.SafePublicationLazyImpl  [2×]
              ↑ field data in kotlin.reflect.jvm.internal.KClassImpl  [2×]
                ↑ field type in io.ktor.util.reflect.TypeInfo  [1×]
                  ↑ field type in io.ktor.util.AttributeKey  [1×]
                ↑ kotlin.reflect.KClass[][]  [1×]
```

The first line names the class and how many instances were merged: 5 `ProtoBasedClassDataFinder` objects. Each following line is one hop *up* from the object, as a field of a holder class:

- `↑ field classDataFinder in …BuiltInsPackageFragmentImpl  [5×]` means all five instances are held by that field.
- Indentation goes up the chain: the child line is the holder of the line above it.
- The count in brackets is how many of the instances pass through that hop. When paths split, the count falls: `[5×]` becomes `[3×]` and `[2×]`, and each branch continues on its own.
- A hop through an array has no field name: `↑ java.util.concurrent.ConcurrentHashMap$Node[][]  [1×]`.

The shared hops at the top are the common holder you are after. Here, all five finders hang off a Kotlin reflection package fragment. A tree whose first hop says `[47×]` tells you in one line that all 47 leaked instances share a holder.

## Textual or graph-verified

The line under the title says how the merge was done.

| Banner | Meaning |
|---|---|
| `(merge verified via dominator convergence)` | You passed `--retained-size`. The fold is checked against the dominator tree. |
| `(textual merge — re-run with --retained-size for graph-verified convergence)` | Paths are folded by comparing holder class and field names. Two paths that merely share names are folded together even if they never meet at the same object. |

The textual merge is usually right. Use `--retained-size` when the answer matters. In the JSON, the choice is `graph_verified`.

## The target must be an instance

The id has to belong to an object that is an instance of a class. A primitive array, or an id that is not in the dump, fails with a message that says "not yet implemented" and means "not found as an instance":

```bash
heaptrail -i heap.hprof --paths-from-id 1661812752 --merge-paths
```

<!-- output: merge-prim.txt from="error:" -->
```text
error: not yet implemented: object id not found in dump (--merge-paths)
```

For a primitive array, use plain [`--paths-from-id`](paths-to-root.md).

## What it costs

HeapTrail walks every instance on its own, and each hop of each walk reads the file. So the time is roughly *instances × hops × the time of one pass*. On a 224 MiB dump, merging 5 instances to depth 12 took 15 seconds. On a 186 MiB dump, merging 10 instances to depth 8 took 11 seconds.

!!! warning "There is no instance cap"
    A class with thousands of instances will run for a very long time. Do not point `--merge-paths` at `java.util.ArrayList` or at a model class with half a million instances. Pick a class with tens of instances, such as an
    activity, a view model or a manager, and lower `--max-depth` to the depth you need.

## With weak references excluded

`--exclude-soft-weak` skips weak holders while walking. The tree for the same five instances changes shape, because two of the paths used to go through a `SoftReference`:

```bash
heaptrail -i heap.hprof --paths-from-id 534941512 --merge-paths --exclude-soft-weak --max-depth 12
```

<!-- output: merge-sw.txt from="Target:" head="12" -->
```text
Target: kotlin.reflect.jvm.internal.impl.serialization.deserialization.ProtoBasedClassDataFinder — 5 instance(s) merged.
(textual merge — re-run with --retained-size for graph-verified convergence)
  ↑ field classDataFinder in kotlin.reflect.jvm.internal.impl.serialization.deserialization.builtins.BuiltInsPackageFragmentImpl  [5×]
    ↑ field containingDeclaration in kotlin.reflect.jvm.internal.impl.serialization.deserialization.descriptors.DeserializedClassDescriptor  [3×]
      ↑ field this$0 in kotlin.reflect.jvm.internal.impl.serialization.deserialization.descriptors.DeserializedClassDescriptor$DeserializedClassTypeConstructor  [3×]
        ↑ field constructor in kotlin.reflect.jvm.internal.impl.types.SimpleTypeImpl  [3×]
          ↑ field outType in kotlin.reflect.jvm.internal.impl.descriptors.impl.ValueParameterDescriptorImpl  [1×]
            ↑ java.lang.Object[][]  [1×]
              ↑ field elementData in java.util.ArrayList  [1×]
                ↑ field unsubstitutedValueParameters in kotlin.reflect.jvm.internal.impl.serialization.deserialization.descriptors.DeserializedClassConstructorDescriptor  [1×]
                  ↑ field arg$0 in kotlin.reflect.jvm.internal.KCallableImpl$$Lambda$8  [1×]
                    ↑ field initializer in kotlin.reflect.jvm.internal.ReflectProperties$LazySoftVal  [1×]
```

Without the flag, a branch ran `↑ field referent in java.lang.ref.SoftReference [2×]`. With it, that branch is gone and the paths continue through other holders. See [Exclude weak references](exclude-soft-weak.md).

## JSON

`--json` writes the tree as `target_label`, `instance_count`, `graph_verified` and `root`, a nested object of `source_class`, `field_name`, `instance_count` and `children`.

```bash
heaptrail -i heap.hprof --paths-from-id 534941512 --merge-paths --max-depth 3 --json --json-out reports/merge.json > /dev/null
```

<!-- output: merge-json.txt -->
```text
{"target_label":"kotlin.reflect.jvm.internal.impl.serialization.deserialization.ProtoBasedClassDataFinder","instance_count":5,"graph_verified":false,"first_hop":{"source_class":"kotlin.reflect.jvm.internal.impl.serialization.deserialization.builtins.BuiltInsPackageFragmentImpl","field_name":"classDataFinder","instance_count":5}}
```

## Options

| Flag | Effect |
|---|---|
| `--merge-paths` | Merge the paths of all instances of the id's class. Only valid with `--paths-from-id`. |
| `--retained-size` | Verify the merge against the dominator tree. |
| `--exclude-soft-weak` | Skip weak, soft and phantom holders. |
| `--max-depth <N>` | The depth of each walk (12 by default). The main lever on run time. |
| `--mapping`, `--auto-mapping` | Restore real names. |
| `--json`, `--json-out` | Write the tree as JSON. |

## Related

- [Paths to a GC root](paths-to-root.md) follows one instance.
- [Who holds an activity](recipes/who-holds-an-activity.md) uses it on a leaking activity.
- [Leak suspects](../analyze/leak-suspects.md) is a source of instance ids.
