from jose import jwt, JWTError
from api.config import get
from typing import Dict, Any
import requests

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
            audience=f"https://{get('DOMAIN_NAME')}/api/v2/",
            issuer=f"https://{get('DOMAIN_NAME')}/"
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token validation failed: {e}")

def get_user_info(token: str) -> Dict[str, Any]:
    userinfo_url = f"https://{get('DOMAIN_NAME')}/userinfo"
    response = requests.get(
        userinfo_url,
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch user info: {response.status_code}")
    return response.json()