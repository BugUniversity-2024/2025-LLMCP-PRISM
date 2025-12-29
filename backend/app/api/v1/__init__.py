"""
API v1 路由注册
"""
from fastapi import APIRouter
from .generate import router as generate_router
from .feedback import router as feedback_router
from .sessions import router as sessions_router

api_router = APIRouter()

# 注册子路由
api_router.include_router(generate_router, tags=["generate"])
api_router.include_router(feedback_router, tags=["feedback"])
api_router.include_router(sessions_router, tags=["sessions"])

