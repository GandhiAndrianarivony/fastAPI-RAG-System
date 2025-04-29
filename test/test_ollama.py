from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from src.services.llms.providers import OllamaProvider

import asyncio


text_splitter = SentenceSplitter(chunk_size=2000, chunk_overlap=500)
Settings.text_splitter = text_splitter


temp_dir = "./test/data"

docs = SimpleDirectoryReader(temp_dir).load_data()

provider = OllamaProvider(host="http://localhost:11434")

# TODO: Add Qdrant vector store

index = VectorStoreIndex.from_documents(
    docs,
    # storage_context=storage_context,
    # use_async=True,
    embed_model=provider._get_embedding_model(),
    show_progress=True,
    transformations=[text_splitter],
)


query_engine = index.as_query_engine(
    llm=provider._get_chat_model(),
    streaming=True
)
response = query_engine.query("Give me the definition of Fine number")

response.print_response_stream()