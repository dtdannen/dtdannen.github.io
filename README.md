# dustintd.github.io
Personal Webpage

## Writing section

`/writing/` is generated from markdown at author time, so the published pages are plain
HTML and need no client-side markdown library.

- **Sources:** `writing/src/*.md`, one file per article, each with a front-matter block
  (`title`, `date`, `summary`, `slug`, optional `headerImage` and `tags`, plus the Nostr
  event id / `d` tag for provenance).
- **Build:** `python3 scripts/build_writing.py` (needs `pip install markdown`). Writes
  `writing/<slug>.html` plus `writing/index.html`.
- **Images:** `assets/writing/` (webp, max 1400px wide).
- **Styles:** `assets/writing.css`, layered on the palette and shell from `assets/site.css`.

To add a post: drop a new `.md` into `writing/src/`, run the build, commit both the source
and the generated HTML.

`scripts/check_content.py` compares `index.html` copy against an older git baseline; it is
expected to flag the `Writing` nav link, the About callout and the footer date, since those
are deliberate copy changes.
