"""
API 请求数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class PreviewRequest(BaseModel):
    """预览 Prompt 请求"""
    user_input: str = Field(..., description="用户的创意描述")


class GenerateRequest(BaseModel):
    """生成图片请求"""
    user_input: str = Field(..., description="用户的创意描述")
    session_id: Optional[str] = Field(None, description="会话 ID（可选，不提供则创建新会话）")
    schema: Optional[dict] = Field(None, description="预览确认的 Schema（可选）")
    prompt: Optional[str] = Field(None, description="预览确认的 Prompt（可选）")


class FeedbackRequest(BaseModel):
    """反馈优化请求"""
    session_id: str = Field(..., description="会话 ID")
    version: int = Field(..., description="当前版本号")
    feedback: str = Field(..., description="用户反馈")
