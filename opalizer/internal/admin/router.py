from typing import Annotated

from fastapi import APIRouter, Depends

from opalizer.internal.admin.utils import validate_basic_credentials

admin_router = APIRouter(prefix="/admin")


@admin_router.get("/me")
def read_current_user(username: Annotated[str, Depends(validate_basic_credentials)]):
    return {"username": username}
