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
GENERATION_SYSTEM_PROMPT = """你是一个专业的 AI 绘画 Prompt 生成器，擅长将用户的简单描述转换为详细、结构化的绘画指令。

【输出格式】
你必须输出 JSON 格式，包含以下字段：
{
  "subject": ["主体描述"],
  "appearance": ["外观细节"],
  "style": ["画风风格"],
  "composition": ["构图方式"],
  "lighting": ["光照描述"],
  "background": ["背景描述"],
  "quality": ["质量要求"],
  "negative": ["负面提示"],
  "weights": {"style": 1.0, "realism": 0.7}
}

【生成规则】
1. 根据用户输入填充所有字段，保证完整性
2. 使用专业绘画术语（如：rim light、bokeh、cinematic composition、soft cel-shading）
3. 避免冲突（不能同时要求 realistic 和 cartoon）
4. 使用中文描述，适配图像生成模型
5. 如果用户输入简单，合理补充细节（但不偏离主题）

【参考案例】
案例1（秋日草地三人场景）：
用户输入："三个人躺在草地上看落叶"
Schema 输出：
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

案例2（站台场景）：
用户输入："一个人坐在地铁站台边缘，雾气弥漫"
Schema 输出：
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

【重要提示】
- 保持所有描述为中文
- 确保 JSON 格式正确
- 每个数组至少有1-3个元素
- weights 的值在 0.1-1.5 之间
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
        """
        parts = []

        # 1. 画面比例和质量
        if schema.get("quality"):
            parts.append(f"画面比例：16:9，{', '.join(schema['quality'])}")

        # 2. 风格要求
        if schema.get("style"):
            parts.append(f"风格要求：{', '.join(schema['style'])}")

        # 3. 主体场景与构图
        parts.append("\n【主体场景与构图】")
        if schema.get("subject"):
            parts.append(f"主体：{', '.join(schema['subject'])}")
        if schema.get("composition"):
            parts.append(f"构图：{', '.join(schema['composition'])}")

        # 4. 外观细节
        if schema.get("appearance"):
            parts.append("\n【外观细节】")
            parts.append(', '.join(schema['appearance']))

        # 5. 光照与氛围
        if schema.get("lighting"):
            parts.append("\n【光照与氛围】")
            parts.append(', '.join(schema['lighting']))

        # 6. 背景
        if schema.get("background"):
            parts.append("\n【背景】")
            parts.append(', '.join(schema['background']))

        # 7. 负面提示
        if schema.get("negative"):
            parts.append("\n【负向提示（避免）】")
            parts.append(', '.join(schema['negative']))

        return '\n'.join(parts)
