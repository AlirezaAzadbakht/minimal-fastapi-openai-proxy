# minimal-fastapi-openai-proxy

A **minimal FastAPI proxy** for [OpenAI](https://platform.openai.com) APIs — focused on **Chat Completions** and **Embeddings**.

✨ Features:
- Exposes **OpenAI-compatible endpoints** (`/v1/chat/completions`, `/v1/embeddings`)
- Works seamlessly with the **official OpenAI Python SDK**
- Supports **streaming chat completions (SSE)**
- Simple **wrapper → real API key mapping** (multi-tenant friendly)
- Lightweight & minimal — no database needed
- Deployable via **Supervisor** with included config

---

## 🚀 Quick Start

### 1. Clone & install
```bash
git clone https://github.com/yourname/minimal-fastapi-openai-proxy.git
cd minimal-fastapi-openai-proxy
pip install -r requirements.txt
````

### 2. Configure keys

Copy the example config and add your keys:

```bash
cp configs/config.py.example configs/config.py
```

Edit `configs/config.py` and set your wrapper → real OpenAI key mappings:

```python
API_KEY_MAP = {
    "wrapper-key-alice": "sk-alice-real-openai-key",
    "wrapper-key-bob":   "sk-bob-real-openai-key",
}
```

Each **wrapper key** is used by clients.
Each **mapped key** is the real OpenAI API key.

### 3. Run the server (local dev)

```bash
uvicorn server:app --reload
```

Server runs at: [http://localhost:8000](http://localhost:8000)

---

## 🔑 Usage with OpenAI SDK

Point the SDK to your proxy and use a **wrapper key**:

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
    for text in stream.text_stream:
        print(text, end="")
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
  Compatible with OpenAI **Chat Completions API** (supports `stream: true` for SSE).

* `POST /v1/embeddings`
  Compatible with OpenAI **Embeddings API**.

* `GET /health`
  Health check endpoint.

---

## 📦 Deployment with Supervisor

For production, use **Supervisor** to manage the process.

### 1. Supervisor config

Save as `configs/minimal-fastapi-openai-proxy.conf`:

```ini
[program:minimal-fastapi-openai-proxy]
command=/home/ubuntu/minimal-fastapi-openai-proxy/service.sh
directory=/home/ubuntu/minimal-fastapi-openai-proxy
autostart=true
autorestart=true
environment=PATH=/home/ubuntu/miniconda3/envs/minimal-fastapi-openai-proxy/bin:/usr/bin
redirect_stderr=true
stdout_logfile=/home/ubuntu/minimal-fastapi-openai-proxy/server.log
stopasgroup=true
```

Place it in `/etc/supervisor/conf.d/` and reload:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start minimal-fastapi-openai-proxy
```

### 2. `service.sh`

Included script to run Uvicorn:

```bash
#!/bin/bash
PORT=8000
PID=$(lsof -t -i:$PORT)
if [ -n "$PID" ]; then
    kill -9 $PID
    echo "Killed process using port $PORT"
fi
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1
```

Adjust `--workers` to fit your server resources.

---

## 🙌 Why?

OpenAI’s API is powerful, but sometimes you need:

* Multi-tenant key management
* A lightweight proxy layer
* Compatibility with the official SDK
* Minimal setup with no DB

That’s exactly what **minimal-fastapi-openai-proxy** provides.

---

## 📜 License

MIT License – free to use, modify, and share.
See [LICENSE](./LICENSE) for details.