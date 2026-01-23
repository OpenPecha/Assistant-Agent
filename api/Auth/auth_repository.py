from jose import jwt,JWTError
from api.config import get
from typing import Dict, Any
import requests

def validate_token(token: str) -> Dict[str, Any]:
    if get("DOMAIN_NAME") in jwt.get_unverified_claims(token=token)["iss"]:
        return verify_auth0_token(token)
    else:
        return decode_backend_token(token)

def decode_backend_token(token: str):
    return jwt.decode(token, get("JWT_SECRET_KEY"), algorithms=[get("JWT_ALGORITHM")], audience=get("JWT_AUD"))

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