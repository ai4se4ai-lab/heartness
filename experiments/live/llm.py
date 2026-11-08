"""Deterministic local LLM access through Ollama with an append-only response cache.

Every request is keyed by (model, prompt, options). Cached responses make every run
replayable bit-for-bit without the model server; a fresh cache reproduces the run with
the same pinned model digest (recorded in each run record).
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

HOST = os.environ.get("HEARTNESS_OLLAMA", "http://127.0.0.1:11435")
_LOCK = threading.Lock()


def _post(path: str, payload: dict[str, Any], timeout: float = 600) -> dict[str, Any]:
    req = urllib.request.Request(HOST + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        result: dict[str, Any] = json.loads(response.read())
        return result


def model_digest(model: str) -> str:
    with urllib.request.urlopen(HOST + "/api/tags", timeout=30) as response:
        for item in json.loads(response.read())["models"]:
            if item["name"] == model:
                return str(item["digest"])
    raise KeyError(model)


class LLM:
    def __init__(self, cache_dir: Path, name: str) -> None:
        """Load every cache file in `cache_dir`; append only to this process's own file."""
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / f"{name}.jsonl"
        self.cache: dict[str, Any] = {}
        self.calls = 0
        self.hits = 0
        self.seconds = 0.0
        self.tokens_in = 0
        self.tokens_out = 0
        for path in sorted(cache_dir.glob("*.jsonl")):
            for line in path.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.cache[row["key"]] = row["value"]

    def _key(self, kind: str, model: str, body: Any) -> str:
        return hashlib.sha256(json.dumps([kind, model, body], sort_keys=True).encode()).hexdigest()

    def _store(self, key: str, value: Any) -> None:
        with _LOCK:
            self.cache[key] = value
            with self.cache_path.open("a") as handle:
                handle.write(json.dumps({"key": key, "value": value}) + "\n")

    def generate(self, model: str, prompt: str, *, seed: int = 0, max_tokens: int = 600,
                 system: str = "", fmt: dict[str, Any] | None = None) -> str:
        options = {"temperature": 0, "seed": seed, "num_predict": max_tokens, "num_ctx": 8192}
        body: dict[str, Any] = {"prompt": prompt, "system": system, "options": options}
        if fmt is not None:
            body["format"] = fmt  # constrained (structured) decoding
        key = self._key("generate", model, body)
        with _LOCK:
            self.calls += 1
            if key in self.cache:
                self.hits += 1
                return str(self.cache[key]["response"])
        start = time.perf_counter()
        payload: dict[str, Any] = {"model": model, "stream": False, **body}
        if model.startswith(("qwen3", "deepseek-r1")):
            payload["think"] = False  # hybrid reasoning models: answer directly
        data = _post("/api/generate", payload)
        with _LOCK:
            self.seconds += time.perf_counter() - start
        value = {"response": data.get("response", ""),
                 "prompt_eval_count": data.get("prompt_eval_count", 0),
                 "eval_count": data.get("eval_count", 0)}
        with _LOCK:
            self.tokens_in += int(value["prompt_eval_count"])
            self.tokens_out += int(value["eval_count"])
        self._store(key, value)
        return str(value["response"])

    def embed(self, model: str, text: str) -> list[float]:
        key = self._key("embed", model, text)
        if key in self.cache:
            return list(self.cache[key])
        data = _post("/api/embed", {"model": model, "input": text})
        vector = [float(x) for x in data["embeddings"][0]]
        self._store(key, vector)
        return vector

    def stats(self) -> dict[str, Any]:
        return {"calls": self.calls, "cache_hits": self.hits, "llm_seconds": round(self.seconds, 3),
                "tokens_in": self.tokens_in, "tokens_out": self.tokens_out}
