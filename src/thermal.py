#!/usr/bin/env python3
"""
OpenFOAM 热学/浮力求解模块
支持浮力求解器、温度求解器、墙体传热、送回风口设置、辐射模型、
空气龄、内部热源、PMV-PPD 指标等功能
兼容 OpenFOAM v8
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import re


class ThermalConfig:
    """热学配置管理类 - 用于热/浮力相关求解器的配置"""

    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.system_dir = case_dir / "system"
        self.constant_dir = case_dir / "constant"
        self.zero_dir = case_dir / "0"

    # ==================== 浮力求解器相关 ====================

    @staticmethod
    def get_buoyancy_solver_templates() -> Dict[str, Dict]:
        """
        获取浮力求解器配置模板

        返回:
            包含不同浮力求解器类型的模板字典
        """
        return {
            "buoyantSimpleFoam": {
                "description": "稳态浮力驱动流动求解器（Boussinesq近似）",
                "controlDict": {
                    "application": "buoyantSimpleFoam",
                    "solver": "steady-state",
                },
                "fvSchemes": {
                    "ddtSchemes": "steadyState",
                },
                "requires": ["T", "p_rgh", "U", "k", "epsilon", "omega"]
            },
            "buoyantPimpleFoam": {
                "description": "瞬态浮力驱动流动求解器（Boussinesq近似）",
                "controlDict": {
                    "application": "buoyantPimpleFoam",
                    "solver": "transient",
                },
                "fvSchemes": {
                    "ddtSchemes": {
                        "default": "Euler"
                    },
                },
                "requires": ["T", "p_rgh", "U", "k", "epsilon", "omega"]
            },
            "buoyantBoussinesqSimpleFoam": {
                "description": "稳态 Boussinesq 浮力驱动流动",
                "controlDict": {
                    "application": "buoyantBoussinesqSimpleFoam",
                    "solver": "steady-state",
                },
                "fvSchemes": {
                    "ddtSchemes": "steadyState",
                },
                "requires": ["T", "p", "U", "k", "epsilon", "omega"]
            },
            "buoyantBoussinesqPimpleFoam": {
                "description": "瞬态 Boussinesq 浮力驱动流动",
                "controlDict": {
                    "application": "buoyantBoussinesqPimpleFoam",
                    "solver": "transient",
                },
                "fvSchemes": {
                    "ddtSchemes": {
                        "default": "Euler"
                    },
                },
                "requires": ["T", "p", "U", "k", "epsilon", "omega"]
            },
        }

    @staticmethod
    def get_buoyancy_properties_template() -> str:
        """
        获取浮力属性文件模板 (constant/thermophysicalProperties)

        返回:
            thermophysicalProperties 文件内容
        """
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  8                                     |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      thermophysicalProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       28.96;
    }

    thermodynamics
    {
        Cp              1007;
        Hf              0;
    }

    transport
    {
        mu              1.81e-05;
        Pr              0.7;
    }
}

// ************************************************************************* //
"""

    @staticmethod
    def get_gravity_template() -> str:
        """
        获取重力设置模板 (constant/g)

        返回:
            g 文件内容
        """
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  8                                     |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       uniformDimensionedVectorField;
    location    "constant";
    object      g;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -2 0 0 0 0];
value           (0 0 -9.81);

// ************************************************************************* //
"""

    @staticmethod
    def get_t_rgh_field_template() -> str:
        """
        获取 p_rgh 场文件模板 (0/p_rgh)

        返回:
            p_rgh 场文件内容
        """
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  8                                     |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p_rgh;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    // 修改边界条件以匹配您的几何
    inlet
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }

    outlet
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }

    walls
    {
        type            fixedFluxPressure;
        value           uniform 0;
    }
}

// ************************************************************************* //
"""

    # ==================== 温度求解器相关 ====================

    @staticmethod
    def get_temperature_field_template() -> str:
        """
        获取温度场文件模板 (0/T)

        返回:
            T 场文件内容
        """
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  8                                     |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 0 1 0 0 0];

internalField   uniform 293;  // 20°C

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 293;
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""

    # ==================== 墙体传热相关 ====================

    @staticmethod
    def get_wall_thermal_boundary_template(
        wall_name: str = "walls",
        temperature: float = 293.0,
        heat_flux: Optional[float] = None,
        heat_transfer_coeff: Optional[float] = None,
        external_temp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        获取墙体热边界条件配置

        Args:
            wall_name: 墙体边界名称
            temperature: 墙体温度（K）
            heat_flux: 热通量（W/m²），如果设置则优先使用
            heat_transfer_coeff: 对流换热系数（W/m²K）
            external_temp: 外部温度（K）

        Returns:
            边界条件字典
        """
        if heat_flux is not None:
            return {
                "type": "externalWallHeatFlux",
                "mode": "flux",
                "q": f"uniform {heat_flux}",
            }
        elif heat_transfer_coeff is not None and external_temp is not None:
            return {
                "type": "externalWallHeatFlux",
                "mode": "coefficient",
                "h": f"uniform {heat_transfer_coeff}",
                "Ta": f"uniform {external_temp}",
            }
        else:
            return {
                "type": "fixedValue",
                "value": f"uniform {temperature}",
            }

    # ==================== 送回风口设置 ====================

    @staticmethod
    def get_inlet_velocity_temperature_template(
        inlet_name: str = "inlet",
        velocity: List[float] = [1.0, 0.0, 0.0],
        temperature: float = 293.0,
        turbulence_intensity: float = 0.05
    ) -> Dict[str, Dict[str, str]]:
        """
        获取送风口（入口）速度和温度边界条件模板

        Args:
            inlet_name: 入口边界名称
            velocity: 速度向量 (vx, vy, vz) m/s
            temperature: 温度 K
            turbulence_intensity: 湍流强度

        Returns:
            包含 U、T、k、epsilon/omega 边界条件的字典
        """
        return {
            "U": {
                "type": "fixedValue",
                "value": f"uniform ({velocity[0]} {velocity[1]} {velocity[2]})",
            },
            "T": {
                "type": "fixedValue",
                "value": f"uniform {temperature}",
            },
            "k": {
                "type": "fixedValue",
                "value": f"uniform {1.5 * (sum(v**2 for v in velocity) ** 0.5 * turbulence_intensity) ** 2}",
            },
            "epsilon": {
                "type": "fixedValue",
                "value": f"uniform {0.09 * (1.5 * (sum(v**2 for v in velocity) ** 0.5 * turbulence_intensity) ** 3) / (0.07 * 1.0)}",
            },
            "omega": {
                "type": "fixedValue",
                "value": f"uniform {(1.5 * (sum(v**2 for v in velocity) ** 0.5 * turbulence_intensity) ** 2) / (0.09 * 1.0)}",
            }
        }

    @staticmethod
    def get_outlet_template(
        outlet_name: str = "outlet",
        pressure: float = 0.0
    ) -> Dict[str, Dict[str, str]]:
        """
        获取回风口（出口）边界条件模板

        Args:
            outlet_name: 出口边界名称
            pressure: 压力值 Pa

        Returns:
            包含各场变量的边界条件
        """
        return {
            "p_rgh": {
                "type": "fixedValue",
                "value": f"uniform {pressure}",
            },
            "p": {
                "type": "fixedValue",
                "value": f"uniform {pressure}",
            },
            "U": {
                "type": "inletOutlet",
                "inletValue": "uniform (0 0 0)",
                "value": "uniform (0 0 0)",
            },
            "T": {
                "type": "inletOutlet",
                "inletValue": "uniform 293",
                "value": "uniform 293",
            },
            "k": {
                "type": "inletOutlet",
                "inletValue": "uniform 0.01",
                "value": "uniform 0.01",
            },
            "epsilon": {
                "type": "inletOutlet",
                "inletValue": "uniform 0.001",
                "value": "uniform 0.001",
            },
        }

    # ==================== 辐射模型相关 ====================

    @staticmethod
    def get_radiation_model_templates() -> Dict[str, Dict]:
        """
        获取辐射模型模板

        Returns:
            包含不同辐射模型的配置字典
        """
        return {
            "none": {
                "description": "无辐射模型",
                "radiationProperties": """radiation       off;
""",
            },
            "P1": {
                "description": "P1 辐射模型（适用于光学厚介质）",
                "radiationProperties": """radiationModel  P1;
absorptionEmissionModel constantAbsorptionEmission;
scatterModel     none;

constantAbsorptionEmissionCoeffs
{
    absorptionCoeff    uniform 0;
    emissionCoeff      uniform 0;
    E                  uniform 0;
}

// ************************************************************************* //
""",
            },
            "viewFactor": {
                "description": "视角系数辐射模型（适用于封闭空间）",
                "radiationProperties": """radiationModel  viewFactor;
absorptionEmissionModel greyMeanAbsorptionEmission;
scatterModel     none;

viewFactorCoeffs
{
    nFacesInCoarsestMesh   10;
    maxProcFaces           1000;
    useCachedAgglomeration true;
}

// ************************************************************************* //
""",
            },
            "surfaceToSurface": {
                "description": "面到面辐射模型",
                "radiationProperties": """radiationModel  surfaceToSurface;
absorptionEmissionModel greyMeanAbsorptionEmission;
scatterModel     none;

surfaceToSurfaceCoeffs
{
    nFacesInCoarsestMesh   10;
    maxProcFaces           1000;
    useCachedAgglomeration true;
}

// ************************************************************************* //
""",
            },
            "DO": {
                "description": "离散坐标辐射模型（DO模型，最精确但计算量大）",
                "radiationProperties": """radiationModel  DO;
absorptionEmissionModel greyMeanAbsorptionEmission;
scatterModel     none;

DORadiationCoeffs
{
    nPhi            2;      // Azimuthal angles
    nTheta          2;      // Polar angles
    convergenceTol  1e-4;
    maxIter         50;
}

greyMeanAbsorptionEmissionCoeffs
{
    a               uniform 0.1;
    e               uniform 0.9;
}

// ************************************************************************* //
""",
            },
        }

    @staticmethod
    def get_radiation_fv_schemes() -> str:
        """
        获取辐射模型的 fvSchemes 配置

        Returns:
            fvSchemes 中添加辐射离散化方案
        """
        return """// Radiation discretization
laplacianSchemes
{
    laplacian(G,I_h)      Gauss linear uncorrected;
}

interpolationSchemes
{
    interpolate(I_h)      linear;
}
"""

    # ==================== 空气龄相关 ====================

    @staticmethod
    def get_age_of_air_field_template() -> str:
        """
        获取空气龄场文件模板

        Returns:
            age 空气龄场文件内容
        """
        return """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version: 8                                      |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      age;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 0 1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0;  // 空气龄在入口处为0
    }

    outlet
    {
        type            zeroGradient;
    }

    walls
    {
        type            zeroGradient;
    }
}

// ************************************************************************* //
"""

    @staticmethod
    def get_age_of_air_control_dict_additions() -> Dict[str, str]:
        """
        获取空气龄计算的 controlDict 添加内容

        Returns:
            需要添加到 controlDict 的配置
        """
        return {
            "libs": '("libscalarTransportFunctionObjects.so");',
            "functions": """{
    ageOfAir
    {
        type            scalarTransport;
        libs            ("libscalarTransportFunctionObjects.so");
        writeControl    writeTime;
        writeInterval   1;
        field           age;
        rho             rho;
        U               U;
        phi             phi;
        nCorr           1;
    }
}"""
        }

    # ==================== 内部热源相关 ====================

    @staticmethod
    def get_heat_source_template(
        source_name: str = "internalHeatSource",
        power: float = 100.0,  # W
        volume: float = 1.0,  # m³
        source_type: str = "uniform"
    ) -> str:
        """
        获取内部热源配置模板

        Args:
            source_name: 热源名称
            power: 热源功率（W）
            volume: 热源体积（m³）
            source_type: 热源类型（uniform, mapped, coded）

        Returns:
            热源配置内容
        """
        heat_source_density = power / volume  # W/m³

        template = """// Internal Heat Source Configuration
// Total Power: %s W
// Volume: %s m³
// Heat Source Density: %s W/m³

heatSource
{
    type            %s;
    value           uniform %s;

    // Additional options for different source types:
    // - For人体 heat: use人体 model with metabolic rate
    // - For equipment: use specific power density
    // - For lamps: use radiant and convective components

    // Human body heat example (metabolic rate ~ 100W per person)
    // {
    //     type            coded;
    //     value           uniform 0;
    //     code
    //     #{{{
    //         // 计算人体热源
    //         const vectorField& C = mesh().C();
    //         scalarField& sourceField = *this;
    //
    //         // 定义人体位置和代谢率
    //         const scalar humanMetabolicRate = 100.0; // W/person
    //         const scalar humanVolume = 0.075; // m³ (average人体)
    //
    //         forAll(C, i)
    //         #{{{
    //             // 检查是否在人体区域内
    //             // 这里需要根据实际几何设置
    //             scalar dist = mag(C[i] - humanPosition);
    //             if (dist < humanRadius)
    //             #{{{
    //                 sourceField[i] = humanMetabolicRate / humanVolume;
    //             #}}}
    //         #}}}
    //     #}}};
    // }
}

// ************************************************************************* //
"""
        return template % (power, volume, heat_source_density, source_type, heat_source_density)

    @staticmethod
    def get_heat_source_scalar_transport_template() -> str:
        """
        获取热源标量输运函数对象模板

        Returns:
            标量输运函数对象配置
        """
        return """// Heat source scalar transport function
heatSourceTransport
{
    type            fvOptions;
    active          true;

    sources
    {
        heatSource
        {
            type            scalarSemiImplicitSource;
            active          true;
            selectionMode   all;  // or cellZone, points

            scalarSemiImplicitSourceCoeffs
            {
                volumeMode      absolute;  // or specific
                injectionRate   0;  // Will be set by user
            }
        }
    }
}

// ************************************************************************* //
"""

    # ==================== PMV-PPD 指标相关 ====================

    @staticmethod
    def get_pmv_ppd_control_dict_additions(
        enable_pmv: bool = True,
        enable_ppd: bool = True,
        metabolic_rate: float = 1.0,  # met
        clothing_insulation: float = 0.5,  # clo
        air_velocity: float = 0.1,  # m/s
        radiant_temp: float = 293.0,  # K
    ) -> Dict[str, str]:
        """
        获取 PMV-PPD 计算的 controlDict 配置

        Args:
            enable_pmv: 是否启用 PMV 计算
            enable_ppd: 是否启用 PPD 计算
            metabolic_rate: 代谢率
            clothing_insulation: 服装热阻
            air_velocity: 空气流速
            radiant_temp: 平均辐射温度

        Returns:
            需要添加到 controlDict 的函数对象配置
        """
        functions_template = """{
    // PMV (Predicted Mean Vote) - 预测平均投票
    pmv
    {
        type            coded;
        libs            ("libutilityFunctionObjects.so");
        writeControl    writeTime;
        writeInterval   1;
        code
        #{{{
            // PMV 计算基于 Fanger 舒适方程
            const volScalarField& T = mesh().lookupObject<volScalarField>("T");
            const volScalarField& U = mesh().lookupObject<volScalarField>("U");
            const volScalarField& epsilon = mesh().lookupObject<volScalarField>("epsilon");

            // PMV 参数
            const scalar M = %s * 58.2;  // W/m² (代谢率)
            const scalar Icl = %s;  // m²K/W (服装热阻)
            const scalar fcl = 1.05 + 0.1 * Icl;  // 服装面积系数
            const scalar h = 12.1 * sqrt(mag(U));  // 对流换热系数

            // 平均辐射温度 (简化为操作温度)
            const scalar Tr = %s;
            const scalar Ta = T;  // 空气温度

            // 操作温度
            const scalar To = (h * Ta + h * Tr) / (h + h);

            // PMV 计算 (简化版)
            // 完整公式需要迭代求解皮肤温度
            volScalarField pmv
            (
                IOobject
                (
                    "pmv",
                    mesh().time().timeName(),
                    mesh(),
                    IOobject::NO_READ,
                    IOobject::AUTO_WRITE
                ),
                mesh(),
                dimensionedScalar("pmv", dimless, 0)
            );

            // 简化的 PMV 计算
            forAll(T, i)
            {{
                scalar t = T[i] - 273.15;  // 转换为°C
                pmv[i] = 0.303 * exp(-0.036 * M) *
                         (M - 35.7) - 0.028 * (M - 35.7) -
                         0.42 * (M - 58.15) -
                         0.0014 * M * (34 - t) -
                         0.017 * M * (58.15 - t);
            }}

            pmv.write();
        }}}#;
    }

    // PPD (Predicted Percentage of Dissatisfied) - 预测不满意百分比
    ppd
    {
        type            coded;
        libs            ("libutilityFunctionObjects.so");
        writeControl    writeTime;
        writeInterval   1;
        code
        #{{{
            const volScalarField& pmv =
                mesh().lookupObject<volScalarField>("pmv");

            volScalarField ppd
            (
                IOobject
                (
                    "ppd",
                    mesh().time().timeName(),
                    mesh(),
                    IOobject::NO_READ,
                    IOobject::AUTO_WRITE
                ),
                mesh(),
                dimensionedScalar("ppd", dimless, 0)
            );

            // PPD 与 PMV 的关系 (ISO 7730)
            forAll(pmv, i)
            {{
                ppd[i] = 100 - 95 * exp(-0.03353 * pow(pmv[i], 4) -
                                       0.2179 * pow(pmv[i], 2));
            }}

            ppd.write();
        }}}#;
    }
}"""

        config = {
            "libs": '("libutilityFunctionObjects.so" "libfieldFunctionObjects.so");',
            "functions": functions_template % (
                metabolic_rate,
                clothing_insulation,
                radiant_temp
            )
        }

        return config

    @staticmethod
    def get_comfort_criteria_template() -> str:
        """
        获取舒适度标准说明模板

        Returns:
            舒适度标准说明文本
        """
        return """
/* ========================================
   热舒适度标准说明
   基于 ISO 7730 和 ASHRAE Standard 55
   ========================================

PMV (Predicted Mean Vote) 范围:
  -3  冷       -3 冷 discomfort
  -2  冷       -2 cool
  -1  稍微冷   -1 slightly cool
   0  中性     0 neutral
  +1  稍微热   +1 slightly warm
  +2  热       +2 warm
  +3  热       +3 hot discomfort

舒适范围:
  - PMV: -0.5 ~ +0.5 (ISO 7730)
  - PPD: < 10% (ISO 7730)
  - PPD: < 15% (ASHRAE Standard 55)

参数含义:
  - M (代谢率): 1.0 met = 静坐 = 58.2 W/m²
    静坐: 0.8-1.0 met
    轻度活动: 1.2-1.6 met
    中度活动: 1.6-2.0 met

  - Icl (服装热阻): 1.0 clo = 0.155 m²K/W
    夏季薄装: 0.3-0.5 clo
    春秋装: 0.5-1.0 clo
    冬季厚装: 1.0-1.5 clo

  - 空气流速: 通常 0.1-0.3 m/s
    空调房间: 0.1-0.2 m/s
    自然通风: 0.2-0.5 m/s

  - 辐射温度: 环境平均辐射温度
    通常与空气温度相差不大

======================================== */
"""

    # ==================== 综合配置 ====================

    def configure_indoor_air_thermal(self, **kwargs) -> str:
        """
        配置室内空气热环境（综合配置）

        Args:
            **kwargs: 包含以下可选参数
                - solver_type: 求解器类型 (buoyantSimpleFoam, buoyantPimpleFoam, etc.)
                - ambient_temp: 环境温度 (K)
                - inlet_velocity: 入口速度 (vx, vy, vz)
                - inlet_temp: 入口温度 (K)
                - wall_temp: 墙体温度 (K)
                - enable_buoyancy: 是否启用浮力
                - enable_radiation: 辐射模型 (none, P1, viewFactor, DO)
                - enable_age_of_air: 是否计算空气龄
                - enable_heat_source: 是否启用内部热源
                - heat_source_power: 热源功率 (W)
                - enable_pmv_ppd: 是否计算 PMV-PPD
                - metabolic_rate: 代谢率
                - clothing_insulation: 服装热阻

        Returns:
            配置结果说明
        """
        results = []

        # 1. 设置浮力求解器
        solver_type = kwargs.get("solver_type", "buoyantBoussinesqSimpleFoam")
        enable_buoyancy = kwargs.get("enable_buoyancy", True)

        if enable_buoyancy and solver_type:
            results.append(f"✅ 浮力求解器: {solver_type}")

        # 2. 配置温度场
        ambient_temp = kwargs.get("ambient_temp", 293.0)
        results.append(f"✅ 环境温度: {ambient_temp} K")

        # 3. 配置送回风口
        inlet_velocity = kwargs.get("inlet_velocity", [1.0, 0.0, 0.0])
        inlet_temp = kwargs.get("inlet_temp", 293.0)
        results.append(f"✅ 送风口: 速度 {inlet_velocity} m/s, 温度 {inlet_temp} K")

        # 4. 配置墙体传热
        wall_temp = kwargs.get("wall_temp", 293.0)
        heat_transfer_coeff = kwargs.get("heat_transfer_coeff", 8.0)
        results.append(f"✅ 墙体: 温度 {wall_temp} K, 对流换热系数 {heat_transfer_coeff} W/m²K")

        # 5. 配置辐射模型
        radiation_model = kwargs.get("enable_radiation", "none")
        if radiation_model != "none":
            results.append(f"✅ 辐射模型: {radiation_model}")

        # 6. 配置空气龄
        enable_age = kwargs.get("enable_age_of_air", False)
        if enable_age:
            results.append(f"✅ 空气龄计算: 已启用")

        # 7. 配置内部热源
        enable_heat_source = kwargs.get("enable_heat_source", False)
        if enable_heat_source:
            heat_power = kwargs.get("heat_source_power", 100.0)
            results.append(f"✅ 内部热源: {heat_power} W")

        # 8. 配置 PMV-PPD
        enable_pmv_ppd = kwargs.get("enable_pmv_ppd", False)
        if enable_pmv_ppd:
            metabolic_rate = kwargs.get("metabolic_rate", 1.0)
            clothing_insulation = kwargs.get("clothing_insulation", 0.5)
            results.append(f"✅ PMV-PPD: 代谢率 {metabolic_rate} met, 服装热阻 {clothing_insulation} clo")

        return "\n".join(results)


class ThermalEditor:
    """热学配置编辑器 - 用于修改热/浮力相关配置文件"""

    def __init__(self, case_dir: Path):
        self.case_dir = case_dir
        self.config = ThermalConfig(case_dir)

    def set_buoyancy_solver(self, solver_type: str) -> Tuple[bool, str]:
        """
        设置浮力求解器

        Args:
            solver_type: 求解器类型

        Returns:
            (是否成功, 消息)
        """
        control_dict = self.case_dir / "system" / "controlDict"

        if not control_dict.exists():
            return False, "controlDict 文件不存在"

        try:
            with open(control_dict, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换或添加 application
            if 'application' in content:
                content = re.sub(
                    r'application\s+[^;]+;',
                    f'application {solver_type};',
                    content
                )
            else:
                # 在文件开头添加
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('FoamFile'):
                        # 找到 FoamFile 块的结束
                        for j in range(i+1, min(i+20, len(lines))):
                            if lines[j].strip() == '}':
                                insert_pos = j + 1
                                break
                        break
                if insert_pos == 0:
                    insert_pos = 1
                lines.insert(insert_pos, f'application {solver_type};')
                content = '\n'.join(lines)

            with open(control_dict, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, f"✅ 已设置求解器为: {solver_type}"
        except Exception as e:
            return False, f"❌ 设置失败: {str(e)}"

    def add_temperature_field(self, temperature: float = 293.0) -> Tuple[bool, str]:
        """
        添加温度场文件

        Args:
            temperature: 初始温度 (K)

        Returns:
            (是否成功, 消息)
        """
        t_file = self.case_dir / "0" / "T"

        template = self.config.get_temperature_field_template()
        template = template.replace('uniform 293;', f'uniform {temperature};')

        try:
            t_file.write_text(template, encoding='utf-8')
            return True, f"✅ 已创建 T 场文件，初始温度: {temperature} K"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def set_inlet_conditions(
        self,
        inlet_name: str,
        velocity: List[float],
        temperature: float,
        turbulence_intensity: float = 0.05
    ) -> Tuple[bool, str]:
        """
        设置入口边界条件

        Args:
            inlet_name: 入口边界名称
            velocity: 速度向量
            temperature: 温度 (K)
            turbulence_intensity: 湍流强度

        Returns:
            (是否成功, 消息)
        """
        modifications = []

        for field_name, boundary_data in self.config.get_inlet_velocity_temperature_template(
            inlet_name, velocity, temperature, turbulence_intensity
        ).items():
            field_file = self.case_dir / "0" / field_name

            if not field_file.exists():
                continue

            try:
                with open(field_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 查找入口边界块
                inlet_pattern = rf'{inlet_name}\s*\{{[^}}]+\}}'
                inlet_block = re.search(inlet_pattern, content, re.DOTALL)

                if inlet_block:
                    old_block = inlet_block.group(0)
                    new_block = f'{inlet_name}\n' + '{\n'
                    for key, value in boundary_data.items():
                        new_block += f'    type            {value["type"]};\n'
                        if key == "value":
                            new_block += f'    value           {value};\n'
                        else:
                            if isinstance(value, dict):
                                new_block += f'    {key}           {value["value"]};\n'
                    new_block += '}'

                    content = content.replace(old_block, new_block)

                    with open(field_file, 'w', encoding='utf-8') as f:
                        f.write(content)

                    modifications.append(f"{field_name}: {boundary_data.get('type')}")
            except Exception as e:
                return False, f"❌ 设置 {field_name} 失败: {str(e)}"

        if modifications:
            return True, f"✅ 已设置入口 {inlet_name}:\n" + "\n".join(f"  - {m}" for m in modifications)
        else:
            return False, f"⚠️ 未找到入口边界 '{inlet_name}'"

    def set_wall_thermal_conditions(
        self,
        wall_name: str = "walls",
        temperature: Optional[float] = None,
        heat_flux: Optional[float] = None,
        heat_transfer_coeff: Optional[float] = None,
        external_temp: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        设置墙体热边界条件

        Args:
            wall_name: 墙体边界名称
            temperature: 固定温度 (K)
            heat_flux: 热通量 (W/m²)
            heat_transfer_coeff: 对流换热系数 (W/m²K)
            external_temp: 外部温度 (K)

        Returns:
            (是否成功, 消息)
        """
        t_file = self.case_dir / "0" / "T"

        if not t_file.exists():
            return False, "T 场文件不存在，请先创建"

        boundary_config = self.config.get_wall_thermal_boundary_template(
            wall_name, temperature, heat_flux, heat_transfer_coeff, external_temp
        )

        try:
            with open(t_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找墙体边界块
            wall_pattern = rf'{wall_name}\s*\{{[^}}]+\}}'
            wall_block = re.search(wall_pattern, content, re.DOTALL)

            if wall_block:
                old_block = wall_block.group(0)
                new_block = f'{wall_name}\n'
                new_block += '{\n'
                for key, value in boundary_config.items():
                    new_block += f'    type            {value};\n'
                new_block += '}\n'

                content = content.replace(old_block, new_block)

                with open(t_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                return True, f"✅ 已设置墙体 {wall_name} 热边界条件: {boundary_config['type']}"
            else:
                return False, f"⚠️ 未找到墙体边界 '{wall_name}'"
        except Exception as e:
            return False, f"❌ 设置失败: {str(e)}"

    def add_gravity_file(self, gravity: List[float] = [0, 0, -9.81]) -> Tuple[bool, str]:
        """
        添加重力文件

        Args:
            gravity: 重力向量

        Returns:
            (是否成功, 消息)
        """
        g_file = self.case_dir / "constant" / "g"

        template = self.config.get_gravity_template()
        template = template.replace(
            'value           (0 0 -9.81);',
            f'value           ({gravity[0]} {gravity[1]} {gravity[2]});'
        )

        try:
            g_file.write_text(template, encoding='utf-8')
            return True, f"✅ 已创建重力文件: gravity = {gravity}"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def add_thermophysical_properties(self) -> Tuple[bool, str]:
        """
        添加热物理属性文件

        Returns:
            (是否成功, 消息)
        """
        props_file = self.case_dir / "constant" / "thermophysicalProperties"

        try:
            props_file.write_text(
                self.config.get_buoyancy_properties_template(),
                encoding='utf-8'
            )
            return True, "✅ 已创建 thermophysicalProperties 文件"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def add_radiation_model(self, model: str = "P1") -> Tuple[bool, str]:
        """
        添加辐射模型配置

        Args:
            model: 辐射模型类型

        Returns:
            (是否成功, 消息)
        """
        rad_file = self.case_dir / "constant" / "radiationProperties"

        templates = self.config.get_radiation_model_templates()

        if model not in templates:
            return False, f"❌ 不支持的辐射模型: {model}"

        try:
            rad_file.write_text(
                "FoamFile\n{\n    version     2.0;\n    format      ascii;\n    class       dictionary;\n    object      radiationProperties;\n}\n// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n" +
                templates[model]["radiationProperties"],
                encoding='utf-8'
            )
            return True, f"✅ 已创建辐射模型: {model} ({templates[model]['description']})"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def add_age_of_air_field(self) -> Tuple[bool, str]:
        """
        添加空气龄场文件

        Returns:
            (是否成功, 消息)
        """
        age_file = self.case_dir / "0" / "age"

        try:
            age_file.write_text(
                self.config.get_age_of_air_field_template(),
                encoding='utf-8'
            )
            return True, "✅ 已创建空气龄场文件"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def add_heat_source_config(
        self,
        power: float = 100.0,
        volume: float = 1.0,
        source_type: str = "uniform"
    ) -> Tuple[bool, str]:
        """
        添加热源配置文件

        Args:
            power: 热源功率
            volume: 热源体积
            source_type: 热源类型

        Returns:
            (是否成功, 消息)
        """
        heat_source_dir = self.case_dir / "constant" / "heatSource"

        try:
            heat_source_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"❌ 创建目录失败: {str(e)}"

        config_file = heat_source_dir / "heatSourceProperties"

        try:
            config_file.write_text(
                self.config.get_heat_source_template(
                    "internalHeatSource", power, volume, source_type
                ),
                encoding='utf-8'
            )
            return True, f"✅ 已创建热源配置: {power} W ({power/volume:.1f} W/m³)"
        except Exception as e:
            return False, f"❌ 创建失败: {str(e)}"

    def add_pmv_ppd_function(
        self,
        metabolic_rate: float = 1.0,
        clothing_insulation: float = 0.5,
        air_velocity: float = 0.1,
        radiant_temp: float = 293.0
    ) -> Tuple[bool, str]:
        """
        在 controlDict 中添加 PMV-PPD 计算函数

        Args:
            metabolic_rate: 代谢率
            clothing_insulation: 服装热阻
            air_velocity: 空气流速
            radiant_temp: 辐射温度

        Returns:
            (是否成功, 消息)
        """
        control_dict = self.case_dir / "system" / "controlDict"

        if not control_dict.exists():
            return False, "controlDict 文件不存在"

        try:
            with open(control_dict, 'r', encoding='utf-8') as f:
                content = f.read()

            pmv_config = self.config.get_pmv_ppd_control_dict_additions(
                True, True, metabolic_rate, clothing_insulation,
                air_velocity, radiant_temp
            )

            # 添加 libs 和 functions
            if 'libs' not in content:
                # 在文件开头添加
                content = content.replace(
                    '// * * * * * * *',
                    pmv_config['libs'] + '\n\n// * * * * * * *'
                )

            if 'functions' not in content:
                # 在文件末尾添加
                content += '\n' + pmv_config['functions']

            with open(control_dict, 'w', encoding='utf-8') as f:
                f.write(content)

            return True, f"✅ 已添加 PMV-PPD 计算函数 (met={metabolic_rate} met, icl={clothing_insulation} clo)"
        except Exception as e:
            return False, f"❌ 添加失败: {str(e)}"
