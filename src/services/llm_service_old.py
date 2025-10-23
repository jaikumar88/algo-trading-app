import os
import hashlib
from typing import List, Dict, Any

try:
    import openai as _openai
except Exception:
    _openai = None

import numpy as np

MOCK = os.getenv("MOCK_OPENAI", "false").lower() in ("1", "true", "yes")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not MOCK and _openai is not None and OPENAI_API_KEY:
    # configure the real openai client
    try:
        _openai.api_key = OPENAI_API_KEY
    except Exception:
        pass


def _mock_embedding(text: str) -> np.ndarray:
    """Create a deterministic mock embedding from the SHA256 digest."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    # convert bytes to floats in range [-1,1]
    arr = np.frombuffer(digest, dtype=np.uint8).astype("float32")
    arr = (arr / 255.0) * 2 - 1
    return arr


def embed_texts(
    texts: List[str], model: str = "text-embedding-3-small"
) -> List[np.ndarray]:
    """Return embeddings for a list of texts.

    Uses mock when MOCK_OPENAI is true. When mocking, returns deterministic
    small vectors (derived from a SHA256 digest).
    """
    if MOCK or _openai is None:
        return [_mock_embedding(t) for t in texts]

    resp = _openai.Embedding.create(model=model, input=texts)
    return [np.array(d["embedding"]) for d in resp["data"]]


def chat_completion(
    model: str,
    messages: List[Dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """Invoke ChatCompletion; returns an object similar to OpenAI's response.

    In MOCK mode, returns a fixed reply that echoes the user's last message.
    """
    if MOCK or _openai is None:
        # find last user message
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")
                break
        reply = (
            "MOCK RESPONSE:\nThis is a mocked ChatCompletion response.\n\n"
            f"User content (truncated 400 chars): {last_user[:400]}"
        )
        return {"choices": [{"message": {"content": reply}}]}

    resp = _openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp
