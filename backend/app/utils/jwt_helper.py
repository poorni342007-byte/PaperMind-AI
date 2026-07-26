import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings

def hash_password(password: str) -> str:
    """
    Generate a secure bcrypt hash of a plain text password.
    Bcrypt automatically generates a unique salt and includes it in the resulting hash.
    """
    # Encodes the password string to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt
    salt = bcrypt.gensalt()
    # Hash password
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Decode back to UTF-8 string to save in database
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain text password matches the stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JSON Web Token (JWT) containing the user details.
    """
    to_encode = data.copy()
    
    # Configure token expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    
    # Add expiration claim ('exp') to the token payload
    to_encode.update({"exp": expire})
    
    # Sign token using the global secret and algorithm
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    Returns the decoded claims dictionary if valid, or None if expired/corrupted.
    """
    try:
        decoded_payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_payload
    except jwt.ExpiredSignatureError:
        print("[JWT Decode Error] Token signature has expired.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[JWT Decode Error] Token is invalid: {e}")
        return None
