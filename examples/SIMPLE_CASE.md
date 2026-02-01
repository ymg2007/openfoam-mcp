# OpenFOAM MCP 使用示例

## 1. 获取 Case 信息

```
请帮我获取当前 OpenFOAM case 的信息
```

AI 会调用 `get_case_info` 工具，返回目录结构和主要文件列表。

## 2. 读取配置文件

```
读取 controlDict 文件
```

```
读取 fvSchemes 文件
```

AI 会调用 `read_dict_file` 工具，返回解析后的 JSON 格式内容。

## 3. 修改求解器参数

```
把 deltaT 改为 0.0005
```

```
设置 end_time 为 1000
```

AI 会调用 `modify_control_dict` 工具修改参数。

## 4. 查看边界条件

```
列出所有场文件
```

AI 会调用 `list_field_files` 工具。

```
查看 U 场的边界条件
```

AI 会调用 `get_boundary_conditions` 工具。

## 5. 修改边界条件

```
把 U 场 inlet 边界改为 zeroGradient
```

```
把 p 场 outlet 边界设为 fixedValue 0
```

AI 会调用 `modify_boundary_condition` 工具。

## 6. 搜索文件内容

```
搜索所有文件中的 "turbulence" 关键词
```

AI 会调用 `search_case_files` 工具。

## 7. 读取物理属性

```
读取输运属性
```

```
读取湍流模型设置
```

AI 会调用 `get_transport_properties` 或 `get_turbulence_properties` 工具。
