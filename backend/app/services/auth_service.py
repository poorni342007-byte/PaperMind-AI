from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import users_collection
from app.schemas import UserSignupSchema, UserLoginSchema, UserResponseSchema, TokenSchema
from app.utils.jwt_helper import hash_password, verify_password, create_access_token, decode_access_token

# Define standard security scheme for extracting Bearer tokens from request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

class AuthService:
    """
    Business logic layer handling account creation, credential checks,
    and security session validations against MongoDB.
    """
    
    @staticmethod
    async def register_user(user_data: UserSignupSchema) -> dict:
        """
        Creates a new user record in the database.
        """
        # Ensure email uniqueness
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )
        
        # Hash password and create record dict
        hashed_pwd = hash_password(user_data.password)
        new_user = {
            "name": user_data.name,
            "email": user_data.email,
            "password_hash": hashed_pwd,
            "created_at": datetime.utcnow()
        }
        
        # Insert document in MongoDB
        result = await users_collection.insert_one(new_user)
        
        # Return serialized user details matching UserResponseSchema fields
        return {
            "id": str(result.inserted_id),
            "name": new_user["name"],
            "email": new_user["email"],
            "created_at": new_user["created_at"]
        }

    @staticmethod
    async def authenticate_user(credentials: UserLoginSchema) -> TokenSchema:
        """
        Verifies login credentials and returns a signed access token.
        """
        # Retrieve user record by email
        user = await users_collection.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password matches stored hash
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token payload (store string ID in sub claim)
        user_id_str = str(user["_id"])
        token_data = {"sub": user_id_str, "email": user["email"]}
        access_token = create_access_token(data=token_data)
        
        return TokenSchema(access_token=access_token, token_type="bearer")

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
        """
        FastAPI dependency handler extracting the current active session user.
        """
        unauthorized_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
        if not token:
            raise unauthorized_exception
            
        # Decode and inspect token payload
        payload = decode_access_token(token)
        if not payload:
            raise unauthorized_exception
            
        user_id_str: str = payload.get("sub")
        if not user_id_str:
            raise unauthorized_exception
            
        try:
            # Query user from MongoDB using converted ObjectId
            user = await users_collection.find_one({"_id": ObjectId(user_id_str)})
        except Exception:
            raise unauthorized_exception
            
        if not user:
            raise unauthorized_exception
            
        return user
