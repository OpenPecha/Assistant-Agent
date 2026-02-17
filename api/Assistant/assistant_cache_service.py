from api.utils import Utils
from api.cache.cache_repository import get_cache_data, set_cache, delete_cache
from api.cache.cache_enums import CacheType
from api.Assistant.assistant_response_model import AssistantResponse, AssistantInfoResponse
from api import config


async def get_assistants_cache(
    skip: int = None,
    limit: int = None,
    cache_type: CacheType = None
) -> AssistantResponse:
    payload = [skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload=payload)
    cache_data: AssistantResponse = await get_cache_data(hash_key=hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = AssistantResponse(**cache_data)
    return cache_data


async def set_assistants_cache(
    skip: int = None,
    limit: int = None,
    data: AssistantResponse = None,
    cache_type: CacheType = None
):
    payload = [skip, limit, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload=payload)
    cache_time_out = config.get_int("CACHE_ASSISTANT_TIMEOUT")
    await set_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)


async def get_assistant_detail_cache(
    assistant_id: str = None,
    cache_type: CacheType = None
) -> AssistantInfoResponse:
    payload = [assistant_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload=payload)
    cache_data: AssistantInfoResponse = await get_cache_data(hash_key=hashed_key)
    if cache_data and isinstance(cache_data, dict):
        cache_data = AssistantInfoResponse(**cache_data)
    return cache_data


async def set_assistant_detail_cache(
    assistant_id: str = None,
    data: AssistantInfoResponse = None,
    cache_type: CacheType = None
):
    payload = [assistant_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload=payload)
    cache_time_out = config.get_int("CACHE_ASSISTANT_TIMEOUT")
    await set_cache(hash_key=hashed_key, value=data, cache_time_out=cache_time_out)


async def delete_assistant_detail_cache(
    assistant_id: str = None,
    cache_type: CacheType = None
):
    payload = [assistant_id, cache_type]
    hashed_key: str = Utils.generate_hash_key(payload=payload)
    await delete_cache(hash_key=hashed_key)
