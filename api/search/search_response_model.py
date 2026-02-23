from pydantic import BaseModel
from typing import Optional

class SearchTextsDetailsResponse(BaseModel):
    id: str
    content: str
    type: str
    source: str
    incipit_title: Optional[dict[str, str]] = None
