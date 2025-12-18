"""
反馈优化 API (Mock 版本)
"""
from fastapi import APIRouter
from datetime import datetime
import random

from app.schemas.requests import FeedbackRequest
from app.schemas.responses import FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(request: FeedbackRequest):
    """
    反馈优化接口（Mock 版本）

    根据反馈返回迭代后的 Schema 和图片
    """
    # Mock Schema (优化后的)
    optimized_schema = {
        "subject": ["一只猫"],
        "appearance": ["橘色毛发", "蓝色眼睛", "蓬松尾巴"],
        "style": ["半写实", "动漫风格", "柔和线条"],
        "composition": ["特写", "浅景深", "正面视角"],
        "lighting": ["柔和侧光", "暖色调", "轮廓高光", "更亮的环境光", "增加高光"],  # 添加了优化
        "background": ["窗边", "清晨", "简洁背景"],  # 简化了背景
        "quality": ["高清", "细节丰富", "16:9"],
        "negative": ["模糊", "变形", "多余肢体"],
        "weights": {"style": 1.0, "realism": 0.7, "lighting": 1.1}  # 提升了 lighting 权重
    }

    # Mock Diff
    mock_diff = {
        "operations": [
            {"action": "add", "field": "lighting", "values": ["更亮的环境光", "增加高光"]},
            {"action": "adjust", "field": "weights.lighting", "delta": 0.3},
            {"action": "replace", "field": "background", "values": ["窗边", "清晨", "简洁背景"]}
        ],
        "reasoning": f"根据用户反馈「{request.feedback}」，优化了光照和背景描述"
    }

    # 生成优化后的 Prompt
    prompt = f"""画面比例：16:9，{', '.join(optimized_schema['quality'])}
风格要求：{', '.join(optimized_schema['style'])}

【主体场景与构图】
主体：{', '.join(optimized_schema['subject'])}
构图：{', '.join(optimized_schema['composition'])}

【外观细节】
{', '.join(optimized_schema['appearance'])}

【光照与氛围】（已优化）
{', '.join(optimized_schema['lighting'])}

【背景】（已优化）
{', '.join(optimized_schema['background'])}

【负向提示（避免）】
{', '.join(optimized_schema['negative'])}

优化说明：{mock_diff['reasoning']}
"""

    # 使用不同的随机图片（模拟优化后的效果）
    random_seed = random.randint(1001, 2000)
    image_url = f"https://picsum.photos/seed/{random_seed}/1920/1080"

    return FeedbackResponse(
        session_id=request.session_id,
        version=request.version + 1,
        parent_version=request.version,
        diff=mock_diff,
        schema=optimized_schema,
        prompt=prompt,
        image_url=image_url,
        created_at=datetime.now().isoformat()
    )
