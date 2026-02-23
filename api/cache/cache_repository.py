import json
from redis.asyncio import Redis
from api.config import get
from typing import Any, Optional
from pydantic.json import pydantic_encoder
import logging



_client: Optional[Redis] = None

def get_client() -> Redis:
    global _client
    if _client is None:
        redis_url = get("CACHE_CONNECTION_STRING")
        _client = Redis.from_url(redis_url)
    return _client

def _build_key(key: str) -> str:
    prefix = get("CACHE_PREFIX")
    return f"{prefix}{key}"

async def set_cache(hash_key: str, value: Any, cache_time_out: int) -> bool:
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)
        return bool(await client.setex(full_key, cache_time_out, value))
    except Exception:
        logging.error("An error occurred in set_cache", exc_info=True)
        return False

async def get_cache_data(hash_key: str) -> Optional[Any]:
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        value = await client.get(full_key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from cache", exc_info=True)
            return value
    except Exception:
        logging.error("An error occurred in get_cache_data", exc_info=True)
        return None

async def delete_cache(hash_key: str) -> bool:
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        return bool(await client.delete(full_key))
    except Exception:
        logging.error("An error occurred in delete_cache", exc_info=True)
        return False

async def update_cache(hash_key: str, value: Any, cache_time_out: int) -> bool:
    try:
        client = get_client()
        full_key = _build_key(hash_key)
        
        if not await client.exists(full_key):
            logging.warning(f"Cache key {hash_key} does not exist, cannot update")
            return False
        
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value, default=pydantic_encoder)

        return bool(await client.setex(full_key, cache_time_out, value))
    except Exception:
        logging.error("An error occurred in update_cache", exc_info=True)
        return False