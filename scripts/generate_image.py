"""Generate one or more images via Seedream (BytePlus Ark) for a profile-html page.

Reads settings from this skill's own config.json/credential.json — self-contained,
no dependency on any other skill. Each non-empty line in the prompt file becomes a
separate generated image (same convention as agent_work/skill/video-workflow).

Usage:
    python scripts/generate_image.py --prompt prompt.txt --output _output/<slug>/assets/hero.jpg

See prompt_templates/image_prompt_*.md for the prompt formulas to fill in before running this.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ark_service import ArkImageService, download_file

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIAL_PATH = BASE_DIR / "credential.json"
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "_log"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    return read_json(CONFIG_PATH)


def load_api_key() -> str:
    import os
    env_key = os.environ.get("ARK_API_KEY")
    if env_key:
        return env_key
    if not CREDENTIAL_PATH.exists():
        raise FileNotFoundError(
            f"ARK_API_KEY env var not set, and credential file not found: {CREDENTIAL_PATH}"
        )
    cred = read_json(CREDENTIAL_PATH)
    api_key = cred.get("model_ark_key")
    if not api_key:
        raise KeyError("ARK_API_KEY env var not set and `model_ark_key` missing in credential.json")
    return api_key


def read_prompts(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    prompts = [line.strip() for line in text.splitlines() if line.strip()]
    if not prompts:
        raise ValueError(f"Prompt file is empty: {path}")
    return prompts


def write_log(log_path: Path, data: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", required=True, help="Path to prompt text file (one prompt per line)")
    parser.add_argument("--output", required=True, help="Output image file path (e.g. _output/<slug>/assets/hero.jpg)")
    args = parser.parse_args()

    prompt_path = Path(args.prompt)
    output_base = Path(args.output)
    log_path = LOG_DIR / f"{output_base.name}.log"

    output_base.parent.mkdir(parents=True, exist_ok=True)

    try:
        config = load_config()
        model_id = config["image_model_id"]
        size = config.get("image_size")
        watermark = config.get("watermark", False)
        base_url = config["maas_api_endpoint"]

        api_key = load_api_key()
        prompts = read_prompts(prompt_path)
        service = ArkImageService(base_url=base_url, api_key=api_key)

        print(f"Prompt file: {prompt_path} ({len(prompts)} prompt(s))", file=sys.stderr)
        print(f"Model: {model_id}  Size: {size}", file=sys.stderr)
        print(f"Output: {output_base}\n", file=sys.stderr)

        results = []
        for i, prompt in enumerate(prompts, start=1):
            t_img = time.monotonic()
            output_path = output_base if len(prompts) == 1 else output_base.with_stem(f"{output_base.stem}_{i:03d}")

            print(f"[{i}/{len(prompts)}] Generating: {prompt[:80]}{'...' if len(prompt) > 80 else ''}", file=sys.stderr)

            try:
                images = service.generate_image(model_id=model_id, prompt=prompt, size=size, watermark=watermark)
                url = images[0]["url"] if images else None
                if not url:
                    raise RuntimeError(f"No image URL returned for prompt: {prompt!r}")
                dl_s = download_file(url, output_path)
                elapsed = time.monotonic() - t_img
                print(f"  Saved: {output_path}  ({elapsed:.1f}s, download {dl_s:.1f}s)", file=sys.stderr)
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(), "model": model_id,
                    "index": i, "prompt": prompt, "output": str(output_path),
                    "image_url": url, "elapsed_s": round(elapsed, 2), "status": "succeeded",
                }
            except Exception as exc:
                elapsed = time.monotonic() - t_img
                print(f"  Failed: {exc}", file=sys.stderr)
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(), "model": model_id,
                    "index": i, "prompt": prompt, "elapsed_s": round(elapsed, 2),
                    "status": "failed", "error": str(exc),
                }

            write_log(log_path, entry)
            results.append(entry)

        succeeded = sum(1 for r in results if r["status"] == "succeeded")
        for r in results:
            if r["status"] == "succeeded":
                print(r["output"])
        return 0 if succeeded == len(prompts) else 1

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
