from fastapi import HTTPException, status

UNAUTH_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authorization required",
    headers={"WWW-Authenticate": "Bearer"}
)
FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Access denied"
)
BAD_REQUEST_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Bad request"
)
UNSUPPORTED_MEDIA_EXCEPTION = HTTPException(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    detail="Unsupported media type"
)
