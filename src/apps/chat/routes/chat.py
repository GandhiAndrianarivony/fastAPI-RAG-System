import asyncio
import tempfile
import os
import uuid
import logging

from fastapi import APIRouter, UploadFile, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from llama_index.core.base.llms.types import CompletionResponseGen
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core import Settings

from src.services.llms.registry import get_provider
from src.services.llms.providers import AbstractProvider

from ..schemas import QASchema, ProviderSchema

chat_router_v1 = APIRouter(prefix="/v1", tags=["Chat (v1)"])


async def generate(generator: CompletionResponseGen):
    for chunk in generator:
        await asyncio.sleep(0.05)
        yield chunk


@chat_router_v1.post("/chat")
async def chat(request: Request, question: QASchema):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Engine ID: {question.id}")

    rag = request.app.state.rag.get(question.id)
    if not rag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong id")

    engine: BaseQueryEngine = rag.get("query_engine")
    if not engine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Query engine not found"
        )

    response = engine.query(question.query)
    return StreamingResponse(
        generate(response.response_gen),
        media_type="text/event-stream",
    )


@chat_router_v1.post("/provider")
async def choose_provider(request: Request, provider: ProviderSchema):
    provider_name = provider.name
    identifier = uuid.uuid4().hex
    request.app.state.rag[identifier] = {"provider": get_provider(provider_name)}

    return {"id": identifier, "status": f"Successfully built provider: {provider_name}"}


@chat_router_v1.post("/files/{identifier}")
async def upload_files_for_chat(
    request: Request, identifier: str, files: list[UploadFile]
):
    document_content_types = {"application/pdf"}

    rag = request.app.state.rag.get(identifier)
    if not rag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong id")

    provider: AbstractProvider = rag.get("provider")
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found"
        )

    # Basic settings
    Settings.llm = provider.llm
    Settings.emded_model = provider.embedding
    Settings.chunk_size = 512
    node_parser = Settings.node_parser

    for file in files:
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File content type is required")

        if file.content_type not in document_content_types:
            error_detail = f"Unsupported file content type: {file.content_type}. Support file type include .pdf"
            raise HTTPException(status_code=400, detail=error_detail)

    # TODO: Chat with multiple data
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, files[-1].filename)

        with open(temp_file, "wb") as f:
            contents = files[-1].file.read()
            f.write(contents)

        documents = SimpleDirectoryReader(temp_dir).load_data()

    nodes = node_parser.get_nodes_from_documents(documents)
    index = VectorStoreIndex(nodes, embed_model=provider.embedding, show_progress=True)

    query_engine = index.as_query_engine(llm=provider.llm, streaming=True)
    request.app.state.rag[identifier]["query_engine"] = query_engine

    return {"id": identifier, "status": "Successfully create engine"}
