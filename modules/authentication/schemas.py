from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime

# Department Schemas
class DepartmentCreate(BaseModel):
  name: str
  code: str
  description: Optional[str] = None

class DepartmentResponse(DepartmentCreate):
  id: UUID
  created_at: datetime

# Role & Permission Schemas
class RoleCreate(BaseModel):
  name: str
  description: Optional[str] = None

class RolePermissionToggle(BaseModel):
  role_id: UUID
  permission_id: UUID
  is_action: bool

# User Schemas
class UserRegister(BaseModel):
  username: str
  password: str
  email: EmailStr
  full_name: str
  phone_number: Optional[str] = None
  address: Optional[str] = None  # Check kỹ chữ 'address' ở đây
  place_of_birth: Optional[str] = None
  date_of_birth: Optional[date] = None
  id_card_number: Optional[str] = None
  department_id: Optional[UUID] = None
  position_name: Optional[str] = None
  role_id: Optional[UUID] = None

class UserUpdate(BaseModel):
  full_name: Optional[str] = None
  phone_number: Optional[str] = None
  address: Optional[str] = None
  place_of_birthday: Optional[str] = None
  date_of_birth: Optional[date] = None
  id_card_number: Optional[str] = None
  department_id: Optional[UUID] = None
  position_name: Optional[str] = None
  role_id: Optional[UUID] = None
  is_active: Optional[bool] = None

class UserResponse(BaseModel):
  id: UUID
  username: str
  email: EmailStr
  full_name: str
  phone_number: Optional[str]
  address: Optional[str]
  place_of_birth: Optional[str]
  date_of_birth: Optional[date]
  id_card_number: Optional[str]
  is_active: bool
  department_id: Optional[UUID]
  position_name: Optional[str]
  role_id: Optional[UUID]
  created_at: datetime

class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"