"""Minimal OpenAI-compatible embedding function using requests.

chromadb's OpenAIEmbeddingFunction uses an httpx client that fails against the
local gateway (connection error) even though /v1/embeddings works with curl.
"""
from __future__ import annotations

import time
from typing import Sequence

import requests
from chromadb.api.types import Documents, Embeddings


class HTTPEmbeddingFunction:
    def __init__(self, model_name: str, base_url: str, api_key: str, timeout: float = 120.0):
        self.model_name = model_name
        self.url = base_url.rstrip("/") + "/embeddings"
        self.api_key = api_key
        self.timeout = timeout

    def name(self) -> str:
        return "http-embedding"

    def __call__(self, input: Documents) -> Embeddings:
        docs = list(input)
        last = None
        for attempt in range(4):
            try:
                resp = requests.post(
                    self.url,
                    headers={"Authorization": f"Bearer {self.api_key}",
                             "Content-Type": "application/json"},
                    json={"model": self.model_name, "input": docs},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                data = resp.json()["data"]
                data = sorted(data, key=lambda x: x.get("index", 0))
                out = [x["embedding"] for x in data]
                if len(out) != len(docs):
                    raise RuntimeError(f"embedding count {len(out)} != {len(docs)}")
                return out
            except Exception as exc:
                last = exc
                time.sleep(1 + attempt)
        raise RuntimeError(f"embedding request failed: {last}")