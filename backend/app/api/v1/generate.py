"""
生成图片 API（集成数据库版本）
阶段 1: Mock 服务
阶段 2: 真实 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as SQLSession

from app.schemas.requests import GenerateRequest, PreviewRequest
from app.schemas.responses import GenerateResponse, PreviewResponse
from app.core.database import get_db
from app.services.prompt_engine import PromptEngine
from app.services.image_adapter import ImageAdapter
from app.services.session_manager import SessionManager
from app.config import settings

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    db: SQLSession = Depends(get_db)
):
    """
    生成图片接口

    流程：
    1. 调用 PromptEngine 生成 Schema（阶段1用Mock）
    2. 调用 ImageAdapter 生成图片（阶段1下载picsum图片）
    3. 存储到数据库
    4. 返回结果
    """
    try:
        # 初始化服务（从配置读取 use_real_api）
        prompt_engine = PromptEngine(use_real_api=settings.use_real_api)
        image_adapter = ImageAdapter(use_real_api=settings.use_real_api)
        session_manager = SessionManager(db)

        # 1. 生成或使用已有 Schema
        if request.schema and request.prompt:
            # 用户已确认的 Schema（来自 preview）
            schema = request.schema
            prompt = request.prompt
        else:
            # 重新生成 Schema
            result = prompt_engine.generate_schema(request.user_input)
            schema = result["schema"]
            prompt = result["prompt"]

        # 2. 创建或获取 Session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="会话不存在")
        else:
            session = session_manager.create_session()

        # 3. 生成图片
        image_result = await image_adapter.generate_image(
            prompt=prompt,
            session_id=session.id,
            version=1
        )

        # 4. 存储版本到数据库
        version = session_manager.create_version(
            session_id=session.id,
            schema=schema,
            prompt=prompt,
            image_url=image_result["image_url"],
            image_path=image_result["image_path"],
            user_input=request.user_input
        )

        # 5. 返回响应
        return GenerateResponse(
            session_id=session.id,
            version=version.version_number,
            schema=schema,
            prompt=prompt,
            image_url=image_result["image_url"],
            created_at=version.created_at.isoformat()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")


@router.post("/preview", response_model=PreviewResponse)
async def preview_prompt(request: PreviewRequest):
    """
    预览 Prompt（不生成图片）

    流程：
    1. 调用 PromptEngine 生成 Schema
    2. 返回 Schema 和 Prompt（不创建 Session/Version，不生成图片）
    """
    try:
        prompt_engine = PromptEngine(use_real_api=settings.use_real_api)

        # 只生成 Schema，不调用 ImageAdapter
        result = prompt_engine.generate_schema(request.user_input)

        return PreviewResponse(
            schema=result["schema"],
            prompt=result["prompt"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部错误: {str(e)}")
