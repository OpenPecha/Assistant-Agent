import os

DEFAULT = dict(
    APP_NAME="Assistant Agent",
    DATABASE_URL="postgresql://admin:assistantAdmin@localhost:5434/assistant",
    DOMAIN_NAME="your-domain-name",
    CLIENT_ID="your-client-id",
    ANTHROPIC_API_KEY="your-anthropic-api-key",
    OPENAI_API_KEY="your-openai-api-key",
    GEMINI_API_KEY="your-gemini-api-key",
    DHARMAMITRA_TOKEN="your-dharmamitra-token",
    DHARMAMITRA_PASSWORD="your-dharmamitra-password",
    LANGSMITH_API_KEY="your-langsmith-api-key",
    LANGSMITH_ENDPOINT="your-langsmith-endpoint",
    LANGSMITH_PROJECT="your-langsmith-project",
    LANGSMITH_TRACING="true",
    MAX_BATCH_SIZE="50",
    MAX_QUERY_LENGTH="10000",
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    return str(DEFAULT.get(key, ""))