"""Pre-flight check: confirm credentials load correctly and that publishing
to TOS actually works end-to-end, before doing any real page-building work.
TOS is optional: if none of its settings are configured, this checks the local
publish folder instead (config.json's `local_publish_dir`, if set).
Run this first when setting up the skill somewhere new, after changing
credential.json, or whenever a build's publish step seems off.

Usage:
    python scripts/precheck.py

Exits 0 if everything needed for a normal build+publish run checks out,
1 if anything is missing or broken (with a specific reason for each).
"""
import json
import sys
import time
import uuid
from pathlib import Path


from credentials import describe_credential, load_bucket, tos_status
from site_paths import local_publish_root

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

CREDENTIAL_CHECKS = [
    ("tos_access_key_id", "publish_site.py / unpublish_site.py"),
    ("tos_secret_access_key", "publish_site.py / unpublish_site.py"),
]


def _mask(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def check_credentials() -> bool:
    print("Checking credentials...")
    all_ok = True
    for key_name, needed_by in CREDENTIAL_CHECKS:
        value, source = describe_credential(key_name)
        if value:
            print(f"  {key_name:<24} OK       ({source}, {_mask(value)}) — needed by {needed_by}")
        else:
            print(f"  {key_name:<24} MISSING  — needed by {needed_by}. Set it in credential.json "
                  f"(copy credential_tmp.json first) or the ${key_name} environment variable.")
            all_ok = False
    return all_ok


def check_publish() -> bool:
    import requests  # TOS only — not needed when sites are kept locally
    from tos_client import delete_object, put_object

    print("\nChecking site publish (live TOS round-trip)...")

    try:
        config = load_config()
        endpoint, region, bucket = config["tos_endpoint"], config["tos_region"], load_bucket(config)
    except Exception as exc:
        print(f"  FAILED — couldn't read TOS settings from config.json: {exc}")
        return False

    access_key, _ = describe_credential("tos_access_key_id")
    secret_key, _ = describe_credential("tos_secret_access_key")
    if not access_key or not secret_key:
        print("  SKIPPED — TOS credentials aren't loaded (see credential check above).")
        return False

    test_key = f"_precheck/{uuid.uuid4().hex}.txt"
    test_content = f"precheck {time.time()}".encode("utf-8")
    public_url = f"https://{bucket}.{endpoint}/{test_key}"

    try:
        put_object(endpoint, region, bucket, test_key, access_key, secret_key, test_content, "text/plain")
        print("  publish test object ..... OK")
    except Exception as exc:
        print(f"  publish test object ..... FAILED: {exc}")
        return False

    fetch_ok = False
    try:
        resp = requests.get(public_url, timeout=30)
        if resp.status_code == 200 and resp.content == test_content:
            print("  fetch test object ....... OK (200, content matches)")
            fetch_ok = True
        else:
            print(f"  fetch test object ....... FAILED (status {resp.status_code})")
    except Exception as exc:
        print(f"  fetch test object ....... FAILED: {exc}")

    cleanup_ok = False
    try:
        delete_object(endpoint, region, bucket, test_key, access_key, secret_key)
        print("  unpublish test object ... OK")
        cleanup_ok = True
    except Exception as exc:
        print(f"  unpublish test object ... FAILED: {exc} (remove {test_key!r} from the bucket manually)")

    return fetch_ok and cleanup_ok


def check_local(config: dict) -> bool:
    root = local_publish_root(config)
    if root is None:
        print("  Finished pages stay in _output/<slug>/ (no local_publish_dir set in config.json).")
        return True
    probe = root / f".precheck-{uuid.uuid4().hex}"
    try:
        probe.write_text("precheck", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        print(f"  local_publish_dir {root} ... FAILED: not writable ({exc})")
        return False
    print(f"  Finished pages are copied to {root}/<slug>/ ... OK (writable)")
    return True


def main() -> int:
    try:
        config = load_config()
    except Exception as exc:
        print(f"FAILED — couldn't read config.json: {exc}")
        return 1
    state, missing = tos_status(config)
    if state == "off":
        print("TOS publishing isn't configured (optional) — sites are kept locally.")
        ok = check_local(config)
        print("\nAll checks passed — safe to proceed." if ok else "\nFix the issue above before proceeding.")
        return 0 if ok else 1
    if state == "partial":
        print(f"TOS is only partly configured — missing: {', '.join(missing)}.\n"
              f"Fill those in to publish to TOS, or remove the other TOS settings to keep sites local.")
        return 1

    creds_ok = check_credentials()

    tos_creds_present = bool(describe_credential("tos_access_key_id")[0]) and \
        bool(describe_credential("tos_secret_access_key")[0])
    if tos_creds_present:
        publish_ok = check_publish()
    else:
        print("\nSkipping publish check — TOS credentials aren't loaded.")
        publish_ok = False

    print()
    if creds_ok and publish_ok:
        print("All checks passed — safe to proceed.")
        return 0
    print("One or more checks failed — fix the issues above before proceeding.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
