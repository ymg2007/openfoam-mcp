#!/usr/bin/env python3
"""
OpenFOAM MCP Server 测试脚本
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 切换到示例 case 目录
os.chdir(Path(__file__).parent / "examples" / "test_case")

print(f"工作目录: {os.getcwd()}")

# 导入并测试解析器
from parser import parse_openfoam_dict

# 测试字典解析
print("\n" + "="*50)
print("=== 测试字典解析 ===")
print("="*50)

files_to_test = [
    "system/controlDict",
    "system/fvSchemes",
    "system/fvSolution",
    "constant/transportProperties",
    "0/U",
    "0/p",
]

for file_path in files_to_test:
    full_path = Path(file_path)
    if full_path.exists():
        print(f"\n📄 {file_path}")
        print("-" * 40)
        try:
            result = parse_openfoam_dict(str(full_path))
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"解析错误: {e}")

print("\n" + "="*50)
print("✅ 测试完成！")
print("="*50)
