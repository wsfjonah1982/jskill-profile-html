"""Publish a finished static page/site (from _output/<slug>/) to BytePlus TOS
object storage, public-read — the same client/credential pattern already used in
web_app/jonah-agentbot/main/app.py (get_tos_client / upload_site_to_tos /
tos_public_url), made self-contained here with this skill's own config.json/
credential.json rather than depending on that app being present.

Usage:
    python scripts/upload_site.py --dir _output/jonah-wang-sofas --slug jonah-wang-sofas

Prints the public URL to stdout on success (the index file, per --index-name).
"""
import argparse
import json
import mimetypes
import sys
from datetime import datetime, timezone
from pathlib import Path

import tos

from credentials import load_credential

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "_log"

# A generated site should never carry these along when published.
EXCLUDE_DIR_NAMES = {".git", ".claude", "__pycache__"}


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    return read_json(CONFIG_PATH)


def load_tos_credentials() -> tuple[str, str]:
    access_key = load_credential("tos_access_key_id", "TOS_ACCESS_KEY_ID")
    secret_key = load_credential("tos_secret_access_key", "TOS_SECRET_ACCESS_KEY")
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
    args = parser.parse_args()

    source_dir = Path(args.dir)
    log_path = LOG_DIR / f"upload-{args.slug}.log"

    try:
        if not source_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {source_dir}")

        config = load_config()
        endpoint = config["tos_endpoint"]
        region = config["tos_region"]
        bucket = config["tos_bucket"]
        key_prefix = config.get("tos_key_prefix_template", "site/manual/{slug}").replace("{slug}", args.slug)

        access_key, secret_key = load_tos_credentials()
        client = tos.TosClientV2(access_key, secret_key, endpoint, region)

        uploaded = []
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            if EXCLUDE_DIR_NAMES & set(path.relative_to(source_dir).parts[:-1]):
                continue
            rel = path.relative_to(source_dir).as_posix()
            mime_type = "text/html" if path.suffix.lower() in (".html", ".htm") else (
                mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            )
            key = f"{key_prefix}/{rel}"
            data = path.read_bytes()
            client.put_object(bucket, key, content=data, content_type=mime_type,
                               acl=tos.ACLType.ACL_Public_Read)
            uploaded.append(rel)
            print(f"  uploaded: {rel}  ({mime_type}, {len(data)} bytes)", file=sys.stderr)

        public_url = f"https://{bucket}.{endpoint}/{key_prefix}/{args.index_name}"

        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "slug": args.slug,
            "dir": str(source_dir), "key_prefix": key_prefix, "file_count": len(uploaded),
            "status": "succeeded", "public_url": public_url,
        })

        print(f"\n{len(uploaded)} files uploaded.", file=sys.stderr)
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
