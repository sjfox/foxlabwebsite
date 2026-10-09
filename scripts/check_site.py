"""Check generated pages for broken local references and missing image alternatives."""
import sys
import argparse
import re
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()
        self.images = []
        self.metadata = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == "img":
            self.images.append(attrs)
        if tag == "meta" and attrs.get("property", attrs.get("name", "")).startswith(("og:", "twitter:")):
            self.metadata[attrs.get("property", attrs.get("name"))] = attrs.get("content", "")


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", nargs="?", default="docs")
parser.add_argument("--external", action="store_true", help="Also check HTTP(S) links; report rate limits and bot blocking separately.")
args = parser.parse_args()
root = Path(args.root).resolve()
config = (Path(__file__).resolve().parents[1] / "_quarto.yml").read_text()
site_url = urlparse(re.search(r'\bsite-url:\s*["\']?([^\s"\']+)', config).group(1))
base_path = site_url.path.rstrip("/")


def site_path(path):
    if base_path and (path == base_path or path.startswith(base_path + "/")):
        path = path[len(base_path):]
    return root / unquote(path).lstrip("/")


pages = {}
errors = []
external = set()
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
            if url.scheme in ("https", "http"):
                external.add(reference.split("#", 1)[0])
            continue
        target = (site_path(url.path) if url.path.startswith("/")
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
    for key in ("og:title", "og:description", "og:image", "twitter:card"):
        if not page.metadata.get(key):
            errors.append(f"{path.relative_to(root)}: missing sharing metadata {key}")
    preview = page.metadata.get("og:image", "")
    if preview and urlparse(preview).scheme not in ("http", "https"):
        errors.append(f"{path.relative_to(root)}: sharing preview needs an absolute image URL")
    elif preview and urlparse(preview).netloc == site_url.netloc and not site_path(urlparse(preview).path).is_file():
        errors.append(f"{path.relative_to(root)}: sharing preview image does not exist: {preview}")


def check_external(url):
    request = Request(url, headers={"User-Agent": "FoxLabWebsiteLinkCheck/1.0", "Range": "bytes=0-1023"})
    try:
        with urlopen(request, timeout=20) as response:
            return url, "ok", response.status
    except HTTPError as error:
        # A DOI resolver can pass its Range request to a server that rejects it.
        if error.code == 416:
            try:
                with urlopen(Request(url, headers={"User-Agent": "FoxLabWebsiteLinkCheck/1.0"}), timeout=20) as response:
                    return url, "ok", response.status
            except (HTTPError, URLError, TimeoutError) as retry:
                error = retry
        code = getattr(error, "code", None)
        return url, "broken" if code in (404, 410) else "unverified", str(code or error)
    except (URLError, TimeoutError, OSError) as error:
        return url, "unverified", str(error)


if args.external:
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(check_external, sorted(external)))
    for url, state, status in results:
        if state == "broken":
            errors.append(f"Broken external link ({status}): {url}")
        elif state == "unverified":
            print(f"Could not verify ({status}): {url}")
    print(f"External links: {sum(state == 'ok' for _, state, _ in results)} passed, "
          f"{sum(state == 'broken' for _, state, _ in results)} broken, "
          f"{sum(state == 'unverified' for _, state, _ in results)} need manual verification.")
for error in errors:
    print(error)
if errors:
    sys.exit(1)
print(f"Checked {len(pages)} pages: local links, anchors, images, alternative-text attributes, and sharing metadata passed.")
