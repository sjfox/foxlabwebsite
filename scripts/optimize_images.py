"""Build web-sized copies while preserving original images. Requires Pillow."""
from pathlib import Path
from shutil import copy2
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
before = after = 0
for folder in ("home", "people", "blog", "news", "general", "publications"):
    for source in sorted((IMAGES / folder).iterdir()):
        if source.suffix.lower() not in (".jpg", ".jpeg", ".png", ".gif"):
            continue
        target = IMAGES / "web" / folder / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        before += source.stat().st_size
        if source.suffix.lower() == ".gif":
            copy2(source, target)
        elif folder == "publications":
            with Image.open(source) as image:
                image.save(target, optimize=True)
        else:
            with Image.open(source) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((2000, 2000) if folder == "home" else
                                (1000, 1000) if folder == "people" else (1600, 1600),
                                Image.Resampling.LANCZOS)
                if source.suffix.lower() == ".png":
                    target = target.with_suffix(".jpg")
                image.save(target, quality=82, optimize=True, progressive=True)
        after += target.stat().st_size

branding = IMAGES / "web" / "branding"
branding.mkdir(parents=True, exist_ok=True)
with Image.open(IMAGES / "people" / "spencer-fox.jpeg") as image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    logo = ImageOps.fit(image, (128, 128), Image.Resampling.LANCZOS)
    logo.save(branding / "portrait.jpg", quality=85, optimize=True)
    logo.resize((48, 48), Image.Resampling.LANCZOS).save(branding / "favicon.png", optimize=True)
print(f"Image copies: {before / 1e6:.1f} MB → {after / 1e6:.1f} MB")
