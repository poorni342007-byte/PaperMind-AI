from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from bson import ObjectId
from models import UserSignup, UserLogin, UserResponse, Token
from database import users_collection
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup):
    # Check if email is already registered
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    # Hash password and create user object
    hashed_pwd = hash_password(user_data.password)
    new_user = {
        "name": user_data.name,
        "email": user_data.email,
        "password_hash": hashed_pwd,
        "created_at": datetime.utcnow()
    }
    
    # Save user into DB
    result = await users_collection.insert_one(new_user)
    
    # Prepare response
    return UserResponse(
        id=str(result.inserted_id),
        name=new_user["name"],
        email=new_user["email"],
        created_at=new_user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    # Find user by email
    user = await users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password hash
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    user_id_str = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id_str, "email": user["email"]})
    
    return Token(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return UserResponse(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )
