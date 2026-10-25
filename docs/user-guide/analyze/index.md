# Analyze

These modes answer *what is in memory and what is big*. They work on a single dump. To find out what keeps
something alive, go to [Trace holders](../holders/index.md). To see what changed over time, go to [Compare](../compare/index.md).

## Start here

1. [Summary](summary.md) is the default mode. Run it first on any dump to see the shape of the heap.
2. [Leak suspects](leak-suspects.md) ranks the objects that keep the most alive, so you need no prior idea where to look.
3. [Content previews](preview-bytes.md) turn "a 5 MiB `char[]`" into "a JSON document".

## Your goal, and the page

| Your goal | Command | Page |
|---|---|---|
| See what takes the space, by class | `heaptrail -i heap.hprof` | [Summary](summary.md) |
| Rank classes by what they keep alive | `--retained-size` | [Retained size](retained-size.md) |
| Find what is wrong without knowing where to look | `--leak-suspects --exclude-soft-weak` | [Leak suspects](leak-suspects.md) |
| See the content of large arrays | `--preview-bytes 200` | [Content previews](preview-bytes.md) |
| List every string, or every large text array | `-l` | [List strings and arrays](list-strings.md) |
| Find the biggest bitmaps | `--bitmaps` | [Bitmaps](bitmaps.md) |
| Find the code that allocated something | `--allocation-sites` | [Allocation sites](allocation-sites.md) |

## Recipes

| Your problem | Recipe |
|---|---|
| One giant array and no idea what it is | [Identify a giant array](recipes/identify-a-giant-array.md) |
| The same large payload may be in memory many times | [Find duplicate payloads](recipes/find-duplicate-payloads.md) |
| A dump you did not take, from an app you do not know | [Triage an unfamiliar dump](recipes/triage-an-unfamiliar-dump.md) |

## Related

- [Concepts](../concepts/index.md) explains shallow and retained size.
- [Trace holders](../holders/index.md) is the next step once you have a class or an id.
- [Choose the right mode](../getting-started/choose-a-mode.md) maps questions to commands.
