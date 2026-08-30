"""Shared credential loading for this skill's scripts.

Priority: credential.json first (the artifact this skill ships and documents,
see credential_tmp.json), falling back to an environment variable only if the
key is missing, blank, or the file doesn't exist at all.
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


def load_credential(key_name: str, env_var: str) -> str:
    """Look up `key_name` in credential.json; if it's missing, blank, or the
    file doesn't exist, fall back to the `env_var` environment variable.
    Raises KeyError if neither source has it."""
    value = _load_credential_file().get(key_name)
    if value:
        return value
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    raise KeyError(
        f"`{key_name}` not found in {CREDENTIAL_PATH.name} and {env_var} is not set. "
        f"Copy credential_tmp.json to credential.json and fill it in, or set {env_var}."
    )
