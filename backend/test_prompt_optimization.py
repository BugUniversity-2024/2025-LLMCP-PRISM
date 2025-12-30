"""测试 Prompt 优化效果"""
import sys
sys.path.append('.')

from app.services.prompt_engine import PromptEngine

# 创建引擎实例（使用 Mock 模式）
engine = PromptEngine(use_real_api=False)

# 测试案例
test_cases = [
    "一只橘猫在窗边晒太阳",
    "科幻城市夜景",
    "森林中的精灵"
]

print("=" * 80)
print("Prompt 优化效果测试")
print("=" * 80)

for i, user_input in enumerate(test_cases, 1):
    print(f"\n【案例 {i}】")
    print(f"用户输入: {user_input}")
    print("-" * 80)

    result = engine.generate_schema(user_input)

    print("\n生成的 Schema:")
    import json
    print(json.dumps(result["schema"], ensure_ascii=False, indent=2))

    print("\n生成的 Prompt:")
    print(result["prompt"])
    print("\n" + "=" * 80)
