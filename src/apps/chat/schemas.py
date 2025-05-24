from pydantic import BaseModel

from src.services.llms.enum import ProviderEnum

class QASchema(BaseModel):
    query: str
    id: str


class ProviderSchema(BaseModel):
    name: ProviderEnum