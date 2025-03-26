from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps  # Ensures function metadata is preserved
from flask import request, jsonify

# Load SECRET_KEY from config
SECRET_KEY = os.getenv("SECRET_KEY")

def hash_password(password):
    """Hash password before storing."""
    return generate_password_hash(password)

def verify_password(stored_password, provided_password):
    """Verify provided password against stored hash."""
    return check_password_hash(stored_password, provided_password)

def generate_token(user_email, user_type):
    """Generate JWT token for authenticated users."""
    payload = {
        "email": user_email,
        "user_type": user_type,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    """Verify and decode JWT token."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(f):
    """Decorator to check if the request has a valid JWT token."""
    @wraps(f)  # Preserve function metadata
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 403

        # Extract token from "Bearer <token>"
        token = token.split(" ")[1] if "Bearer " in token else token

        user_data = verify_token(token)
        if not user_data:
            return jsonify({"error": "Invalid or expired token!"}), 403

        return f(user_data, *args, **kwargs)  # Pass user data to the route
    
    return decorated_function
