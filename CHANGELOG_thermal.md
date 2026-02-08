# OpenFOAM MCP Server 更新说明

## 版本: v1.1.0 - 热/浮力求解器增强模块

**发布日期:** 2026-02-08
**兼容性:** OpenFOAM v8

---

## 📌 更新摘要

本次更新为 OpenFOAM MCP Server 添加了完整的热/浮力求解器支持，使工具能够配置室内热环境 CFD 模拟的所有关键组件，包括浮力求解器、温度场、墙体传热、送回风口、辐射模型、空气龄、内部热源和 PMV-PPD 舒适度指标。

### 主要变化

- 🆕 新增 15 个热学 MCP 工具
- 🆕 新增 `src/thermal.py` 核心模块（1329 行）
- 🆕 新增热学功能测试脚本 `test_thermal.py`
- 📝 更新 README.md 和 PROJECT_SUMMARY.md 文档
- ✅ 所有配置兼容 OpenFOAM v8

---

## ✨ 新增功能

### 1. 浮力求解器配置

支持 4 种 OpenFOAM 浮力驱动流动求解器：

| 求解器 | 类型 | 描述 |
|--------|------|------|
| `buoyantSimpleFoam` | 稳态 | 稳态浮力驱动流动（Boussinesq 近似） |
| `buoyantPimpleFoam` | 瞬态 | 瞬态浮力驱动流动 |
| `buoyantBoussinesqSimpleFoam` | 稳态 | 稳态 Boussinesq 浮力驱动 |
| `buoyantBoussinesqPimpleFoam` | 瞬态 | 瞬态 Boussinesq 浮力驱动 |

**新增工具：**
- `list_buoyancy_solvers()` - 列出所有可用浮力求解器
- `set_buoyancy_solver(solver_type)` - 设置浮力求解器

### 2. 温度求解器配置

**新增文件模板：**
- `0/T` - 温度场文件
- `constant/thermophysicalProperties` - 热物理属性文件

**新增工具：**
- `add_temperature_field(temperature)` - 创建温度场文件
- `add_thermophysical_properties()` - 创建热物理属性文件

### 3. 墙体传热设置

支持 3 种墙体热边界条件类型：

| 类型 | 说明 |
|------|------|
| 固定温度 (fixedValue) | 指定墙体表面温度 |
| 热通量 (externalWallHeatFlux - flux mode) | 指定通过墙体的热通量 |
| 对流换热 (externalWallHeatFlux - coefficient mode) | 指定对流换热系数和外部温度 |

**新增工具：**
- `set_wall_thermal_conditions(wall_name, temperature, heat_flux, heat_transfer_coeff, external_temp)` - 设置墙体热边界条件

### 4. 送回风口设置

自动配置入口/出口的速度、温度和湍流参数边界条件。

**新增工具：**
- `set_inlet_thermal_conditions(inlet_name, velocity_x, velocity_y, velocity_z, temperature, turbulence_intensity)` - 设置入口热边界条件

**自动配置的场变量：**
- `U` - 速度
- `T` - 温度
- `k` - 湍动能
- `epsilon` / `omega` - 湍流耗散率/比耗散率

### 5. 辐射模型设置

支持 5 种辐射模型：

| 模型 | 描述 | 适用场景 |
|------|------|----------|
| `none` | 无辐射模型 | 不考虑辐射换热 |
| `P1` | P1 辐射模型 | 光学厚介质 |
| `viewFactor` | 视角系数模型 | 封闭空间 |
| `surfaceToSurface` | 面到面模型 | 复杂几何 |
| `DO` | 离散坐标模型 | 最精确（计算量大） |

**新增工具：**
- `list_radiation_models()` - 列出所有可用辐射模型
- `add_radiation_model(model)` - 添加辐射模型配置

### 6. 空气龄计算

空气龄（Age of Air）是空气从进入室内空间起所经历的平均时间，用于评估通风效率和室内空气质量。

**新增文件模板：**
- `0/age` - 空气龄场文件

**新增工具：**
- `add_age_of_air_field()` - 创建空气龄场文件

### 7. 内部热源设置

支持多种热源类型配置：

| 热源类型 | 说明 |
|----------|------|
| `uniform` | 均匀热源 |
| `mapped` | 映射热源 |
| `coded` | 自定义代码热源（可模拟人体、设备等） |

**新增文件模板：**
- `constant/heatSource/heatSourceProperties` - 热源配置文件

**新增工具：**
- `add_heat_source_config(power, volume, source_type)` - 添加热源配置

### 8. PMV-PPD 舒适度指标

基于 ISO 7730 和 ASHRAE Standard 55 标准计算热舒适度指标：

**PMV (Predicted Mean Vote)** - 预测平均投票
- 范围：-3（冷）~ +3（热）
- 舒适范围：-0.5 ~ +0.5

**PPD (Predicted Percentage of Dissatisfied)** - 预测不满意百分比
- 舒适标准：< 10% (ISO 7730) 或 < 15% (ASHRAE Standard 55)

**新增工具：**
- `add_pmv_ppd_comfort_metrics(metabolic_rate, clothing_insulation, air_velocity, radiant_temp)` - 添加 PMV-PPD 计算函数
- `get_comfort_criteria_info()` - 获取舒适度标准说明

### 9. 一键配置

**新增工具：**
- `configure_indoor_thermal_environment()` - 一键配置完整室内热环境

该工具可一次性配置：
- 浮力求解器
- 温度场和热物理属性
- 重力文件（如果启用浮力）
- 送回风口边界条件
- 墙体传热边界条件
- 辐射模型
- 空气龄计算
- 内部热源
- PMV-PPD 舒适度指标

---

## 📁 新增文件

```
src/
└── thermal.py              # 热/浮力配置核心模块 (1329 行)
    ├── ThermalConfig       # 热学配置模板类
    └── ThermalEditor       # 热学配置编辑器类

test_thermal.py             # 热学模块测试脚本 (10 个测试)
```

## 📝 更新文件

```
src/server.py               # 新增 15 个热学 MCP 工具
README.md                   # 更新功能说明和使用示例
PROJECT_SUMMARY.md          # 更新项目总结
```

---

## 🔧 API 变更

### 新增 MCP 工具列表

| 工具名 | 功能 |
|--------|------|
| `list_buoyancy_solvers` | 列出可用的浮力求解器 |
| `set_buoyancy_solver` | 设置浮力求解器类型 |
| `add_temperature_field` | 创建温度场文件 (0/T) |
| `add_gravity_file` | 创建重力文件 (constant/g) |
| `add_thermophysical_properties` | 创建热物理属性文件 |
| `set_inlet_thermal_conditions` | 设置入口速度和温度边界条件 |
| `set_wall_thermal_conditions` | 设置墙体热边界条件 |
| `list_radiation_models` | 列出可用的辐射模型 |
| `add_radiation_model` | 添加辐射模型配置 |
| `add_age_of_air_field` | 创建空气龄场文件 (0/age) |
| `add_heat_source_config` | 创建内部热源配置文件 |
| `add_pmv_ppd_comfort_metrics` | 添加 PMV-PPD 计算函数 |
| `get_comfort_criteria_info` | 获取舒适度标准说明 |
| `configure_indoor_thermal_environment` | 一键配置完整室内热环境 |

---

## 📊 代码统计

| 文件 | 行数 | 变化 |
|------|------|------|
| `src/thermal.py` | 1329 | +1329 (新文件) |
| `test_thermal.py` | 170 | +170 (新文件) |
| `src/server.py` | 951 | +15 (新增工具) |
| `README.md` | ~600 | +150 (文档更新) |
| `PROJECT_SUMMARY.md` | ~370 | +100 (文档更新) |
| **总计** | **~3420** | **+2372** |

---

## 🧪 测试

新增 `test_thermal.py` 包含 10 个完整测试：

1. ✅ 浮力求解器模板测试
2. ✅ 温度场模板测试
3. ✅ 墙体热边界条件模板测试
4. ✅ 入口边界条件模板测试
5. ✅ 辐射模型模板测试
6. ✅ 空气龄模板测试
7. ✅ 热源配置模板测试
8. ✅ PMV-PPD 模板测试
9. ✅ 舒适度标准说明测试
10. ✅ 室内热环境综合配置测试

运行测试：
```bash
python3 test_thermal.py
```

---

## 💡 使用示例

### 示例 1: 查看可用的浮力求解器

```
用户: 显示可用的浮力求解器
AI: [调用 list_buoyancy_solvers()]
返回: === 可用的浮力求解器 ===

🔹 buoyantSimpleFoam
   描述: 稳态浮力驱动流动求解器（Boussinesq近似）
   求解器类型: steady-state
   需要的场变量: T, p_rgh, U, k, epsilon, omega

...
```

### 示例 2: 配置完整的室内热环境

```
用户: 配置浮力求解器为 buoyantBoussinesqSimpleFoam，温度 293K，
     入口速度 1 m/s 温度 293K，墙体温度 295K，启用浮力和辐射 P1 模型，
     启用空气龄、热源 500W、PMV-PPD 计算
AI: [调用 configure_indoor_thermal_environment(...)]
返回: === 室内热环境配置完成 ===

✅ 已设置求解器为: buoyantBoussinesqSimpleFoam
✅ 已创建 T 场文件，初始温度: 293 K
✅ 已创建重力文件: gravity = [0, 0, -9.81]
✅ 已设置入口 inlet: ...
✅ 已设置墙体 walls 热边界条件: ...
✅ 已创建辐射模型: P1 ...
✅ 已创建空气龄场文件
✅ 已创建热源配置: 500.0 W ...
✅ 已添加 PMV-PPD 计算函数 ...
```

---

## 🔄 升级指南

### 现有用户

无需任何更改，只需更新代码：

```bash
cd openfoam-mcp
git pull origin main
```

MCP 服务器会自动加载新的热学工具。

### 配置文件

MCP 配置文件（`claude_desktop_config.json` 等）无需更改。

---

## 🔗 室内热环境 CFD 完整工作流

使用本 MCP 服务器，可以完整配置室内热环境 CFD 模拟：

```
1. 选择浮力求解器 (set_buoyancy_solver)
   ↓
2. 创建温度场和热物理属性 (add_temperature_field, add_thermophysical_properties)
   ↓
3. 配置重力文件用于浮力计算 (add_gravity_file)
   ↓
4. 设置送回风口边界条件 (set_inlet_thermal_conditions)
   ↓
5. 配置墙体传热 (set_wall_thermal_conditions)
   ↓
6. (可选) 添加辐射模型 (add_radiation_model)
   ↓
7. (可选) 配置空气龄计算 (add_age_of_air_field)
   ↓
8. (可选) 添加内部热源 (add_heat_source_config)
   ↓
9. (可选) 配置 PMV-PPD 舒适度指标 (add_pmv_ppd_comfort_metrics)
   ↓
10. 运行求解器并分析结果
```

**或者使用一键配置工具：**
```
configure_indoor_thermal_environment()
```

---

## 📚 兼容性

- ✅ OpenFOAM v8
- ✅ Python 3.10+
- ✅ MCP 协议

---

## 🐛 已知问题

暂无已知问题。

---

## 📝 未来计划

### 热学功能扩展
- 支持更多湍流模型（k-omegaSST, LES, DES）
- 添加多组分输运（燃烧、污染物扩散）
- 支持太阳辐射模型
- 添加 HVAC 系统（风机、过滤器）配置
- 支持 CO₂ 浓度和换气次数计算

### 基础功能扩展
- 边界条件类型的自动补全
- 支持更多物理属性文件
- 添加 case 模板生成功能
- 支持网格文件信息读取
- 添加运行求解器的工具

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可

MIT License

---

## 🔗 相关链接

- GitHub: https://github.com/ymg2007/openfoam-mcp
- OpenFOAM 官方文档: https://www.openfoam.com/documentation
- MCP 协议规范: https://modelcontextprotocol.io/
- ISO 7730 舒适度标准: https://www.iso.org/standard/79131.html
- ASHRAE Standard 55: https://www.ashrae.org/technical-resources/standards-and-guidelines

---

**更新日期:** 2026-02-08
**版本:** v1.1.0
