"""Generate the news include from data/news.json before Quarto renders."""
import html
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def escaped(value):
    return html.escape(str(value), quote=True)


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower().replace("'", "").replace("’", "")).strip("-")


def build():
    items = json.loads((ROOT / "data/news.json").read_text())
    if not isinstance(items, list) or not items:
        raise ValueError("News must be a nonempty list of entries.")
    ids = set()
    for item in items:
        for key in ("date", "title", "summary", "details"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"Missing news field: {key}")
        if not re.fullmatch(r"\d{4}-\d{2}(?:-\d{2})?", item["date"]):
            raise ValueError(f"Invalid news date: {item['date']}")
        date.fromisoformat(item["date"] + ("-01" if len(item["date"]) == 7 else ""))
        identifier = slug(item["title"])
        if identifier in ids:
            raise ValueError(f"Duplicate news title: {item['title']}")
        ids.add(identifier)
        if not isinstance(item.get("tags", []), list) or any(not isinstance(t, str) for t in item.get("tags", [])):
            raise ValueError("News tags must be a list of strings.")
        for image in item.get("images", []):
            path = image if isinstance(image, str) else image["src"]
            if not (ROOT / "news" / path).resolve().is_file():
                raise ValueError(f"Missing news image: {path}")
        for link in item.get("links", []):
            if urlparse(link["href"]).scheme not in ("https", "http"):
                raise ValueError(f"News links must use HTTP(S): {link['href']}")
    items.sort(key=lambda item: item["date"], reverse=True)
    tags = sorted({tag for item in items for tag in item.get("tags", [])})
    output = ['```{=html}', '<div class="timeline-tools" hidden>',
              '<input id="news-search" type="search" placeholder="Search news…" aria-label="Search lab news">',
              '<select id="news-tag" aria-label="Filter lab news by topic"><option value="">All topics</option>']
    output.extend(f'<option value="{escaped(tag)}">{escaped(tag.replace("-", " ").capitalize())}</option>' for tag in tags)
    output.extend(['</select></div>', '<p id="news-status" class="muted" role="status" aria-live="polite"></p>',
                   '<noscript><p>All updates are shown below. Enable JavaScript to search and filter them.</p></noscript>',
                   '<div id="news-timeline" class="timeline">'])
    for index, item in enumerate(items):
        identifier = slug(item["title"])
        panel = "detail-" + identifier
        search = " ".join([item["date"], item["title"], item["summary"], item["details"], *item.get("tags", [])]).lower()
        output.append(f'<article id="{identifier}" class="timeline-item{" is-open" if index == 0 else ""}" data-search="{escaped(search)}" data-tags="{escaped("|".join(item.get("tags", [])))}">')
        output.append(f'<button class="timeline-summary" type="button" aria-expanded="true" aria-controls="{panel}">')
        output.append(f'<time datetime="{escaped(item["date"])}">{escaped(item["date"])}</time><h3>{escaped(item["title"])}</h3><p>{escaped(item["summary"])}</p>')
        output.append('<div class="tag-list">' + ''.join(f'<span>{escaped(tag.replace("-", " "))}</span>' for tag in item.get("tags", [])) + '</div></button>')
        output.append(f'<div id="{panel}" class="timeline-detail"><p>{escaped(item["details"])}</p>')
        for link in item.get("links", []):
            output.append(f'<p><a href="{escaped(link["href"])}">{escaped(link["label"])}</a></p>')
        if item.get("images"):
            output.append('<div class="timeline-gallery">')
            for number, image in enumerate(item["images"], 1):
                source = image if isinstance(image, str) else image["src"]
                fallback = f'{item["title"]} — photo {number} of {len(item["images"])}'
                alt = fallback if isinstance(image, str) else image.get("alt", fallback)
                output.append(f'<img src="{escaped(source)}" alt="{escaped(alt)}" loading="lazy" decoding="async">')
            output.append('</div>')
        output.append('</div></article>')
    output.extend(['</div>', '<script src="../assets/news-timeline.js" defer></script>', '```', ''])
    (ROOT / "news/_timeline.qmd").write_text("\n".join(output))
    print(f"Generated {len(items)} news entries and {len(tags)} topic filters from data/news.json.")


if __name__ == "__main__":
    build()
