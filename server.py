from fastapi import FastAPI
from routers import chat, embeddings

app = FastAPI(title="Multi-key OpenAI Wrapper", version="1.0.0")

app.include_router(chat.router, prefix="/api/v1")
app.include_router(embeddings.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)