from jose import JWTError
from jose.exceptions import JWTClaimsError
from api.Auth.auth_repository import validate_token
from jwt import ExpiredSignatureError
from fastapi import HTTPException, status
from api.error_constant import ErrorConstants
from api.db.pg_database import SessionLocal
import logging


def validate_and_extract_user_email(token: str) -> str:
    try:
        payload = validate_token(token)
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
        return email
    except ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except jose.ExpiredSignatureError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTClaimsError as exception:
        logging.debug(f"exception: {exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except ValueError as value_exception:
        logging.debug(f"exception: {value_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
    except JWTError as jwt_exception:
        logging.debug(f"exception: {jwt_exception}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)