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
def test_chat_basic():
    c = client()
    resp = c.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say 'ok'"}],
        max_tokens=10,
    )
    assert resp.choices and resp.choices[0].message and resp.choices[0].message.content
    assert isinstance(resp.choices[0].message.content, str)
