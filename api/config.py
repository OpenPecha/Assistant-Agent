import os

DEFAULT = dict(
    APP_NAME="Assistant Agent",
    DATABASE_URL="postgresql://admin:assistantAdmin@localhost:5434/assistant",
    DOMAIN_NAME="yourdomain",
    CLIENT_ID="yourclientid",
)

def get(key: str) -> str:
    if key in os.environ:
        return os.environ[key]
    else:
        return str(DEFAULT[key])