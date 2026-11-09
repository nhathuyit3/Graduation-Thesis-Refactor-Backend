# 5.1. Bảng `users`

``` sql
-- Kích hoạt extension để sinh UUID tự động
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Bảng Phòng ban (Departments)
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(150) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Vai trò (Roles)
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Quyền hạn (Permissions)
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,      -- Ví dụ: "USER_CREATE", "USER_READ"
    code VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- 4. Bảng liên kết Role - Permission (Phân quyền & Cho phép bật/tắt quyền theo Role)
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (role_id, permission_id)
);

-- 5. Bảng Người dùng (Users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(20),
    address TEXT,
    place_of_birth VARCHAR(150),
    date_of_birth DATE,
    id_card_number VARCHAR(20) UNIQUE, -- Số CCCD
    is_active BOOLEAN DEFAULT TRUE,
    department_id UUID REFERENCES departments(id) ON DELETE SET NULL,
    position_name VARCHAR(100),
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```