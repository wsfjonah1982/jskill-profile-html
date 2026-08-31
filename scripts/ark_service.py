"""BytePlus Ark REST API client used by this skill's scripts — chat completions
for content writing. Plain HTTP via `requests`, no vendor SDK.

This skill does not generate images (see scripts/fit_image.py instead, which
processes a user's own uploaded photo — no Ark call, no credentials needed).
"""
import sys

import requests


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
