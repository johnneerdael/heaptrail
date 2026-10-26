# Handle dumps safely

A heap dump is a copy of a process's memory. Anything the process held when you captured it is in the file:
passwords, API keys and session tokens, cookies, personal data, the contents of documents it had open. The file is
as sensitive as the most sensitive thing the app touches.

HeapTrail puts the contents in front of you, which is the point of it, and also the reason to be careful with its
output. This page lists where text from a dump can end up.

## Where dump contents appear

| What you run | What it can print |
|---|---|
| `-l` (list strings) | Every name in the dump's string table: class, field, method and file names, often more than 100,000 lines. It shows your code's structure, not the contents of strings. |
| `--preview-bytes N` | The first N bytes of large `char[]` and `byte[]` arrays: JSON bodies, XML preferences, tokens. |
| `-l --preview-bytes N` | A preview of every standalone array above the size threshold. |
| `--leak-suspects --preview-bytes N` | A preview of any suspect that is a primitive array. |
| `--paths-from-id`, `--find-referrers id:…` with `--preview-bytes` | A preview of the arrays on the path or at the target. |
| Class and field names | Names from your code, which may reveal product internals even when no values are shown. |

JSON reports carry class names, ids, counts and sizes. Most of them carry no array content. The exception is
`--leak-suspects --json`: with `--preview-bytes`, it writes the first 120 characters of a suspect's preview as
`preview_snippet`.

## Before you share

1. **Decide who needs the dump.** Most questions can be answered from a report instead of the file.
2. **Share the report, not the dump,** when you can. A suspect list or a diff has class names and numbers. Use the
   default `--preview-bytes 0`, which prints no array content, for output you will paste into a ticket.
3. **Read what you paste.** Previews often contain URLs, ids, tokens and names, and `-l` lists every class and field name. Quote only
   the lines you need.
4. **Keep dumps off shared storage.** Treat the file like a credential: restrict access, and delete it when the
   investigation is over. HeapTrail's [`.gitignore` ignores `*.hprof`](https://github.com/johnneerdael/heaptrail/blob/master/.gitignore) so
   that dumps are not committed by accident. Do the same in your own repositories.
5. **Rotate secrets** if a dump with live credentials leaves the control of the people who should see them.

!!! warning "HeapTrail does not redact"
    There is no flag that removes secrets from a dump or from a report. Previews are not scrubbed.
    If a privacy-aware report matters to you, run with `--preview-bytes 0` and share only the summary and the
    suspects.

## On a device or server

- A dump written to `/data/local/tmp` on an Android device is readable by the shell user. `android-capture` deletes it after
  pulling it, and cleans up older `*.hprof` files in that folder. A dump you take by hand stays until you remove it.
- A JVM dump written by `-XX:+HeapDumpOnOutOfMemoryError` lands in `HeapDumpPath`. Put that on a disk with restricted access,
  and prune it, so repeated crashes do not fill the disk.

## Related

- [Content previews](../analyze/preview-bytes.md) explains exactly what `--preview-bytes` prints.
- [List strings and arrays](../analyze/list-strings.md) for `-l`.
- [JSON output](../automate/json-output.md) lists what each report writes to a file.
