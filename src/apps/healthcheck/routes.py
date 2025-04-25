from fastapi import APIRouter


healthcheck_router = APIRouter()

@healthcheck_router.get("/healthcheck")
async def healthcheck()-> dict:
    return {"status": "ok"}