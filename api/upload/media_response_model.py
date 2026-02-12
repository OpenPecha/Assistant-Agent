from pydantic import BaseModel
from api.constant import Constant

class MediaUploadResponse(BaseModel):
    file_url: str
    key: str
    path: str
    message: str = Constant.IMAGE_UPLOAD_SUCCESS