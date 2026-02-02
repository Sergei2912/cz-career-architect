import os

from fastapi import Header, HTTPException, status


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """Optional API-key auth.

    If API_KEY env var is set, require callers to send matching X-API-Key.
    If API_KEY is not set, allow requests (dev-friendly default).
    """

    expected = os.getenv("API_KEY")
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
