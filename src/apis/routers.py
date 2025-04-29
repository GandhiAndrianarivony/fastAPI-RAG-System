import logging
import os
from contextlib import asynccontextmanager

import nltk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter

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
        # Initialize NLP resources
        logger.info("Initializing NLP resources...")
        nltk.download("punkt", quiet=True)  # Required for sentence splitting
        nltk.download("stopwords", quiet=True)

        # Configure LLM settings
        logger.info("Configuring LLM settings...")
        Settings.chunk_size = int(os.environ.get("CHUNK_SIZE", 256))
        text_splitter = SentenceSplitter(
            chunk_size=Settings.chunk_size,
            chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", 200)),
        )
        Settings.text_splitter = text_splitter

        # Initialize LLM provider
        provider_name = os.environ.get("PROVIDER", "Ollama").strip().lower()
        logger.info(f"Initializing {provider_name} provider...")

        # Create LLMEngine instance
        app.state.llm_engines = dict()
        app.state.llm_provider = OllamaProvider()

        logger.info("LLMEngine initialized successfully")
        yield

    except Exception as e:
        logger.error(f"Error during LLMEngine initialization: {str(e)}")
        raise
    finally:
        # Cleanup resources if needed
        logger.info("Cleaning up LLM resources...")
        # if hasattr(app.state, 'engine') and app.state.engine["query_engine"]:
        #     await app.state.engine["query_engine"].aclose()


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
