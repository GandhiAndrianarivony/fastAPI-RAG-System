import asyncio
import tempfile
import os
import uuid
import logging

from fastapi import APIRouter, UploadFile, HTTPException, Request
from fastapi.responses import StreamingResponse

from llama_index.core.base.llms.types import CompletionResponseGen
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine

from ..schemas import QASchema

chat_router_v1 = APIRouter(prefix="/v1", tags=["Chat (v1)"])


async def generate(generator: CompletionResponseGen):
    for chunk in generator:
        await asyncio.sleep(0.05)
        yield chunk


@chat_router_v1.post("/chat")
async def chat(request: Request, question: QASchema):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Engine ID: {question.engine_id}")
    engine:  BaseQueryEngine = request.app.state.llm_engines.get(question.engine_id)
    logger.info(f"Engine keys: {list(request.app.state.llm_engines.keys())}")
    if engine is None:
        raise HTTPException(status_code=404, detail="Engine not found")

    else:
        response = engine.query(question.query)

        return StreamingResponse(
            generate(response.response_gen),
            media_type="text/event-stream",
        )


@chat_router_v1.post("/files")
async def upload_files_for_chat(request: Request, files: list[UploadFile]):
    document_content_types = {"application/pdf"}

    provider = request.app.state.llm_provider
    for file in files:
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File content type is required")

        if file.content_type not in document_content_types:
            error_detail = f"Unsupported file content type: {file.content_type}. Support file type include .pdf"
            raise HTTPException(status_code=400, detail=error_detail)

    # LOAD DATA
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(temp_dir, files[-1].filename)

        with open(temp_file, "wb") as f:
            contents = files[-1].file.read()
            f.write(contents)

        docs = SimpleDirectoryReader(temp_dir).load_data()

    # TODO: Add Qdrant vector store
    index = VectorStoreIndex.from_documents(
        docs,
        # storage_context=storage_context,
        embed_model=provider.embedding,
        show_progress=True,
    )

    query_engine = index.as_query_engine(llm=provider.llm, streaming=True)
    engine_id = uuid.uuid4()
    request.app.state.llm_engines[engine_id.hex] = query_engine

    # TODO: StoStoreStoreStorere in cookies
    return {"engine_id": engine_id.hex}

    # response = query_engine.query("Give me the definition of Fine number")
    # return StreamingResponse(
    #     generate(response.response_gen),
    #     media_type="text/event-stream",
    # )

    # TODO: Process files
