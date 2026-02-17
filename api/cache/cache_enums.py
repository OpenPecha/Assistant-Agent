from enum import Enum


class CacheType(str, Enum):
    ASSISTANTS = "assistants"
    ASSISTANT_DETAIL = "assistant_detail"
