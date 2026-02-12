from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


class CurrentUser(BaseModel):
    username: str
    role: str
    site: str | None


DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get('sub')
        role = payload.get('role')
        site = payload.get('site')
        if username is None or role is None:
            raise credentials_exception
        return CurrentUser(username=username, role=role, site=site)
    except JWTError as exc:
        raise credentials_exception from exc


UserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_admin(user: UserDep) -> CurrentUser:
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail='Admin role required')
    return user
