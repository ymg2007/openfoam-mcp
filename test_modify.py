#!/usr/bin/env python3
"""
测试修改功能
"""

import sys
import os
from pathlib import Path
import shutil

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 备份原始文件
case_dir = Path(__file__).parent / "examples" / "test_case"
os.chdir(case_dir)

# 备份 controlDict
if Path("system/controlDict.bak").exists():
    Path("system/controlDict.bak").unlink()
shutil.copy("system/controlDict", "system/controlDict.bak")

# 备份 U
if Path("0/U.bak").exists():
    Path("0/U.bak").unlink()
shutil.copy("0/U", "0/U.bak")

from server import read_dict_file, modify_control_dict, modify_boundary_condition

print("="*60)
print("测试修改功能")
print("="*60)

# 测试 1: 修改 controlDict
print("\n1. 读取原始 controlDict:")
result = read_dict_file("system/controlDict")
print(f"  deltaT: {result[:200]}...")

print("\n2. 修改 deltaT 为 0.0005:")
result = modify_control_dict(delta_t=0.0005)
print(f"  {result}")

print("\n3. 读取修改后的 controlDict:")
result = read_dict_file("system/controlDict")
import json
parsed = json.loads(result)
print(f"  deltaT: {parsed.get('deltaT')}")

# 恢复
print("\n4. 恢复 deltaT 为 0.001:")
result = modify_control_dict(delta_t=0.001)
print(f"  {result}")

# 测试 2: 修改边界条件
print("\n5. 修改 U 场 inlet 边界:")
print("   将入口速度从 (10 0 0) 改为 (15 0 0)")

result = modify_boundary_condition("U", "inlet", value="uniform (15 0 0)")
print(f"  {result}")

print("\n6. 读取修改后的 U 场:")
result = read_dict_file("0/U")
parsed = json.loads(result)
inlet_value = parsed.get("boundaryField", {}).get("inlet", {}).get("value")
print(f"  inlet value: {inlet_value}")

# 恢复
print("\n7. 恢复入口速度为 (10 0 0):")
result = modify_boundary_condition("U", "inlet", value="uniform (10 0 0)")
print(f"  {result}")

# 恢复备份
shutil.copy("system/controlDict.bak", "system/controlDict")
shutil.copy("0/U.bak", "0/U")

print("\n" + "="*60)
print("测试完成！")
print("="*60)
