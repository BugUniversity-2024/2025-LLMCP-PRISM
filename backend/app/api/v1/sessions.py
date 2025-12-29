"""
会话和版本管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SQLSession
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.services.session_manager import SessionManager
from app.services.feedback_engine import FeedbackEngine
from app.services.image_adapter import ImageAdapter

router = APIRouter()


# 响应模型
class SessionListItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    version_count: int
    created_at: str
    updated_at: str

class SessionsListResponse(BaseModel):
    sessions: List[SessionListItem]
    total: int

class UpdateSessionRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class VersionDetail(BaseModel):
    id: str
    session_id: str
    version_number: int
    parent_version_id: Optional[str]
    user_input: Optional[str]
    user_feedback: Optional[str]
    schema: Dict[str, Any]
    prompt: str
    diff: Optional[Dict[str, Any]]
    image_url: str
    created_at: str


class VersionsResponse(BaseModel):
    session_id: str
    versions: List[VersionDetail]


class VersionTreeResponse(BaseModel):
    session_id: str
    tree: Dict[str, Any]


class RollbackRequest(BaseModel):
    target_version: int
    new_feedback: Optional[str] = None


@router.get("/sessions/{session_id}/versions", response_model=VersionsResponse)
async def get_versions(
    session_id: str,
    db: SQLSession = Depends(get_db)
):
    """获取会话的所有版本"""
    manager = SessionManager(db)

    # 检查会话是否存在
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 获取所有版本
    versions = manager.get_all_versions(session_id)

    return VersionsResponse(
        session_id=session_id,
        versions=[
            VersionDetail(
                id=str(v.id),
                session_id=str(v.session_id),
                version_number=v.version_number,
                parent_version_id=str(v.parent_version_id) if v.parent_version_id else None,
                user_input=v.user_input,
                user_feedback=v.user_feedback,
                schema=v.schema,
                prompt=v.prompt,
                diff=v.diff,
                image_url=v.image_url,
                created_at=v.created_at.isoformat()
            )
            for v in versions
        ]
    )


@router.get("/sessions/{session_id}/tree", response_model=VersionTreeResponse)
async def get_version_tree(
    session_id: str,
    db: SQLSession = Depends(get_db)
):
    """获取版本树结构"""
    manager = SessionManager(db)

    # 检查会话是否存在
    session = manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 构建版本树
    tree = manager.get_version_tree(session_id)

    return VersionTreeResponse(
        session_id=session_id,
        tree=tree
    )


@router.post("/sessions/{session_id}/rollback")
async def rollback(
    session_id: str,
    request: RollbackRequest,
    db: SQLSession = Depends(get_db)
):
    """
    回滚到指定版本

    如果提供 new_feedback，则在目标版本基础上应用新的修改
    """
    try:
        manager = SessionManager(db)
        feedback_engine = FeedbackEngine(use_real_api=False)
        image_adapter = ImageAdapter(use_real_api=False)

        # 获取目标版本
        target_version = manager.get_version(
            session_id=session_id,
            version_number=request.target_version
        )
        if not target_version:
            raise HTTPException(status_code=404, detail="目标版本不存在")

        # 如果有新的反馈，应用修改
        if request.new_feedback:
            result = feedback_engine.analyze_feedback(
                feedback=request.new_feedback,
                current_schema=target_version.schema
            )
            new_schema = result["new_schema"]
            prompt = result["prompt"]
            diff = result["diff"]
        else:
            # 直接使用目标版本的 Schema
            new_schema = target_version.schema
            prompt = target_version.prompt
            diff = None

        # 生成新图片
        # 使用较大的版本号避免冲突
        max_version = manager.get_all_versions(session_id)[-1].version_number if manager.get_all_versions(session_id) else 0
        new_version_number = max_version + 1

        image_result = await image_adapter.generate_image(
            prompt=prompt,
            session_id=session_id,
            version=new_version_number,
            reference_image_path=target_version.image_path if request.new_feedback else None
        )

        # 创建新版本
        new_version = manager.create_version(
            session_id=session_id,
            schema=new_schema,
            prompt=prompt,
            image_url=image_result["image_url"],
            image_path=image_result["image_path"],
            user_feedback=request.new_feedback,
            diff=diff,
            parent_version_id=target_version.id
        )

        return {
            "session_id": session_id,
            "version": new_version.version_number,
            "parent_version": request.target_version,
            "diff": diff,
            "schema": new_schema,
            "prompt": prompt,
            "image_url": image_result["image_url"],
            "created_at": new_version.created_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回滚失败: {str(e)}")


@router.get("/sessions", response_model=SessionsListResponse)
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: SQLSession = Depends(get_db)
):
    """获取所有项目列表"""
    manager = SessionManager(db)

    sessions = manager.get_all_sessions(skip=skip, limit=limit)
    total = manager.count_sessions()

    return SessionsListResponse(
        sessions=[
            SessionListItem(
                id=s.id,
                name=s.name or f"项目 {s.id[:8]}",
                description=s.description,
                thumbnail_url=s.versions[-1].image_url if s.versions else None,
                version_count=len(s.versions),
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat()
            )
            for s in sessions
        ],
        total=total
    )


@router.patch("/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    db: SQLSession = Depends(get_db)
):
    """更新项目元数据"""
    manager = SessionManager(db)

    try:
        session = manager.update_session(
            session_id,
            name=request.name,
            description=request.description
        )

        return {
            "id": session.id,
            "name": session.name or "未命名项目",
            "description": session.description
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: SQLSession = Depends(get_db)
):
    """删除项目"""
    manager = SessionManager(db)
    success = manager.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {"status": "deleted", "session_id": session_id}

