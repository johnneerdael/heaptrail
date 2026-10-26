"""Find the prose in a Markdown page, so the naming rule applies to sentences and not to code.

The brand guide says: write HeapTrail in prose and branding; the executable stays `heaptrail`.
So a bare lowercase "heaptrail" in a sentence is wrong, while `heaptrail` in code, a command in a
fence, a URL, a path, a link target or an HTML attribute is right.

Used by scripts/docs-check.py. Run on its own, it lists (or with --fix, repairs) the lowercase
names in the pages it is given:

    python3 scripts/docs_prose.py [--fix] <page.md> ...
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
SKIP_LINE = re.compile(r"^\s*(--8<--|\*\[[^\]]+\]:)")

# Things inside a line that are not prose.
PROTECT = re.compile(
    r"""
      (?P<code>(?P<tick>`+)(?:(?!(?P=tick)).)+(?P=tick))      # inline code
    | (?P<dest>\]\([^)\s]*(?:\s+"[^"]*")?\))                  # link or image destination
    | (?P<refdef>^\s*\[[^\]]+\]:\s*\S+)                       # [id]: target
    | (?P<auto><https?://[^>]+>)                              # <https://...>
    | (?P<url>https?://[^\s)<>\]"']+)                         # bare URL
    | (?P<tag><[A-Za-z/!][^>]*>)                              # HTML tag or one-line comment
    | (?P<attrs>\{[^}]*\})                                    # { .class #id } attribute list
    """,
    re.X,
)

# A product name in a sentence. Not part of a path, URL, file name, option or identifier.
NAME = re.compile(r"(?<![\w/.@#=:\-])heaptrail(?![\w/@=\-])(?!\.\w)")


def prose_spans(text: str) -> list[tuple[int, int]]:
    """Return (start, end) offsets of the prose in text."""
    spans: list[tuple[int, int]] = []
    offset = 0
    lines = text.splitlines(keepends=True)
    in_fence: str | None = None
    in_comment = False
    in_pre = False

    # YAML front matter at the top of a page is configuration.
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    for i in range(start):
        offset += len(lines[i])

    for line in lines[start:]:
        here = offset
        offset += len(line)
        stripped = line.strip()

        if in_fence is not None:
            m = FENCE.match(line)
            if m and m.group(1)[0] == in_fence[0] and len(m.group(1)) >= len(in_fence) and stripped.strip("`~") == "":
                in_fence = None
            continue
        m = FENCE.match(line)
        if m:
            in_fence = m.group(1)
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if "<!--" in line and "-->" not in line:
            in_comment = True
            continue
        if in_pre:
            if re.search(r"</pre\s*>", line, re.I):
                in_pre = False
            continue
        if re.search(r"<pre[\s>]", line, re.I) and not re.search(r"</pre\s*>", line, re.I):
            in_pre = True
            continue
        if SKIP_LINE.match(line):
            continue

        body = line.rstrip("\n")
        cursor = 0
        for m in PROTECT.finditer(body):
            if m.start() > cursor:
                spans.append((here + cursor, here + m.start()))
            cursor = m.end()
        if cursor < len(body):
            spans.append((here + cursor, here + len(body)))
    return spans


def find_names(text: str) -> list[tuple[int, int, str]]:
    """Return (line, column, context) for every lowercase product name in prose."""
    found = []
    for a, b in prose_spans(text):
        for m in NAME.finditer(text, a, b):
            line = text.count("\n", 0, m.start()) + 1
            col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
            lo = max(a, m.start() - 28)
            hi = min(b, m.end() + 28)
            found.append((line, col, text[lo:hi].strip()))
    return found


def fix_names(text: str) -> str:
    """Capitalise the product name wherever it is prose."""
    out = []
    last = 0
    for a, b in prose_spans(text):
        out.append(text[last:a])
        out.append(NAME.sub("HeapTrail", text[a:b]))
        last = b
    out.append(text[last:])
    return "".join(out)


def main(argv: list[str]) -> int:
    fix = "--fix" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    total = 0
    for path in paths:
        text = path.read_text()
        names = find_names(text)
        total += len(names)
        if fix and names:
            path.write_text(fix_names(text))
        for line, col, ctx in names:
            print(f"{path}:{line}:{col}: {ctx}")
    print(f"{total} lowercase product name(s)" + (" fixed" if fix else ""), file=sys.stderr)
    return 0 if fix or total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
