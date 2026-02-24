from pydantic import BaseModel

class SearchTextsDetailsResponse(BaseModel):
    id: str
    content: str
    type: str
    source: str