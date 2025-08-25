import json
from typing import AsyncIterator, Dict, Any
from configs.config import DEFAULT_CHAT_MODEL
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from services.authentication import extract_wrapper_key, get_client

router = APIRouter()

@router.post("/v1/chat/completions")
async def chat_completions(request: Request, body: Dict[str, Any]):
    wrapper_key = extract_wrapper_key(request)
    client = get_client(wrapper_key)

    model = body.get("model", DEFAULT_CHAT_MODEL)
    stream = bool(body.get("stream", False))

    kwargs = dict(
        model=model,
        messages=body.get("messages"),
        temperature=body.get("temperature"),
        max_tokens=body.get("max_tokens"),
    )

    try:
        if not stream:
            result = client.chat.completions.create(**kwargs)
            return JSONResponse(result.model_dump())

        def gen() -> AsyncIterator[bytes]:
            try:
                with client.chat.completions.stream(**kwargs) as s:
                    for event in s:
                        yield f"data: {json.dumps(event.model_dump())}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"
            except Exception as e:
                err = {"error": {"message": str(e)}}
                yield f"data: {json.dumps(err)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
