#!/usr/bin/env python3
"""
OpenFOAM 文件编辑器
用于安全地修改 OpenFOAM 配置文件
"""

import re
from pathlib import Path
from typing import Optional


def modify_dict_value(
    filepath: Path,
    key: str,
    new_value: str,
) -> bool:
    """修改字典文件中的简单键值对"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配模式: key 值;
    pattern = rf'^(\s*){re.escape(key)}\s+[^;]+;'
    replacement = rf'\1{key} {new_value};'

    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def modify_boundary_value(
    filepath: Path,
    boundary_name: str,
    new_value: Optional[str] = None,
    new_type: Optional[str] = None,
) -> tuple:
    """修改场文件中的边界条件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modifications = []

    # 使用逐行方法修改
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 检测边界名（可能是单独一行）
        # 格式: boundaryName
        #         {
        if stripped and not stripped.startswith('//') and stripped == boundary_name:
            # 检查下一行是否是 {
            if i + 1 < len(lines) and lines[i + 1].strip() == '{':
                # 找到目标边界
                result_lines.append(line)  # 保留边界名行
                i += 1
                result_lines.append(lines[i])  # 保留 { 行
                i += 1

                # 处理边界块内容
                while i < len(lines):
                    inner_line = lines[i]
                    inner_stripped = inner_line.strip()

                    # 边界块结束
                    if inner_stripped == '}':
                        result_lines.append(inner_line)
                        i += 1
                        break

                    # 修改 type
                    if new_type and inner_stripped.startswith('type') and ';' in inner_stripped:
                        indent = len(inner_line) - len(inner_line.lstrip())
                        result_lines.append(' ' * indent + f"type            {new_type};")
                        modifications.append(f"type -> {new_type}")
                        i += 1
                        continue

                    # 修改 value
                    if new_value and inner_stripped.startswith('value') and ';' in inner_stripped:
                        parts = inner_stripped.split(None, 1)
                        if len(parts) > 0 and parts[0] == 'value':
                            indent = len(inner_line) - len(inner_line.lstrip())
                            result_lines.append(' ' * indent + f"value           {new_value};")
                            modifications.append(f"value -> {new_value}")
                            i += 1
                            continue

                    result_lines.append(inner_line)
                    i += 1
            else:
                result_lines.append(line)
                i += 1
        else:
            result_lines.append(line)
            i += 1

    if modifications:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result_lines))
        return True, modifications

    return False, []


if __name__ == "__main__":
    # 测试
    test_file = Path("examples/test_case/0/U")
    if test_file.exists():
        print("原始内容:")
        print(test_file.read_text())

        print("\n修改边界条件...")
        success, mods = modify_boundary_value(test_file, "inlet", new_value="uniform (15 0 0)")
        print(f"成功: {success}, 修改: {mods}")

        print("\n修改后内容:")
        print(test_file.read_text())

        # 恢复
        modify_boundary_value(test_file, "inlet", new_value="uniform (10 0 0)")
