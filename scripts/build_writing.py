#!/usr/bin/env python3
"""Build the /writing/ section of dtdannen.github.io from markdown sources.

Each file in writing/src/*.md carries a small front-matter block:

    ---
    title: ...
    date: YYYY-MM-DD
    summary: ...
    slug: ...
    tags: a, b, c
    headerImage: assets/writing/foo.webp     (optional)
    nostrEvent: <64-char hex>
    nostrDtag: ...
    nostrRelays: ...
    ---

    Markdown body follows.

Rendering happens here, at build time, so the pages ship as plain HTML:
no client-side markdown library, no runtime JS beyond the site's existing
navigation script. Run this after editing anything in writing/src/:

    python3 scripts/build_writing.py

Requires python-markdown (`pip install markdown`).
"""
from __future__ import annotations

import html
import re
from datetime import date as date_cls
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "writing" / "src"
OUT_DIR = ROOT / "writing"
SITE = "https://dtdannen.github.io"
SITE_NAME = "Dustin Dannenhauer"
NAV = [
    ("../index.html#about", "About Me"),
    ("index.html", "Writing"),
    ("../index.html#publications", "Publications"),
    ("../index.html#service", "Service"),
    ("../index.html#conf", "Conferences"),
    ("../index.html#misc", "Misc"),
]

MD = markdown.Markdown(
    extensions=["extra", "sane_lists", "smarty", "toc"],
    extension_configs={"toc": {"permalink": False, "toc_depth": "2-3"}},
)

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def parse(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: missing front matter")
    head, _, body = text[4:].partition("\n---\n")
    meta: dict[str, str] = {}
    for line in head.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for required in ("title", "date", "slug", "summary"):
        if not meta.get(required):
            raise SystemExit(f"{path}: front matter needs '{required}'")
    meta["body"] = body.strip()
    meta["source"] = str(path.relative_to(ROOT))
    return meta


def pretty_date(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def reading_time(text: str) -> int:
    return max(1, round(len(re.findall(r"\w+", text)) / 220))


def normalise(text: str) -> str:
    return " ".join(text.split()).lower()


def strip_summary(body: str, summary: str) -> str:
    """NIP-23 authors often paste the summary tag as the opening paragraph;
    drop that paragraph when it repeats, since the page already shows a dek."""
    target = normalise(summary)
    if not target:
        return body
    paragraphs = body.split("\n\n")
    for i, para in enumerate(paragraphs):
        if normalise(re.sub(r"[*_`#>\[\]]", "", para)) == target:
            del paragraphs[i]
            break
    else:
        return body
    return "\n\n".join(p for p in paragraphs if p.strip())


def space_headings(body: str) -> str:
    """Ensure a blank line before ATX headings and fences so nothing merges."""
    lines = body.split("\n")
    out: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            if not in_fence and out and out[-1].strip():
                out.append("")
            in_fence = not in_fence
        elif not in_fence and re.match(r"#{1,6} \S", line) and out and out[-1].strip():
            out.append("")
        out.append(line)
    return "\n".join(out)


URL_RE = re.compile(r"(?<![\w\"'=/<>(\[])(https?://[^\s<>()\"']+[^\s<>()\"'.,;:])")


def linkify_urls(body: str) -> str:
    """Wrap bare URLs in markdown links, leaving code blocks alone."""
    parts = re.split(r"(```.*?```)", body, flags=re.S)
    for i, part in enumerate(parts):
        if part.startswith("```"):
            continue
        parts[i] = URL_RE.sub(lambda m: f"[{m.group(1)}]({m.group(1)})", part)
    return "".join(parts)


def fix_link_spaces(body: str) -> str:
    """Sources often write ']( https://…)' — a space after the paren, which
    markdown then treats as plain text. Close that gap so the link works."""
    return re.sub(r"\]\(\s+", "](", body)


NOSTR_RE = re.compile(r"(?<![\w(\[])(?:nostr:)?((?:npub1|nprofile1|naddr1|nnote1|note1|nevent1)[0-9a-z]+)")
NOSTR_HREF_RE = re.compile(r"\]\(nostr:((?:npub1|nprofile1|naddr1|nnote1|note1|nevent1)[0-9a-z]+)\)")


def linkify_nostr(body: str) -> str:
    # a link whose destination is nostr:... becomes a njump link
    body = NOSTR_HREF_RE.sub(lambda m: f"](https://njump.me/{m.group(1)})", body)

    def repl(m):
        bech = m.group(1)
        return f"[{bech[:18]}…{bech[-6:]}](https://njump.me/{bech})"
    return NOSTR_RE.sub(repl, body)


def render_body(md_text: str, summary: str = "") -> str:
    text = space_headings(md_text)
    text = strip_summary(text, summary)
    text = fix_link_spaces(text)
    text = linkify_nostr(text)
    text = linkify_urls(text)
    MD.reset()
    return MD.convert(text)


def page(title: str, description: str, canonical: str, main: str, current: str,
         og_type: str = "article", og_image: str | None = None) -> str:
    links = []
    for href, label in NAV:
        marker = ' aria-current="page"' if label == current else ""
        links.append(f'<a href="{href}"{marker}>{html.escape(label)}</a>')
    nav = "".join(links)
    og = ""
    if og_image:
        og = (f'\n<meta property="og:image" content="{SITE}/{og_image}">'
              f'\n<meta name="twitter:card" content="summary_large_image">')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} | {SITE_NAME}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="author" content="{SITE_NAME}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:url" content="{canonical}">{og}
<link rel="stylesheet" href="../assets/site.css">
<link rel="stylesheet" href="../assets/writing.css">
<script src="../assets/site.js" defer></script>
</head>
<body class="editorial"><a class="skip-link" href="#main">Skip to content</a>
<div class="site-shell">
<header class="site-header">
<div class="header-brand">
<div class="brand-links"><a href="https://github.com/dtdannen" aria-label="GitHub"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg></a><a href="https://www.linkedin.com/in/dustindannenhauer" aria-label="LinkedIn"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.71 1.637-2.165 3.37-2.165 3.601 0 4.267 2.37 4.267 4.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a></div>
<a class="wordmark" href="../index.html">{SITE_NAME}</a>
</div>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="section-navigation" aria-label="Open navigation" hidden>
<svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
<svg class="close-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg>
</button>
<nav id="section-navigation" class="section-nav" aria-label="Sections">{nav}</nav>
</header>
<main id="main">
{main}
</main>
<footer class="site-footer"><p>Originally published on Nostr; archived here so it can be read and cited.</p><p>Last Updated: November 2026</p></footer>
</div>
</body>
</html>
"""


def article_page(a: dict) -> str:
    body = render_body(a["body"], a["summary"])
    mins = reading_time(a["body"])
    header = ""
    if a.get("headerImage"):
        header = (f'<figure class="post-image"><img src="../{a["headerImage"]}" '
                  f'alt="" width="1024" height="1024" fetchpriority="high"></figure>')
    tags = ""
    if a.get("tags"):
        tags = ('<ul class="post-tags">'
                + "".join(f"<li>{html.escape(t.strip())}</li>"
                          for t in a["tags"].split(",") if t.strip())
                + "</ul>")
    provenance = ""
    if a.get("nostrEvent"):
        provenance = (f'<p class="post-provenance">Nostr long-form event '
                      f'<code>{a["nostrEvent"][:12]}…</code> · first published '
                      f'{pretty_date(a["date"])}</p>')
    main = f"""<article class="post">
<header class="post-head">
<p class="post-meta"><time datetime="{a['date']}">{pretty_date(a['date'])}</time> · {mins} min read</p>
<h1>{html.escape(a['title'])}</h1>
<p class="post-summary">{html.escape(a['summary'])}</p>
</header>
{header}
<div class="prose">
{body}
</div>
<footer class="post-foot">
{provenance}
{tags}
<p class="post-back"><a href="index.html">← All writing</a></p>
</footer>
</article>"""
    return page(a["title"], a["summary"], f"{SITE}/writing/{a['slug']}.html", main,
                current="Writing", og_image=a.get("headerImage"))


def index_page(articles: list[dict]) -> str:
    by_year: dict[str, list[dict]] = {}
    for a in articles:
        by_year.setdefault(a["date"][:4], []).append(a)
    blocks = []
    for year in sorted(by_year, reverse=True):
        items = []
        for a in sorted(by_year[year], key=lambda x: x["date"], reverse=True):
            mins = reading_time(a["body"])
            items.append(
                f"""<li>
<time datetime="{a['date']}">{pretty_date(a['date'])}</time>
<div><h3><a href="{a['slug']}.html">{html.escape(a['title'])}</a></h3>
<p>{html.escape(a['summary'])}</p>
<span class="writing-meta">{mins} min read</span></div>
</li>""")
        blocks.append(f'<section class="writing-year"><h2>{year}</h2><ul class="writing-list">'
                      + "\n".join(items) + "</ul></section>")
    main = f"""<header class="hero writing-hero">
<div class="hero-copy">
<p class="role">Writing</p>
<h1>Essays on AI, Nostr,<br>and building things</h1>
<p class="tagline">Long-form pieces I published on Nostr between 2024 and 2025 — recovered from the relays and kept here in readable form.</p>
</div>
</header>
<div class="content">
{''.join(blocks)}
</div>"""
    return page("Writing", "Essays by Dustin Dannenhauer on AI, Nostr and Data Vending Machines.",
                f"{SITE}/writing/", main, current="Writing", og_type="website")


def main() -> None:
    if not SRC_DIR.is_dir():
        raise SystemExit(f"no sources at {SRC_DIR}")
    articles = [parse(p) for p in sorted(SRC_DIR.glob("*.md"))]
    slugs = [a["slug"] for a in articles]
    if len(set(slugs)) != len(slugs):
        raise SystemExit("duplicate slugs in writing/src")

    OUT_DIR.mkdir(exist_ok=True)
    for a in articles:
        (OUT_DIR / f"{a['slug']}.html").write_text(article_page(a), encoding="utf-8")
    (OUT_DIR / "index.html").write_text(
        index_page(sorted(articles, key=lambda a: a["date"])), encoding="utf-8")
    print(f"built {len(articles)} articles + index into {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
