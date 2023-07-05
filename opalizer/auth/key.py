from fastapi import Depends, HTTPException, status

from opalizer.api.tenants.schemas import TenantSchema
from opalizer.auth.utils import ensure_api_key
from opalizer.database import get_tanant


def validate_api_key(
    tenant: TenantSchema = Depends(get_tanant),
    api_key: str = Depends(ensure_api_key),
) -> str:
    """Retrieve and validate an API key from the query parameters or HTTP header.

    :param  tenant: Tenant object.
    :param  api_key_header: The API key passed in the HTTP header.

    :returns
        The validated API key.

    :raises
        HTTPException: If the API key is invalid or missing.
    """

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing (Tenant name or Tenant Id)",
        )

    if api_key == tenant.api_key:
        return api_key

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )
