import logging

from fastapi import FastAPI, Header, Request, Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from opalizer.api.events.router import events_router
from opalizer.api.store.router import stores_router
from opalizer.api.tenants.router import tenants_router
from opalizer.api.tenants.service import upgrade_head
from opalizer.config import settings
from opalizer.core.logging import setup_logging
from opalizer.core.rate_limiter import limiter

log = logging.getLogger(__name__)
setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app.name)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return app


app = create_app()
app.include_router(router=tenants_router)
app.include_router(stores_router)
app.include_router(events_router)


@app.get("/")
@limiter.limit("10/second")
def get_home(
    request: Request,
    response: Response,
):
    return {"name": settings.app.name}


@app.get("/ip")
@limiter.limit("10/second")
def get_ip(
    request: Request,
    response: Response,
    x_forwarded_for: str = Header(None, alias="X-Forwarded-For"),
):
    return {"ip": x_forwarded_for}


@app.on_event("startup")
async def startup_event():
    try:
        await upgrade_head(tenant_name="public", revision="192b914e7f19")
        logging.info("Starting up...")
    except Exception as e:
        print(f"startup error - {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    import os

    try:
        os.remove("log.log")
    except FileNotFoundError:
        print("File is not present in the system.")
    logging.info("Shutting down...")
