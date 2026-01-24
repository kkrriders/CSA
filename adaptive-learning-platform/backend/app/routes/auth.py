from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.database import get_database
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user_id
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db=Depends(get_database)):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user document
    user_doc = {
        "email": user_data.email,
        "username": user_data.email,  # Use email as username
        "name": user_data.name,
        "password_hash": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "last_login": None
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)

    # Generate token
    access_token = create_access_token(data={"sub": str(result.inserted_id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            _id=str(result.inserted_id),
            email=user_data.email,
            name=user_data.name,
            created_at=user_doc["created_at"]
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db=Depends(get_database)):
    """Login user"""
    user = await db.users.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )

    # Generate token
    access_token = create_access_token(data={"sub": str(user["_id"])})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            _id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            created_at=user["created_at"],
            last_login=datetime.utcnow()
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db=Depends(get_database)
):
    """Get current user profile"""
    from bson import ObjectId

    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        _id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"],
        last_login=user.get("last_login")
    )
