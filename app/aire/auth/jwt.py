import os
from jose import jwt, jwe, JWTError
from jose.exceptions import JWEError
from typing import Annotated
from fastapi import Header, HTTPException, status
from ..models.auth import AireToken

TOKEN_SIGNING_KEY = os.getenv("TOKEN_SIGNING_KEY")
TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY")
allow_anonymous_users = os.getenv("ALLOW_ANONYMOUS_USERS") == "1"

def verify_token(authorization: Annotated[str | None, Header()] = None):
    if TOKEN_SIGNING_KEY == None or TOKEN_ENCRYPTION_KEY == None:
        raise RuntimeError("TOKEN_SIGNING_KEY and/or TOKEN_ENCRYPTION_KEY not configured.")
    
    unauth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token required",
        headers={"WWW-Authenticate": "Bearer"})
    
    if authorization == None:
        if not allow_anonymous_users:
            raise unauth_exception
        else:
            return AireToken()
    
    header = authorization.split(" ")
    if len(header) != 2:
        raise unauth_exception
    
    token = header[1]

    try:
        enc_key = bytes(TOKEN_ENCRYPTION_KEY, "ascii")
        dec_token = jwe.decrypt(token, enc_key)

        sig_key = bytes(TOKEN_SIGNING_KEY, "ascii")
        payload = jwt.decode(dec_token, sig_key, "HS256", {
            "verify_aud": False,
            "require_sub": True,
            "require_iat": True,
            "require_exp": True
        })

        print(f"Payload: {payload}")
        payload_scopes = payload.get("scope")

        if isinstance(payload_scopes, str):
            scopes = payload_scopes.split(" ")
            
        return AireToken(
            subject=payload.get("sub"),
            role=payload.get("role"),
            scopes=scopes,
            user_key=payload.get("user_enc_key"),
            connected_services=payload.get("connected_services"))
    
    except JWTError as e:
        print(f"Token decode error: {e}")
        raise unauth_exception
    except JWEError as e:
        print(f"Token decrypt error: {e}")
        raise unauth_exception
    except BaseException as e:
        print(f"Token verification exception: {e}")
        raise e
    