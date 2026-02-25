from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

class TokenCounter:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key
        )
    
    def count_tokens(self, text: Optional[str]) -> int:
        if not text:
            return 0
        return self.model.get_num_tokens(text)