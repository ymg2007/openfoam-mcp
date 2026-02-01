#!/usr/bin/env python3
"""
OpenFOAM 字典文件解析器
支持解析 OpenFOAM 的字典格式
"""

import re
from typing import Any, Dict, List, Tuple, Optional


class OpenFOAMDict:
    """OpenFOAM 字典文件解析器"""

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        self.parsed = self._parse()

    def _remove_comments(self, text: str) -> str:
        """移除注释"""
        # 移除单行注释 //
        result = []
        for line in text.split('\n'):
            if '//' in line:
                line = line[:line.index('//')]
            result.append(line)
        text = '\n'.join(result)

        # 移除多行注释 /* ... */
        while '/*' in text:
            start = text.index('/*')
            end = text.index('*/', start) + 2
            text = text[:start] + text[end:]

        return text

    def _parse(self) -> Dict[str, Any]:
        """解析整个字典"""
        content = self._remove_comments(self.content)
        result, _ = self._parse_dict(content, 0)
        return result

    def _parse_dict(self, text: str, pos: int) -> Tuple[Dict[str, Any], int]:
        """从指定位置解析字典"""
        result = {}
        i = pos

        while i < len(text):
            # 跳过空白
            while i < len(text) and text[i] in ' \t\n\r':
                i += 1

            if i >= len(text):
                break

            # 检查字典结束
            if text[i] == '}':
                i += 1
                return result, i

            # 跳过分号
            if text[i] == ';':
                i += 1
                continue

            # 读取标识符（键名）
            if text[i] in '(){};':
                i += 1
                continue

            # 读取键名
            key, i = self._read_identifier(text, i)
            if not key:
                i += 1
                continue

            # 跳过空白
            while i < len(text) and text[i] in ' \t\n\r':
                i += 1

            if i >= len(text):
                break

            # 检查值的类型
            if text[i] == '{':
                # 子字典
                i += 1
                sub_dict, i = self._parse_dict(text, i)
                result[key] = sub_dict
            elif text[i] == '(':
                # 列表/向量
                value, i = self._read_list(text, i)
                result[key] = value
            else:
                # 普通值
                value, i = self._read_value(text, i)
                if value is not None:
                    result[key] = value

        return result, i

    def _read_identifier(self, text: str, pos: int) -> Tuple[str, int]:
        """读取标识符"""
        start = pos
        while pos < len(text) and text[pos] not in '{}(); \t\n\r':
            pos += 1
        return text[start:pos].strip(), pos

    def _read_value(self, text: str, pos: int) -> Tuple[Any, int]:
        """读取值直到分号"""
        start = pos
        while pos < len(text) and text[pos] != ';':
            pos += 1
        if pos > len(text):
            return None, pos
        value = text[start:pos].strip()
        return self._parse_value(value), pos + 1

    def _read_list(self, text: str, pos: int) -> Tuple[Any, int]:
        """读取列表/向量 ( ... )"""
        pos += 1  # 跳过 '('
        start = pos
        depth = 1

        while pos < len(text) and depth > 0:
            if text[pos] == '(':
                depth += 1
            elif text[pos] == ')':
                depth -= 1
            pos += 1

        list_text = text[start:pos-1].strip()

        # 尝试解析为数字列表
        parts = [p.strip() for p in list_text.split() if p.strip()]
        numeric_list = []
        all_numeric = True
        for part in parts:
            try:
                if '.' in part:
                    numeric_list.append(float(part))
                else:
                    numeric_list.append(int(part))
            except ValueError:
                all_numeric = False
                break

        if all_numeric:
            return numeric_list, pos
        else:
            return parts, pos

    def _parse_value(self, value: str) -> Any:
        """解析单个值的类型"""
        value = value.strip()

        # 空
        if not value:
            return None

        # 带单位的数字 (如 "1e-05 [0 2 -1 0 0 0 0]")
        if '[' in value and ']' in value:
            parts = value.split('[')
            if parts[0].strip():
                try:
                    num = float(parts[0].strip())
                    return {"value": num, "dimensions": parts[1].strip()}
                except ValueError:
                    pass

        # 数字
        try:
            if 'e-' in value.lower() or 'e+' in value.lower() or '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # 布尔值
        lower = value.lower()
        if lower in ['yes', 'true', 'on']:
            return True
        if lower in ['no', 'false', 'off']:
            return False

        # uniform 开头的值
        if value.startswith('uniform'):
            rest = value[7:].strip()
            # uniform (x y z)
            if rest.startswith('(') and rest.endswith(')'):
                inner = rest[1:-1].strip()
                parts = inner.split()
                try:
                    return {"type": "uniform", "value": [float(p) for p in parts]}
                except ValueError:
                    return value
            # uniform 0
            try:
                num = float(rest)
                return {"type": "uniform", "value": num}
            except ValueError:
                return {"type": "uniform", "value": rest}

        # nonuniform
        if value.startswith('nonuniform'):
            return {"type": "nonuniform", "value": value[10:].strip()}

        return value


def parse_openfoam_dict(filepath: str) -> Dict[str, Any]:
    """便捷函数：解析 OpenFOAM 字典文件"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    parser = OpenFOAMDict(content)
    return parser.parsed


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        result = parse_openfoam_dict(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
