# Website images

The published and versioned images live in `images/web/`, organized into `home`, `people`, `blog`, `news`, `publications`, `general`, and `branding`.

Original photographs and the WordPress media archive remain in the other folders under `images/`. They are preserved locally, excluded from Git, and not deployed. Keep a separate backup of those originals; a repository clone contains only the web copies.

## Adding or replacing images

Add an appropriately sized image directly to `images/web/<folder>/` and reference that path from the page. Aim for 1000 pixels on the longest side for headshots, 1600 for photographs, and 2000 for the homepage background. Use JPEG for photographs, ideally below 500 KB. Keep scientific diagrams as PNG at sufficient resolution for readable labels.

If the original curated folders are present, `python3 scripts/optimize_images.py` regenerates the web copies with Pillow. This is optional and is not needed to build or publish the site. It preserves originals and GIF animation, removes photograph metadata, and preserves full-resolution scientific figures.

For a root page, use:

```markdown
![Photo caption](images/web/people/spencer-fox.jpeg){fig-alt="Portrait of Spencer J. Fox" loading="lazy" decoding="async"}
```

For blog and profile pages, prefix image paths with `../../`. For news, use `../images/web/news/...`.

Keep `fig-alt` meaningful: the caption alone does not become an image alternative in Quarto. For scientific figures, describe the variables and the main pattern rather than just saying “results.” Add `image-alt` to blog front matter so listing thumbnails also have alternatives.

The 128-pixel navigation portrait and 48-pixel favicon are in `images/web/branding/`.

## Photo review placeholders

See `PHOTO-PLAN.md` at the project root for the nine proposed photo locations and replacement instructions. The temporary illustrations are in `images/web/placeholders/`.
