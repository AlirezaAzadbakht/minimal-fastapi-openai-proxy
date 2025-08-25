# minimal-fastapi-openai-proxy

A **minimal FastAPI proxy** for [OpenAI](https://platform.openai.com) APIs — focused on **Chat Completions** and **Embeddings**.

✨ Features:
- Exposes **OpenAI-compatible endpoints** (`/v1/chat/completions`, `/v1/embeddings`)
- Works out-of-the-box with the **official OpenAI Python SDK**
- Supports **streaming chat completions (SSE)**
- Simple **wrapper API keys → real OpenAI API key mapping** (multi-tenant friendly)
- Lightweight & minimal — no database required (can extend if needed)

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/yourname/minimal-fastapi-openai-proxy.git
cd minimal-fastapi-openai-proxy
pip install -r requirements.txt
````

### 2. Configure keys

Edit `main.py` or set environment variables:

```python
# main.py
API_KEY_MAP = {
    "wrapper-key-alice": "sk-alice-real-openai-key",
    "wrapper-key-bob":   "sk-bob-real-openai-key",
}
```

Each **wrapper key** is what your clients use.
Each **mapped OpenAI key** is the real upstream key.

### 3. Run the server

```bash
uvicorn main:app --reload
```

Server runs at [http://localhost:8000](http://localhost:8000).

---

## 🔑 Usage with OpenAI SDK

Point the SDK to your proxy, and pass a **wrapper key**:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="wrapper-key-alice",  # your wrapper key
)

# Chat
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello from FastAPI proxy!"}],
)
print(resp.choices[0].message.content)

# Streaming Chat
with client.chat.completions.stream(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a haiku about FastAPI"}],
) as stream:
    for event in stream:
        if event.choices:
            delta = event.choices[0].delta
            if delta.content:
                print(delta.content, end="")
    print()

# Embeddings
emb = client.embeddings.create(
    model="text-embedding-3-small",
    input=["fast and minimal proxy"],
)
print(len(emb.data[0].embedding), "dims")
```

---

## 🧩 API Endpoints

* `POST /v1/chat/completions`
  Compatible with OpenAI Chat Completions API (supports `stream: true` for SSE).

* `POST /v1/embeddings`
  Compatible with OpenAI Embeddings API.

* `GET /health`
  Simple health check endpoint.

---

## 📜 License

MIT License – free to use, modify, and share.
See [LICENSE](./LICENSE) for details.

---

## 🙌 Why?

OpenAI’s official API is powerful, but sometimes you need:

* Multi-tenant key management
* A lightweight proxy layer
* Compatibility with the OpenAI Python SDK
* Minimal setup without extra dependencies

That’s exactly what **minimal-fastapi-openai-proxy** provides.

