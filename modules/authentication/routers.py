from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from database.session import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token
from modules.authentication.schemas import (
    UserRegister, UserUpdate, UserResponse, TokenResponse,
    DepartmentCreate, DepartmentResponse, RoleCreate, RolePermissionToggle
)
from modules.authentication.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & User Management"])

# --- PUBLIC ROUTES (Không cần xác thực OAuth2) ---

@router.post("/register-public", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_public(
    user_in: UserRegister, 
    db: AsyncSession = Depends(get_db)
):
    """
    Tạo tài khoản công khai (Không yêu cầu đăng nhập/OAuth2 token).
    Dùng để tự đăng ký người dùng hoặc khởi tạo tài khoản Admin ban đầu.
    """
    return await AuthService.register_user(db, user_in)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Tài khoản hoặc mật khẩu không chính xác")
    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}


# --- PROTECTED ROUTES (Yêu cầu Token OAuth2 Bearer) ---

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_internal(
    user_in: UserRegister, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Tạo tài khoản nội bộ (Yêu cầu Admin/User đã đăng nhập gọi)"""
    return await AuthService.register_user(db, user_in)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập"""
    return current_user

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = 100, 
    offset: int = 0, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return await AuthService.get_all_users(db, limit, offset)

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = await AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID, 
    user_in: UserUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    updated_user = await AuthService.update_user(db, user_id, user_in)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Cập nhật thất bại hoặc người dùng không tồn tại")
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    deleted = await AuthService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng để xóa")
    return {"message": f"Đã xóa thành công user {user_id}"}

# --- DEPARTMENTS & ROLES (Tùy chọn bảo mật) ---

@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(dept: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService.create_department(db, dept)

@router.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await AuthService.create_role(db, role)

@router.post("/roles/toggle-permission")
async def toggle_permission(item: RolePermissionToggle, db: AsyncSession = Depends(get_db)):
    return await AuthService.toggle_role_permission(db, item.role_id, item.permission_id, item.is_active)