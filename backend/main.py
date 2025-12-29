"""
PRISM 后端服务主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings
from app.api.v1 import api_router
from app.core.database import init_db

app = FastAPI(
    title="PRISM API",
    description="Prompt Refinement & Image Synthesis Manager",
    version="1.0.0",
    debug=settings.debug
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（图片）
storage_path = Path(settings.storage_path)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/images", StaticFiles(directory=str(storage_path)), name="images")

# 挂载 API 路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库（仅开发环境）"""
    if settings.app_env == "development":
        print("🗄️  初始化数据库...")
        init_db()
        print("✅ 数据库初始化完成")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "PRISM API is running"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


