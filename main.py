from fastapi import FastAPI
from modules.authentication.routers import router as auth_router

app = FastAPI(
    title="Core Backend API Framework",
    description="Hệ thống API backend với FastAPI, PostgreSQL (Raw SQL Async Engine), Phân quyền & User Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Nơi include router các module trong tương lai
app.include_router(auth_router)

@app.get("/", tags=["Healthcheck"])
async def root():
    return {"message": "Server đang hoạt động bình thường"}