"""Publish a finished static page/site (from _output/<slug>/) to BytePlus TOS
object storage, public-read — via tos_client.py's plain-HTTP TOS4-HMAC-SHA256
signing, no vendor SDK.

Usage:
    python scripts/publish_site.py --dir _output/jane-doe-portfolio --slug jane-doe-portfolio

Prints the public URL to stdout on success (the index file, per --index-name).

After uploading, any object left under the site's prefix that isn't part of
this build (a file the rebuild dropped or renamed) is deleted, so nothing
stale stays public. Pass --keep-stale to skip that.

HTML is uploaded with Cache-Control: no-cache so a republish shows up
immediately; other assets get a short max-age.
"""
import argparse
import json
import mimetypes
import sys
from datetime import datetime, timezone
from pathlib import Path

from credentials import load_bucket, load_credential
from site_paths import site_prefix, validate_slug
from tos_client import delete_object, list_objects, put_object

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "_log"

# A generated site should never carry these along when published.
EXCLUDE_DIR_NAMES = {".git", ".claude", "__pycache__"}

CACHE_HTML = "no-cache"
CACHE_ASSET = "public, max-age=3600"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    return read_json(CONFIG_PATH)


def load_tos_credentials() -> tuple[str, str]:
    access_key = load_credential("tos_access_key_id")
    secret_key = load_credential("tos_secret_access_key")
    return access_key, secret_key


def write_log(log_path: Path, data: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Local directory to publish (e.g. _output/<slug>)")
    parser.add_argument("--slug", required=True, help="URL slug — files land under <tos_key_prefix_template>/")
    parser.add_argument("--index-name", default="index.html", help="Entry file to report the public URL for")
    parser.add_argument("--keep-stale", action="store_true",
                        help="Don't delete objects under the site prefix that aren't in this build")
    args = parser.parse_args()

    try:
        validate_slug(args.slug)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    source_dir = Path(args.dir)
    log_path = LOG_DIR / f"publish-{args.slug}.log"

    try:
        if not source_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {source_dir}")

        config = load_config()
        endpoint = config["tos_endpoint"]
        region = config["tos_region"]
        bucket = load_bucket(config)
        key_prefix = site_prefix(config, args.slug)

        access_key, secret_key = load_tos_credentials()

        published = []
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            if EXCLUDE_DIR_NAMES & set(path.relative_to(source_dir).parts[:-1]):
                continue
            rel = path.relative_to(source_dir).as_posix()
            is_html = path.suffix.lower() in (".html", ".htm")
            mime_type = "text/html" if is_html else (
                mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            key = f"{key_prefix}/{rel}"
            data = path.read_bytes()
            put_object(endpoint, region, bucket, key, access_key, secret_key, data, mime_type,
                       cache_control=CACHE_HTML if is_html else CACHE_ASSET)
            published.append(rel)
            print(f"  published: {rel}  ({mime_type}, {len(data)} bytes)", file=sys.stderr)

        if not published:
            raise RuntimeError(f"No files found in {source_dir} — nothing published, nothing pruned.")

        pruned = []
        if not args.keep_stale:
            current = {f"{key_prefix}/{rel}" for rel in published}
            for k in list_objects(endpoint, region, bucket, access_key, secret_key, prefix=key_prefix + "/"):
                if k not in current:
                    delete_object(endpoint, region, bucket, k, access_key, secret_key)
                    pruned.append(k)
                    print(f"  removed stale: {k[len(key_prefix) + 1:]}", file=sys.stderr)

        public_url = f"https://{bucket}.{endpoint}/{key_prefix}/{args.index_name}"

        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "slug": args.slug,
            "dir": str(source_dir), "key_prefix": key_prefix, "file_count": len(published),
            "pruned_count": len(pruned),
            "status": "succeeded", "public_url": public_url,
        })

        print(f"\n{len(published)} files published, {len(pruned)} stale removed.", file=sys.stderr)
        print(public_url)
        return 0

    except Exception as exc:
        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "slug": args.slug,
            "dir": str(source_dir), "status": "failed", "error": str(exc),
        })
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
