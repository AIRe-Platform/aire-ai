import os
from jose import jwt, jwe, JWTError
from jose.exceptions import JWEError
from typing import Annotated
from fastapi import Header
from ..models.auth import AireAuth, AireScope

TOKEN_SIGNING_KEY = os.getenv("TOKEN_SIGNING_KEY")
TOKEN_ENCRYPTION_KEY = os.getenv("TOKEN_ENCRYPTION_KEY")

allow_anonymous_users = os.getenv("ALLOW_ANONYMOUS_USERS") == "1"
AnonymousScopes = [AireScope.ChatCompletion, AireScope.ChatSummary]

def verify_token(authorization: Annotated[str | None, Header()] = None):
    if TOKEN_SIGNING_KEY == None or TOKEN_ENCRYPTION_KEY == None:
        raise RuntimeError("TOKEN_SIGNING_KEY and/or TOKEN_ENCRYPTION_KEY not configured.")
    
    if authorization == None:
        if not allow_anonymous_users:
            return None
        else:
            return AireAuth(scopes=AnonymousScopes)
    
    header = authorization.split(" ")
    if len(header) != 2:
        return None
    
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
            
        return AireAuth(
            subject=payload.get("sub"),
            role=payload.get("role"),
            scopes=scopes,
            user_key=payload.get("user_enc_key"),
            connected_services=payload.get("connected_services"))
    
    except JWTError as e:
        print(f"Token decode error: {e}")
        return None
    except JWEError as e:
        print(f"Token decrypt error: {e}")
        return None
    except BaseException as e:
        print(f"Token verification exception: {e}")
        raise e
    