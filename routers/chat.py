# routers/chat.py
from typing import Dict, Any
import json
from configs.config import UPSTREAM_BASE, DEFAULT_CHAT_MODEL
import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from services.authentication import authenticate_and_get_api_key

router = APIRouter()

@router.post("/chat/completions")
async def chat_completions(body: Dict[str, Any], real_key: str = Depends(authenticate_and_get_api_key)):
    allowed = {
        "messages","temperature","max_tokens","top_p","n","stop",
        "presence_penalty","frequency_penalty","logit_bias","user",
        "tools","tool_choice","response_format","metadata","logprobs",
        "top_logprobs","seed"
    }
    payload: Dict[str, Any] = {"model": body.get("model", DEFAULT_CHAT_MODEL)}
    payload.update({k: v for k, v in body.items() if k in allowed and v is not None})

    stream = bool(body.get("stream", False))

    if not stream:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                r = await client.post(
                    f"{UPSTREAM_BASE}/chat/completions",
                    headers={"Authorization": f"Bearer {real_key}", "Content-Type": "application/json"},
                    json=payload,
                )
                r.raise_for_status()
                return JSONResponse(r.json())
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

    # --- Streaming ---
    payload["stream"] = True
    url = f"{UPSTREAM_BASE}/chat/completions"

    async def forward_sse():
        headers = {
            "Authorization": f"Bearer {real_key}",
            "Content-Type": "application/json",
            "Accept-Encoding": "identity",
        }
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as r:
                    r.raise_for_status()
                    async for chunk in r.aiter_raw():
                        if chunk:
                            yield chunk
        except Exception as e:
            err = {"error": {"message": str(e)}}
            yield f"data: {json.dumps(err)}\n\n".encode()
            yield b"data: [DONE]\n\n"

    return StreamingResponse(
        forward_sse(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
