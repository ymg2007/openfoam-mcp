# OpenFOAM MCP Server 安装和使用指南

## 安装步骤

### 1. 安装依赖

```bash
cd openfoam-mcp
pip install -r requirements.txt
```

### 2. 配置 Claude Desktop

在 Claude Desktop 的配置文件中添加 OpenFOAM MCP 服务器：

**macOS / Linux:**
```bash
# 配置文件位置
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Linux: ~/.config/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

添加以下配置：

```json
{
  "mcpServers": {
    "openfoam": {
      "command": "python",
      "args": ["/path/to/openfoam-mcp/src/server.py"]
    }
  }
}
```

将 `/path/to/openfoam-mcp/` 替换为实际的绝对路径。

### 3. 重启 Claude Desktop

重启 Claude Desktop 使配置生效。

## 使用方法

### 切换到 OpenFOAM Case 目录

在使用 MCP 工具前，需要先切换到你的 OpenFOAM case 目录，或者在配置中指定 case 目录路径。

```bash
cd /path/to/your/OpenFOAM/case
```

然后在 Claude Desktop 中使用工具。

### 可用工具

| 工具名 | 功能 |
|--------|------|
| `get_case_info` | 获取当前 case 目录信息和文件列表 |
| `read_dict_file` | 读取并解析 OpenFOAM 字典文件 |
| `read_file_content` | 读取文件的原始内容 |
| `list_field_files` | 列出 0/ 目录中的所有场文件 |
| `get_boundary_conditions` | 获取指定场的边界条件 |
| `modify_control_dict` | 修改 controlDict 中的求解器参数 |
| `modify_boundary_condition` | 修改场文件的边界条件 |
| `get_transport_properties` | 读取输运属性 |
| `get_turbulence_properties` | 读取湍流模型设置 |
| `get_fv_schemes` | 读取离散化方案 |
| `get_fv_solution` | 读取求解器设置 |
| `search_case_files` | 在所有配置文件中搜索关键词 |

### 示例对话

**示例 1: 获取 Case 信息**
```
用户: 帮我看看这个 case 的结构
AI: 调用 get_case_info，返回目录结构
```

**示例 2: 修改求解器参数**
```
用户: 把时间步长改成 0.0005，结束时间设为 2000
AI: 调用 modify_control_dict(delta_t=0.0005, end_time=2000)
```

**示例 3: 查看并修改边界条件**
```
用户: 先看看速度场的边界条件，然后把入口改成 uniform (15 0 0)
AI: 1. 调用 get_boundary_conditions("U")
    2. 调用 modify_boundary_condition("U", "inlet", value="uniform (15 0 0)")
```

**示例 4: 搜索配置**
```
用户: 找一下所有和湍流相关的设置
AI: 调用 search_case_files("turbulence")
```

## 测试

使用示例 case 测试：

```bash
cd openfoam-mcp/examples/test_case
# 启动 Claude Desktop 并尝试使用工具
```

## 故障排除

### 问题: 找不到 case 目录
**解决**: 确保你在 case 目录或其子目录中，case 目录应包含 `0/`, `constant/`, `system/` 子目录。

### 问题: 服务器无法启动
**解决**: 检查 Python 路径是否正确，确保所有依赖已安装。

### 问题: 无法读取文件
**解决**: 检查文件权限和路径。

## 开发

### 运行测试服务器

```bash
cd openfoam-mcp
python src/server.py
```

### 添加新工具

在 `src/server.py` 中使用 `@mcp.tool()` 装饰器添加新工具。

## 贡献

欢迎提交 Issue 和 Pull Request！
