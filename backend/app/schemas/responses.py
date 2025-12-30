"""
API 响应数据模型
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class PromptSchema(BaseModel):
    """Prompt Schema 数据结构"""
    subject: List[str] = Field(default_factory=list)
    appearance: List[str] = Field(default_factory=list)
    style: List[str] = Field(default_factory=list)
    composition: List[str] = Field(default_factory=list)
    lighting: List[str] = Field(default_factory=list)
    background: List[str] = Field(default_factory=list)
    quality: List[str] = Field(default_factory=list)
    negative: List[str] = Field(default_factory=list)
    weights: Dict[str, float] = Field(default_factory=dict)


class PromptDiff(BaseModel):
    """Prompt Diff 数据结构"""
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning: Optional[str] = None


class GenerateResponse(BaseModel):
    """生成图片响应"""
    session_id: str
    version: int
    schema: Dict[str, Any]
    prompt: str
    image_url: str
    created_at: str


class FeedbackResponse(BaseModel):
    """反馈优化响应"""
    session_id: str
    version: int
    parent_version: int
    diff: Dict[str, Any]
    schema: Dict[str, Any]
    prompt: str
    image_url: str
    created_at: str


class PreviewResponse(BaseModel):
    """预览 Prompt 响应"""
    schema: Dict[str, Any]
    prompt: str
