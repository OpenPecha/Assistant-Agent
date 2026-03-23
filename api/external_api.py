import httpx
from api.http_message_utils import handle_http_status_error, handle_request_error
from api.config import get
from api.constant import Constant

client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

ACCEPT_JSON_HEADER = {"Accept": "application/json"}
EXTERNAL_PECHA_API_URL = get("EXTERNAL_PECHA_API_URL")


async def call_external_pecha_api_instances(text_id: str) -> list[dict]:
    endpoint = f"{EXTERNAL_PECHA_API_URL}/texts/{text_id}/instances?instance_type={Constant.INSTANCE_TYPE}"
    try:
        response = await client.get(endpoint, headers=ACCEPT_JSON_HEADER)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)


async def call_external_pecha_api_instances_content(instance_id: str) -> str:
    endpoint = f"{EXTERNAL_PECHA_API_URL}/instances/{instance_id}?annotation=false&content=true"
    try:
        response = await client.get(endpoint, headers=ACCEPT_JSON_HEADER)
        response.raise_for_status()
        data = response.json()
        return data.get("content", "")
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)

async def get_segment_content(segment_id:str) -> str:
    endpoint = f"{EXTERNAL_PECHA_API_URL}/segments/{segment_id}/content"
    try:
        response = await client.get(endpoint, headers=ACCEPT_JSON_HEADER)
        response.raise_for_status()
        data = response.json()
        return data.get("content", "")
    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)

async def get_related_segment_ids(
    instance_id: str, span_start: int, span_end: int
) -> list[str]:
    endpoint = f"{EXTERNAL_PECHA_API_URL}/instances/{instance_id}/segment-related?span_start={span_start}&span_end={span_end}&transform=false"
    try:
        response = await client.get(endpoint, headers=ACCEPT_JSON_HEADER, timeout=60.0)
        response.raise_for_status()
        data = response.json()
        segment_ids = []
        for related in data if isinstance(data, list) else []:
            for segment in related.get("segments", []):
                sid = segment.get("segment_id")
                if sid:
                    segment_ids.append(sid)
        return segment_ids

    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        print(f"RequestError type: {type(e).__name__}, details: {repr(e)}")
        handle_request_error(e)
