#!/usr/bin/env python3
"""
从 Claude Code 对话记录中提取指定项目路径的对话记录

用法:
    python filter_conversations.py <输入文件> <目标项目路径> [输出文件]

示例:
    python filter_conversations.py ../docs/1547-conversation.md /Users/esap/Desktop/2025-Study/2025-LLMCP-PRISM
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def filter_conversations(
    input_file: str,
    target_project: str,
    output_file: str | None = None,
) -> list[dict]:
    """
    从对话记录文件中提取指定项目的记录
    """
    filtered_records = []
    total_count = 0
    matched_count = 0

    print(f"读取文件: {input_file}")
    print(f"目标项目路径: {target_project}")

    with open(input_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            total_count += 1
            try:
                record = json.loads(line)
                project_path = record.get("project", "")

                if target_project in project_path:
                    matched_count += 1
                    filtered_records.append(record)

            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行 JSON 解析失败: {e}", file=sys.stderr)
                continue

    print(f"\n统计:")
    print(f"  总记录数: {total_count}")
    print(f"  匹配记录数: {matched_count}")
    print(f"  匹配率: {matched_count / total_count * 100:.2f}%")

    # 写入输出文件
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for record in filtered_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        print(f"\n已保存到: {output_path.absolute()}")

    # 预览
    if filtered_records:
        print(f"\n预览 (前 3 条):")
        for i, record in enumerate(filtered_records[:3], 1):
            display = record.get("display", "")[:60]
            ts = record.get("timestamp", 0)
            time_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else "N/A"
            print(f"  {i}. [{time_str}] {display}...")

    return filtered_records


def main():
    parser = argparse.ArgumentParser(
        description="从 Claude Code 对话记录中提取指定项目路径的记录"
    )
    parser.add_argument("input_file", help="输入的对话记录文件")
    parser.add_argument("target_project", help="目标项目路径（支持部分匹配）")
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（默认不保存，仅统计）",
        default=None,
    )

    args = parser.parse_args()
    filter_conversations(args.input_file, args.target_project, args.output)


if __name__ == "__main__":
    main()
