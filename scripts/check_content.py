"""Check the redesign preserves copy, links, and anchors from a Git baseline."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://dtdannen.github.io/"


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.hidden = []
        self.text = []
        self.links = []
        self.anchors = set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # Captions are new copy with no baseline counterpart.
        if tag in {"head", "script", "style", "figcaption"} or (tag == "a" and "data-a11y" in attrs):
            self.hidden.append(tag)
        if self.hidden:
            return
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        for name in ("id", "name"):
            if name in attrs:
                self.anchors.add(attrs[name])

    def handle_endtag(self, tag):
        if self.hidden and self.hidden[-1] == tag:
            self.hidden.pop()

    def handle_data(self, value):
        if not self.hidden:
            self.text.append(value)

    @property
    def tokens(self):
        # The old navigation's literal pipes are presentation separators.
        return Counter(re.findall(r"\w+|[^\w\s|]", " ".join(self.text)))


def normalized(value):
    return " ".join(value.split())


def destination(href, path):
    # Local fragment links retain their meaning within each design option.
    return href if href.startswith("#") else urljoin(ORIGIN + path.as_posix(), href)


def check(source_path, preview_path, baseline):
    source_bytes = subprocess.check_output(["git", "show", f"{baseline}:{source_path.as_posix()}"], cwd=ROOT)
    original = Page(source_bytes.decode())
    preview = Page((ROOT / preview_path).read_text())
    missing, added = original.tokens - preview.tokens, preview.tokens - original.tokens
    assert not (missing or added), f"Copy differs in {preview_path}: missing={missing}, added={added}"

    rendered_text = " " + " ".join(re.findall(r"\w+|[^\w\s|]", " ".join(preview.text))) + " "
    passages = [normalized(part) for part in original.text if len(normalized(part)) >= 40]
    for passage in passages:
        assert " " + " ".join(re.findall(r"\w+|[^\w\s|]", passage)) + " " in rendered_text, f"Passage changed in {preview_path}: {passage[:100]}"

    old_links = Counter(destination(href, source_path) for href in original.links)
    new_links = Counter(destination(href, preview_path) for href in preview.links)
    assert not (old_links - new_links), f"Links changed in {preview_path}: {old_links - new_links}"
    extras = new_links - old_links
    header_links = {"https://github.com/dtdannen", "https://www.linkedin.com/in/dustindannenhauer"}
    assert all(url.startswith("mailto:") or url in header_links for url in extras), f"Unexpected links in {preview_path}: {extras}"
    for href in original.links:
        if href.startswith("#"):
            assert href[1:] in preview.anchors, f"Missing anchor in {preview_path}: {href}"
        elif not urlsplit(href).scheme and not href.startswith("//"):
            assert (ROOT / source_path.parent / href).is_file(), f"Missing local link target: {href}"
    print(f"PASS {preview_path}: {sum(original.tokens.values())} copy tokens, "
          f"{len(passages)} intact passages, {sum(old_links.values())} original links preserved")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/master", help="Git ref containing the original copy")
    args = parser.parse_args()
    for source in (Path("index.html"), Path("dcss-ai-wrapper/icaps2021tutorial.html")):
        check(source, source, args.base)
