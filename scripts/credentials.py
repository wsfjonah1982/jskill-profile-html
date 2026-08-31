"""Shared credential loading for this skill's scripts.

Priority: credential.json first (the artifact this skill ships and documents,
see credential_tmp.json), falling back to an environment variable of the same
name as the credential.json key — only if the key is missing, blank, or the
file doesn't exist at all.
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIAL_PATH = BASE_DIR / "credential.json"


def _load_credential_file() -> dict:
    if not CREDENTIAL_PATH.exists():
        return {}
    with CREDENTIAL_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_credential(key_name: str) -> str:
    """Look up `key_name` in credential.json; if it's missing, blank, or the
    file doesn't exist, fall back to the environment variable of the same
    name (e.g. `model_ark_key` -> $model_ark_key). Raises KeyError if neither
    source has it."""
    value, source = describe_credential(key_name)
    if source == "missing":
        raise KeyError(
            f"`{key_name}` not found in {CREDENTIAL_PATH.name} and ${key_name} is not set. "
            f"Copy credential_tmp.json to credential.json and fill it in, or set ${key_name}."
        )
    return value


def describe_credential(key_name: str) -> tuple[str | None, str]:
    """Non-raising counterpart to load_credential — returns (value, source)
    where source is 'credential.json', 'environment variable', or 'missing'.
    Used by scripts/precheck.py to report where each credential is coming
    from (or that it's absent) without failing outright."""
    value = _load_credential_file().get(key_name)
    if value:
        return value, "credential.json"
    env_value = os.environ.get(key_name)
    if env_value:
        return env_value, "environment variable"
    return None, "missing"
