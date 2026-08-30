"""Delete a previously-published site from BytePlus TOS — the counterpart to
upload_site.py, for when a build is superseded or was published by mistake.
Removes every object under the site's key prefix.

Usage:
    python scripts/delete_site.py --slug jonah-wang-sofas
"""
import argparse
import json
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


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    return read_json(CONFIG_PATH)


def write_log(log_path: Path, data: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", required=True, help="URL slug of the published site to delete")
    args = parser.parse_args()

    log_path = LOG_DIR / f"delete-{args.slug}.log"

    try:
        config = load_config()
        endpoint = config["tos_endpoint"]
        region = config["tos_region"]
        bucket = config["tos_bucket"]
        key_prefix = config.get("tos_key_prefix_template", "site/manual/{slug}").replace("{slug}", args.slug)

        access_key = load_credential("tos_access_key_id", "TOS_ACCESS_KEY_ID")
        secret_key = load_credential("tos_secret_access_key", "TOS_SECRET_ACCESS_KEY")
        client = tos.TosClientV2(access_key, secret_key, endpoint, region)

        keys = []
        result = client.list_objects_type2(bucket, prefix=key_prefix + "/")
        keys.extend(o.key for o in result.contents)
        while result.is_truncated:
            result = client.list_objects_type2(bucket, prefix=key_prefix + "/",
                                                 continuation_token=result.next_continuation_token)
            keys.extend(o.key for o in result.contents)

        if not keys:
            print(f"Nothing found under {key_prefix}/ — already empty or never published.", file=sys.stderr)
        else:
            client.delete_multi_objects(bucket, [tos.models2.ObjectTobeDeleted(key=k) for k in keys])
            for k in keys:
                print(f"  deleted: {k}", file=sys.stderr)

        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "slug": args.slug,
            "key_prefix": key_prefix, "deleted_count": len(keys), "status": "succeeded",
        })
        print(f"{len(keys)} object(s) deleted from {key_prefix}/")
        return 0

    except Exception as exc:
        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "slug": args.slug,
            "status": "failed", "error": str(exc),
        })
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
