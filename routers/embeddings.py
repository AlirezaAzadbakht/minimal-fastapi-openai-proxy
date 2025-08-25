from typing import Dict, Any
from configs.config import DEFAULT_EMBED_MODEL
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from services.authentication import extract_wrapper_key, get_client

router = APIRouter()

@router.post("/v1/embeddings")
async def embeddings(request: Request, body: Dict[str, Any]):
    wrapper_key = extract_wrapper_key(request)
    client = get_client(wrapper_key)

    try:
        result = client.embeddings.create(
            model=body.get("model", DEFAULT_EMBED_MODEL),
            input=body.get("input"),
        )
        return JSONResponse(result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
