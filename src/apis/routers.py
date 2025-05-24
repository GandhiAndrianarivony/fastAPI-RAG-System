import logging
from contextlib import asynccontextmanager
from collections import defaultdict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.apps.healthcheck.routes import healthcheck_router_v1
from src.apps.chat.routes.chat import chat_router_v1
from src.services.llms.providers import OllamaProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async context manager for LLMEngine lifecycle management."""

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Create LLMEngine instance
        app.state.rag = defaultdict(dict)
        app.state.rag["default"] = {
            "provider": OllamaProvider()
        }
        yield

    except Exception as e:
        logger.error(f"Error during LLMEngine initialization: {str(e)}")
        raise
    finally:
        # Cleanup resources if needed
        logger.info("Cleaning up LLM resources...")



def create_app():
    app = FastAPI(lifespan=lifespan)

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


def include_router(app: FastAPI) -> None:
    api_prefix = "/api"

    app.include_router(healthcheck_router_v1, prefix=api_prefix)
    app.include_router(chat_router_v1, prefix=api_prefix)


app = create_app()
