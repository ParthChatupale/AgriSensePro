"""
Authentication router and JWT helpers.

Exposes the following endpoints under `/api/auth`:
- POST /signup  -> register a new user
- POST /login   -> returns JWT access token (valid for 1 hour) and user info
- GET  /me      -> returns current user details (requires Authorization header)

Uses python-jose for token creation and passlib for password hashing.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv

from . import schemas, crud
from .database import get_db
from .services.geocode import reverse_geocode

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-random-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

router = APIRouter()

# For docs and dependencies. tokenUrl points to our login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT token with an expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to return the current user from the provided JWT token.

    Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    Expects JSON: { email, password, name, phone (optional), userType, crop (optional), location (optional) }
    Returns created user (without password).
    """
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = user_in.model_dump()
    lat = user_data.pop("latitude", None)
    lon = user_data.pop("longitude", None)

    if lat is not None and lon is not None:
        geo = await reverse_geocode(lat, lon)
        for key in ("state", "district", "village"):
            if geo.get(key):
                user_data[key] = geo[key]
        # Persist raw coordinates in location field if not provided
        if not user_data.get("location"):
            user_data["location"] = f"{lat},{lon}"

    user = crud.create_user(db, schemas.UserCreate(**user_data))
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "userType": user.user_type,
        "crop": user.crop,
        "location": user.location,
        "state": user.state,
        "district": user.district,
        "village": user.village,
        "is_active": user.is_active,
    }


@router.post("/login", response_model=dict)
async def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token and user info.

    Expects JSON: { email, password }
    Returns: { access_token, token_type, user }
    """
    user = crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "userType": user.user_type,
        "crop": user.crop,
        "location": user.location,
        "state": user.state,
        "district": user.district,
        "village": user.village,
        "is_active": user.is_active,
    }}


@router.get("/me", response_model=schemas.UserOut)
async def me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Return current logged-in user details.

    Requires header: Authorization: Bearer <token>
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "userType": current_user.user_type,
        "crop": current_user.crop,
        "location": current_user.location,
        "state": current_user.state,
        "district": current_user.district,
        "village": current_user.village,
        "is_active": current_user.is_active,
    }


@router.patch("/profile", response_model=schemas.UserOut)
async def update_profile(
    user_update: schemas.UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile.

    Requires header: Authorization: Bearer <token>
    """
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "name": updated_user.name,
        "phone": updated_user.phone,
        "userType": updated_user.user_type,
        "crop": updated_user.crop,
        "location": updated_user.location,
        "state": updated_user.state,
        "district": updated_user.district,
        "village": updated_user.village,
        "is_active": updated_user.is_active,
    }
