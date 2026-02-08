#!/usr/bin/env python3
"""
OpenFOAM MCP Server
一个用于读取和修改 OpenFOAM 配置文件的 MCP 服务器
"""

import os
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

# 导入解析器和编辑器
try:
    from .parser import OpenFOAMDict
    from .editor import modify_dict_value, modify_boundary_value
    from .thermal import ThermalConfig, ThermalEditor
except ImportError:
    from parser import OpenFOAMDict
    from editor import modify_dict_value, modify_boundary_value
    from thermal import ThermalConfig, ThermalEditor

# 创建 MCP 实例
mcp = FastMCP("OpenFOAM MCP Server")


def find_openfoam_case() -> Optional[Path]:
    """查找 OpenFOAM case 目录"""
    current = Path.cwd()

    while current != current.parent:
        if (current / "system").exists() and (current / "constant").exists():
            return current
        if (current / "0").exists():
            return current
        current = current.parent

    return None


def parse_dict_file(filepath: Path) -> Dict[str, Any]:
    """解析 OpenFOAM 字典文件"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        parser = OpenFOAMDict(content)
        return parser.parsed
    except Exception as e:
        return {"error": str(e)}


def parse_key_value_line(line: str) -> tuple:
    """解析键值对行"""
    # 移除注释
    if '//' in line:
        line = line[:line.index('//')]

    line = line.strip()
    if not line or line in ['{', '}']:
        return None, None

    # 查找分号
    if ';' not in line:
        return None, None

    line = line[:line.rindex(';')].strip()

    # 查找第一个空格后的值
    parts = line.split(None, 1)
    if len(parts) < 2:
        return parts[0] if parts else None, None

    return parts[0], parts[1].strip()


# ============== MCP 工具定义 ==============

@mcp.tool()
def get_case_info() -> str:
    """
    获取当前 OpenFOAM case 目录信息

    返回 case 目录路径和包含的主要文件列表
    """
    case_dir = find_openfoam_case()

    if not case_dir:
        return "未找到 OpenFOAM case 目录。请确保你在 case 目录或其子目录中运行。"

    result = f"OpenFOAM Case 目录: {case_dir}\n\n"
    result += "=== 目录结构 ===\n"

    for subdir in ["0", "constant", "system"]:
        subdir_path = case_dir / subdir
        if subdir_path.exists():
            result += f"\n{subdir}/\n"
            for item in sorted(subdir_path.iterdir()):
                if item.is_file():
                    result += f"  - {item.name}\n"
                elif item.is_dir():
                    result += f"  - {item.name}/\n"

    return result


@mcp.tool()
def read_dict_file(file_path: str) -> str:
    """
    读取 OpenFOAM 字典文件并返回解析后的内容

    Args:
        file_path: 文件路径，相对于 case 目录（如 "system/controlDict"）
                   或绝对路径

    返回:
        文件的解析内容（JSON 格式）
    """
    case_dir = find_openfoam_case()
    if case_dir and not os.path.isabs(file_path):
        filepath = case_dir / file_path
    else:
        filepath = Path(file_path)

    if not filepath.exists():
        return f"错误: 文件不存在: {filepath}"

    parsed = parse_dict_file(filepath)

    return json.dumps(parsed, indent=2, ensure_ascii=False)


@mcp.tool()
def read_file_content(file_path: str) -> str:
    """
    读取 OpenFOAM 文件的原始内容

    Args:
        file_path: 文件路径，相对于 case 目录或绝对路径

    返回:
        文件的原始文本内容
    """
    case_dir = find_openfoam_case()
    if case_dir and not os.path.isabs(file_path):
        filepath = case_dir / file_path
    else:
        filepath = Path(file_path)

    if not filepath.exists():
        return f"错误: 文件不存在: {filepath}"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        return f"错误: {str(e)}"


@mcp.tool()
def list_field_files() -> str:
    """
    列出 0/ 目录中的所有场文件

    返回:
        场文件列表及其基本信息
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    fields_dir = case_dir / "0"
    if not fields_dir.exists():
        return "0/ 目录不存在"

    result = "=== 0/ 目录中的场文件 ===\n\n"

    for item in sorted(fields_dir.iterdir()):
        if item.is_file():
            result += f"📄 {item.name}\n"
            # 尝试获取一些信息
            with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # 提取 dimensions
                if 'dimensions' in content:
                    for line in content.split('\n'):
                        if 'dimensions' in line and '[' in line:
                            result += f"  维度: {line.strip()}\n"
                            break
                # 提取内部场类型
                if 'internalField' in content:
                    for line in content.split('\n'):
                        if 'internalField' in line:
                            result += f"  内部场: {line.strip()}\n"
                            break
            result += "\n"

    return result


@mcp.tool()
def get_boundary_conditions(field_name: str) -> str:
    """
    获取指定场的边界条件

    Args:
        field_name: 场文件名（如 "U", "p", "T"）

    返回:
        边界条件的详细信息
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    field_file = case_dir / "0" / field_name
    if not field_file.exists():
        return f"错误: 场文件不存在: {field_name}"

    parsed = parse_dict_file(field_file)

    result = f"=== {field_name} 边界条件 ===\n\n"

    if "boundaryField" in parsed:
        for boundary_name, boundary_data in parsed["boundaryField"].items():
            result += f"📍 {boundary_name}\n"
            for key, value in boundary_data.items():
                result += f"  {key}: {value}\n"
            result += "\n"

    return result


@mcp.tool()
def modify_control_dict(
    application: Optional[str] = None,
    start_from: Optional[str] = None,
    delta_t: Optional[float] = None,
    end_time: Optional[float] = None,
    write_control: Optional[str] = None,
    write_interval: Optional[int] = None,
    purge_write: Optional[int] = None,
) -> str:
    """
    修改 controlDict 文件中的求解器控制参数

    Args:
        application: 求解器名称（如 simpleFoam, pimpleFoam）
        start_from: 从哪个时间步开始（如 "latestTime", "0"）
        delta_t: 时间步长
        end_time: 结束时间
        write_control: 写入控制（如 "timeStep", "runTime"）
        write_interval: 写入间隔
        purge_write: 保留的时间步数量

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    control_dict = case_dir / "system" / "controlDict"
    if not control_dict.exists():
        return "错误: controlDict 文件不存在"

    changes = []

    # 映射参数到文件中的键名
    param_map = {
        'application': 'application',
        'start_from': 'startFrom',
        'delta_t': 'deltaT',
        'end_time': 'endTime',
        'write_control': 'writeControl',
        'write_interval': 'writeInterval',
        'purge_write': 'purgeWrite',
    }

    params = {
        'application': application,
        'start_from': start_from,
        'delta_t': delta_t,
        'end_time': end_time,
        'write_control': write_control,
        'write_interval': write_interval,
        'purge_write': purge_write,
    }

    with open(control_dict, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified_lines = []

    for line in lines:
        new_line = line
        parsed_key, parsed_value = parse_key_value_line(line)

        if parsed_key:
            for param_name, file_key in param_map.items():
                if parsed_key == file_key and params[param_name] is not None:
                    indent = len(line) - len(line.lstrip())
                    new_value = params[param_name]
                    new_line = ' ' * indent + f"{file_key} {new_value};\n"
                    changes.append(f"{file_key} -> {new_value}")
                    break

        modified_lines.append(new_line)

    with open(control_dict, 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)

    if changes:
        return f"✅ 已修改 controlDict:\n" + "\n".join(f"  - {c}" for c in changes)
    else:
        return "⚠️ 没有修改任何参数"


@mcp.tool()
def modify_boundary_condition(
    field_name: str,
    boundary_name: str,
    condition_type: Optional[str] = None,
    value: Optional[str] = None,
) -> str:
    """
    修改场文件的边界条件

    Args:
        field_name: 场文件名（如 "U", "p", "T"）
        boundary_name: 边界名称（如 "inlet", "outlet", "walls"）
        condition_type: 边界条件类型（如 "fixedValue", "zeroGradient", "fixedFluxPressure"）
        value: 边界值（如 "uniform (0 0 0)", "uniform 0", "uniform 300"）

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    field_file = case_dir / "0" / field_name
    if not field_file.exists():
        return f"错误: 场文件不存在: {field_name}"

    # 使用新的编辑器函数
    success, modifications = modify_boundary_value(
        field_file, boundary_name, new_value=value, new_type=condition_type
    )

    if success:
        return f"✅ 已修改 {field_name} 的边界条件:\n" + "\n".join(f"  - {m}" for m in modifications)
    else:
        return f"⚠️ 没有修改任何边界条件（可能边界 '{boundary_name}' 不存在或参数无效）"


@mcp.tool()
def get_transport_properties() -> str:
    """
    读取并返回输运属性（transportProperties）文件内容

    返回:
        输运属性的解析内容
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    transport_file = case_dir / "constant" / "transportProperties"
    if not transport_file.exists():
        return "错误: transportProperties 文件不存在"

    parsed = parse_dict_file(transport_file)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


@mcp.tool()
def get_turbulence_properties() -> str:
    """
    读取并返回湍流属性（turbulenceProperties）文件内容

    返回:
        湍流属性的解析内容
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    turbulence_file = case_dir / "constant" / "turbulenceProperties"
    if not turbulence_file.exists():
        # 尝试 RASProperties 或 LESProperties
        ras_file = case_dir / "constant" / "RASProperties"
        les_file = case_dir / "constant" / "LESProperties"

        if ras_file.exists():
            parsed = parse_dict_file(ras_file)
            return f"RASProperties:\n" + json.dumps(parsed, indent=2, ensure_ascii=False)
        elif les_file.exists():
            parsed = parse_dict_file(les_file)
            return f"LESProperties:\n" + json.dumps(parsed, indent=2, ensure_ascii=False)
        else:
            return "错误: 未找到湍流属性文件"

    parsed = parse_dict_file(turbulence_file)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


@mcp.tool()
def get_fv_schemes() -> str:
    """
    读取并返回离散化方案（fvSchemes）文件内容

    返回:
        离散化方案的解析内容
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    fv_schemes = case_dir / "system" / "fvSchemes"
    if not fv_schemes.exists():
        return "错误: fvSchemes 文件不存在"

    parsed = parse_dict_file(fv_schemes)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


@mcp.tool()
def get_fv_solution() -> str:
    """
    读取并返回求解器设置（fvSolution）文件内容

    返回:
        求解器设置的解析内容
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    fv_solution = case_dir / "system" / "fvSolution"
    if not fv_solution.exists():
        return "错误: fvSolution 文件不存在"

    parsed = parse_dict_file(fv_solution)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


@mcp.tool()
def search_case_files(keyword: str) -> str:
    """
    在 case 目录的所有配置文件中搜索关键词

    Args:
        keyword: 要搜索的关键词

    返回:
        匹配的文件和行
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    results = []

    # 搜索的目录
    search_dirs = ["0", "constant", "system"]
    for subdir in search_dirs:
        dir_path = case_dir / subdir
        if not dir_path.exists():
            continue

        for item in dir_path.rglob("*"):
            if item.is_file():
                try:
                    with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if keyword.lower() in line.lower():
                                rel_path = item.relative_to(case_dir)
                                results.append(f"{rel_path}:{line_num}: {line.strip()}")
                except Exception:
                    continue

    if results:
        return "=== 搜索结果 ===\n\n" + "\n".join(results[:50])  # 限制结果数量
    else:
        return f"未找到包含 '{keyword}' 的内容"


# ============== 热/浮力求解器相关 MCP 工具 ==============

@mcp.tool()
def list_buoyancy_solvers() -> str:
    """
    列出所有可用的浮力求解器类型及其描述

    返回:
        可用的浮力求解器列表
    """
    templates = ThermalConfig.get_buoyancy_solver_templates()

    result = "=== 可用的浮力求解器 ===\n\n"

    for solver_name, config in templates.items():
        result += f"🔹 {solver_name}\n"
        result += f"   描述: {config['description']}\n"
        result += f"   求解器类型: {config['controlDict']['solver']}\n"
        result += f"   需要的场变量: {', '.join(config['requires'])}\n\n"

    return result


@mcp.tool()
def set_buoyancy_solver(solver_type: str) -> str:
    """
    设置浮力求解器（修改 controlDict 中的 application）

    Args:
        solver_type: 求解器类型（如 buoyantSimpleFoam, buoyantPimpleFoam,
                     buoyantBoussinesqSimpleFoam, buoyantBoussinesqPimpleFoam）

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.set_buoyancy_solver(solver_type)

    return message


@mcp.tool()
def add_temperature_field(temperature: float = 293.0) -> str:
    """
    创建温度场文件 (0/T)

    Args:
        temperature: 初始温度（单位：K）

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_temperature_field(temperature)

    return message


@mcp.tool()
def add_gravity_file(gravity_x: float = 0.0, gravity_y: float = 0.0,
                     gravity_z: float = -9.81) -> str:
    """
    创建重力文件 (constant/g) 用于浮力计算

    Args:
        gravity_x: X 方向重力加速度 (m/s²)
        gravity_y: Y 方向重力加速度 (m/s²)
        gravity_z: Z 方向重力加速度 (m/s²)

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_gravity_file([gravity_x, gravity_y, gravity_z])

    return message


@mcp.tool()
def add_thermophysical_properties() -> str:
    """
    创建热物理属性文件 (constant/thermophysicalProperties)

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_thermophysical_properties()

    return message


@mcp.tool()
def set_inlet_thermal_conditions(
    inlet_name: str,
    velocity_x: float,
    velocity_y: float,
    velocity_z: float,
    temperature: float,
    turbulence_intensity: float = 0.05
) -> str:
    """
    设置入口的热边界条件（速度和温度）

    Args:
        inlet_name: 入口边界名称
        velocity_x: X 方向速度 (m/s)
        velocity_y: Y 方向速度 (m/s)
        velocity_z: Z 方向速度 (m/s)
        temperature: 入口温度 (K)
        turbulence_intensity: 湍流强度 (0-1)

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.set_inlet_conditions(
        inlet_name,
        [velocity_x, velocity_y, velocity_z],
        temperature,
        turbulence_intensity
    )

    return message


@mcp.tool()
def set_wall_thermal_conditions(
    wall_name: str = "walls",
    temperature: Optional[float] = None,
    heat_flux: Optional[float] = None,
    heat_transfer_coeff: Optional[float] = None,
    external_temp: Optional[float] = None
) -> str:
    """
    设置墙体的热边界条件

    Args:
        wall_name: 墙体边界名称
        temperature: 固定温度 (K)
        heat_flux: 热通量 (W/m²)
        heat_transfer_coeff: 对流换热系数 (W/m²K)
        external_temp: 外部温度 (K)

    说明:
        - 如果指定 heat_flux，使用热通量边界条件
        - 如果指定 heat_transfer_coeff 和 external_temp，使用对流换热边界条件
        - 否则使用固定温度边界条件

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.set_wall_thermal_conditions(
        wall_name, temperature, heat_flux, heat_transfer_coeff, external_temp
    )

    return message


@mcp.tool()
def list_radiation_models() -> str:
    """
    列出所有可用的辐射模型及其描述

    返回:
        可用的辐射模型列表
    """
    templates = ThermalConfig.get_radiation_model_templates()

    result = "=== 可用的辐射模型 ===\n\n"

    for model_name, config in templates.items():
        result += f"🔹 {model_name}\n"
        result += f"   描述: {config['description']}\n\n"

    return result


@mcp.tool()
def add_radiation_model(model: str = "P1") -> str:
    """
    创建辐射模型配置文件 (constant/radiationProperties)

    Args:
        model: 辐射模型类型
               - none: 无辐射模型
               - P1: P1 辐射模型
               - viewFactor: 视角系数模型
               - surfaceToSurface: 面到面模型
               - DO: 离散坐标模型（最精确）

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_radiation_model(model)

    return message


@mcp.tool()
def add_age_of_air_field() -> str:
    """
    创建空气龄场文件 (0/age)

    空气龄是空气从进入室内空间起所经历的平均时间，
    用于评估通风效率和室内空气质量。

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_age_of_air_field()

    return message


@mcp.tool()
def add_heat_source_config(
    power: float = 100.0,
    volume: float = 1.0,
    source_type: str = "uniform"
) -> str:
    """
    创建内部热源配置文件

    Args:
        power: 热源功率 (W)
        volume: 热源体积 (m³)
        source_type: 热源类型
                     - uniform: 均匀热源
                     - mapped: 映射热源
                     - coded: 自定义代码热源

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_heat_source_config(power, volume, source_type)

    return message


@mcp.tool()
def add_pmv_ppd_comfort_metrics(
    metabolic_rate: float = 1.0,
    clothing_insulation: float = 0.5,
    air_velocity: float = 0.1,
    radiant_temp: float = 293.0
) -> str:
    """
    在 controlDict 中添加 PMV-PPD 舒适度指标计算函数

    Args:
        metabolic_rate: 代谢率
                        0.8-1.0: 静坐
                        1.2-1.6: 轻度活动
                        1.6-2.0: 中度活动
        clothing_insulation: 服装热阻
                             0.3-0.5: 夏季薄装
                             0.5-1.0: 春秋装
                             1.0-1.5: 冬季厚装
        air_velocity: 空气流速 (m/s)
                      空调房间: 0.1-0.2
                      自然通风: 0.2-0.5
        radiant_temp: 平均辐射温度 (K)

    PMV (Predicted Mean Vote): 预测平均投票
    PPD (Predicted Percentage of Dissatisfied): 预测不满意百分比

    舒适度标准 (ISO 7730):
    - PMV: -0.5 ~ +0.5
    - PPD: < 10%

    返回:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    success, message = editor.add_pmv_ppd_function(
        metabolic_rate, clothing_insulation, air_velocity, radiant_temp
    )

    return message


@mcp.tool()
def get_comfort_criteria_info() -> str:
    """
    获取热舒适度标准说明

    基于 ISO 7730 和 ASHRAE Standard 55

    返回:
        舒适度标准说明文本
    """
    return ThermalConfig.get_comfort_criteria_template()


@mcp.tool()
def configure_indoor_thermal_environment(
    solver_type: str = "buoyantBoussinesqSimpleFoam",
    ambient_temp: float = 293.0,
    inlet_velocity_x: float = 1.0,
    inlet_velocity_y: float = 0.0,
    inlet_velocity_z: float = 0.0,
    inlet_temp: float = 293.0,
    wall_temp: float = 293.0,
    heat_transfer_coeff: float = 8.0,
    enable_buoyancy: bool = True,
    radiation_model: str = "none",
    enable_age_of_air: bool = False,
    enable_heat_source: bool = False,
    heat_source_power: float = 100.0,
    enable_pmv_ppd: bool = False,
    metabolic_rate: float = 1.0,
    clothing_insulation: float = 0.5
) -> str:
    """
    一键配置室内热环境（综合配置）

    这个工具会自动设置浮力求解器、温度场、送回风口、墙体传热、
    辐射模型、空气龄、内部热源和 PMV-PPD 指标等所有热学相关配置。

    Args:
        solver_type: 浮力求解器类型
        ambient_temp: 环境温度 (K)
        inlet_velocity_x/y/z: 入口速度 (m/s)
        inlet_temp: 入口温度 (K)
        wall_temp: 墙体温度 (K)
        heat_transfer_coeff: 墙体对流换热系数 (W/m²K)
        enable_buoyancy: 是否启用浮力（会自动设置重力文件）
        radiation_model: 辐射模型
        enable_age_of_air: 是否计算空气龄
        enable_heat_source: 是否启用内部热源
        heat_source_power: 热源功率 (W)
        enable_pmv_ppd: 是否计算 PMV-PPD
        metabolic_rate: 代谢率
        clothing_insulation: 服装热阻

    返回:
        操作结果汇总
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "❌ 未找到 OpenFOAM case 目录"

    editor = ThermalEditor(case_dir)
    results = []

    # 1. 设置浮力求解器
    success, msg = editor.set_buoyancy_solver(solver_type)
    results.append(msg)

    # 2. 添加温度场
    success, msg = editor.add_temperature_field(ambient_temp)
    results.append(msg)

    # 3. 添加重力文件（如果启用浮力）
    if enable_buoyancy:
        success, msg = editor.add_gravity_file()
        results.append(msg)

    # 4. 设置入口边界条件
    success, msg = editor.set_inlet_conditions(
        "inlet", [inlet_velocity_x, inlet_velocity_y, inlet_velocity_z],
        inlet_temp
    )
    results.append(msg)

    # 5. 设置墙体热边界条件
    success, msg = editor.set_wall_thermal_conditions(
        "walls", temperature=wall_temp,
        heat_transfer_coeff=heat_transfer_coeff
    )
    results.append(msg)

    # 6. 添加辐射模型
    if radiation_model != "none":
        success, msg = editor.add_radiation_model(radiation_model)
        results.append(msg)

    # 7. 添加空气龄
    if enable_age_of_air:
        success, msg = editor.add_age_of_air_field()
        results.append(msg)

    # 8. 添加热源
    if enable_heat_source:
        success, msg = editor.add_heat_source_config(heat_source_power)
        results.append(msg)

    # 9. 添加 PMV-PPD
    if enable_pmv_ppd:
        success, msg = editor.add_pmv_ppd_function(
            metabolic_rate, clothing_insulation
        )
        results.append(msg)

    return "=== 室内热环境配置完成 ===\n\n" + "\n".join(results)


def main():
    """启动 MCP 服务器"""
    # 尝试导入风雨模拟扩展
    try:
        parent_dir = Path(__file__).parent.parent
        wind_rain_path = parent_dir / "winddrivenrain_tools.py"
        if wind_rain_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("winddrivenrain", wind_rain_path)
            wind_rain = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(wind_rain)
            # 工具通过 @mcp.tool() 装饰器自动注册
    except Exception as e:
        # 如果加载失败，继续运行基础服务器
        pass

    mcp.run()


if __name__ == "__main__":
    main()
