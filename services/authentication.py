# services/authentication.py
from configs.config import API_KEY_MAP
from fastapi import Request, HTTPException

def authenticate_and_get_api_key(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    wrapper_key = auth.split(" ", 1)[1].strip()
    real_key = API_KEY_MAP.get(wrapper_key)
    if not real_key:
        raise HTTPException(status_code=403, detail="Invalid wrapper API key")

    return real_key