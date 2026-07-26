from fastapi import APIRouter, Depends, status
from app.schemas import UserSignupSchema, UserLoginSchema, UserResponseSchema, TokenSchema
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignupSchema):
    """
    Register a new user account.
    """
    user_record = await AuthService.register_user(user_data)
    return user_record

@router.post("/login", response_model=TokenSchema)
async def login(credentials: UserLoginSchema):
    """
    Authenticate user and return a JWT access token.
    """
    token_response = await AuthService.authenticate_user(credentials)
    return token_response

@router.get("/me", response_model=UserResponseSchema)
async def get_me(current_user: dict = Depends(AuthService.get_current_user)):
    """
    Get profile details of the currently authenticated user session.
    Requires header "Authorization: Bearer <JWT_TOKEN>"
    """
    # Serialize ObjectId into a string representation for standard JSON output
    return UserResponseSchema(
        id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user["created_at"]
    )
