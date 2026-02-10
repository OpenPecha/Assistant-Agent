from jose import jwt, JWTError
from api.config import get
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

optional_bearer = HTTPBearer(auto_error=False)

def get_optional_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer)
) -> Optional[str]:
    if credentials:
        return credentials.credentials
    
    if get("DEMO_MODE").lower() == "true":
        return None
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user_email(token: Optional[str] = None) -> str:
    if token and token.strip():
        try:
            payload = verify_auth0_token(token)
            return payload.get("email")
        except (ValueError, JWTError) as e:
            raise ValueError(f"Invalid token: {e}")
    
    if get("DEMO_MODE").lower() == "true":
        return get("DEMO_EMAIL")
    
    raise ValueError("Authentication token required")

def validate_token(token: str) -> Dict[str, Any]:
    return verify_auth0_token(token)

def get_auth0_public_key():
    jwks_url = f"https://{get('DOMAIN_NAME')}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    return {key["kid"]: key for key in jwks["keys"]}

def verify_auth0_token(token: str):
    try:
        jwks = get_auth0_public_key()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = jwks.get(unverified_header["kid"])

        if not rsa_key:
            raise ValueError("Unable to find appropriate key")

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=get("CLIENT_ID"),
            issuer=f"https://{get('DOMAIN_NAME')}/"
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {e}")