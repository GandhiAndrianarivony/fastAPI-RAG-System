from pydantic import BaseModel


class QASchema(BaseModel):
    query: str
    engine_id: str
