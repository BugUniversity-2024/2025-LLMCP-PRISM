"""
反馈优化 API（集成数据库版本）
阶段 1: Mock 服务
阶段 2: 真实 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SQLSession

from app.schemas.requests import FeedbackRequest
from app.schemas.responses import FeedbackResponse
from app.core.database import get_db
from app.services.feedback_engine import FeedbackEngine, ConflictError
from app.services.image_adapter import ImageAdapter
from app.services.session_manager import SessionManager
from app.config import settings

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(
    request: FeedbackRequest,
    db: SQLSession = Depends(get_db)
):
    """
    反馈优化接口

    流程：
    1. 获取当前版本的 Schema
    2. 调用 FeedbackEngine 生成 Diff（阶段1用Mock）
    3. 调用 ImageAdapter 生成新图片（阶段1下载picsum图片）
    4. 存储新版本到数据库
    5. 返回结果
    """
    try:
        # 初始化服务（从配置读取 use_real_api）
        feedback_engine = FeedbackEngine(use_real_api=settings.use_real_api)
        image_adapter = ImageAdapter(use_real_api=settings.use_real_api)
        session_manager = SessionManager(db)

        # 1. 获取当前版本
        current_version = session_manager.get_version(
            session_id=request.session_id,
            version_number=request.version
        )
        if not current_version:
            raise HTTPException(status_code=404, detail="版本不存在")

        # 2. 分析反馈并生成 Diff
        result = feedback_engine.analyze_feedback(
            feedback=request.feedback,
            current_schema=current_version.schema
        )

        diff = result["diff"]
        new_schema = result["new_schema"]
        prompt = result["prompt"]

        # 3. 生成新图片（传入参考图片路径）
        next_version_number = current_version.version_number + 1
        image_result = await image_adapter.generate_image(
            prompt=prompt,
            session_id=request.session_id,
            version=next_version_number,
            reference_image_path=current_version.image_path
        )

        # 4. 存储新版本
        new_version = session_manager.create_version(
            session_id=request.session_id,
            schema=new_schema,
            prompt=prompt,
            image_url=image_result["image_url"],
            image_path=image_result["image_path"],
            user_feedback=request.feedback,
            diff=diff,
            parent_version_id=current_version.id
        )

        # 5. 返回响应
        return FeedbackResponse(
            session_id=request.session_id,
            version=new_version.version_number,
            parent_version=request.version,
            diff=diff,
            schema=new_schema,
            prompt=prompt,
            image_url=image_result["image_url"],
            created_at=new_version.created_at.isoformat()
        )

    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")
