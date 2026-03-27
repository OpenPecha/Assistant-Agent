from jose import JWTError
from jose.exceptions import JWTClaimsError, ExpiredSignatureError
from api.Auth.auth_repository import validate_token, get_user_info
from fastapi import HTTPException, status
from api.error_constant import ErrorConstants
import logging


def validate_and_extract_user_email(token: str) -> str:
    try:
        validate_token(token)
        user_info = get_user_info(token)
        email = user_info.get("email")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ErrorConstants.TOKEN_ERROR_MESSAGE)
        return email
    except ExpiredSignatureError as exception:
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