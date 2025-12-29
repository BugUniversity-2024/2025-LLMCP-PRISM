"""
数据库连接和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SQLSession
from app.config import settings
from app.models import Base


# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> SQLSession:
    """
    数据库会话依赖注入

    用法：
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库（创建所有表）

    注意：仅在开发环境使用
    生产环境应使用 Alembic 迁移
    """
    Base.metadata.create_all(bind=engine)
