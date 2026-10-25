#!/usr/bin/env python3
"""Check the user guide against the tool it describes.

What it checks (see docs/user-guide/_meta/style.md):

  nav       every page in mkdocs.yml exists, and every page is in mkdocs.yml
  output    a fenced block that follows `<!-- output: name.txt -->` quotes only
            lines that the capture docs/user-guide/_meta/outputs/name.txt contains
            (a line that is only `...` marks an elision; timing lines are ignored)
  flags     every `--flag` in code spans and fenced blocks is a flag of heaptrail
            or of a tool the guide names (see EXTERNAL_FLAGS)
  voice     none of the filler words the style guide bans appears in prose
  ending    every page ends with a Related, Next steps or What you learned section

Run it from anywhere: python3 scripts/docs-check.py [--no-voice]
Exit status is 1 when a check fails, so CI can gate on it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "docs" / "user-guide"
OUTPUTS = GUIDE / "_meta" / "outputs"
MKDOCS = ROOT / "mkdocs.yml"

# Flags that belong to other tools the guide shows (adb, cargo, curl, jq, ...).
EXTERNAL_FLAGS = {
    "--force", "--git", "--proto", "--tlsv1.2", "--release", "--version", "--help",
    "--bin", "--profile", "--out", "--tmp", "--arg", "--argjson", "--exit-status",
    "--raw-output", "--slurpfile", "--fail", "--no-verify-ssl", "--strict",
    "--allow-dirty", "--verbose", "--live", "--format", "--dump", "--file",
    "--check", "--workspace", "--all-targets", "--all-features", "--all",
}

BANNED = [
    "simply", "just", "easy", "easily", "powerful", "seamless", "seamlessly",
    "robust", "leverage", "leverages", "utilize", "utilizes", "blazing",
]

TIMING = re.compile(r"processed in|^\[exit ")
ELISION = re.compile(r"^\s*(\.\.\.|…)\s*$")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
OUTPUT_MARK = re.compile(r"<!--\s*output:\s*(\S+)[^>]*?-->")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.\d+)?)")

errors: list[str] = []
warnings: list[str] = []


def err(path: Path, line: int, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}:{line}: {msg}")


def warn(path: Path, line: int, msg: str) -> None:
    warnings.append(f"{path.relative_to(ROOT)}:{line}: {msg}")


def pages() -> list[Path]:
    out = []
    for p in sorted(GUIDE.rglob("*.md")):
        rel = p.relative_to(GUIDE).parts
        if rel[0] in ("_meta", "_snippets"):
            continue
        out.append(p)
    return out


def nav_pages() -> list[str]:
    text = MKDOCS.read_text()
    nav = text[text.index("\nnav:") :] if "\nnav:" in text else ""
    return re.findall(r"([\w./-]+\.md)", nav)


def check_nav() -> None:
    listed = nav_pages()
    missing = [n for n in listed if not (GUIDE / n).exists()]
    for n in missing:
        errors.append(f"mkdocs.yml: nav entry {n} does not exist")
    have = {p.relative_to(GUIDE).as_posix() for p in pages()}
    for n in sorted(have - set(listed)):
        errors.append(f"{n}: page is not in the mkdocs.yml nav")
    dupes = {n for n in listed if listed.count(n) > 1}
    for n in sorted(dupes):
        errors.append(f"mkdocs.yml: nav lists {n} more than once")


def known_flags() -> set[str]:
    flags = set(EXTERNAL_FLAGS)
    for name in ("help-main", "help-capture"):
        f = OUTPUTS / f"{name}.txt"
        if f.exists():
            flags |= set(FLAG.findall(f.read_text()))
    return flags


def read_capture(name: str) -> set[str] | None:
    f = OUTPUTS / name
    if not f.exists():
        return None
    raw_lines = f.read_text().splitlines()
    # The runner writes two header lines: the command and its exit status.
    if raw_lines and raw_lines[0].startswith("$ "):
        raw_lines = raw_lines[1:]
    if raw_lines and raw_lines[0].startswith("# exit"):
        raw_lines = raw_lines[1:]
    return {raw.rstrip() for raw in raw_lines}


def capture_command(name: str) -> str | None:
    f = OUTPUTS / name
    if not f.exists():
        return None
    first = f.read_text().splitlines()[:1]
    if first and first[0].startswith("$ "):
        return first[0][2:].strip()
    return None


def norm_cmd(cmd: str) -> str:
    """Normalize a shell command for comparison: join continuations, drop quotes and spacing."""
    cmd = cmd.replace("\\\n", " ")
    cmd = re.sub(r"\s+", " ", cmd).strip()
    cmd = cmd.replace(" > /dev/null", "")
    return cmd.replace('"', "'")


def walk(path: Path):
    """Yield (line_no, text, in_fence, fence_info, mark) for every line of a page."""
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_indent = 0
    info = ""
    pending_mark: str | None = None
    for i, raw in enumerate(path.read_text().splitlines(), 1):
        m = FENCE.match(raw)
        if m:
            marker = m.group(2)
            if not in_fence:
                in_fence, fence_char, fence_len, info = True, marker[0], len(marker), m.group(3).strip()
                fence_indent = len(m.group(1))
                yield i, raw, True, info, pending_mark, True
                continue
            if marker[0] == fence_char and len(marker) >= fence_len and not m.group(3).strip():
                in_fence = False
                yield i, raw, True, info, pending_mark, True
                pending_mark = None
                continue
        if in_fence:
            # Dedent by the fence's own indentation (blocks inside admonitions and tabs).
            yield i, raw[fence_indent:] if raw[:fence_indent].strip() == "" else raw, True, info, pending_mark, False
        else:
            mk = OUTPUT_MARK.search(raw)
            if mk:
                pending_mark = mk.group(1)
            elif raw.strip() and not raw.lstrip().startswith("<!--"):
                pending_mark = None
            yield i, raw, False, "", None, False


def check_page(path: Path, flags: set[str], voice: bool) -> None:
    text = path.read_text()
    rel = path.relative_to(GUIDE).as_posix()
    headings = [ln for ln in text.splitlines() if ln.startswith("## ")]
    is_landing = rel == "index.md"
    if not is_landing and not any(
        h.startswith(("## Related", "## Next steps", "## What you learned")) for h in headings
    ):
        warn(path, 1, "page has no Related / Next steps / What you learned section")

    captures: dict[str, set[str] | None] = {}
    shell_text = []
    cur_shell: list[str] = []
    used: dict[str, int] = {}
    for line_no, raw, in_fence, info, mark, is_fence_line in walk(path):
        if in_fence and not is_fence_line and info.split(" ")[0] in ("bash", "sh", "shell", "console"):
            cur_shell.append(raw)
        elif not in_fence and cur_shell:
            shell_text.append("\n".join(cur_shell))
            cur_shell = []
        if mark and in_fence and is_fence_line:
            for name in [n.strip() for n in mark.split(",")]:
                used.setdefault(name, line_no)
        if in_fence and not is_fence_line:
            if mark:
                for name in [n.strip() for n in mark.split(",")]:
                    if name not in captures:
                        captures[name] = read_capture(name)
                        if captures[name] is None:
                            err(path, line_no, f"output capture {name} does not exist")
                    pool = captures[name]
                    if pool is None:
                        continue
                for name in [n.strip() for n in mark.split(",")]:
                    pool = captures.get(name)
                    if pool is None:
                        continue
                if (
                    raw.strip()
                    and not ELISION.match(raw)
                    and not TIMING.search(raw)
                    and not raw.lstrip().startswith("$ ")
                ):
                    pools = [captures[n.strip()] for n in mark.split(",") if captures.get(n.strip())]
                    if pools and not any(raw.rstrip() in p for p in pools):
                        err(path, line_no, f"line is not in {mark}: {raw.strip()[:90]}")
            for f in FLAG.findall(raw):
                if f not in flags:
                    err(path, line_no, f"unknown flag {f}")
        elif not in_fence:
            for span in re.findall(r"`([^`\n]+)`", raw):
                for f in FLAG.findall(span):
                    if f not in flags:
                        err(path, line_no, f"unknown flag {f}")
            if voice and not raw.lstrip().startswith(("<", "!!!", "|", "#", "---")):
                prose = re.sub(r"`[^`]*`", "", raw)
                prose = re.sub(r"\]\([^)]*\)", "]", prose)
                for word in BANNED:
                    if re.search(rf"\b{word}\b", prose, re.IGNORECASE):
                        warn(path, line_no, f"avoid the word “{word}”")
    if cur_shell:
        shell_text.append("\n".join(cur_shell))
    check_commands(path, shell_text, used)


def check_commands(path: Path, shell_text: list[str], used: dict[str, int]) -> None:
    """Every capture a page embeds must have its command shown on that page."""
    blob = norm_cmd("\n".join(shell_text))
    for name, line_no in used.items():
        want = capture_command(name)
        if not want:
            continue
        head = norm_cmd(want.split(" | ")[0].split(" && ")[0])
        if head not in blob:
            warn(path, line_no, f"no command block shows the command behind {name}: {head[:90]}")


def main() -> int:
    voice = "--no-voice" not in sys.argv
    check_nav()
    flags = known_flags()
    if not any(f.startswith("--find") for f in flags):
        warnings.append("no help captures found; flag check is limited (run scripts/docs-capture.sh)")
    for p in pages():
        check_page(p, flags, voice)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:  ", e)
    print(f"\n{len(pages())} pages, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
