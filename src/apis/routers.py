from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.apps.healthcheck.routes import healthcheck_router
from src.apps.chat.routes.chat import chat_router


def create_app():
    app = FastAPI()

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update this with your frontend URL for security
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],
    )

    include_router(app)

    return app


def include_router(app: FastAPI, version: str = "v1") -> None:
    api_prefix = f"/api/{version}"
    app.include_router(healthcheck_router, prefix=api_prefix)
    app.include_router(chat_router, prefix=api_prefix)


app = create_app()
