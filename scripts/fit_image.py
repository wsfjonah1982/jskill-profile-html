"""Prepare a user's own uploaded photo for a specific HTML image slot — crop it
to the slot's aspect ratio and resize it down to a sensible web size. No AI
generation, no network call, no credentials: this skill only ever uses real
photos the user provided (in _input/images/), never a generated stand-in.

Steps:
  1. Auto-orient via EXIF (fixes sideways/upside-down phone photos).
  2. If --aspect is given, center-crop to that ratio — mirrors the
     object-fit:cover behavior every template's CSS already uses for image
     slots (.avatar-frame, .hero-panel, .product-photo, .portrait, etc.), so
     the shipped file matches what the page actually shows instead of
     carrying pixels that would just be cropped away by the browser anyway.
  3. Resize down (never up) so the longest side is at most --max-dimension.
  4. Save, format inferred from the output file's extension. Flattens
     transparency onto white before saving as JPEG; keeps PNG's alpha
     (e.g. for a logo) untouched.

Usage:
    python scripts/fit_image.py --input _input/images/photo.jpg --output _output/<slug>/assets/images/hero.jpg --aspect 16:9
    python scripts/fit_image.py --input _input/images/logo.png --output _output/<slug>/assets/images/logo.png
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_aspect(spec: str) -> float:
    try:
        w, h = spec.split(":")
        ratio = float(w) / float(h)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"--aspect must be like '4:3' or '16:9', got: {spec!r}")
    if ratio <= 0:
        raise ValueError(f"--aspect must be positive, got: {spec!r}")
    return ratio


def crop_to_aspect(img: Image.Image, target_ratio: float) -> Image.Image:
    w, h = img.size
    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 1e-6:
        return img
    if current_ratio > target_ratio:
        new_w = round(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = round(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def resize_down(img: Image.Image, max_dimension: int) -> Image.Image:
    w, h = img.size
    longest = max(w, h)
    if longest <= max_dimension:
        return img
    scale = max_dimension / longest
    new_size = (round(w * scale), round(h * scale))
    return img.resize(new_size, Image.LANCZOS)


def main() -> int:
    config = load_config()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to the source photo")
    parser.add_argument("--output", required=True, help="Output path (format inferred from extension)")
    parser.add_argument("--aspect", default=None, help="Target aspect ratio, e.g. '16:9', '1:1', '3:4'. Omit to skip cropping.")
    parser.add_argument("--max-dimension", type=int, default=config.get("image_fit_max_dimension", 1600),
                         help="Cap the longest side to this many pixels (never upscales)")
    parser.add_argument("--quality", type=int, default=config.get("image_fit_quality", 85),
                         help="JPEG/WEBP save quality (1-100)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_file():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        img = Image.open(input_path)
        img = ImageOps.exif_transpose(img)

        if args.aspect:
            ratio = parse_aspect(args.aspect)
            img = crop_to_aspect(img, ratio)
            print(f"Cropped to aspect {args.aspect}: {img.size[0]}x{img.size[1]}", file=sys.stderr)

        before_size = img.size
        img = resize_down(img, args.max_dimension)
        if img.size != before_size:
            print(f"Resized to fit {args.max_dimension}px: {img.size[0]}x{img.size[1]}", file=sys.stderr)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        ext = output_path.suffix.lower()

        if ext in (".jpg", ".jpeg"):
            if img.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                rgba = img.convert("RGBA")
                background.paste(rgba, mask=rgba.split()[-1])
                img = background
            else:
                img = img.convert("RGB")
            img.save(output_path, "JPEG", quality=args.quality, optimize=True)
        elif ext == ".png":
            img.save(output_path, "PNG", optimize=True)
        elif ext == ".webp":
            img.save(output_path, "WEBP", quality=args.quality)
        else:
            print(f"Error: unsupported output extension {ext!r} — use .jpg, .png, or .webp", file=sys.stderr)
            return 1

        print(str(output_path))
        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
