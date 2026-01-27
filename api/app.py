from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status
from api.Assistant import assistant_view
from api.ai import ai_view
import uvicorn

api = FastAPI(
    title="Assistant Agent API",
    description="This is the API documentation for Assistant Agent application",
    root_path="/api/v1",
    redoc_url="/docs"
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "Assistant Agent API is running"}
    
api.include_router(assistant_view.assistant_router)
api.include_router(ai_view.ai_router)

if __name__ == "__main__":
    uvicorn.run("api.app:api", host="127.0.0.1", port=8000, reload=True)