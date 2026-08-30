"""BytePlus Ark REST API clients used by this skill's scripts — chat completions
(content writing) and image generation. Plain HTTP via `requests`, no vendor SDK.

Trimmed from agent_work/skill/video-workflow/scripts/ark_service.py: this skill only
ever writes copy and generates static images, so the video-generation client isn't
included here.
"""
import base64
import sys
import time
import urllib.request
from pathlib import Path

import requests


def guess_mime_from_path(path) -> str:
    ext = str(path).rsplit(".", 1)[-1].lower() if "." in str(path) else ""
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "png":
        return "image/png"
    if ext == "gif":
        return "image/gif"
    if ext == "webp":
        return "image/webp"
    return "application/octet-stream"


def file_to_data_url(path) -> str:
    path = Path(path)
    data = path.read_bytes()
    mime = guess_mime_from_path(path)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def download_file(url: str, output_path) -> float:
    """Downloads file and returns elapsed seconds."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    with urllib.request.urlopen(url) as resp, output_path.open("wb") as f:
        f.write(resp.read())
    return time.monotonic() - t0


class ArkChatService:
    """Text chat-completions client (e.g. Deepseek models) for content writing."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 120):
        self._url = base_url.rstrip('/') + '/chat/completions'
        self._headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        self._timeout = timeout

    def complete(self, model_id: str, system_prompt: str, user_prompt: str,
                 temperature: float | None = None) -> str:
        print(f"Chat completion: model={model_id} system_len={len(system_prompt)} "
              f"user_len={len(user_prompt)}", file=sys.stderr)

        payload = {
            'model': model_id,
            'messages': [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            'stream': False,
        }
        if temperature is not None:
            payload['temperature'] = temperature

        resp = requests.post(self._url, headers=self._headers, json=payload, timeout=self._timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"Ark API error {resp.status_code}: {resp.text}")
        data = resp.json()

        choices = data.get('choices') or []
        if not choices:
            raise RuntimeError(f"Chat completion returned no choices: {data}")
        text = (choices[0].get('message') or {}).get('content', '').strip()
        print(f"Chat completion done: result_len={len(text)}", file=sys.stderr)
        return text


class ArkImageService:
    """Seedream image generation client."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 300):
        self._url = base_url.rstrip('/') + '/images/generations'
        self._headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        self._timeout = timeout

    def generate_image(self, model_id: str, prompt: str, image: list[str] | str | None = None,
                        size: str | None = None, watermark: bool | None = None) -> list[dict]:
        img_count = len(image) if isinstance(image, list) else (1 if image else 0)
        print(f"Image generation: model={model_id} prompt_len={len(prompt)} images={img_count} "
              f"size={size} watermark={watermark}", file=sys.stderr)

        payload = {
            'model': model_id,
            'prompt': prompt,
            'response_format': 'url',
        }
        if image:
            payload['image'] = image
        if size is not None:
            payload['size'] = size
        if watermark is not None:
            payload['watermark'] = watermark

        resp = requests.post(self._url, headers=self._headers, json=payload, timeout=self._timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"Ark API error {resp.status_code}: {resp.text}")
        data = resp.json()

        images = [
            {'url': img.get('url'), 'b64_json': img.get('b64_json')}
            for img in (data.get('data') or [])
        ]
        print(f"Image generation done: count={len(images)}", file=sys.stderr)
        return images
