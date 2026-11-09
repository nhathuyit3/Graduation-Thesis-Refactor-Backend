from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings
from database.session import get_db
from modules.authentication.services import AuthService

# Khai báo OAuth2 Scheme chỉ định endpoint lấy token (/auth/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Dependency xác thực token và lấy thông tin user hiện tại từ DB.
    Dùng đặt vào các route cần bảo mật.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token xác thực không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # Truy vấn lấy user từ DB
    user = await AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Tài khoản người dùng đã bị khóa")
        
    return user