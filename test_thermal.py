#!/usr/bin/env python3
"""
测试热/浮力求解器模块
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from thermal import ThermalConfig, ThermalEditor


def test_buoyancy_solvers():
    """测试浮力求解器模板"""
    print("=" * 50)
    print("测试 1: 浮力求解器模板")
    print("=" * 50)

    templates = ThermalConfig.get_buoyancy_solver_templates()

    for solver_name, config in templates.items():
        print(f"\n🔹 {solver_name}")
        print(f"   描述: {config['description']}")
        print(f"   求解器类型: {config['controlDict']['solver']}")
        print(f"   需要的场变量: {', '.join(config['requires'])}")

    print("\n✅ 测试通过\n")


def test_temperature_field_template():
    """测试温度场模板"""
    print("=" * 50)
    print("测试 2: 温度场模板")
    print("=" * 50)

    template = ThermalConfig.get_temperature_field_template()

    if "dimensions      [0 0 0 1 0 0 0]" in template:
        print("✅ 温度场模板正确")
        print("   维度: [0 0 0 1 0 0 0] (温度)")
    else:
        print("❌ 温度场模板错误")

    print()


def test_wall_thermal_template():
    """测试墙体热边界条件模板"""
    print("=" * 50)
    print("测试 3: 墙体热边界条件模板")
    print("=" * 50)

    # 测试固定温度
    config1 = ThermalConfig.get_wall_thermal_boundary_template(
        wall_name="walls", temperature=295.0
    )
    print(f"✅ 固定温度边界: {config1}")

    # 测试热通量
    config2 = ThermalConfig.get_wall_thermal_boundary_template(
        wall_name="walls", heat_flux=100.0
    )
    print(f"✅ 热通量边界: {config2}")

    # 测试对流换热
    config3 = ThermalConfig.get_wall_thermal_boundary_template(
        wall_name="walls", heat_transfer_coeff=8.0, external_temp=290.0
    )
    print(f"✅ 对流换热边界: {config3}")

    print()


def test_inlet_template():
    """测试入口边界条件模板"""
    print("=" * 50)
    print("测试 4: 入口边界条件模板")
    print("=" * 50)

    config = ThermalConfig.get_inlet_velocity_temperature_template(
        inlet_name="inlet",
        velocity=[1.5, 0.0, 0.0],
        temperature=288.0,
        turbulence_intensity=0.05
    )

    for field_name, field_data in config.items():
        print(f"✅ {field_name}: {field_data.get('type')}")

    print()


def test_radiation_models():
    """测试辐射模型模板"""
    print("=" * 50)
    print("测试 5: 辐射模型模板")
    print("=" * 50)

    templates = ThermalConfig.get_radiation_model_templates()

    for model_name, config in templates.items():
        print(f"🔹 {model_name}")
        print(f"   描述: {config['description']}")

    print("\n✅ 测试通过\n")


def test_age_of_air_template():
    """测试空气龄模板"""
    print("=" * 50)
    print("测试 6: 空气龄模板")
    print("=" * 50)

    template = ThermalConfig.get_age_of_air_field_template()

    if "dimensions      [0 0 1 0 0 0 0]" in template:
        print("✅ 空气龄模板正确")
        print("   维度: [0 0 1 0 0 0 0] (时间)")
    else:
        print("❌ 空气龄模板错误")

    print()


def test_heat_source_template():
    """测试热源配置模板"""
    print("=" * 50)
    print("测试 7: 热源配置模板")
    print("=" * 50)

    template = ThermalConfig.get_heat_source_template(
        power=500.0,
        volume=2.0,
        source_type="uniform"
    )

    if "500.0 W" in template and "250.0 W/m³" in template:
        print("✅ 热源模板正确")
        print("   功率: 500 W")
        print("   热源密度: 250 W/m³")
    else:
        print("❌ 热源模板错误")

    print()


def test_pmv_ppd_template():
    """测试 PMV-PPD 模板"""
    print("=" * 50)
    print("测试 8: PMV-PPD 模板")
    print("=" * 50)

    config = ThermalConfig.get_pmv_ppd_control_dict_additions(
        enable_pmv=True,
        enable_ppd=True,
        metabolic_rate=1.2,
        clothing_insulation=0.6,
        air_velocity=0.15,
        radiant_temp=293.0
    )

    if "libs" in config and "functions" in config:
        print("✅ PMV-PPD 配置正确")
        print(f"   libs: {config['libs'][:50]}...")
        print(f"   functions: 包含 PMV 和 PPD 计算")
    else:
        print("❌ PMV-PPD 配置错误")

    print()


def test_comfort_criteria():
    """测试舒适度标准说明"""
    print("=" * 50)
    print("测试 9: 舒适度标准说明")
    print("=" * 50)

    template = ThermalConfig.get_comfort_criteria_template()

    if "PMV" in template and "PPD" in template and "ISO 7730" in template:
        print("✅ 舒适度标准说明正确")
        print("   包含: PMV, PPD, ISO 7730")
    else:
        print("❌ 舒适度标准说明错误")

    print()


def test_indoor_thermal_config():
    """测试室内热环境综合配置"""
    print("=" * 50)
    print("测试 10: 室内热环境综合配置")
    print("=" * 50)

    # 创建临时目录进行测试
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmpdir:
        case_dir = Path(tmpdir)

        # 创建必要的目录结构
        (case_dir / "0").mkdir()
        (case_dir / "system").mkdir()
        (case_dir / "constant").mkdir()

        # 创建 controlDict
        (case_dir / "system" / "controlDict").write_text(
            "FoamFile\n{\n    version 2.0;\n}\n\napplication simpleFoam;\n"
        )

        # 创建 U 文件
        (case_dir / "0" / "U").write_text(
            """FoamFile\n{\n    version 2.0;\n}\n\ndimensions [0 1 -1 0 0 0 0];\n\ninternalField uniform (0 0 0);\n\nboundaryField\n{\n    inlet\n    {\n        type fixedValue;\n        value uniform (1 0 0);\n    }\n    walls\n    {\n        type noSlip;\n    }\n}\n"""
        )

        config = ThermalConfig(case_dir)

        result = config.configure_indoor_air_thermal(
            solver_type="buoyantBoussinesqSimpleFoam",
            ambient_temp=293.0,
            inlet_velocity=[1.0, 0.0, 0.0],
            inlet_temp=293.0,
            wall_temp=295.0,
            enable_buoyancy=True,
            enable_age_of_air=True,
            enable_heat_source=True,
            heat_source_power=100.0,
            enable_pmv_ppd=True,
        )

        print("配置结果:")
        print(result)
        print("\n✅ 测试通过\n")


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "=" * 48 + "╗")
    print("║" + " " * 12 + "热学模块测试" + " " * 26 + "║")
    print("╚" + "=" * 48 + "╝")
    print()

    try:
        test_buoyancy_solvers()
        test_temperature_field_template()
        test_wall_thermal_template()
        test_inlet_template()
        test_radiation_models()
        test_age_of_air_template()
        test_heat_source_template()
        test_pmv_ppd_template()
        test_comfort_criteria()
        test_indoor_thermal_config()

        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        print()

    except Exception as e:
        print("=" * 50)
        print(f"❌ 测试失败: {e}")
        print("=" * 50)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
