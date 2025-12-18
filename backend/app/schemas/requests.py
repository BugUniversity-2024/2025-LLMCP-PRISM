"""
API 请求数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class GenerateRequest(BaseModel):
    """生成图片请求"""
    user_input: str = Field(..., description="用户的创意描述")
    session_id: Optional[str] = Field(None, description="会话 ID（可选，不提供则创建新会话）")


class FeedbackRequest(BaseModel):
    """反馈优化请求"""
    session_id: str = Field(..., description="会话 ID")
    version: int = Field(..., description="当前版本号")
    feedback: str = Field(..., description="用户反馈")
