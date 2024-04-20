import os
import jwt
from flask import request
from functools import wraps
from api.helpers.api_helpers import create_response
from datetime import datetime, timedelta, timezone

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

def generate_jwt(user_id):
    """
    Generate a JWT token with user ID as claim.

    Parameters:
    - user_id (str): The ID of the current authenticated user.

    Returns:
    - str: The generated JWT token.
    """
    token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
    token_payload = {'user_id': user_id, 'exp': token_expiry}
    jwt_token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm='HS256')
    return jwt_token.decode('utf-8') 