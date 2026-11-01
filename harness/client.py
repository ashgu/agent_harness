"""Thin HTTP client for Ollama's /api/chat endpoint.

Uses only urllib (stdlib). No requests, no SDK.
The client is stateless: the CALLER manages the messages list.
"""

import json
import urllib.request
import urllib.error
from typing import List, Optional, Union

from .config import Config

class OllamaError(Exception):
    """Raised when the Ollama API is unreachable or returns an error."""

class OllamaClient:
    def __init__(self, config: Config):
        self._cfg = config

    def chat(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        fmt: Optional[Union[str, dict]] = None,
    ) -> dict:
        """POST to /api/chat and return the response `message` dict.

        messages + Config ──► build body (dict) ──► JSON POST ──► Ollama
                                                                  │
        response dict ◄── json.loads ◄── urlopen ◄────────────────┘

        Returns:
            Text reply:  {"role": "assistant", "content": "…"}
            Tool call:   {"role": "assistant", "content": "", "tool_calls": […]}
        """

        # body: JSON payload you send in the body of the HTTP POST request to Ollama
        body: dict = {
            "model": self._cfg.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self._cfg.temperature},
        }
        if tools:
            body["tools"] = tools
        if fmt is not None:
            body["format"] = fmt

        url = f"{self._cfg.base_url.rstrip('/')}/api/chat"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(), # body serialized to JSON bytes
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self._cfg.timeout) as resp:
                payload = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            err = e.read().decode(errors="replace")
            raise OllamaError(f"HTTP {e.code}: {err}") from e
        except urllib.error.URLError as e:
            raise OllamaError(f"Cannot reach Ollama at {url}: {e}") from e

        return payload.get("message", {})
