"""List every site currently published to the TOS bucket — so old test builds
don't stay public unnoticed.

For each slug under the site prefix (e.g. site/manual/<slug>/) it shows the
file count, total size, last update, whether a local build exists in
_output/<slug>/, and the public URL. Objects directly under the prefix that
don't belong to any slug are listed separately.

When TOS isn't configured, it lists the site folders in config.json's
`local_publish_dir` instead (or says where builds stay if that isn't set).

Read-only: it never deletes anything. To take a site down:
    python scripts/unpublish_site.py --slug <slug>

Usage:
    python scripts/list_sites.py
    python scripts/list_sites.py --json
"""
import argparse
import json
import sys
from pathlib import Path

from credentials import load_bucket, load_credential, tos_status
from site_paths import DEFAULT_PREFIX_TEMPLATE, local_publish_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
OUTPUT_DIR = BASE_DIR / "_output"


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def list_local(config: dict, as_json: bool) -> int:
    root = local_publish_root(config)
    rows = []
    if root and root.is_dir():
        for d in sorted(p for p in root.iterdir() if (p / "index.html").is_file()):
            files = [f for f in d.rglob("*") if f.is_file()]
            rows.append({"slug": d.name, "files": len(files), "bytes": sum(f.stat().st_size for f in files),
                         "local_build": (OUTPUT_DIR / d.name / "index.html").exists(),
                         "url": (d / "index.html").as_uri()})
    if as_json:
        print(json.dumps({"target": "local", "root": str(root) if root else None, "sites": rows}, indent=2))
        return 0
    if root is None:
        print(f"TOS isn't configured and no local_publish_dir is set — finished sites stay in {OUTPUT_DIR}.")
        return 0
    print(f"TOS isn't configured — {len(rows)} site(s) in local_publish_dir {root}\n")
    for r in rows:
        print(f"  {r['slug']}  {r['files']} files  {human(r['bytes'])}  {r['url']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    state, missing = tos_status(config)
    if state == "off":
        return list_local(config, args.json)
    if state == "partial":
        print(f"TOS is only partly configured (missing: {', '.join(missing)}).", file=sys.stderr)
        return 1
    from tos_client import list_object_entries  # needs `requests`; TOS only

    endpoint, region = config["tos_endpoint"], config["tos_region"]
    bucket = load_bucket(config)
    template = config.get("tos_key_prefix_template", DEFAULT_PREFIX_TEMPLATE)
    base = template.split("{slug}")[0].strip("/")
    base = f"{base}/" if base else ""

    entries = list_object_entries(endpoint, region, bucket,
                                  load_credential("tos_access_key_id"),
                                  load_credential("tos_secret_access_key"), prefix=base)

    sites, loose = {}, []
    for e in entries:
        rest = e["Key"][len(base):]
        if "/" not in rest:
            loose.append(e)
            continue
        slug = rest.split("/", 1)[0]
        s = sites.setdefault(slug, {"slug": slug, "files": 0, "bytes": 0, "updated": ""})
        s["files"] += 1
        s["bytes"] += int(e.get("Size", 0))
        s["updated"] = max(s["updated"], e.get("LastModified", ""))

    rows = []
    for slug in sorted(sites):
        s = sites[slug]
        s["local_build"] = (OUTPUT_DIR / slug / "index.html").exists()
        s["url"] = f"https://{bucket}.{endpoint}/{base}{slug}/index.html"
        rows.append(s)

    if args.json:
        print(json.dumps({"bucket": bucket, "prefix": base, "sites": rows,
                          "loose_objects": [e["Key"] for e in loose]}, indent=2))
        return 0

    print(f"Bucket {bucket}, prefix {base or '(root)'}: {len(rows)} published site(s)\n")
    if rows:
        w = max(len(r["slug"]) for r in rows)
        print(f"  {'slug'.ljust(w)}  files      size  updated (UTC)        local  url")
        for r in rows:
            print(f"  {r['slug'].ljust(w)}  {r['files']:>5}  {human(r['bytes']):>8}  {r['updated'][:19].replace('T', ' '):19}  "
                  f"{'yes' if r['local_build'] else 'NO ':5}  {r['url']}")
    if loose:
        print(f"\n  {len(loose)} object(s) directly under {base or 'the bucket root'} (not part of any site):")
        for e in loose[:20]:
            print(f"    {e['Key']}")
    print("\nTo remove a site: python scripts/unpublish_site.py --slug <slug>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
