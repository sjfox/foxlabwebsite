"""Check generated pages for broken local references and missing image alternatives."""
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == "img":
            self.images.append(attrs)


root = Path(sys.argv[1] if len(sys.argv) > 1 else "docs").resolve()
pages = {}
errors = []
for path in root.rglob("*.html"):
    if any(part in ("assets", "site_libs") for part in path.relative_to(root).parts):
        continue
    page = Page()
    page.feed(path.read_text())
    pages[path] = page
if root / "index.html" not in pages:
    errors.append("Missing homepage")
for path, page in pages.items():
    for reference in page.references:
        url = urlparse(reference)
        if url.scheme or url.netloc:
            continue
        target = ((root / unquote(url.path).lstrip("/")) if url.path.startswith("/")
                  else (path.parent / unquote(url.path))).resolve() if url.path else path
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            errors.append(f"{path.relative_to(root)}: missing {reference}")
        elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
            errors.append(f"{path.relative_to(root)}: missing anchor {reference}")
    for image in page.images:
        if "alt" not in image:
            errors.append(f"{path.relative_to(root)}: missing alt on {image.get('src')}")
for error in errors:
    print(error)
if errors:
    sys.exit(1)
print(f"Checked {len(pages)} pages: local links, anchors, images, and alternative-text attributes passed.")
