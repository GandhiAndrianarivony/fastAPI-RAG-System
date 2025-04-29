from fastapi import APIRouter


healthcheck_router_v1 = APIRouter(prefix="/v1", tags=["Healthcheck (v1)"])


@healthcheck_router_v1.get("/healthcheck")
async def healthcheck() -> dict:
    return {"status": "ok"}
