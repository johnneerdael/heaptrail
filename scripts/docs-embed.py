#!/usr/bin/env python3
"""Fill the output blocks of the user guide from the captured command output.

A page quotes tool output like this:

    <!-- output: first-summary.txt from="Found a total" until="Top 5 largest" -->
    ```text
    ...this block is written by scripts/docs-embed.py...
    ```

The marker names a capture in docs/user-guide/_meta/outputs/ (see
scripts/docs-capture.sh). The fenced block that follows it is rewritten from the
capture, so a quoted line can never drift from what heaptrail printed.

Options on the marker (all optional, all quoted):

    from="text"      start at the first line that contains text
    until="text"     stop before the first later line that contains text
    through="text"   stop after the first later line that contains text
    head="N"         keep the first N lines of what is left
    keep             do not rewrite the block; scripts/docs-check.py still verifies
                     that every line comes from the capture (use for elisions)
    cmd              start the block with `$ <the command that produced the capture>`,
                     as a terminal session; use a `console` fence for it

Capture headers (`$ command`, `# exit N`) and the `File successfully processed in`
timing line are never included. Leading and trailing blank lines are trimmed.

usage: scripts/docs-embed.py [--check]     --check exits 1 if any block would change
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "user-guide"
OUTPUTS = GUIDE / "_meta" / "outputs"

MARK = re.compile(r"^\s*<!--\s*output:\s*(\S+)(.*?)-->\s*$")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
OPT = re.compile(r'(\w+)="([^"]*)"')


def load(name: str) -> list[str]:
    path = OUTPUTS / name
    if not path.exists():
        raise SystemExit(f"capture not found: {path.relative_to(ROOT)} (run scripts/docs-capture.sh)")
    lines = path.read_text().splitlines()
    # The runner writes two header lines: the command and its exit status.
    if lines and lines[0].startswith("$ "):
        lines = lines[1:]
    if lines and lines[0].startswith("# exit"):
        lines = lines[1:]
    return lines


def command_of(name: str) -> str:
    first = (OUTPUTS / name).read_text().splitlines()[:1]
    return first[0][2:].strip() if first and first[0].startswith("$ ") else name


def excerpt(name: str, opts: dict[str, str]) -> list[str]:
    lines = [ln.rstrip() for ln in load(name) if "File successfully processed in" not in ln]
    if "from" in opts:
        idx = next((i for i, ln in enumerate(lines) if opts["from"] in ln), None)
        if idx is None:
            raise SystemExit(f'{name}: from="{opts["from"]}" not found')
        lines = lines[idx:]
    if "until" in opts:
        idx = next((i for i, ln in enumerate(lines) if i > 0 and opts["until"] in ln), None)
        if idx is None:
            raise SystemExit(f'{name}: until="{opts["until"]}" not found')
        lines = lines[:idx]
    if "through" in opts:
        idx = next((i for i, ln in enumerate(lines) if i > 0 and opts["through"] in ln), None)
        if idx is None:
            raise SystemExit(f'{name}: through="{opts["through"]}" not found')
        lines = lines[: idx + 1]
    if "head" in opts:
        lines = lines[: int(opts["head"])]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def process(path: Path, check: bool) -> bool:
    src = path.read_text().splitlines()
    out: list[str] = []
    i = 0
    changed = False
    while i < len(src):
        line = src[i]
        out.append(line)
        m = MARK.match(line)
        i += 1
        if not m:
            continue
        name, rest = m.group(1), m.group(2)
        opts = dict(OPT.findall(rest))
        bare = OPT.sub("", rest)
        keep = re.search(r"(?<![\w=])keep(?![\w=])", bare) is not None
        with_cmd = re.search(r"(?<![\w=])cmd(?![\w=])", bare) is not None
        # The target is the next fenced block; only blank lines may separate it.
        j = i
        while j < len(src) and not src[j].strip():
            out.append(src[j])
            j += 1
        if j >= len(src) or not FENCE.match(src[j]):
            raise SystemExit(f"{path.relative_to(ROOT)}:{i}: output marker is not followed by a fenced block")
        fence = FENCE.match(src[j])
        indent, ticks = fence.group(1), fence.group(2)
        k = j + 1
        while k < len(src) and not (
            FENCE.match(src[k]) and FENCE.match(src[k]).group(2).startswith(ticks[0])
            and len(FENCE.match(src[k]).group(2)) >= len(ticks) and not FENCE.match(src[k]).group(3).strip()
        ):
            k += 1
        if k >= len(src):
            raise SystemExit(f"{path.relative_to(ROOT)}:{j + 1}: unterminated fenced block")
        old_body = src[j + 1 : k]
        out.append(src[j])
        if keep:
            out.extend(old_body)
        else:
            body = excerpt(name, opts)
            if with_cmd:
                body = ["$ " + command_of(name)] + body
            new_body = [(indent + ln) if ln else "" for ln in body]
            if new_body != old_body:
                changed = True
            out.extend(new_body)
        out.append(src[k])
        i = k + 1
    if changed and not check:
        path.write_text("\n".join(out) + "\n")
    return changed


def main() -> int:
    check = "--check" in sys.argv
    changed = []
    for p in sorted(GUIDE.rglob("*.md")):
        rel = p.relative_to(GUIDE).parts
        if rel[0] in ("_meta", "_snippets"):
            continue
        if process(p, check):
            changed.append(p.relative_to(ROOT).as_posix())
    for c in changed:
        print(("would change " if check else "updated ") + c)
    if not changed:
        print("all output blocks are up to date")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
