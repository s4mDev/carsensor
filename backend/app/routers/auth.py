from fastapi import APIRouter, HTTPException, status

from app.auth import create_access_token, verify_password, hash_password
from app.config import settings
from app.schemas import LoginRequest, TokenResponse


router = APIRouter(prefix="/auth", tags=["auth"])

# Хэшируем пароль администратора один раз при загрузке модуля,
# чтобы не хранить и не сравнивать его в открытом виде во время работы
_admin_password_hash = hash_password(settings.admin_password)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    if body.username != settings.admin_username or not verify_password(body.password, _admin_password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
        )
    token = create_access_token({"sub": body.username})
    return TokenResponse(access_token=token)
