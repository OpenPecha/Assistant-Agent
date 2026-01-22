from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette import status

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
    
if __name__ == "__main__":
    uvicorn.run("pecha_api.app:api", host="127.0.0.1", port=8000, reload=True)