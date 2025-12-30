"""
Feedback Engine - 负责理解反馈并生成 Prompt Diff
阶段 1: Mock 实现
阶段 2: 接入 OpenAI GPT-4o
"""
import json
import copy
import time
from pathlib import Path
from typing import Dict, Any


# Feedback System Prompt（阶段 2 使用）
FEEDBACK_SYSTEM_PROMPT = """你是一个 Prompt 反馈分析器，负责理解用户对图片的反馈，并生成精确的修改指令。

【任务】
根据用户反馈，生成 Prompt Diff JSON：
{
  "operations": [
    {"action": "add", "field": "lighting", "values": ["更亮的光线"]},
    {"action": "remove", "field": "background", "values": ["复杂背景"]},
    {"action": "adjust", "field": "weights.lighting", "delta": 0.3}
  ],
  "reasoning": "用户反馈图片太暗，因此增加lighting字段的亮度描述，并提升权重"
}

【反馈映射规则】
常见反馈类型 → 对应字段：
- "太暗" / "太亮" / "光线不好" → lighting
- "脸怪" / "人物变形" / "表情不对" → appearance + negative
- "背景太乱" / "背景太简单" → background
- "风格不对" / "不够写实" / "太卡通" → style + weights
- "构图不好" / "角度不对" → composition
- "不够清晰" / "质量不好" → quality

【操作类型】
1. add: 在指定字段添加新的描述元素
2. remove: 从指定字段移除某些元素
3. adjust: 调整 weights 权重（delta 范围 -0.5 到 +0.5）
4. replace: 完全替换某个字段（慎用）

【关键原则】
1. 最小修改：只修改与反馈相关的字段
2. 保持一致：不要改变用户未提及的内容
3. 冲突检测：如果修改会导致矛盾，在 reasoning 中说明
4. 解释清楚：在 reasoning 中说明为什么这样修改

【示例】
用户反馈："太暗了"
原 Schema: {"lighting": ["柔和侧光"], "weights": {"lighting": 0.5}}
Diff 输出:
{
  "operations": [
    {"action": "add", "field": "lighting", "values": ["更亮的环境光", "增加高光"]},
    {"action": "adjust", "field": "weights.lighting", "delta": 0.3}
  ],
  "reasoning": "用户反馈图片太暗，在lighting字段添加更亮的描述，并将lighting权重从0.5提升到0.8"
}
"""


class ConflictError(Exception):
    """Schema 冲突异常"""
    pass


class FeedbackEngine:
    """反馈分析引擎（阶段 1: Mock 实现）"""

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

            # 加载 System Prompt
            self.system_prompt = self._load_system_prompt("feedback.txt")

    def _load_system_prompt(self, filename: str) -> str:
        """从 prompts 目录加载 System Prompt"""
        prompt_path = Path(__file__).parent.parent / "prompts" / filename
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Prompt 文件未找到：{prompt_path}，使用默认 prompt")
            return FEEDBACK_SYSTEM_PROMPT

    def analyze_feedback(
        self,
        feedback: str,
        current_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析用户反馈并生成 Prompt Diff

        Args:
            feedback: 用户反馈
            current_schema: 当前版本的 Schema

        Returns:
            {
                "diff": dict,         # Prompt Diff
                "new_schema": dict,   # 应用 Diff 后的新 Schema
                "prompt": str         # 新的自然语言 Prompt
            }

        Raises:
            ValueError: 反馈为空
            RuntimeError: OpenAI API 调用失败
            ConflictError: Schema 冲突
        """
        if not feedback or not feedback.strip():
            raise ValueError("用户反馈不能为空")

        if self.use_real_api:
            return self._analyze_with_openai(feedback, current_schema)
        else:
            return self._analyze_mock(feedback, current_schema)

    def _analyze_mock(self, feedback: str, current_schema: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 1: Mock 实现"""
        # 简单的反馈映射规则
        diff_operations = []

        if "暗" in feedback or "亮" in feedback:
            diff_operations.extend([
                {"action": "add", "field": "lighting", "values": ["更亮的环境光", "增加高光"]},
                {"action": "adjust", "field": "weights.lighting", "delta": 0.3}
            ])

        if "背景" in feedback:
            if "复杂" in feedback or "乱" in feedback:
                diff_operations.append({
                    "action": "replace",
                    "field": "background",
                    "value": ["简洁背景", "纯色背景"]
                })
            else:
                diff_operations.append({
                    "action": "add",
                    "field": "background",
                    "values": ["更丰富的背景细节"]
                })

        if "风格" in feedback:
            diff_operations.extend([
                {"action": "adjust", "field": "weights.style", "delta": 0.2}
            ])

        # 如果没有匹配到规则，使用默认修改
        if not diff_operations:
            diff_operations.append({
                "action": "add",
                "field": "quality",
                "values": ["优化细节"]
            })

        diff = {
            "operations": diff_operations,
            "reasoning": f"根据用户反馈「{feedback}」进行优化调整"
        }

        # 应用 Diff
        new_schema = self._apply_diff(current_schema, diff)

        # 渲染新 Prompt
        from app.services.prompt_engine import PromptEngine
        engine = PromptEngine()
        prompt = engine._render_prompt(new_schema)

        return {
            "diff": diff,
            "new_schema": new_schema,
            "prompt": prompt
        }

    def _analyze_with_openai(
        self,
        feedback: str,
        current_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """阶段 2: 真实 OpenAI API 调用（带重试机制）"""
        max_retries = 3
        retry_delay = 1  # 秒

        user_prompt = f"""当前 Schema:
{json.dumps(current_schema, ensure_ascii=False, indent=2)}

用户反馈: {feedback}

请生成 Prompt Diff。"""

        for attempt in range(max_retries):
            try:
                print(f"🔄 调用 OpenAI API 分析反馈 (尝试 {attempt + 1}/{max_retries})...")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.5,
                    max_tokens=1000
                )

                diff = json.loads(response.choices[0].message.content)

                # 验证 Diff 格式
                self._validate_diff(diff)

                # 应用 Diff
                new_schema = self._apply_diff(current_schema, diff)

                # 渲染新 Prompt
                from app.services.prompt_engine import PromptEngine
                engine = PromptEngine()
                prompt = engine._render_prompt(new_schema)

                print(f"✅ 反馈分析成功")
                return {
                    "diff": diff,
                    "new_schema": new_schema,
                    "prompt": prompt
                }

            except json.JSONDecodeError as e:
                print(f"⚠️ Diff 解析失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ 解析失败，回退到 mock 模式")
                    return self._analyze_mock(feedback, current_schema)

            except Exception as e:
                print(f"⚠️ OpenAI API 调用失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                else:
                    print(f"❌ API 调用失败，回退到 mock 模式")
                    return self._analyze_mock(feedback, current_schema)

    def _validate_diff(self, diff: Dict[str, Any]):
        """验证 Diff 格式"""
        if "operations" not in diff:
            raise ValueError("Diff 缺少 operations 字段")
        if not isinstance(diff["operations"], list):
            raise ValueError("operations 必须是数组")
        if len(diff["operations"]) == 0:
            raise ValueError("operations 不能为空")

    def _apply_diff(
        self,
        original_schema: Dict[str, Any],
        diff: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        应用 Prompt Diff 到原 Schema
        """
        new_schema = copy.deepcopy(original_schema)

        for op in diff["operations"]:
            action = op["action"]
            field = op["field"]

            if action == "add":
                if field not in new_schema:
                    new_schema[field] = []
                new_schema[field].extend(op["values"])

            elif action == "remove":
                if field in new_schema and "values" in op:
                    for val in op["values"]:
                        if val in new_schema[field]:
                            new_schema[field].remove(val)

            elif action == "adjust":
                keys = field.split(".")
                current = new_schema
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]

                last_key = keys[-1]
                current_value = current.get(last_key, 0.5)
                new_value = current_value + op["delta"]
                current[last_key] = max(0.1, min(1.5, new_value))

            elif action == "replace":
                keys = field.split(".")
                current = new_schema
                for key in keys[:-1]:
                    current = current[key]
                current[keys[-1]] = op["value"]

        # 冲突检测
        self._detect_conflicts(new_schema)

        return new_schema

    def _detect_conflicts(self, schema: Dict[str, Any]):
        """检测 Schema 冲突"""
        style = ' '.join(schema.get("style", []))

        # 冲突检测规则（更宽松）
        conflicting_pairs = [
            (["纯写实", "超写实"], ["纯卡通", "像素风"]),
            (["极度明亮", "高曝光"], ["极度黑暗", "纯黑背景"]),
        ]

        for group1, group2 in conflicting_pairs:
            has_group1 = any(s in style for s in group1)
            has_group2 = any(s in style for s in group2)
            if has_group1 and has_group2:
                raise ConflictError(f"Style 冲突：不能同时包含 {group1} 和 {group2}")
