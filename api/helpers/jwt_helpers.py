import os
import jwt
from flask import request
from functools import wraps
from helpers.api_helpers import create_response


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

def validate_jwt(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        jwt_token = request.headers.get('Authorization')
        if jwt_token:
            try:
                decoded_token = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=['HS256'])
                kwargs['decoded_token'] = decoded_token
                return func(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return create_response("Forbidden", 403, "JWT token expired.")
            except jwt.InvalidTokenError:
                return create_response("Forbidden", 403, "Invalid JWT token.")
        else:
            return create_response("Forbidden", 403, "JWT token missing.")
    return wrapper