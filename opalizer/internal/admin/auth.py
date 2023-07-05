import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from opalizer.config import settings

basicAuth = HTTPBasic()


def validate_basic_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(basicAuth)]
):
    """ """
    current_username_bytes = credentials.username.encode("utf8")

    correct_username_bytes = settings.admin.username.encode("utf-8")

    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )

    current_password_bytes = credentials.password.encode("utf8")

    correct_password_bytes = settings.admin.password.encode("utf-8")

    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
