# The Fox Lab website

Quarto source for <https://www.foxandtheflu.com>.

## Preview locally

Install Quarto, then run:

```bash
quarto preview
```

Or open `foxlabwebsite.Rproj` in RStudio and run:

```r
source("preview.R")
```

This helper starts Quarto directly from R and avoids the R package preview callback. Stop it with Esc or Ctrl+C in the R console.

You can also use the RStudio Build pane to preview/render the Quarto website.

## Render locally

```bash
quarto render
```

Or from R:

```r
source("render.R")
```

The site renders to `docs/`. GitHub Actions builds and checks all pages, then deploys the rendered output directly to GitHub Pages. Generated output is not committed.

## Publishing

Repository: <https://github.com/sjfox/foxlabwebsite>.

Push changes to `main` to publish automatically, or run the **Publish website** workflow manually. The workflow uses GitHub Pages with **GitHub Actions** as its publishing source. It does not require a `gh-pages` branch or a separate access token.

The initial address is <https://sjfox.github.io/foxlabwebsite/>. The intended custom domain is <https://www.foxandtheflu.com/>.

### Connect the custom domain

1. In repository **Settings → Pages**, set the custom domain to `www.foxandtheflu.com`.
2. At the domain's DNS provider, add a `CNAME` record for `www` pointing to `sjfox.github.io` (no repository path).
3. For the bare domain, add GitHub Pages' four `A` records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`.
4. After DNS validation and certificate issuance, enable **Enforce HTTPS**.
5. Verify both domain names and direct links to blog/profile pages.

The root `CNAME` file records the intended domain. Sharing metadata currently uses the working GitHub address. After connecting the domain, update `website.site-url` in `_quarto.yml` and the base URLs in `assets/structured-data.html` and `llms.txt`. These files do not change public DNS or GitHub Pages settings on their own.

## Checks

After rendering, run `python3 scripts/check_site.py docs`. This checks local links, anchor targets, referenced assets, image alternative-text attributes, and sharing metadata. GitHub Actions runs the same check before deploying.

For external links, run `python3 scripts/check_site.py docs --external`. The **Check website links** workflow runs this on pull requests, every Monday, and on manual request. A confirmed 404 or 410 fails the check; timeouts, rate limiting, and bot blocking are reported as unverified rather than mislabeled as broken.

## Content model

- Main pages live at the project root.
- Long-form blog posts live in `blog/YYYY-MM-DD-slug/index.qmd`. The blog listing discovers them automatically.
- Lab news timeline entries live in `data/news.json`. The pre-render step generates `news/_timeline.qmd`, including topic filters, sorted entries, accessible image descriptions, and stable anchors. Do not edit the generated include.
- Seed publication metadata lives in `data/publications.csv`.
- Original WordPress media and full-size photographs are retained locally and excluded from Git and deployment.
- Published image copies live in `images/web/`; see `images/README.md`.
- `llms.txt` gives AI agents a concise map of the site, expertise, consulting areas, and contact details.

## Editing news

Edit `data/news.json`, then run `quarto render` or restart `quarto preview` to regenerate the timeline. Each entry needs `date` (`YYYY-MM` or `YYYY-MM-DD`), `title`, `summary`, and `details`; `tags`, `images`, and `links` are optional. Entries are sorted newest first. Titles must be unique; each generates a linkable anchor, so keep established titles stable.

Images can be a relative path string or an object with `src` and a descriptive `alt`. Paths are relative to the rendered `news/` page, for example `../images/web/news/sismid-2025.jpeg`. Link objects have `label` and an HTTP(S) `href`. Text is escaped as plain text to keep updates safe and predictable.

The generated timeline remains readable without JavaScript. With JavaScript, visitors can search, filter topics, expand entries with the keyboard, and link directly to a specific update.
