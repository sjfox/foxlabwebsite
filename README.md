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

The root `CNAME` file and Quarto `site-url` already contain the intended domain. They do not change public DNS or GitHub Pages settings on their own when publishing with Actions.

## Checks

After rendering, run `python3 scripts/check_site.py docs`. This checks local links, anchor targets, referenced assets, and image alternative-text attributes. GitHub Actions runs the same check before deploying.

## Content model

- Main pages live at the project root.
- Long-form blog posts live in `blog/YYYY-MM-DD-slug/index.qmd`.
- Lab news timeline entries live in `data/news.json`.
- Seed publication metadata lives in `data/publications.csv`.
- Original WordPress media and full-size photographs are retained locally and excluded from Git and deployment.
- Published image copies live in `images/web/`; see `images/README.md`.
- `llms.txt` gives AI agents a concise map of the site, expertise, consulting areas, and contact details.
