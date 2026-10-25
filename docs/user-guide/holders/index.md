# Trace holders

An object stays in memory because something holds a reference to it. These modes find that something: the field, array slot or static that points at a class
or an object, and the chain of holders that leads up to a GC root. This is the half of a leak investigation that comes after you know *what* is big.

## Start here

1. [Find referrers](find-referrers.md) shows every field that holds a class or an object. It is the most-used tracing mode.
2. [Paths to a GC root](paths-to-root.md) follows one object up to the root, one hop per line.
3. [Exclude weak references](exclude-soft-weak.md) removes the weak-reference noise that buries real holders on Android.

## Your goal, and the page

| Your goal | Command | Page |
|---|---|---|
| Who holds every instance of a class? | `--find-referrers <class> --hops 2` | [Find referrers](find-referrers.md) |
| Who holds this one object? | `--find-referrers id:<id>` | [Find referrers](find-referrers.md#target-an-object) |
| Who holds a whole package of classes, or every `$Itr`? | `--target-glob 'pkg.**'` | [Target glob](target-glob.md) |
| Collapse a long holder table into owners | `--group-holders` | [Group holders](group-holders.md) |
| Follow an object up to a GC root | `--paths-from-id <id>` | [Paths to a GC root](paths-to-root.md) |
| Do many instances share one holder? | `--paths-from-id <id> --merge-paths` | [Merge paths](merge-paths.md) |
| Ignore weak, soft and phantom references | `--exclude-soft-weak` | [Exclude weak references](exclude-soft-weak.md) |

## Which mode when

| Use | When |
|---|---|
| `--find-referrers` | You have a class or an id and want *every* holder, including class statics. |
| `--paths-from-id` | You have one id and want the *chain* to a root, with thread names for thread-owned roots. |
| Both | A path ends in `orphan`, or loops. Ask referrers about the last id. |

## Recipes

| Your problem | Recipe |
|---|---|
| Is my `Activity` held by something that outlives it? | [Who holds an activity](recipes/who-holds-an-activity.md) |
| A path says `orphan`, and a cache is the suspect | [Find the static that holds a cache](recipes/find-the-static-that-holds-a-cache.md) |

## Related

- [Concepts: GC roots and paths](../concepts/gc-roots-and-paths.md) explains what a path proves.
- [Analyze](../analyze/index.md) finds what to trace.
- [Object ids](../concepts/object-ids.md) says where ids come from.
