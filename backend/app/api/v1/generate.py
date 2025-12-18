"""
生成图片 API (Mock 版本)
"""
from fastapi import APIRouter
from datetime import datetime
import uuid
import random

from app.schemas.requests import GenerateRequest
from app.schemas.responses import GenerateResponse

router = APIRouter()

# Mock 数据
MOCK_SCHEMAS = [
    {
        "subject": ["一只猫"],
        "appearance": ["橘色毛发", "蓝色眼睛", "蓬松尾巴"],
        "style": ["半写实", "动漫风格", "柔和线条"],
        "composition": ["特写", "浅景深", "正面视角"],
        "lighting": ["柔和侧光", "暖色调", "轮廓高光"],
        "background": ["窗边", "清晨", "朦胧背景"],
        "quality": ["高清", "细节丰富", "16:9"],
        "negative": ["模糊", "变形", "多余肢体"],
        "weights": {"style": 1.0, "realism": 0.7, "lighting": 0.8}
    },
    {
        "subject": ["一位角色坐在站台边缘"],
        "appearance": ["动漫线条", "柔和上色", "沉静表情"],
        "style": ["电影感", "半写实背景", "动漫角色"],
        "composition": ["平视", "中距离", "对面视角"],
        "lighting": ["清晨淡金蓝混合", "体积雾", "柔光"],
        "background": ["地铁站台", "轻微雾气", "轨道延伸"],
        "quality": ["16:9", "高清", "浅景深"],
        "negative": ["拥挤", "科幻UI", "夸张比例"],
        "weights": {"style": 1.0, "realism": 0.6}
    }
]


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """
    生成图片接口（Mock 版本）

    返回随机的 Schema 和图片
    """
    # 生成或使用现有 session_id
    session_id = request.session_id or str(uuid.uuid4())

    # 随机选择一个 Mock Schema
    schema = random.choice(MOCK_SCHEMAS)

    # 生成假的 Prompt
    prompt = f"""画面比例：16:9，{', '.join(schema['quality'])}
风格要求：{', '.join(schema['style'])}

【主体场景与构图】
主体：{', '.join(schema['subject'])}
构图：{', '.join(schema['composition'])}

【外观细节】
{', '.join(schema['appearance'])}

【光照与氛围】
{', '.join(schema['lighting'])}

【背景】
{', '.join(schema['background'])}

【负向提示（避免）】
{', '.join(schema['negative'])}
"""

    # 使用 picsum.photos 提供随机图片
    # 添加随机参数确保每次都是不同的图片
    random_seed = random.randint(1, 1000)
    image_url = f"https://picsum.photos/seed/{random_seed}/1920/1080"

    return GenerateResponse(
        session_id=session_id,
        version=1,
        schema=schema,
        prompt=prompt,
        image_url=image_url,
        created_at=datetime.now().isoformat()
    )
