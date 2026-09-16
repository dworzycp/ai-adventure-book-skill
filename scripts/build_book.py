#!/usr/bin/env python3
"""Build a self-contained interactive adventure-book HTML file.

Usage:
    python3 build_book.py --content book.json --out adventure.html [--source doc.md] [--quiet]

book.json (paths are relative to the JSON file):
{
  "title": "The Quest for the Portal",
  "subtitle": "A knight's journey through AGENTS.md",
  "theme": "knight",                       # preset name, or {"extends": "knight", "colors": {...}, ...}
  "source": "../AGENTS.md",                # the document being retold (optional but strongly recommended)
  "cover":  {"scene": "scenes/cover.svg", "blurb": "cover.md", "eyebrow": "An interactive adventure"},
  "stages": ["stages/01-gates.md", "stages/02-forge.md", { ...inline stage object... }],
  "ending": {"scene": "scenes/end.svg", "blurb": "ending.md", "recap": ["**VPN** first, always", "..."]},
  "popouts": [ ...optional book-wide pop-outs, same shape as stage pop-outs... ]
}

Stage markdown file format:
---
id: gates
title: The Gates of the Keep
chapter: Chapter I
source: Local Development Setup          # heading in the source doc; its section becomes the "original scroll"
scene: scenes/01-gates.svg                # optional; omit for a generated themed backdrop
---
Narrative in Markdown. Mark the words that hide something real with [[the Veil|vpn]]
(display text | pop-out id) or [[docker]] (id doubles as display text).

## popout: vpn
title: VPN
source: Local Development Setup           # optional heading whose section is shown under "From the original"

Plain-language explanation in Markdown. May include `code` and fenced blocks.

Every prose field (narrative, explanation, blurb, recap item) is Markdown. Every scene is inline SVG
(a string starting with <svg, or a path to a .svg file). Fields ending in .md/.svg that point to an
existing file are loaded from that file.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

WARNINGS: list[str] = []
TERMS: dict[str, str] = {}  # pop-out id -> first display text seen in a narrative


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------- markdown
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_ITALIC = re.compile(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])|(?<![_\w])_(?!\s)(.+?)(?<!\s)_(?![_\w])")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_POPOUT = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_UL = re.compile(r"^(\s*)[-*+]\s+(.*)$")
_OL = re.compile(r"^(\s*)\d+[.)]\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


def inline(text: str, popout_ids: set[str] | None = None) -> str:
    """Convert inline Markdown. Code spans are protected from further processing."""
    codes: list[str] = []

    def stash(m: re.Match) -> str:
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = _INLINE_CODE.sub(stash, text)
    text = html.escape(text, quote=False)

    def popout(m: re.Match) -> str:
        term = m.group(1).strip()
        pid = (m.group(2) or slugify(term)).strip()
        if popout_ids is not None:
            popout_ids.add(pid)
            TERMS.setdefault(pid, term)
        # an <a>, not a <button>: Chrome renders buttons as inline-block, which centres wrapped lines and
        # strands trailing punctuation on its own line
        return f'<a class="popout-link" role="button" tabindex="0" data-popout="{html.escape(pid, quote=True)}">{term}</a>'

    text = _POPOUT.sub(popout, text)
    text = _LINK.sub(lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', text)
    text = _BOLD.sub(lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
    text = _ITALIC.sub(lambda m: f"<em>{m.group(1) or m.group(2)}</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)
    return text


def markdown(md: str, popout_ids: set[str] | None = None) -> str:
    """A deliberately small Markdown converter: headings, paragraphs, lists, fenced code, quotes, tables, raw HTML."""
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    para: list[str] = []

    def flush_para() -> None:
        if para:
            out.append("<p>" + inline(" ".join(s.strip() for s in para), popout_ids) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush_para()
            fence = stripped[:3]
            lang = stripped[3:].strip()
            i += 1
            code: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith(fence):
                code.append(lines[i])
                i += 1
            i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>" + html.escape("\n".join(code)) + "</code></pre>")
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("<") and not stripped.startswith("<code"):
            flush_para()
            out.append(line)
            i += 1
            continue

        m = _HEADING.match(stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(f"<h{level}>" + inline(m.group(2), popout_ids) + f"</h{level}>")
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            flush_para()
            quote: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].lstrip())
                i += 1
            out.append("<blockquote>" + markdown("\n".join(quote), popout_ids) + "</blockquote>")
            continue

        if "|" in stripped and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]):
            flush_para()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{inline(c, popout_ids)}</th>" for c in header)
            tbody = "".join("<tr>" + "".join(f"<td>{inline(c, popout_ids)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue

        if _UL.match(line) or _OL.match(line):
            flush_para()
            block, i = _list(lines, i, popout_ids)
            out.append(block)
            continue

        para.append(line)
        i += 1

    flush_para()
    return "\n".join(out)


def _list(lines: list[str], i: int, popout_ids: set[str] | None) -> tuple[str, int]:
    """Parse a (possibly nested) list starting at line i. Returns (html, next_index)."""
    first = _UL.match(lines[i]) or _OL.match(lines[i])
    ordered = bool(_OL.match(lines[i])) and not _UL.match(lines[i])
    indent = len(first.group(1))
    tag = "ol" if ordered else "ul"
    items: list[str] = []
    while i < len(lines):
        line = lines[i]
        m = _UL.match(line) or _OL.match(line)
        if not m or len(m.group(1)) < indent:
            break
        if len(m.group(1)) > indent:
            nested, i = _list(lines, i, popout_ids)
            items[-1] = items[-1][: -len("</li>")] + nested + "</li>"
            continue
        text = m.group(2)
        i += 1
        # continuation lines (indented, non-list)
        while i < len(lines) and lines[i].strip() and not (_UL.match(lines[i]) or _OL.match(lines[i])) and lines[i].startswith(" " * (indent + 2)):
            text += " " + lines[i].strip()
            i += 1
        items.append(f"<li>{inline(text, popout_ids)}</li>")
    return f"<{tag}>" + "".join(items) + f"</{tag}>", i


# --------------------------------------------------------------------------- source document
def norm_heading(text: str) -> str:
    text = re.sub(r"`", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


class SourceDoc:
    def __init__(self, path: Path):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.lines = self.text.split("\n")
        self.headings: list[tuple[int, int, str]] = []  # (line_no, level, text)
        in_fence = False
        for n, line in enumerate(self.lines):
            if line.strip().startswith("```") or line.strip().startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = _HEADING.match(line.strip())
            if m:
                self.headings.append((n, len(m.group(1)), m.group(2).strip()))
        self.used: set[int] = set()

    def find(self, heading: str) -> tuple[int, int, str] | None:
        target = norm_heading(heading)
        exact = [h for h in self.headings if norm_heading(h[2]) == target]
        if len(exact) > 1:
            warn(f"heading '{heading}' appears {len(exact)} times in {self.path.name}; using the first")
        if exact:
            return exact[0]
        loose = [h for h in self.headings if target and target in norm_heading(h[2])]
        if len(loose) == 1:
            return loose[0]
        return None

    def section(self, heading: str) -> str | None:
        hit = self.find(heading)
        if not hit:
            return None
        start, level, _ = hit
        self.used.add(start)
        end = len(self.lines)
        for n, lvl, _t in self.headings:
            if n > start and lvl <= level:
                end = n
                break
        return "\n".join(self.lines[start:end]).strip()

    def uncovered(self, max_level: int = 2) -> list[str]:
        """Headings (at or above max_level) whose section was never referenced, directly or via a parent."""
        covered_ranges: list[tuple[int, int]] = []
        for start in self.used:
            level = next(l for n, l, _ in self.headings if n == start)
            end = len(self.lines)
            for n, lvl, _t in self.headings:
                if n > start and lvl <= level:
                    end = n
                    break
            covered_ranges.append((start, end))
        def covered(n: int) -> bool:
            return any(a <= n < b for a, b in covered_ranges)

        def children(idx: int) -> list[int]:
            n, lvl, _ = self.headings[idx]
            kids = []
            for m, l2, _t in self.headings[idx + 1:]:
                if l2 <= lvl:
                    break
                if l2 == lvl + 1:
                    kids.append(m)
            return kids

        out = []
        for idx, (n, lvl, text) in enumerate(self.headings):
            if lvl == 1 or lvl > max_level:
                continue
            if covered(n):
                continue
            kids = children(idx)
            if kids and all(covered(k) for k in kids):
                continue  # container heading whose subsections are all told
            out.append(text)
        return out


# --------------------------------------------------------------------------- content loading
def load_field(value, base: Path, kinds=(".md", ".svg"), alt_base: Path | None = None):
    """If value is a relative path to an existing file with a known suffix, return its contents.

    Paths resolve against the book.json directory first, then (for stage files) the stage's own directory.
    """
    if isinstance(value, str) and value.lower().endswith(kinds) and "\n" not in value and len(value) < 400:
        for b in [base] + ([alt_base] if alt_base else []):
            p = (b / value).resolve()
            if p.is_file():
                return p.read_text(encoding="utf-8")
        warn(f"referenced file not found: {value} (looked in {base}" + (f" and {alt_base}" if alt_base else "") + ")")
        return ""
    return value


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n")
    meta: dict = {}
    for n in range(1, len(parts)):
        if parts[n].strip() == "---":
            body = "\n".join(parts[n + 1:])
            return meta, body
        if ":" in parts[n]:
            k, v = parts[n].split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return {}, text


_POPOUT_HEADING = re.compile(r"^##\s*popout\s*:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
# "## note" / "## technical" holds a short plain-fact box shown at the foot of the stage panel
_NOTE_HEADING = re.compile(r"^##\s*(?:note|technical)\b[^\n]*\n(.*?)(?=^##\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL)


def parse_stage_markdown(text: str, base: Path, stage_dir: Path | None = None) -> dict:
    meta, body = parse_frontmatter(text)
    stage: dict = {k: v for k, v in meta.items()}
    if "source" in stage:
        stage["sourceHeading"] = stage.pop("source")
    note_match = _NOTE_HEADING.search(body)
    if note_match:
        stage["note"] = note_match.group(1).strip()
        body = body[:note_match.start()] + body[note_match.end():]
    chunks = _POPOUT_HEADING.split(body)
    stage["narrative"] = chunks[0].strip()
    popouts = []
    for k in range(1, len(chunks), 2):
        pid = chunks[k].strip()
        block = chunks[k + 1]
        p: dict = {"id": pid}
        lines = block.strip("\n").split("\n")
        n = 0
        while n < len(lines) and re.match(r"^(title|term|source|sourceHeading)\s*:", lines[n]):
            key, val = lines[n].split(":", 1)
            p[key.strip()] = val.strip().strip('"').strip("'")
            n += 1
        p["explanation"] = "\n".join(lines[n:]).strip()
        if "source" in p and not p["source"].lower().endswith(".md"):
            # a bare heading name; resolved against the source document later
            p["sourceHeading"] = p.pop("source")
        popouts.append(p)
    stage["popouts"] = popouts
    if "scene" in stage:
        stage["scene"] = load_field(stage["scene"], base, alt_base=stage_dir)
    return stage


def resolve_stage(raw, base: Path) -> dict:
    if isinstance(raw, str):
        text = load_field(raw, base, kinds=(".md",))
        if not text:
            raise SystemExit(f"stage file missing or empty: {raw}")
        stage = parse_stage_markdown(text, base, stage_dir=(base / raw).resolve().parent)
        stage.setdefault("id", slugify(Path(raw).stem))
        return stage
    stage = dict(raw)
    stage["narrative"] = load_field(stage.get("narrative", ""), base)
    stage["scene"] = load_field(stage.get("scene"), base)
    if "source" in stage and "sourceHeading" not in stage:
        stage["sourceHeading"] = stage.pop("source")
    for p in stage.get("popouts", []):
        p["explanation"] = load_field(p.get("explanation", ""), base)
    return stage


def resolve_theme(theme, themes: dict) -> dict:
    default = themes["knight"]
    if theme is None:
        return dict(default)
    if isinstance(theme, str):
        if theme not in themes or theme.startswith("_"):
            raise SystemExit(f"unknown theme '{theme}'. Available: {', '.join(k for k in themes if not k.startswith('_'))}")
        return dict(themes[theme])
    base = themes.get(theme.get("extends", "knight"), default)
    merged = dict(base)
    for key in ("colors", "fonts", "vocabulary"):
        merged[key] = {**base.get(key, {}), **theme.get(key, {})}
    for key in ("name", "sceneStyle", "ornament", "typeScale", "dropCap", "panelWidth"):
        if key in theme:
            merged[key] = theme[key]
    return merged


def theme_css(theme: dict) -> str:
    def kebab(k: str) -> str:
        return re.sub(r"(?<=[a-z])(?=[A-Z0-9])", "-", k).lower()

    lines = [f"  --{kebab(k)}: {v};" for k, v in theme.get("colors", {}).items()]
    fonts = theme.get("fonts", {})
    lines.append(f"  --type-scale: {theme.get('typeScale', 1)};")
    if theme.get("panelWidth"):
        lines.append(f"  --panel-width: {theme['panelWidth']};")
    lines.append(f"  --font-display: {fonts.get('display', 'Georgia, serif')};")
    lines.append(f"  --font-body: {fonts.get('body', 'Georgia, serif')};")
    return "\n".join(lines)


# --------------------------------------------------------------------------- build
def build(content_path: Path, out_path: Path, source_override: Path | None, quiet: bool) -> int:
    base = content_path.parent
    book = json.loads(content_path.read_text(encoding="utf-8"))
    themes = json.loads((ASSETS / "themes.json").read_text(encoding="utf-8"))
    template = (ASSETS / "template.html").read_text(encoding="utf-8")

    for key in ("title", "stages"):
        if not book.get(key):
            raise SystemExit(f"book.json is missing required field '{key}'")

    source: SourceDoc | None = None
    src_path = source_override or (Path(book["source"]) if book.get("source") else None)
    if src_path is not None:
        src_path = src_path if src_path.is_absolute() else (base / src_path).resolve()
        if src_path.is_file():
            source = SourceDoc(src_path)
        else:
            warn(f"source document not found: {src_path}")

    theme_spec = book.get("theme")
    if isinstance(book.get("themeOverrides"), dict):
        theme_spec = {"extends": theme_spec if isinstance(theme_spec, str) else "knight", **book["themeOverrides"]}
    theme = resolve_theme(theme_spec, themes)

    stages = [resolve_stage(s, base) for s in book["stages"]]
    seen_ids: set[str] = set()
    total_popouts = 0
    stage_words: list[int] = []
    for n, stage in enumerate(stages, start=1):
        if not stage.get("title"):
            raise SystemExit(f"stage {n} has no title")
        sid = stage.get("id") or slugify(stage["title"])
        if sid in seen_ids:
            warn(f"duplicate stage id '{sid}'")
        seen_ids.add(sid)
        stage["id"] = sid

        used_ids: set[str] = set()
        stage["narrative"] = markdown(stage.get("narrative", ""), used_ids)
        if stage.get("note"):
            stage["note"] = markdown(load_field(stage["note"], base), used_ids)
        min_words = int(book.get("minStageWords", 45))
        max_words = int(book.get("maxStageWords", 120))
        words = len(re.sub(r"<[^>]+>", "", stage["narrative"]).split())
        stage_words.append(words)
        if words < min_words:
            warn(f"stage '{stage['title']}' narrative is {words} words, under {min_words}; readers expect a scene, not a caption")
        elif words > max_words:
            warn(f"stage '{stage['title']}' narrative is {words} words, over {max_words}; cut it back — long sections belong in pop-outs and the original scroll, not the prose")

        defined = {p["id"] for p in stage.get("popouts", [])} | {p["id"] for p in book.get("popouts", [])}
        for pid in sorted(used_ids - defined):
            warn(f"stage '{stage['title']}' marks [[...|{pid}]] but no pop-out with id '{pid}' is defined")
        for pid in sorted(defined - used_ids - {p["id"] for p in book.get("popouts", [])}):
            warn(f"stage '{stage['title']}' defines pop-out '{pid}' that the narrative never marks")
        if not used_ids:
            warn(f"stage '{stage['title']}' has no pop-outs; every stage should let the reader look behind the tale")
        elif len(used_ids) > int(book.get("maxStagePopouts", 5)):
            warn(f"stage '{stage['title']}' marks {len(used_ids)} pop-outs; 2 to 4 keeps the tale readable, more turns it into a glossary")

        for p in stage.get("popouts", []):
            total_popouts += 1
            exp_words = len(re.sub(r"`[^`]*`", "", p.get("explanation", "")).split())
            if exp_words > int(book.get("maxPopoutWords", 90)):
                warn(f"pop-out '{p['id']}' explanation is {exp_words} words (excluding code); say what it is, why it matters here, and quote the source — nothing more")
            p["explanation"] = markdown(p.get("explanation", ""))
            p.setdefault("term", TERMS.get(p["id"]))
            if not p.get("title"):
                p["title"] = p.get("term") or p["id"]
            if p.get("sourceHeading"):
                sec = source.section(p["sourceHeading"]) if source else None
                if sec is None:
                    warn(f"pop-out '{p['id']}': heading '{p['sourceHeading']}' not found in source")
                else:
                    p["source"] = markdown(sec)
            elif p.get("source"):
                p["source"] = markdown(load_field(p["source"], base))

        if stage.get("sourceHeading"):
            sec = source.section(stage["sourceHeading"]) if source else None
            if sec is None:
                warn(f"stage '{stage['title']}': source heading '{stage['sourceHeading']}' not found" + ("" if source else " (no source document loaded)"))
            else:
                stage["sourceExcerpt"] = markdown(sec)
        elif stage.get("sourceExcerpt"):
            stage["sourceExcerpt"] = markdown(load_field(stage["sourceExcerpt"], base))
        else:
            warn(f"stage '{stage['title']}' has no source heading, so the 'original scroll' button is hidden")

        scene = stage.get("scene")
        if scene and not re.match(r"\s*<svg", scene, re.IGNORECASE):
            warn(f"stage '{stage['title']}' scene does not start with <svg; falling back to the generated backdrop")
            stage["scene"] = None

    book["stages"] = stages
    for key in ("cover", "ending"):
        sec = book.get(key) or {}
        sec["scene"] = load_field(sec.get("scene"), base)
        if sec.get("scene") and not re.match(r"\s*<svg", sec["scene"], re.IGNORECASE):
            warn(f"{key} scene does not start with <svg; falling back to the generated backdrop")
            sec["scene"] = None
        if sec.get("blurb"):
            sec["blurb"] = markdown(load_field(sec["blurb"], base))
        if sec.get("recap"):
            sec["recap"] = [inline(r) for r in sec["recap"]]
        book[key] = sec
    for p in book.get("popouts", []):
        total_popouts += 1
        p["explanation"] = markdown(load_field(p.get("explanation", ""), base))
        p.setdefault("title", p.get("term") or p["id"])
        if p.get("sourceHeading") and source:
            sec = source.section(p["sourceHeading"])
            if sec:
                p["source"] = markdown(sec)

    if source:
        missing = source.uncovered(max_level=3)
        if missing:
            warn("source sections no stage or pop-out refers to: " + "; ".join(missing))

    book["theme"] = {k: theme.get(k) for k in ("name", "sceneStyle", "vocabulary", "ornament")}
    payload = json.dumps(book, ensure_ascii=False).replace("</", "<\\/")
    body_class = "" if theme.get("dropCap", True) else "no-drop-cap"
    page = (template.replace("__TITLE__", html.escape(book["title"]))
                    .replace("__THEME_CSS__", theme_css(theme))
                    .replace("__BODY_CLASS__", body_class)
                    .replace("__BOOK_JSON__", payload))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")

    custom_scenes = sum(1 for s in stages if s.get("scene")) + int(bool(book["cover"].get("scene"))) + int(bool(book["ending"].get("scene")))
    if not quiet:
        print(f"built {out_path}  ({out_path.stat().st_size / 1024:.0f} KB)")
        print(f"  theme: {theme.get('name')}   stages: {len(stages)}   pop-outs: {total_popouts}   hand-drawn scenes: {custom_scenes}/{len(stages) + 2}")
        if stage_words:
            print(f"  narrative: {sum(stage_words)} words total, {sum(stage_words) // len(stage_words)} per stage on average (longest {max(stage_words)})")
        if source:
            print(f"  source: {source.path}  ({len(source.headings)} headings)")
        if WARNINGS:
            print(f"  {len(WARNINGS)} warning(s):")
            for w in WARNINGS:
                print("   - " + w)
        else:
            print("  no warnings")
    return 1 if any("not found" in w or "no pop-out with id" in w for w in WARNINGS) else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", required=True, type=Path, help="book.json describing the adventure")
    ap.add_argument("--out", required=True, type=Path, help="output .html path")
    ap.add_argument("--source", type=Path, help="source Markdown document (overrides book.json 'source')")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    sys.exit(build(args.content.resolve(), args.out.resolve(), args.source.resolve() if args.source else None, args.quiet))


if __name__ == "__main__":
    main()
