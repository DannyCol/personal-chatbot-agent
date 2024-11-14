"""
Implements JWT authentication using Firebase Authentication.
To be used with a token received from a frontend using SignInWithGoogle.
"""

import os
from functools import wraps
from typing import Callable
from fastapi import Response, Request
import firebase_admin
from firebase_admin.auth import verify_id_token

firebase_admin.initialize_app(
    credential=firebase_admin.credentials.ApplicationDefault(),
    options={"projectId": os.environ["GCP_CHAT_PROJECT_ID"]},
)

def require_jwt_authentication(func: Callable[..., int]) -> Callable[..., int]:
    """Decorator for JWT authentication"""

    @wraps(func)
    async def decorated_function(request: Request, *args, **kwargs):
        """Authentication logic"""
        header = request.headers.get("Authorization", None)
        if header:
            token = header.split(" ")[1]
            try:
                decoded_token = verify_id_token(token)
            except Exception as e:
                return Response(
                    status_code=403, content=f"Error with authentication: {e}"
                )
        else:
            # Unauthorized JWT
            return Response(status_code=401)

        request.uid = decoded_token["uid"]
        return await func(request, *args, **kwargs)

    return decorated_function
