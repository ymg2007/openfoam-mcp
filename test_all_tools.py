#!/usr/bin/env python3
"""
OpenFOAM MCP 服务器所有工具测试
"""

import sys
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 切换到示例 case 目录
case_dir = Path(__file__).parent / "examples" / "test_case"
os.chdir(case_dir)
print(f"工作目录: {os.getcwd()}\n")

# 导入服务器模块
from server import (
    find_openfoam_case,
    get_case_info,
    read_dict_file,
    read_file_content,
    list_field_files,
    get_boundary_conditions,
    modify_control_dict,
    get_transport_properties,
    get_turbulence_properties,
    get_fv_schemes,
    get_fv_solution,
    search_case_files,
)
from parser import parse_openfoam_dict

# 测试列表
tests = [
    ("1. get_case_info", lambda: get_case_info()),
    ("2. list_field_files", lambda: list_field_files()),
    ("3. read_dict_file - controlDict", lambda: read_dict_file("system/controlDict")),
    ("4. read_dict_file - fvSchemes", lambda: read_dict_file("system/fvSchemes")),
    ("5. read_dict_file - fvSolution", lambda: read_dict_file("system/fvSolution")),
    ("6. get_boundary_conditions - U", lambda: get_boundary_conditions("U")),
    ("7. get_boundary_conditions - p", lambda: get_boundary_conditions("p")),
    ("8. get_transport_properties", lambda: get_transport_properties()),
    ("9. get_fv_schemes", lambda: get_fv_schemes()),
    ("10. search_case_files - 'turbulence'", lambda: search_case_files("turbulence")),
    ("11. search_case_files - 'Gauss'", lambda: search_case_files("Gauss")),
]

print("=" * 60)
print("开始测试 OpenFOAM MCP 工具")
print("=" * 60 + "\n")

for test_name, test_func in tests:
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print('='*60)
    try:
        result = test_func()
        # 限制输出长度
        if len(result) > 500:
            print(result[:500])
            print(f"\n... (输出已截断，共 {len(result)} 字符)")
        else:
            print(result)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("所有测试完成！")
print("=" * 60)

# 测试修改功能（会修改示例文件，取消注释来测试）
"""
print("\n" + "=" * 60)
print("测试修改功能")
print("=" * 60)

# 先读取原始值
print("\n原始 controlDict:")
print(read_dict_file("system/controlDict"))

# 修改
print("\n修改 deltaT 为 0.0005...")
result = modify_control_dict(delta_t=0.0005)
print(result)

# 读取修改后的值
print("\n修改后的 controlDict:")
print(read_dict_file("system/controlDict"))

# 恢复
print("\n恢复 deltaT 为 0.001...")
result = modify_control_dict(delta_t=0.001)
print(result)
"""
