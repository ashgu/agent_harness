"""Tunable settign for the harness.

Priority: explicit constructor args  >  environment variables  >  defaults.
"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    base_url: str = "http://localhost:11434"
    model: str = "qwen3.8:latest"
    temperature: float = 0.1
    timeout: int = 60  # seconds for the HTTP request

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config from OLLAMA_BASE_URL / OLLAMA_MODEL env vars."""
        return cls(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.environ.get("OLLAMA_MODEL", "qwen3.8:latest"),
        )