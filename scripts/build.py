#!/usr/bin/env python3
"""Build the Claude Code handoff static site and zip from pack/."""

from __future__ import annotations

import html
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "pack"
DIST = ROOT / "dist"
SITE_CSS = "styles.css"

# Pack markdown/docs that become browsable HTML pages.
# Maps pack-relative path -> dist-relative HTML path (no leading slash).
PAGE_MAP = {
    "README.md": "README.html",
    "CLAUDE.md": "CLAUDE.html",
    "AGENTS.md": "AGENTS.html",
    "COPY-TO-DESKTOP.md": "COPY-TO-DESKTOP.html",
    "docs/HANDOFF.md": "docs/HANDOFF.html",
    "docs/SKILLS-AND-PLUGINS.md": "docs/SKILLS-AND-PLUGINS.html",
}

NAV = [
    ("Home", "/"),
    ("README", "/README.html"),
    ("CLAUDE", "/CLAUDE.html"),
    ("AGENTS", "/AGENTS.html"),
    ("Handoff", "/docs/HANDOFF.html"),
    ("Skills", "/docs/SKILLS-AND-PLUGINS.html"),
    ("Download zip", "/Claude-Code-Handoff.zip"),
]


def md_to_html_fragment(text: str) -> str:
    """Minimal Markdown → HTML for pack docs (headings, lists, code, tables, links)."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows: list[list[str]] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        if table_rows:
            out.append("<table>")
            for ridx, row in enumerate(table_rows):
                tag = "th" if ridx == 0 else "td"
                # Skip separator row like |---|---|
                if ridx == 1 and all(re.fullmatch(r":?-+:?", c.strip()) for c in row):
                    continue
                cells = "".join(f"<{tag}>{inline_md(c.strip())}</{tag}>" for c in row)
                out.append(f"<tr>{cells}</tr>")
            out.append("</table>")
        in_table = False
        table_rows = []

    def flush_code() -> None:
        nonlocal in_code, code_buf, code_lang
        escaped = html.escape("\n".join(code_buf))
        cls = f' class="language-{html.escape(code_lang)}"' if code_lang else ""
        out.append(f"<pre><code{cls}>{escaped}</code></pre>")
        in_code = False
        code_buf = []
        code_lang = ""

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            close_lists()
            close_table()
            if in_code:
                flush_code()
            else:
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("|") and line.strip().endswith("|"):
            close_lists()
            cells = [c for c in line.strip().strip("|").split("|")]
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            i += 1
            continue
        else:
            close_table()

        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            close_lists()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline_md(heading.group(2))}</h{level}>")
            i += 1
            continue

        ul = re.match(r"^[-*]\s+(.*)$", line)
        if ul:
            close_table()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md(ul.group(1))}</li>")
            i += 1
            continue

        ol = re.match(r"^\d+\.\s+(.*)$", line)
        if ol:
            close_table()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_md(ol.group(1))}</li>")
            i += 1
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        close_lists()
        out.append(f"<p>{inline_md(line)}</p>")
        i += 1

    if in_code:
        flush_code()
    close_lists()
    close_table()
    return "\n".join(out)


def inline_md(text: str) -> str:
    """Escape then apply inline markdown, remapping .md links to .html pages."""

    def link_repl(m: re.Match[str]) -> str:
        label, href = m.group(1), m.group(2)
        mapped = remap_href(href)
        return f'<a href="{html.escape(mapped)}">{html.escape(label)}</a>'

    # Protect code spans
    parts: list[str] = []
    last = 0
    for m in re.finditer(r"`([^`]+)`", text):
        parts.append(("text", text[last : m.start()]))
        parts.append(("code", m.group(1)))
        last = m.end()
    parts.append(("text", text[last:]))

    rendered: list[str] = []
    for kind, value in parts:
        if kind == "code":
            rendered.append(f"<code>{html.escape(value)}</code>")
            continue
        chunk = html.escape(value)
        # Unescape pattern targets carefully via working on original then escaping pieces
        # Re-process from original non-escaped for links/bold/italic
        tmp = value
        tmp = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, tmp)

        def bold_repl(m: re.Match[str]) -> str:
            return f"<strong>{html.escape(m.group(1))}</strong>"

        def em_repl(m: re.Match[str]) -> str:
            return f"<em>{html.escape(m.group(1))}</em>"

        # If link_repl already produced HTML, avoid double-escaping by splitting
        # Simpler path: rebuild from value with sequential transforms on escaped plaintext segments
        # For robustness, redo from value:
        def transform(s: str) -> str:
            out_parts: list[str] = []
            pos = 0
            pattern = re.compile(
                r"(\[([^\]]+)\]\(([^)]+)\))"
                r"|(\*\*([^*]+)\*\*)"
                r"|(\*([^*]+)\*)"
            )
            for m in pattern.finditer(s):
                out_parts.append(html.escape(s[pos : m.start()]))
                if m.group(1):
                    out_parts.append(
                        f'<a href="{html.escape(remap_href(m.group(3)))}">{html.escape(m.group(2))}</a>'
                    )
                elif m.group(4):
                    out_parts.append(f"<strong>{html.escape(m.group(5))}</strong>")
                elif m.group(6):
                    out_parts.append(f"<em>{html.escape(m.group(7))}</em>")
                pos = m.end()
            out_parts.append(html.escape(s[pos:]))
            return "".join(out_parts)

        rendered.append(transform(value))
    return "".join(rendered)


def remap_href(href: str) -> str:
    """Map pack markdown links to HTML site routes; keep external and json/zip."""
    if href.startswith(("http://", "https://", "mailto:", "#")):
        return href
    clean = href.split("#", 1)[0]
    frag = ""
    if "#" in href:
        frag = "#" + href.split("#", 1)[1]
    # Normalize relative
    norm = clean.lstrip("./")
    if norm in PAGE_MAP:
        return "/" + PAGE_MAP[norm] + frag
    # Relative from docs/
    if norm.startswith("docs/") and norm in PAGE_MAP:
        return "/" + PAGE_MAP[norm] + frag
    # Same-folder docs links like HANDOFF.md from docs pages
    alt = f"docs/{norm}"
    if alt in PAGE_MAP:
        return "/" + PAGE_MAP[alt] + frag
    if norm.endswith(".md"):
        # Generic .md → .html
        return "/" + norm[:-3] + ".html" + frag
    if norm.endswith(".json") or norm.endswith(".zip") or norm.endswith(".html"):
        return "/" + norm + frag
    if norm == "Claude-Code-Handoff.zip":
        return "/Claude-Code-Handoff.zip"
    return href


def page_shell(title: str, body: str, *, active: str | None = None) -> str:
    nav_html = []
    for label, href in NAV:
        cls = ' class="active"' if active == href else ""
        nav_html.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)} — Claude Code Handoff</title>
  <link rel="stylesheet" href="/{SITE_CSS}"/>
</head>
<body>
  <div class="bg"></div>
  <header class="top">
    <a class="brand" href="/">Claude Code Handoff</a>
    <nav>{"".join(nav_html)}</nav>
  </header>
  <main class="doc">
{body}
  </main>
  <footer class="foot">
    <p>Portable handoff pack for Claude Code and agent IDEs.</p>
  </footer>
</body>
</html>
"""


def write_css(dest: Path) -> None:
    dest.write_text(
        """:root {
  --ink: #1a2332;
  --muted: #4a5a6a;
  --paper: #f7f3eb;
  --panel: rgba(255, 252, 246, 0.88);
  --line: rgba(26, 35, 50, 0.12);
  --accent: #0b6e4f;
  --accent-2: #c45c26;
  --display: "Fraunces", "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --body: "Source Serif 4", "Iowan Old Style", Georgia, serif;
  --mono: "IBM Plex Mono", "SFMono-Regular", ui-monospace, Menlo, Consolas, monospace;
}
@import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;700&family=IBM+Plex+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;600&display=swap");

* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  min-height: 100vh;
  color: var(--ink);
  font-family: var(--body);
  background: var(--paper);
  line-height: 1.6;
}
.bg {
  position: fixed; inset: 0; z-index: -1;
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(11, 110, 79, 0.18), transparent 55%),
    radial-gradient(900px 500px at 90% 0%, rgba(196, 92, 38, 0.16), transparent 50%),
    radial-gradient(1200px 600px at 10% -10%, rgba(11, 110, 79, 0.18), transparent 55%),
    radial-gradient(900px 500px at 90% 0%, rgba(196, 92, 38, 0.16), transparent 50%),
    linear-gradient(165deg, #f7f3eb 0%, #ebe4d6 45%, #e2ece8 100%);
}
.top {
  display: flex; flex-wrap: wrap; gap: 1rem 1.5rem;
  align-items: center; justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(8px);
  background: rgba(247, 243, 235, 0.7);
}
.brand {
  font-family: var(--display);
  font-weight: 700;
  font-size: 1.35rem;
  color: var(--ink);
  text-decoration: none;
  letter-spacing: -0.02em;
}
nav { display: flex; flex-wrap: wrap; gap: 0.75rem 1rem; }
nav a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.95rem;
}
nav a:hover, nav a.active { color: var(--accent); }
main.doc, main.hero-wrap {
  max-width: 44rem;
  margin: 0 auto;
  padding: 2.5rem 1.5rem 4rem;
}
main.doc {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 2px;
  margin-top: 2rem;
  margin-bottom: 2rem;
  padding: 2rem 1.75rem 2.5rem;
}
h1, h2, h3, h4 { font-family: var(--display); letter-spacing: -0.02em; line-height: 1.2; }
h1 { font-size: clamp(1.8rem, 4vw, 2.4rem); margin-top: 0; }
h2 { margin-top: 2rem; font-size: 1.35rem; }
a { color: var(--accent); }
code, pre { font-family: var(--mono); font-size: 0.9em; }
code {
  background: rgba(26, 35, 50, 0.06);
  padding: 0.1em 0.35em;
  border-radius: 3px;
}
pre {
  background: #1a2332;
  color: #f7f3eb;
  padding: 1rem 1.1rem;
  overflow-x: auto;
  border-radius: 4px;
}
pre code { background: transparent; color: inherit; padding: 0; }
table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.95rem; }
th, td { border: 1px solid var(--line); padding: 0.55rem 0.7rem; text-align: left; vertical-align: top; }
th { background: rgba(11, 110, 79, 0.08); }
.foot {
  text-align: center;
  color: var(--muted);
  font-size: 0.9rem;
  padding: 0 1rem 2.5rem;
}
.hero-wrap { max-width: 52rem; }
.hero {
  padding: 4.5rem 1.5rem 3rem;
  text-align: left;
}
.hero .brand-hero {
  font-family: var(--display);
  font-size: clamp(2.4rem, 6vw, 3.6rem);
  font-weight: 700;
  margin: 0 0 0.75rem;
  letter-spacing: -0.03em;
  animation: rise 700ms ease-out both;
}
.hero h1 {
  font-size: clamp(1.25rem, 2.5vw, 1.6rem);
  font-weight: 500;
  color: var(--muted);
  margin: 0 0 1rem;
  animation: rise 800ms ease-out 80ms both;
}
.hero p.lead {
  max-width: 34rem;
  font-size: 1.15rem;
  color: var(--ink);
  animation: rise 900ms ease-out 140ms both;
}
.cta {
  display: flex; flex-wrap: wrap; gap: 0.75rem;
  margin-top: 1.75rem;
  animation: rise 1000ms ease-out 200ms both;
}
.cta a {
  display: inline-block;
  text-decoration: none;
  padding: 0.7rem 1.15rem;
  border-radius: 2px;
  font-family: var(--mono);
  font-size: 0.9rem;
}
.cta a.primary {
  background: var(--accent);
  color: #fff;
}
.cta a.secondary {
  border: 1px solid var(--line);
  color: var(--ink);
  background: rgba(255,255,255,0.55);
}
.links {
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}
.links ul { padding-left: 1.1rem; }
@keyframes rise {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (max-width: 640px) {
  main.doc { margin-top: 1rem; padding: 1.35rem 1.1rem 1.75rem; }
  .hero { padding-top: 2.5rem; }
}
""",
        encoding="utf-8",
    )


def homepage() -> str:
    body = """
  <section class="hero">
    <p class="brand-hero">Claude Code Handoff</p>
    <h1>A portable pack for clean agent handoffs</h1>
    <p class="lead">Drop-in CLAUDE.md, AGENTS.md, MCP inventory, skills, and a session handoff template — ready for Claude Code, Cursor, and teammates.</p>
    <div class="cta">
      <a class="primary" href="/Claude-Code-Handoff.zip">Download zip</a>
      <a class="secondary" href="/docs/HANDOFF.html">Read handoff guide</a>
    </div>
    <div class="links">
      <h2>Browse the pack</h2>
      <ul>
        <li><a href="/README.html">README</a></li>
        <li><a href="/CLAUDE.html">CLAUDE.md</a></li>
        <li><a href="/AGENTS.html">AGENTS.md</a></li>
        <li><a href="/COPY-TO-DESKTOP.html">Copy to Desktop</a></li>
        <li><a href="/docs/SKILLS-AND-PLUGINS.html">Skills &amp; plugins</a></li>
        <li><a href="/docs/INVENTORY.json">INVENTORY.json</a></li>
      </ul>
    </div>
  </section>
"""
    nav_bits = []
    for label, href in NAV:
        cls = ' class="active"' if href == "/" else ""
        nav_bits.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    nav = "".join(nav_bits)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Claude Code Handoff</title>
  <link rel="stylesheet" href="/{SITE_CSS}"/>
</head>
<body>
  <div class="bg"></div>
  <header class="top">
    <a class="brand" href="/">Claude Code Handoff</a>
    <nav>{nav}</nav>
  </header>
  <main class="hero-wrap">
{body}
  </main>
  <footer class="foot">
    <p>Permanent Workers site for the Claude Code handoff pack.</p>
  </footer>
</body>
</html>
"""


def not_found_page() -> str:
    body = """
    <h1>Page not found</h1>
    <p>That path is not part of the Claude Code Handoff site.</p>
    <p><a href="/">Back to home</a> · <a href="/Claude-Code-Handoff.zip">Download the zip</a></p>
"""
    return page_shell("Not found", body, active=None)


def build_zip(dest: Path) -> None:
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACK.rglob("*")):
            if path.is_file():
                if path.name.endswith(".pyc") or "__pycache__" in path.parts:
                    continue
                arc = Path("Claude-Code-Handoff") / path.relative_to(PACK)
                zf.write(path, arcname=str(arc))


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "docs").mkdir()

    write_css(DIST / SITE_CSS)
    (DIST / "index.html").write_text(homepage(), encoding="utf-8")
    (DIST / "404.html").write_text(not_found_page(), encoding="utf-8")

    for src_rel, html_rel in PAGE_MAP.items():
        src = PACK / src_rel
        text = src.read_text(encoding="utf-8")
        # Strip YAML front matter for skill-like md if present — pack pages don't use it except skill
        fragment = md_to_html_fragment(text)
        title = src_rel
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        out = DIST / html_rel
        out.parent.mkdir(parents=True, exist_ok=True)
        active = "/" + html_rel
        out.write_text(page_shell(title, fragment, active=active), encoding="utf-8")

    # Copy inventory JSON into dist for browsing/download
    shutil.copy2(PACK / "docs" / "INVENTORY.json", DIST / "docs" / "INVENTORY.json")

    build_zip(DIST / "Claude-Code-Handoff.zip")
    print(f"Built site → {DIST}")


if __name__ == "__main__":
    build()
