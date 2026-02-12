from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.security import create_access_token, verify_password
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    """Authenticate a user and return an access token."""

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.username == payload.username))
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail='Invalid username or password')
        token = create_access_token(user.username, user.role.value, user.site.value if user.site else None)
        return TokenResponse(access_token=token, role=user.role.value, site=user.site.value if user.site else None)
    finally:
        db.close()
