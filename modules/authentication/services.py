from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID, uuid4
from app.core.security import hash_password, verify_password
from modules.authentication.schemas import UserRegister, UserUpdate, DepartmentCreate, RoleCreate

class AuthService:
  # --- USER CRUD & AUTH ---
  @staticmethod
  async def register_user(db: AsyncSession, user_data: UserRegister):
      # Dump đầy đủ key từ schema (bao gồm cả các field None)
      params = user_data.model_dump()
      
      # Loại bỏ plain password và thay bằng hashed_password
      raw_password = params.pop("password", None)
      params["hashed_password"] = hash_password(raw_password)
      
      # Thêm UUID mới
      params["id"] = uuid4()

      query = text("""
          INSERT INTO users (
              id, username, hashed_password, email, full_name, phone_number,
              address, place_of_birth, date_of_birth, id_card_number,
              department_id, position_name, role_id
          ) VALUES (
              :id, :username, :hashed_password, :email, :full_name, :phone_number,
              :address, :place_of_birth, :date_of_birth, :id_card_number,
              :department_id, :position_name, :role_id
          ) RETURNING *;
      """)

      result = await db.execute(query, params)
      await db.commit()
      return result.mappings().first()

  @staticmethod
  async def authenticate_user(db: AsyncSession, username: str, password: str):
      query = text("SELECT * FROM users WHERE username = :username AND is_active = TRUE;")
      result = await db.execute(query, {"username": username})
      user = result.mappings().first()
      if not user or not verify_password(password, user["hashed_password"]):
          return None
      return user

  @staticmethod
  async def get_user_by_id(db: AsyncSession, user_id: UUID):
      query = text("SELECT * FROM users WHERE id = :user_id;")
      result = await db.execute(query, {"user_id": user_id})
      return result.mappings().first()

  @staticmethod
  async def get_user_by_id(db: AsyncSession, user_id: UUID):
      query = text("SELECT * FROM users WHERE id = :user_id;")
      result = await db.execute(query, {"user_id": user_id})
      return result.mappings().first()

  @staticmethod
  async def get_all_users(db: AsyncSession, limit: int = 100, offset: int = 0):
      query = text("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit OFFSET :offset;")
      result = await db.execute(query, {"limit": limit, "offset": offset})
      return result.mappings().all()

  @staticmethod
  async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate):
      update_data = user_data.model_dump(exclude_unset=True)
      if not update_data:
          return await AuthService.get_user_by_id(db, user_id)

      set_clause = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
      query = text(f"UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = :user_id RETURNING *;")
      update_data["user_id"] = user_id

      result = await db.execute(query, update_data)
      await db.commit()
      return result.mappings().first()
  
  @staticmethod
  async def delete_user(db: AsyncSession, user_id: UUID):
      query = text("DELETE FROM users WHERE id = :user_id RETURNING id;")
      result = await db.execute(query, {"user_id": user_id})
      await db.commit()
      return result.mappings().first()
  # --- DEPARTMENT SERVICES ---
  @staticmethod
  async def create_department(db: AsyncSession, dept: DepartmentCreate):
      query = text("""
          INSERT INTO departments (id, name, code, description)
          VALUES (:id, :name, :code, :description)
          RETURNING *;
      """)
      result = await db.execute(query, {**dept.model_dump(), "id": uuid4()})
      await db.commit()
      return result.mappings().first()
  # --- ROLE & PERMISSION SERVICES ---
  @staticmethod
  async def create_role(db: AsyncSession, role: RoleCreate):
      query = text("INSERT INTO roles (id, name, description) VALUES (:id, :name, :description) RETURNING *;")
      result = await db.execute(query, {**role.model_dump(), "id": uuid4()})
      await db.commit()
      return result.mappings().first()

  @staticmethod
  async def toggle_role_permission(db: AsyncSession, role_id: UUID, permission_id: UUID, is_active: bool):
      query = text("""
          INSERT INTO role_permissions (role_id, permission_id, is_active)
          VALUES (:role_id, :permission_id, :is_active)
          ON CONFLICT (role_id, permission_id) 
          DO UPDATE SET is_active = EXCLUDED.is_active;
      """)
      await db.execute(query, {"role_id": role_id, "permission_id": permission_id, "is_active": is_active})
      await db.commit()
      return {"message": "Cập nhật trạng thái quyền thành công"}