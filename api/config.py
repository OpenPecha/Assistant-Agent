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
    AWS_ACCESS_KEY="your-aws-access-key",
    AWS_SECRET_KEY="your-aws-secret-key",
    AWS_REGION="your-aws-region",
    AWS_BUCKET_OWNER="your-aws-bucket-owner",
    AWS_BUCKET_NAME="your-aws-bucket-name",
    ALLOWED_EXTENSIONS={'.pdf', '.docx', '.txt', 'doc'},
    MAX_FILE_SIZE_MB=10,
    CACHE_CONNECTION_STRING="your-redis-connection-string",
    CACHE_PREFIX="agent_microservice:",
    CACHE_ASSISTANT_TIMEOUT=3600,
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    return str(DEFAULT.get(key, ""))

def get_int(key: str) -> int:
    try:
        return int(get(key))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Could not convert the value for key '{key}' to int: {e}")