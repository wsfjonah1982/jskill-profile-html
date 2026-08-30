"""Draft page copy (tagline, bio, section-specific content) from a filled
_input/brief.md, via an Ark chat-completion model — using this skill's own
prompt_templates/content_writing_system.md and content_writing_user.md.

This produces a *draft* to review and place into the chosen template's HTML slots
per AGENTS.md §3 — it does not edit any HTML itself. The system prompt enforces the
same no-fabricated-proof-points rule as AGENTS.md §6.

Usage:
    python scripts/write_content.py --brief _input/brief.md --category "e-commerce" --mood "bold and graphic"
    python scripts/write_content.py --brief _input/brief.md --category "restaurant/cafe" --mood "warm and personal" --output _output/warm-bistro-cafe/content-draft.md
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from ark_service import ArkChatService
from credentials import load_credential

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
LOG_DIR = BASE_DIR / "_log"
PROMPT_TEMPLATES_DIR = BASE_DIR / "prompt_templates"


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
    parser.add_argument("--brief", default=str(BASE_DIR / "_input" / "brief.md"),
                         help="Path to the filled content brief (default: _input/brief.md)")
    parser.add_argument("--category", required=True,
                         help='One of: "profile/bio", "e-commerce", "restaurant/cafe", "course/coaching"')
    parser.add_argument("--mood", required=True, help="The requested mood/tone, e.g. \"dark and moody\"")
    parser.add_argument("--output", default=None, help="Optional path to also save the draft to")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    log_path = LOG_DIR / f"{brief_path.stem}-content-draft.log"

    try:
        if not brief_path.exists():
            raise FileNotFoundError(
                f"Brief not found: {brief_path} — copy _input/brief.template.md to _input/brief.md and fill it in first."
            )

        config = load_config()
        model_id = config["chat_model_id"]
        temperature = config.get("chat_temperature")
        base_url = config["maas_api_endpoint"]
        api_key = load_credential("model_ark_key")

        system_prompt = (PROMPT_TEMPLATES_DIR / "content_writing_system.md").read_text(encoding="utf-8")
        user_template = (PROMPT_TEMPLATES_DIR / "content_writing_user.md").read_text(encoding="utf-8")
        brief_text = brief_path.read_text(encoding="utf-8")

        user_prompt = (
            user_template
            .replace("{{category}}", args.category)
            .replace("{{mood}}", args.mood)
            .replace("{{brief}}", brief_text)
        )

        service = ArkChatService(base_url=base_url, api_key=api_key,
                                   timeout=config.get("chat_request_timeout_seconds", 120))
        draft = service.complete(model_id=model_id, system_prompt=system_prompt,
                                  user_prompt=user_prompt, temperature=temperature)

        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "model": model_id,
            "brief": str(brief_path), "category": args.category, "mood": args.mood,
            "status": "succeeded", "result_len": len(draft),
        })

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(draft, encoding="utf-8")
            print(str(output_path))
        else:
            print(draft)
        return 0

    except Exception as exc:
        write_log(log_path, {
            "timestamp": datetime.now(timezone.utc).isoformat(), "brief": str(brief_path),
            "status": "failed", "error": str(exc),
        })
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
