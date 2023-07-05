import base64
import secrets

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


def ensure_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
) -> str:
    """Ensure's that api key is present in headers or query path"""

    if api_key_header:
        return api_key_header
    if api_key_query:
        return api_key_query

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


def generate_api_key(tenant_id: str) -> str:
    sec_bytes = f"{tenant_id}:{secrets.token_urlsafe(16).replace(':', '_')}".encode(
        encoding="utf-8"
    )
    return base64.b64encode(sec_bytes).decode(encoding="utf-8")


def get_tenant_id_from_api_key(api_key: str = Depends(ensure_api_key)) -> str:
    """ """
    try:
        result = base64.b64decode(api_key).decode(encoding="utf=8").split(":")
        if not len(result) == 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key",
            )
        return result[0]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
