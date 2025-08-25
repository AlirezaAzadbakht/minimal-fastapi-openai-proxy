from configs.config import API_KEY_MAP
from fastapi import Request, HTTPException
from openai import OpenAI

def extract_wrapper_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    return auth.split(" ", 1)[1].strip()

def get_client(wrapper_key: str) -> OpenAI:
    if wrapper_key not in API_KEY_MAP:
        raise HTTPException(status_code=403, detail="Invalid wrapper API key")
    return OpenAI(api_key=API_KEY_MAP[wrapper_key])
