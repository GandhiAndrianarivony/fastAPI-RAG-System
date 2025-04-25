import asyncio

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from llama_index.core.base.llms.types import CompletionResponseGen

from src.services.llms.providers import ProviderEnum, OllamaProvider
from src.services.llms import registry

import nltk


nltk.download("punkt")  # Required for sentence splitting
nltk.download("stopwords")


chat_router = APIRouter()


async def generate(generator: CompletionResponseGen):
    for chunk in generator:
        await asyncio.sleep(0.05)
        yield chunk


@chat_router.get("/chat")
async def chat():
    fake_message = "Who is Nelson Mandela?"
    fake_provider = ProviderEnum.OLLAMA

    provider = registry.get_provider(fake_provider)
    response_generator = provider.stream_chat_response(fake_message)

    return StreamingResponse(
        generate(response_generator),
        media_type="text/event-stream",
    )


@chat_router.post("/files")
async def upload_files_for_chat(files: list[UploadFile]):
    import tempfile
    import os
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
    from llama_index.core import Settings
    from llama_index.core.node_parser import SentenceSplitter

    Settings.chunk_size = 512  # Instead of default 1024
    text_splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)
    Settings.text_splitter = text_splitter

    document_content_types = {"application/pdf"}

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

    provider = OllamaProvider()

    # TODO: Add Qdrant vector store

    index = VectorStoreIndex.from_documents(
        docs,
        # storage_context=storage_context,
        # use_async=True,
        embed_model=provider._get_embedding_model(),
        show_progress=True,
        transformations=[text_splitter],
    )

    query_engine = index.as_query_engine(llm=provider._get_chat_model(), streaming=True)
    response = query_engine.query("Give me the definition of Fine number")

    return StreamingResponse(generate(response.response_gen), media_type="text/event-stream",)

    # TODO: Process files
