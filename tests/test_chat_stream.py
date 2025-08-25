import os
import pytest
from openai import OpenAI

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/v1")
WRAPPER_API_KEY = os.getenv("WRAPPER_API_KEY", "wrapper-key-alice")

def client() -> OpenAI:
    return OpenAI(base_url=BASE_URL, api_key=WRAPPER_API_KEY)

def connection_guard(fn):
    def _inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "Connection refused" in str(e) or "ECONNREFUSED" in str(e):
                pytest.skip(f"Server not reachable at {BASE_URL}")
            raise
    return _inner

@connection_guard
def test_chat_streaming_accumulates_text():
    c = client()
    chunks = []
    with c.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Write a 1-line greeting."}],
        max_tokens=30,
        stream=True,
    ) as stream:
        for event in stream:
            # The OpenAI SDK yields choice deltas for chat streams
            if getattr(event, "choices", None):
                delta = event.choices[0].delta
                if delta and getattr(delta, "content", None):
                    chunks.append(delta.content)

    text = "".join(chunks).strip()
    assert len(text) > 0
