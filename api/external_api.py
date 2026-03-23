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


async def get_related_segment_ids(
    instance_id: str, span_start: int, span_end: int
) -> list[str]:
    adjusted_start = max(0, span_start - 10)
    adjusted_end = span_end + 10

    endpoint = (
        f"{EXTERNAL_PECHA_API_URL}/instances/{instance_id}"
        f"/segment-related?span_start={adjusted_start}&span_end={adjusted_end}&transform=false"
    )
    try:
        response = await client.get(endpoint, headers=ACCEPT_JSON_HEADER)
        response.raise_for_status()
        data = response.json()

        segment_ids = []
        for related in data if isinstance(data, list) else []:
            for segment in related.get("segments", []):
                sid = segment.get("segment_id")
                if sid:
                    segment_ids.append(sid)

        print(f"Related segment IDs for instance {instance_id}: {segment_ids}")
        return segment_ids

    except httpx.HTTPStatusError as e:
        handle_http_status_error(e)
    except httpx.RequestError as e:
        handle_request_error(e)
