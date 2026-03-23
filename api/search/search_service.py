from api.external_api import (
    call_external_pecha_api_instances,
    call_external_pecha_api_instances_content,
)
from api.search.search_response_model import SearchTextsDetailsResponse


async def get_search_texts_details(text_id: str) -> list[SearchTextsDetailsResponse]:    
    instances = await call_external_pecha_api_instances(text_id)
    if instances:
        for instance in instances:
            instance_id = instance.get("id")
            if instance_id:
                content = await call_external_pecha_api_instances_content(instance_id)
                instance["content"] = content
    
    return [SearchTextsDetailsResponse(**instance) for instance in instances]