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
            # Helpful skip when server isn’t up or key is wrong
            if "Connection refused" in str(e) or "ECONNREFUSED" in str(e):
                pytest.skip(f"Server not reachable at {BASE_URL}")
            raise
    return _inner

@connection_guard
def test_embeddings_basic():
    c = client()
    resp = c.embeddings.create(
        model="text-embedding-3-small",
        input=["hello world"],
    )
    assert resp.data and isinstance(resp.data[0].embedding, list)
    assert len(resp.data[0].embedding) > 100  # sanity check: dimensionality
