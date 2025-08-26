# routers/embeddings.py
from typing import Dict, Any
from configs.config import UPSTREAM_BASE, DEFAULT_EMBED_MODEL
import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from services.authentication import authenticate_and_get_api_key

router = APIRouter()

@router.post("/embeddings")
async def embeddings(body: Dict[str, Any], real_key: str = Depends(authenticate_and_get_api_key)):

    allowed = {"input", "encoding_format", "dimensions", "user", "metadata"}
    payload: Dict[str, Any] = {"model": body.get("model", DEFAULT_EMBED_MODEL)}
    payload.update({k: v for k, v in body.items() if k in allowed and v is not None})

    if "input" not in payload:
        raise HTTPException(status_code=400, detail="'input' is required")

    headers = {
        "Authorization": f"Bearer {real_key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }

    try:
        async with httpx.AsyncClient(timeout=None) as client:
            r = await client.post(f"{UPSTREAM_BASE}/embeddings", headers=headers, json=payload)
            r.raise_for_status()
            return JSONResponse(r.json())
    except httpx.HTTPStatusError as e:
        detail = e.response.text if e.response is not None else str(e)
        raise HTTPException(status_code=e.response.status_code if e.response else 502, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
