#!/usr/bin/env python3
"""
OpenFOAM MCP Server - Wind Driven Rain Extensions
添加风雨模拟功能的扩展工具
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

# 导入基础服务器
from server import find_openfoam_case, parse_dict_file, mcp


# ============== Wind Driven Rain 工具 ==============

@mcp.tool()
def setup_winddrivenrain(
    rain_diameter: float = 0.001,
    rain_velocity: float = 8.0,
    rain_mass_flow_rate: float = 0.001,
    particle_density: float = 1000.0,
    cloud_name: str = "rainCloud"
) -> str:
    """
    为 OpenFOAM case 设置风雨模拟

    Args:
        rain_diameter: 雨滴直径 (米)
        rain_velocity: 雨滴初始速度 (米/秒)
        rain_mass_flow_rate: 雨滴质量流率 (kg/s)
        particle_density: 雨滴密度 (kg/m³)
        cloud_name: 云名称

    Returns:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    results = []

    # 1. 创建 cloudProperties 文件
    results.append(create_cloud_properties(case_dir, cloud_name))

    # 2. 修改 controlDict 添加云模拟参数
    results.append(modify_control_for_rain(case_dir, cloud_name))

    # 3. 修改 fvSchemes 添加粒子输运方案
    results.append(add_particle_schemes(case_dir, cloud_name))

    # 4. 修改 fvSolution 添加云求解器设置
    results.append(add_cloud_solver(case_dir, cloud_name))

    # 5. 创建 kinematicCloudProperties 文件
    results.append(create_kinematic_cloud_properties(
        case_dir, cloud_name, rain_diameter, rain_velocity,
        rain_mass_flow_rate, particle_density
    ))

    return "\n\n".join(results)


def create_cloud_properties(case_dir: Path, cloud_name: str) -> str:
    """创建 cloudProperties 文件"""
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  10                                     |
|   \\\\  /    A nd           | Website:  www.openfoam.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      cloudProperties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solution1
{{
    solver          {cloud_name};
}}

// ************************************************************************* //
"""

    file_path = case_dir / "constant" / "cloudProperties"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ 已创建 {file_path}"
    except Exception as e:
        return f"❌ 创建 cloudProperties 失败: {e}"


def modify_control_for_rain(case_dir: Path, cloud_name: str) -> str:
    """修改 controlDict 添加云模拟参数"""
    control_dict = case_dir / "system" / "controlDict"

    if not control_dict.exists():
        return "⚠️ controlDict 不存在"

    with open(control_dict, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经有 clouds 参数
    if 'clouds' not in content:
        # 在文件末尾前添加 clouds 参数
        lines = content.split('\n')
        new_lines = []
        inserted = False

        for i, line in enumerate(lines):
            if 'runTimeModifiable' in line and ';' in line and not inserted:
                new_lines.append(line)
                new_lines.append("")
                new_lines.append("// 云模拟设置")
                new_lines.append("clouds")
                new_lines.append("{")
                new_lines.append(f"    {cloud_name}")
                new_lines.append("}")
                inserted = True
            else:
                new_lines.append(line)

        if not inserted:
            # 如果没有找到 runTimeModifiable，在最后添加
            lines.append("")
            lines.append("clouds")
            lines.append("{")
            lines.append(f"    {cloud_name}")
            lines.append("}")
            new_lines = lines

        with open(control_dict, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

        return f"✅ 已在 controlDict 中添加 clouds 设置"
    else:
        return "ℹ️ controlDict 中已有 clouds 设置"


def add_particle_schemes(case_dir: Path, cloud_name: str) -> str:
    """修改 fvSchemes 添加粒子输运方案"""
    fv_schemes = case_dir / "system" / "fvSchemes"

    if not fv_schemes.exists():
        return "⚠️ fvSchemes 不存在"

    with open(fv_schemes, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经有 divSchemes 和粒子输运
    if f'div(phid,{cloud_name})' in content:
        return "ℹ️ fvSchemes 中已有粒子输运方案"

    # 在 divSchemes 中添加粒子输运
    lines = content.split('\n')
    new_lines = []
    inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if 'divSchemes' in line and '{' in line and not inserted:
            # 在 divSchemes 块后添加粒子输运
            if i + 1 < len(lines) and 'default' in lines[i + 1]:
                new_lines.append(lines[i + 1])
                new_lines.append(f"    div(phid,{cloud_name})  Gauss upwind;")
                new_lines.insert(-1, '')  # 标记跳过下一行
                inserted = True

    if inserted:
        # 移除标记
        new_lines = [l for l in new_lines if l != '']
    else:
        # 没有成功插入，直接添加到 divSchemes 块末尾
        for i, line in enumerate(lines):
            if line.strip() == '}' and i > 0 and 'divSchemes' in '\n'.join(lines[max(0,i-20):i]):
                new_lines.insert(i, f"    div(phid,{cloud_name})  Gauss upwind;")
                break

    with open(fv_schemes, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    return f"✅ 已在 fvSchemes 中添加粒子输运方案"


def add_cloud_solver(case_dir: Path, cloud_name: str) -> str:
    """修改 fvSolution 添加云求解器设置"""
    fv_solution = case_dir / "system" / "fvSolution"

    if not fv_solution.exists():
        return "⚠️ fvSolution 不存在"

    with open(fv_solution, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经有 clouds 设置
    if 'clouds' in content and cloud_name in content:
        return "ℹ️ fvSolution 中已有云求解器设置"

    # 在文件末尾添加 clouds 设置
    if 'clouds' not in content:
        content += f"""

// 云求解器设置
clouds
{{
    {cloud_name}
    {{
        U               upwind;

        subCycles       3;
    }}
}}
"""

        with open(fv_solution, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✅ 已在 fvSolution 中添加云求解器设置"
    else:
        # 找到现有 clouds 块并添加新的云
        lines = content.split('\n')
        new_lines = []
        in_clouds = False
        inserted = False

        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'clouds' in line and '{' in line:
                in_clouds = True
            elif in_clouds and '}' in line and not inserted:
                # 在闭括号前插入新云
                indent = len(line) - len(line.lstrip())
                new_lines.insert(-1, ' ' * (indent + 4) + f"{cloud_name}")
                new_lines.insert(-1, ' ' * (indent + 4) + "{")
                new_lines.insert(-1, ' ' * (indent + 8) + "U               upwind;")
                new_lines.insert(-1, ' ' * (indent + 8) + "")
                new_lines.insert(-1, ' ' * (indent + 8) + "subCycles       3;")
                new_lines.insert(-1, ' ' * (indent + 4) + "}")
                new_lines.insert(-1, '')
                inserted = True

        if inserted:
            with open(fv_solution, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            return f"✅ 已在 fvSolution 中添加 {cloud_name} 求解器设置"
        else:
            return "⚠️ 未能添加云求解器设置"


def create_kinematic_cloud_properties(
    case_dir: Path,
    cloud_name: str,
    rain_diameter: float,
    rain_velocity: float,
    rain_mass_flow_rate: float,
    particle_density: float
) -> str:
    """创建 kinematicCloudProperties 文件"""
    content = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  10                                     |
|   \\\\  /    A nd           | Website:  www.openfoam.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      {cloud_name}Properties;
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solution
{{
    active          true;
    transient       yes;
    coupled         true;
    cellValue       yes;
    interpolationSchemes
    {{
        U               cellPoint;
    }}

    sourceTerms
    {{
        schemes
        {{
            U               semiImplicit 1;
        }}
    }}

    integrationSchemes
    {{
        U               Euler;
    }}
}}

// 粒子模型定义
subModels
{{
    // 粒子运动
    particleForces
    {{
        gravity
        {{
            g               (0 -9.81 0);
        }}
        sphereDrag;
    }}

    // 粒子注入
    injectionModels
    {{
        coneInjection
        {{
            massTotal        {rain_mass_flow_rate};
            SOI              0;
            duration         1e6;

            position         (0 0 0);
            direction        (1 0 0);
            parcelBasisType  mass;
            nParticle       1000;

            parcelsPerSecond 1000;
            volumeFlowRate   {rain_mass_flow_rate / particle_density};
            Umag             {rain_velocity};

            sizeDistribution
            {{
                type    fixed;
                d       {rain_diameter};
            }}
        }}
    }}

    // 粒子直径模型
    surfaceFilmModel none;

    // 粒子-壁面交互
    dispersionModel  none;
    patchInteractionModel standardWallInteraction;
    stochasticCollisionModel none;

    standardWallInteractionCoeffs
    {{
        type            escape;
        e                0;
        mu               0;
    }}

    // 粒子属性
    particleTracksFile "particleTracks";

    // 云属性
    cloudFunctions
    {{
        voidFraction
        {{
            type            voidFraction;
        }}
    }}
}}

// 粒子常量
constantProperties
{{
    rho0             {particle_density};
    minParcelMass    1e-10;
}}

initialProperties
{{
    U               uniform ({rain_velocity} 0 0);
}}

// 粒子相属性
phases
{{
    air
    {{
        rho             1.2;
        mu              1.8e-05;
    }}
}}

// ************************************************************************* //
"""

    file_path = case_dir / "constant" / f"{cloud_name}Properties"
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ 已创建 {file_path}"
    except Exception as e:
        return f"❌ 创建 {cloud_name}Properties 失败: {e}"


@mcp.tool()
def create_boundary_injection(
    cloud_name: str = "rainCloud",
    patch_name: str = "inlet",
    injection_height: float = 10.0,
    rain_velocity: float = 8.0,
    rain_diameter: float = 0.001,
    mass_flow_rate: float = 0.001
) -> str:
    """
    在指定边界创建雨滴注入模型

    Args:
        cloud_name: 云名称
        patch_name: 边界名称
        injection_height: 注入高度
        rain_velocity: 雨滴速度
        rain_diameter: 雨滴直径
        mass_flow_rate: 质量流率

    Returns:
        操作结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    cloud_props_file = case_dir / "constant" / f"{cloud_name}Properties"

    if not cloud_props_file.exists():
        return f"⚠️ {cloud_name}Properties 不存在，请先运行 setup_winddrivenrain"

    with open(cloud_props_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换 injectionModels 部分
    new_injection = f"""    injectionModels
    {{
        surfaceInjection
        {{
            massTotal        {mass_flow_rate};
            SOI              0;
            duration         1e6;

            patchName        {patch_name};

            parcelBasisType  mass;
            nParticle        1000;

            parcelsPerSecond 1000;
            Umag             {rain_velocity};

            sizeDistribution
            {{
                type    fixed;
                d       {rain_diameter};
            }}
        }}
    }}"""

    # 简单替换（实际应用中需要更精确的解析）
    if 'coneInjection' in content or 'surfaceInjection' in content:
        # 使用正则表达式替换 injectionModels 块
        import re
        pattern = r'injectionModels\s*\{[^}]*\}'
        content = re.sub(pattern, new_injection, content, flags=re.DOTALL)

        with open(cloud_props_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"✅ 已修改 {cloud_name}Properties，使用边界 {patch_name} 进行注入"
    else:
        return "⚠️ 未找到 injectionModels 块"


@mcp.tool()
def get_cloud_info(cloud_name: str = "rainCloud") -> str:
    """
    获取云模拟配置信息

    Args:
        cloud_name: 云名称

    Returns:
        云配置信息
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    cloud_props_file = case_dir / "constant" / f"{cloud_name}Properties"

    if not cloud_props_file.exists():
        return f"⚠️ {cloud_name}Properties 不存在"

    parsed = parse_dict_file(cloud_props_file)

    result = f"=== {cloud_name} 配置信息 ===\n\n"

    if "subModels" in parsed:
        result += "📦 子模型:\n"
        for key, value in parsed["subModels"].items():
            result += f"  - {key}\n"

    if "injectionModels" in parsed.get("subModels", {}):
        result += "\n💉 注入模型:\n"
        inj_models = parsed["subModels"]["injectionModels"]
        for key, value in inj_models.items():
            if isinstance(value, dict):
                result += f"  - {key}\n"
                for k, v in value.items():
                    result += f"    {k}: {v}\n"

    if "particleForces" in parsed.get("subModels", {}):
        result += "\n⚙️ 粒子力模型:\n"
        forces = parsed["subModels"]["particleForces"]
        for key in forces.keys():
            result += f"  - {key}\n"

    return result


@mcp.tool()
def validate_winddrivenrain_setup(cloud_name: str = "rainCloud") -> str:
    """
    验证风雨模拟设置

    Args:
        cloud_name: 云名称

    Returns:
        验证结果
    """
    case_dir = find_openfoam_case()
    if not case_dir:
        return "未找到 OpenFOAM case 目录"

    results = []
    checks = {
        "cloudProperties": case_dir / "constant" / "cloudProperties",
        f"{cloud_name}Properties": case_dir / "constant" / f"{cloud_name}Properties",
        "controlDict": case_dir / "system" / "controlDict",
        "fvSchemes": case_dir / "system" / "fvSchemes",
        "fvSolution": case_dir / "system" / "fvSolution",
    }

    results.append("=== 风雨模拟设置验证 ===\n")

    for name, path in checks.items():
        if path.exists():
            results.append(f"✅ {name} 存在")
        else:
            results.append(f"❌ {name} 不存在")

    # 检查 controlDict 中的 clouds 参数
    control_dict = checks["controlDict"]
    if control_dict.exists():
        with open(control_dict, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'clouds' in content and cloud_name in content:
            results.append(f"✅ controlDict 包含 clouds.{cloud_name}")
        else:
            results.append(f"⚠️ controlDict 缺少 clouds.{cloud_name}")

    # 检查 fvSchemes 中的粒子输运
    fv_schemes = checks["fvSchemes"]
    if fv_schemes.exists():
        with open(fv_schemes, 'r', encoding='utf-8') as f:
            content = f.read()
        if f'div(phid,{cloud_name})' in content:
            results.append(f"✅ fvSchemes 包含 div(phid,{cloud_name})")
        else:
            results.append(f"⚠️ fvSchemes 缺少 div(phid,{cloud_name})")

    # 检查 fvSolution 中的云求解器
    fv_solution = checks["fvSolution"]
    if fv_solution.exists():
        with open(fv_solution, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'clouds' in content and cloud_name in content:
            results.append(f"✅ fvSolution 包含 clouds.{cloud_name}")
        else:
            results.append(f"⚠️ fvSolution 缺少 clouds.{cloud_name}")

    return "\n".join(results)


# 导出函数供主服务器使用
__all__ = [
    'setup_winddrivenrain',
    'create_boundary_injection',
    'get_cloud_info',
    'validate_winddrivenrain_setup'
]
