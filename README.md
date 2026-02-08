# OpenFOAM MCP Server

一个用于读取和修改 OpenFOAM 配置文件的 MCP (Model Context Protocol) 服务器。支持 Windows、Linux 和 macOS。

## ✨ 功能

### 基础功能
- 📂 **Case 信息查询** - 获取 OpenFOAM case 目录结构和文件列表
- 📄 **字典文件读取** - 解析 OpenFOAM 字典格式文件（controlDict, fvSchemes 等）
- ✏️ **参数修改** - 修改 controlDict 等文件中的求解器参数
- 🔧 **边界条件管理** - 读取和修改场文件的边界条件
- 🔍 **内容搜索** - 在所有配置文件中搜索关键词
- 📋 **物理属性查看** - 读取输运属性和湍流模型设置

### 热学/浮力功能（新增）
- 🌡️ **温度求解器** - 创建和配置温度场文件
- 🎈 **浮力求解器** - 支持多种浮力驱动流动求解器
- 🧱 **墙体传热设置** - 支持固定温度、热通量、对流换热边界条件
- 💨 **送回风口设置** - 配置入口/出口的速度和温度边界条件
- ☀️ **辐射模型设置** - 支持 P1、viewFactor、DO 等辐射模型
- ⏱️ **空气龄计算** - 配置空气龄标量输运方程
- 🔥 **内部热源设置** - 配置人体、设备等内部热源
- 😊 **PMV-PPD 舒适度指标** - 计算预测平均投票和预测不满意百分比

## 📋 支持的文件类型

| 目录 | 文件 | 描述 |
|------|------|------|
| `system/` | controlDict | 求解器控制参数 |
| `system/` | fvSchemes | 离散化方案 |
| `system/` | fvSolution | 线性求解器设置 |
| `constant/` | transportProperties | 输运属性 |
| `constant/` | turbulenceProperties | 湍流模型 |
| `0/` | U, p, T 等 | 初始条件和边界条件 |

## 🚀 快速安装

### Windows 一键安装

```powershell
# 克隆项目
git clone https://github.com/ymg2007/openfoam-mcp.git
cd openfoam-mcp

# 运行安装脚本
install.bat
```

### Linux/macOS 一键安装

```bash
# 克隆项目
git clone https://github.com/ymg2007/openfoam-mcp.git
cd openfoam-mcp

# 运行安装脚本
chmod +x install.sh
./install.sh
```

## 🔧 支持的 AI 助手

OpenFOAM MCP 支持多种 AI 助手，选择你喜欢的：

| AI 助手 | 配置文件路径 |
|----------|-------------|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)<br>`~/.config/Claude/claude_desktop_config.json` (Linux)<br>`%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| **Claude Code** | `~/.claude-code/config.json` |
| **Cursor** | `~/.cursor/mcp_config.json` |
| **OpenCode** | `~/.opencode/config.json` |
| **Cline** | `~/.cline/settings.json` |

## 📦 Windows 安装

### 自动安装（推荐）

1. **下载并运行安装脚本**
```powershell
git clone https://github.com/ymg2007/openfoam-mcp.git
cd openfoam-mcp
install.bat
```

### 手动安装

#### 1. 安装 Python

访问 [Python官网](https://www.python.org/downloads/) 下载并安装 Python 3.10+，安装时勾选 "Add Python to PATH"

#### 2. 创建虚拟环境

```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### Claude Desktop 配置

配置文件：`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "C:\\path\\to\\openfoam-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\openfoam-mcp\\src\\server.py"]
    }
  }
}
```

### Claude Code 配置

配置文件：`~/.claude-code/config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "C:\\path\\to\\openfoam-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\openfoam-mcp\\src\\server.py"]
    }
  ]
}
```

### Cursor 配置

配置文件：`%APPDATA%\Cursor\User\mcp_config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "C:\\path\\to\\openfoam-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\openfoam-mcp\\src\\server.py"]
    }
  ]
}
```

### OpenCode 配置

配置文件：`~/.opencode/config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "C:\\path\\to\\openfoam-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\openfoam-mcp\\src\\server.py"]
    }
  }
}
```

## 🐧 Linux 安装

### 自动安装（推荐）

```bash
git clone https://github.com/ymg2007/openfoam-mcp.git
cd openfoam-mcp
chmod +x install.sh
./install.sh
```

### 手动安装

#### 1. 安装 Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip python3-devel
```

#### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Claude Desktop 配置

配置文件：`~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "/home/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/home/yourname/openfoam-mcp/src/server.py"]
    }
  }
}
```

### Claude Code 配置

配置文件：`~/.claude-code/config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "/home/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/home/yourname/openfoam-mcp/src/server.py"]
    }
  ]
}
```

### Cursor 配置

配置文件：`~/.cursor/mcp_config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "/home/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/home/yourname/openfoam-mcp/src/server.py"]
    }
  ]
}
```

### OpenCode 配置

配置文件：`~/.opencode/config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "/home/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/home/yourname/openfoam-mcp/src/server.py"]
    }
  }
}
```

## 🍎 macOS 安装

### 自动安装（推荐）

```bash
git clone https://github.com/ymg2007/openfoam-mcp.git
cd openfoam-mcp
chmod +x install.sh
./install.sh
```

### 手动安装

#### 1. 安装 Python

```bash
brew install python@3.11
```

#### 2. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Claude Desktop 配置

配置文件：`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "/Users/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/Users/yourname/openfoam-mcp/src/server.py"]
    }
  }
}
```

### Claude Code 配置

配置文件：`~/.claude-code/config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "/Users/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/Users/yourname/openfoam-mcp/src/server.py"]
    }
  ]
}
```

### Cursor 配置

配置文件：`~/.cursor/mcp_config.json`

```json
{
  "mcpServers": [
    {
      "name": "openfoam",
      "command": "/Users/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/Users/yourname/openfoam-mcp/src/server.py"]
    }
  ]
}
```

### OpenCode 配置

配置文件：`~/.opencode/config.json`

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "/Users/yourname/openfoam-mcp/venv/bin/python",
      "args": ["/Users/yourname/openfoam-mcp/src/server.py"]
    }
  }
}
```

## 🧪 验证安装

```bash
# 激活虚拟环境后
python src/server.py
```

如果服务器正常启动，应该看到 MCP 服务器初始化的输出。

## 📖 使用方法

### 切换到 OpenFOAM Case 目录

```bash
cd /path/to/your/OpenFOAM/case
```

然后在 AI 助手中使用工具。

### 可用工具

| 工具名 | 功能 | 示例 |
|--------|------|------|
| `get_case_info` | 获取 case 目录信息 | "获取当前 case 的信息" |
| `read_dict_file` | 读取字典文件 | "读取 controlDict" |
| `read_file_content` | 读取文件原始内容 | "显示 fvSchemes 的内容" |
| `list_field_files` | 列出场文件 | "列出所有场文件" |
| `get_boundary_conditions` | 获取边界条件 | "查看 U 场的边界条件" |
| `modify_control_dict` | 修改求解器参数 | "把 deltaT 改为 0.0005" |
| `modify_boundary_condition` | 修改边界条件 | "修改 U 场 inlet 边界" |
| `get_transport_properties` | 读取输运属性 | "查看输运属性" |
| `get_turbulence_properties` | 读取湍流模型 | "查看湍流设置" |
| `get_fv_schemes` | 读取离散化方案 | "查看离散化方案" |
| `get_fv_solution` | 读取求解器设置 | "查看求解器设置" |
| `search_case_files` | 搜索文件内容 | "搜索 turbulence" |

### 热/浮力求解器工具

| 工具名 | 功能 | 示例 |
|--------|------|------|
| `list_buoyancy_solvers` | 列出浮力求解器 | "显示可用的浮力求解器" |
| `set_buoyancy_solver` | 设置浮力求解器 | "设置求解器为 buoyantSimpleFoam" |
| `add_temperature_field` | 创建温度场 | "创建温度场，初始温度 293K" |
| `add_gravity_file` | 创建重力文件 | "添加重力文件用于浮力计算" |
| `add_thermophysical_properties` | 创建热物理属性 | "添加热物理属性文件" |
| `set_inlet_thermal_conditions` | 设置入口热边界 | "设置入口速度和温度" |
| `set_wall_thermal_conditions` | 设置墙体热边界 | "设置墙体传热边界条件" |
| `list_radiation_models` | 列出辐射模型 | "显示可用的辐射模型" |
| `add_radiation_model` | 添加辐射模型 | "添加 P1 辐射模型" |
| `add_age_of_air_field` | 添加空气龄场 | "创建空气龄计算场" |
| `add_heat_source_config` | 添加热源配置 | "添加内部热源 100W" |
| `add_pmv_ppd_comfort_metrics` | 添加舒适度指标 | "配置 PMV-PPD 计算" |
| `get_comfort_criteria_info` | 获取舒适度标准 | "显示 ISO 7730 舒适度标准" |
| `configure_indoor_thermal_environment` | 一键配置热环境 | "配置完整的室内热环境" |

## 💬 使用示例

### 示例 1: 获取 Case 信息

```
用户: 帮我看看这个 case 的结构
AI: [调用 get_case_info]
返回: OpenFOAM Case 目录: /path/to/case

=== 目录结构 ===

0/
  - U
  - p

constant/
  - transportProperties

system/
  - controlDict
  - fvSchemes
  - fvSolution
```

### 示例 2: 修改求解器参数

```
用户: 把 deltaT 改为 0.0005，结束时间设为 2000
AI: [调用 modify_control_dict(delta_t=0.0005, end_time=2000)]
返回: ✅ 已修改 controlDict:
  - deltaT -> 0.0005
  - endTime -> 2000
```

### 示例 3: 查看并修改边界条件

```
用户: 先看看速度场的边界条件
AI: [调用 get_boundary_conditions("U")]
返回: === U 边界条件 ===

📍 inlet
  type: fixedValue
  value: {'type': 'uniform', 'value': [10.0, 0.0, 0.0]}

📍 outlet
  type: zeroGradient

📍 walls
  type: noSlip

用户: 把入口速度改成 (15 0 0)
AI: [调用 modify_boundary_condition("U", "inlet", value="uniform (15 0 0)")]
返回: ✅ 已修改 U 的边界条件:
  - value -> uniform (15 0 0)
```

### 示例 4: 搜索配置

```
用户: 找一下所有和湍流相关的设置
AI: [调用 search_case_files("turbulence")]
返回: === 搜索结果 ===

system/fvSchemes:31: turbulence bounded Gauss linearUpwind grad(k);
```

### 示例 5: 配置浮力求解器

```
用户: 查看可用的浮力求解器
AI: [调用 list_buoyancy_solvers()]
返回: === 可用的浮力求解器 ===

🔹 buoyantSimpleFoam
   描述: 稳态浮力驱动流动求解器（Boussinesq近似）
   求解器类型: steady-state
   需要的场变量: T, p_rgh, U, k, epsilon, omega

用户: 设置为 buoyantBoussinesqSimpleFoam
AI: [调用 set_buoyancy_solver("buoyantBoussinesqSimpleFoam")]
返回: ✅ 已设置求解器为: buoyantBoussinesqSimpleFoam
```

### 示例 6: 配置温度和墙体传热

```
用户: 创建温度场，初始温度 293K
AI: [调用 add_temperature_field(293.0)]
返回: ✅ 已创建 T 场文件，初始温度: 293 K

用户: 设置墙体温度 295K，对流换热系数 8 W/m²K
AI: [调用 set_wall_thermal_conditions("walls", temperature=295, heat_transfer_coeff=8)]
返回: ✅ 已设置墙体 walls 热边界条件: coefficient
```

### 示例 7: 配置送回风口

```
用户: 设置送风口 inlet，速度 1.5 m/s，温度 288K
AI: [调用 set_inlet_thermal_conditions("inlet", 1.5, 0, 0, 288)]
返回: ✅ 已设置入口 inlet:
  - U: fixedValue
  - T: fixedValue
  - k: fixedValue
  - epsilon: fixedValue
```

### 示例 8: 配置辐射模型

```
用户: 查看可用的辐射模型
AI: [调用 list_radiation_models()]
返回: === 可用的辐射模型 ===

🔹 none
   描述: 无辐射模型

🔹 P1
   描述: P1 辐射模型（适用于光学厚介质）

🔹 viewFactor
   描述: 视角系数辐射模型（适用于封闭空间）

用户: 添加 P1 辐射模型
AI: [调用 add_radiation_model("P1")]
返回: ✅ 已创建辐射模型: P1 (P1 辐射模型（适用于光学厚介质）)
```

### 示例 9: 配置空气龄和热源

```
用户: 添加空气龄计算
AI: [调用 add_age_of_air_field()]
返回: ✅ 已创建空气龄场文件

用户: 添加内部热源 500W
AI: [调用 add_heat_source_config(power=500)]
返回: ✅ 已创建热源配置: 500.0 W (500.0 W/m³)
```

### 示例 10: 配置 PMV-PPD 舒适度指标

```
用户: 配置 PMV-PPD 计算，代谢率 1.2 met，服装热阻 0.6 clo
AI: [调用 add_pmv_ppd_comfort_metrics(metabolic_rate=1.2, clothing_insulation=0.6)]
返回: ✅ 已添加 PMV-PPD 计算函数 (met=1.2 met, icl=0.6 clo)
```

### 示例 11: 一键配置室内热环境

```
用户: 配置完整的室内热环境：浮力求解器、温度 293K、入口速度 1 m/s 温度 293K、
     墙体温度 295K、启用浮力和辐射 P1 模型、启用空气龄、PMV-PPD
AI: [调用 configure_indoor_thermal_environment(
       solver_type="buoyantBoussinesqSimpleFoam",
       ambient_temp=293,
       inlet_velocity_x=1,
       inlet_temp=293,
       wall_temp=295,
       radiation_model="P1",
       enable_age_of_air=True,
       enable_pmv_ppd=True
     )]
返回: === 室内热环境配置完成 ===

✅ 已设置求解器为: buoyantBoussinesqSimpleFoam
✅ 已创建 T 场文件，初始温度: 293 K
✅ 已创建重力文件: gravity = [0, 0, -9.81]
✅ 已设置入口 inlet: ...
✅ 已设置墙体 walls 热边界条件: ...
✅ 已创建辐射模型: P1 ...
✅ 已创建空气龄场文件
✅ 已添加 PMV-PPD 计算函数 ...
```

## 🏗️ 项目结构

```
openfoam-mcp/
├── src/
│   ├── __init__.py          # 包初始化
│   ├── server.py           # MCP 服务器主文件（含热学工具）
│   ├── parser.py           # OpenFOAM 字典解析器
│   ├── editor.py           # 文件编辑工具
│   └── thermal.py          # 热/浮力求解器配置模块（新增）
├── examples/
│   ├── test_case/          # 示例 OpenFOAM case
│   └── SIMPLE_CASE.md      # 使用示例文档
├── install.bat             # Windows 安装脚本
├── install.sh              # Linux/macOS 安装脚本
├── pyproject.toml         # 项目配置
├── requirements.txt       # Python 依赖
├── README.md            # 本文件
└── INSTALL.md           # 详细安装指南
```

## 🔧 故障排除

### 问题: 找不到 case 目录

**错误信息**: "未找到 OpenFOAM case 目录"

**解决方法**:
- 确保你在 case 目录或其子目录中
- case 目录应包含 `0/`, `constant/`, `system/` 子目录

### 问题: 服务器无法启动

**错误信息**: ImportError 或 ModuleNotFoundError

**解决方法**:
- 检查 Python 版本是否 >= 3.10
- 确保安装了所有依赖：`pip install -r requirements.txt`
- 检查虚拟环境是否正确激活

### 问题: 无法修改边界条件

**错误信息**: "没有修改任何边界条件"

**解决方法**:
- 确认边界名称正确（使用 `get_boundary_conditions` 查看实际边界名）
- 检查边界条件值格式是否正确

### Windows 路径问题

**问题**: 路径中的反斜杠导致 JSON 解析错误

**解决方法**:
- 使用双反斜杠 `\\` 或正斜杠 `/`
- 使用绝对路径

### Python 模块未找到

**错误信息**: `ModuleNotFoundError: No module named 'mcp'`

**解决方法**:
```bash
pip install mcp
```

### 虚拟环境创建失败 (Linux)

**错误信息**: `No module named venv`

**解决方法**:
```bash
sudo apt install python3-venv
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 📚 参考

- [OpenFOAM 官方文档](https://www.openfoam.com/documentation)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Claude Desktop 文档](https://docs.anthropic.com/claude/desktop)
- [Claude Code 文档](https://docs.anthropic.com/claude-code)

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐
