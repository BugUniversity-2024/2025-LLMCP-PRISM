"""
Prompt Engine - 负责生成结构化 Prompt
阶段 1: Mock 实现
阶段 2: 接入 OpenAI GPT-4o
"""
import json
import random
import time
from pathlib import Path
from typing import Dict, Any


# System Prompt 模板（阶段 2 使用）
GENERATION_SYSTEM_PROMPT = """你是一个专业的 AI 绘画 Prompt 生成器，专门为火山引擎 Seedream 模型优化提示词。

【核心要求】
- 生成简洁连贯的自然语言描述
- 遵循结构：主体 + 行为 + 环境 + 美学元素
- 使用中文描述，每个元素用短语表达
- 避免冗长句子，保持描述精炼
- 控制总字数合理，避免信息过载

【输出格式】
你必须输出 JSON 格式，包含以下字段：
{
  "subject": ["主体", "动作或姿态"],
  "appearance": ["外观特征1", "外观特征2"],
  "style": ["画风", "艺术风格"],
  "composition": ["构图", "视角"],
  "lighting": ["光照", "色调"],
  "background": ["背景", "环境"],
  "quality": ["画质", "分辨率"],
  "negative": ["避免元素1", "避免元素2"],
  "weights": {"style": 1.0, "realism": 0.7}
}

【字段说明】
- subject: 主体及动作（用2-3个短语描述核心主体）
- appearance: 外观细节（2-4个关键视觉特征）
- style: 画风风格（如：半写实、动漫风、电影感）
- composition: 构图视角（如：特写、俯视、三分法）
- lighting: 光照色调（如：柔光、暖色调、逆光）
- background: 背景环境（简洁描述，2-3个元素）
- quality: 画质要求（如：高清、细节丰富、2K）
- negative: 负面提示（常见质量问题）
- weights: 权重（style: 风格强度, realism: 写实度，范围 0.1-1.5）

【参考案例 1】
用户输入："一只橘猫在窗边晒太阳"
输出：
{
  "subject": ["橘猫", "慵懒趴着"],
  "appearance": ["橘色短毛", "绿色眼睛", "蓬松尾巴"],
  "style": ["半写实风格", "温暖色调"],
  "composition": ["特写镜头", "浅景深"],
  "lighting": ["温暖午后阳光", "柔和侧光"],
  "background": ["木质窗台", "窗外树影"],
  "quality": ["高清", "细节丰富"],
  "negative": ["模糊", "变形", "多余肢体"],
  "weights": {"style": 1.0, "realism": 0.8}
}

【参考案例 2】
用户输入："科幻城市夜景"
输出：
{
  "subject": ["未来城市", "高耸摩天大楼"],
  "appearance": ["玻璃幕墙", "霓虹灯光", "飞行器"],
  "style": ["赛博朋克", "科幻感"],
  "composition": ["广角", "仰视"],
  "lighting": ["霓虹冷光", "紫蓝色调", "光线追踪"],
  "background": ["夜空", "繁星", "光污染"],
  "quality": ["4K", "电影级"],
  "negative": ["模糊", "低清", "噪点"],
  "weights": {"style": 1.3, "realism": 0.6}
}

【生成规则】
1. 每个数组提供 2-4 个简短元素（避免单个元素过长）
2. 使用专业绘画术语和视觉描述
3. 优先描述视觉可见的元素
4. 避免抽象概念，聚焦具体画面
5. negative 列出常见质量问题
6. 确保 JSON 格式正确
"""


class PromptEngine:
    """Prompt 生成引擎（阶段 1: Mock 实现）"""

    def __init__(self, use_real_api: bool = False):
        """
        Args:
            use_real_api: 是否使用真实 OpenAI API（阶段 2 设置为 True）
        """
        self.use_real_api = use_real_api
        if use_real_api:
            from openai import OpenAI
            from app.config import settings
            self.client = OpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base  # 支持自定义 Base URL
            )
            self.model = settings.openai_model

        # 加载 System Prompt（如果使用真实 API）
        if use_real_api:
            self.system_prompt = self._load_system_prompt("generation.txt")

    def _load_system_prompt(self, filename: str) -> str:
        """从 prompts 目录加载 System Prompt"""
        prompt_path = Path(__file__).parent.parent / "prompts" / filename
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Prompt 文件未找到：{prompt_path}，使用默认 prompt")
            return GENERATION_SYSTEM_PROMPT

    def generate_schema(self, user_input: str) -> Dict[str, Any]:
        """
        根据用户输入生成结构化 Schema

        Args:
            user_input: 用户的创意描述

        Returns:
            {
                "schema": dict,  # 结构化 Schema
                "prompt": str    # 自然语言 Prompt
            }

        Raises:
            ValueError: 用户输入为空
            RuntimeError: OpenAI API 调用失败
        """
        if not user_input or not user_input.strip():
            raise ValueError("用户输入不能为空")

        if self.use_real_api:
            return self._generate_with_openai(user_input)
        else:
            return self._generate_mock(user_input)

    def _generate_mock(self, user_input: str) -> Dict[str, Any]:
        """阶段 1: Mock 实现"""
        # 预设的两个 Schema 模板
        templates = [
            {
                "subject": ["一只橘猫", "坐姿"],
                "appearance": ["橘色毛发", "蓝色眼睛", "蓬松尾巴"],
                "style": ["半写实", "动漫风格", "柔和线条"],
                "composition": ["特写", "浅景深", "正面视角"],
                "lighting": ["柔和侧光", "暖色调", "日落光"],
                "background": ["窗边", "日落", "朦胧背景"],
                "quality": ["高清", "细节丰富", "16:9"],
                "negative": ["模糊", "变形", "多余肢体"],
                "weights": {"style": 1.0, "realism": 0.7}
            },
            {
                "subject": ["三位角色", "头对头躺在草地"],
                "appearance": ["面部清晰", "服装自然", "头发随风散开"],
                "style": ["二次元半写实", "明显线条感", "真实光影"],
                "composition": ["俯拍70度", "圆形构图", "头部居中"],
                "lighting": ["温暖午后光", "侧逆光", "柔和高光"],
                "background": ["秋天草地", "黄绿褐色", "落叶飘落"],
                "quality": ["16:9", "1920x1080", "高清细腻"],
                "negative": ["模糊", "变形", "过度扁平"],
                "weights": {"style": 1.0, "realism": 0.8}
            }
        ]

        # 随机选择一个模板
        schema = random.choice(templates)

        # 渲染为 Prompt
        prompt = self._render_prompt(schema)

        return {
            "schema": schema,
            "prompt": prompt
        }

    def _generate_with_openai(self, user_input: str) -> Dict[str, Any]:
        """阶段 2: 真实 OpenAI API 调用（带重试机制）"""
        max_retries = 3
        retry_delay = 1  # 秒

        for attempt in range(max_retries):
            try:
                print(f"🔄 调用 OpenAI API (尝试 {attempt + 1}/{max_retries})...")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=1500
                )

                schema_json = json.loads(response.choices[0].message.content)

                # 验证 Schema 完整性
                self._validate_schema(schema_json)

                prompt = self._render_prompt(schema_json)

                print(f"✅ Prompt 生成成功")
                return {
                    "schema": schema_json,
                    "prompt": prompt
                }

            except json.JSONDecodeError as e:
                print(f"⚠️ Schema 解析失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ 解析失败，回退到 mock 模式")
                    return self._generate_mock(user_input)

            except Exception as e:
                print(f"⚠️ OpenAI API 调用失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                else:
                    print(f"❌ API 调用失败，回退到 mock 模式")
                    return self._generate_mock(user_input)

    def _validate_schema(self, schema: Dict[str, Any]):
        """验证 Schema 完整性"""
        required_fields = [
            "subject", "appearance", "style", "composition",
            "lighting", "background", "quality", "negative", "weights"
        ]
        for field in required_fields:
            if field not in schema:
                raise ValueError(f"Schema 缺少必要字段：{field}")

    def _render_prompt(self, schema: Dict[str, Any]) -> str:
        """
        将 Schema 渲染为自然语言 Prompt

        遵循火山引擎推荐风格：
        - 简洁连贯的自然语言描述
        - 主体 + 行为 + 环境 + 美学元素
        - 控制在 300 字以内
        """
        parts = []

        # 1. 主体场景（核心）
        subject_parts = []
        if schema.get("subject"):
            subject_parts.extend(schema["subject"])
        if schema.get("appearance"):
            subject_parts.extend(schema["appearance"])

        if subject_parts:
            parts.append('，'.join(subject_parts))

        # 2. 构图与视角
        if schema.get("composition"):
            parts.append('，'.join(schema["composition"]))

        # 3. 光照与氛围
        if schema.get("lighting"):
            parts.append('，'.join(schema["lighting"]))

        # 4. 背景环境
        if schema.get("background"):
            parts.append('，'.join(schema["background"]))

        # 5. 风格与质量
        style_parts = []
        if schema.get("style"):
            style_parts.extend(schema["style"])
        if schema.get("quality"):
            style_parts.extend(schema["quality"])

        if style_parts:
            parts.append('，'.join(style_parts))

        # 主要描述（自然流畅的句子）
        main_prompt = '，'.join(parts)

        # 负面提示（单独一行，保持清晰）
        negative_prompt = ""
        if schema.get("negative"):
            negative_prompt = f"\n负面提示：{', '.join(schema['negative'])}"

        return main_prompt + negative_prompt
