# OpenFOAM MCP Server

一个用于读取和修改 OpenFOAM 配置文件的 MCP (Model Context Protocol) 服务器。

## ✨ 功能

- 📂 **Case 信息查询** - 获取 OpenFOAM case 目录结构和文件列表
- 📄 **字典文件读取** - 解析 OpenFOAM 字典格式文件（controlDict, fvSchemes 等）
- ✏️ **参数修改** - 修改 controlDict 等文件中的求解器参数
- 🔧 **边界条件管理** - 读取和修改场文件的边界条件
- 🔍 **内容搜索** - 在所有配置文件中搜索关键词
- 📋 **物理属性查看** - 读取输运属性和湍流模型设置

## 📋 支持的文件类型

| 目录 | 文件 | 描述 |
|------|------|------|
| `system/` | controlDict | 求解器控制参数 |
| `system/` | fvSchemes | 离散化方案 |
| `system/` | fvSolution | 线性求解器设置 |
| `constant/` | transportProperties | 输运属性 |
| `constant/` | turbulenceProperties | 湍流模型 |
| `0/` | U, p, T 等 | 初始条件和边界条件 |

## 🚀 安装

### 1. 安装依赖

```bash
cd openfoam-mcp
pip install -r requirements.txt
```

### 2. 配置 Claude Desktop

在 Claude Desktop 的配置文件中添加 OpenFOAM MCP 服务器：

**配置文件位置：**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "python",
      "args": ["/absolute/path/to/openfoam-mcp/src/server.py"]
    }
  }
}
```

将 `/absolute/path/to/openfoam-mcp/` 替换为实际的绝对路径。

### 3. 重启 Claude Desktop

重启 Claude Desktop 使配置生效。

## 📖 使用方法

### 切换到 OpenFOAM Case 目录

在使用 MCP 工具前，建议先切换到你的 OpenFOAM case 目录：

```bash
cd /path/to/your/OpenFOAM/case
```

然后在 Claude Desktop 中使用工具。

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

## 🧪 测试

项目包含一个示例 case 用于测试：

```bash
cd openfoam-mcp
python3 test_all_tools.py
```

测试修改功能：

```bash
python3 test_modify.py
```

## 🏗️ 项目结构

```
openfoam-mcp/
├── src/
│   ├── __init__.py      # 包初始化
│   ├── server.py        # MCP 服务器主文件
│   ├── parser.py        # OpenFOAM 字典解析器
│   └── editor.py        # 文件编辑工具
├── examples/
│   ├── test_case/       # 示例 OpenFOAM case
│   └── SIMPLE_CASE.md   # 使用示例文档
├── pyproject.toml       # 项目配置
├── requirements.txt     # Python 依赖
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
- 检查 Python 路径是否正确
- 确保安装了所有依赖：`pip install -r requirements.txt`
- 使用 Python 3.10 或更高版本

### 问题: 无法修改边界条件

**错误信息**: "没有修改任何边界条件"

**解决方法**:
- 确认边界名称正确（使用 `get_boundary_conditions` 查看实际边界名）
- 检查边界条件值格式是否正确

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 📚 参考

- [OpenFOAM 官方文档](https://www.openfoam.com/documentation)
- [MCP 协议规范](https://modelcontextprotocol.io/)
