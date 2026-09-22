---
name: mcp-bridge
domain: deep_research
description: Anthropic Model Context Protocol (MCP) 官方标准协议网关与工具调用引擎（支持对接与调度任何本地/远程 Stdio MCP Server，内置 SQLite、目录树与安全数学求值工具）
dependencies: []
---

# Anthropic MCP 协议网关与客户端引擎 (Model Context Protocol Bridge)

## 📌 核心定位与协议特性
本技能实现 Anthropic 官方提出的 **Model Context Protocol (MCP)** 统一通信协议（JSON-RPC 2.0 stdio 传输规约）：
1. **统一工具挂载**：可直接驱动并与任何标准 MCP Server（Python、Node.js / npx、Go、Rust 实现）握手通信。
2. **动态工具自发现**：自动触发 `tools/list` 提取远程工具名称、功能描述与 JSON Schema 输入规约。
3. **安全参数校验与执行**：通过标准 `tools/call` 封装参数并安全转发，捕获返回内容与异常流。
4. **开箱即用内置 Server**：自带纯 Python 零依赖轻量级 MCP Server，提供 `sqlite_query`、`fs_tree`、`safe_eval` 三大核心本地工具。

---

## 🚀 命令行调用指引

### 1. 激活技能
```bash
load_skill mcp-bridge
```

### 2. 连接内置 MCP Server 并列出全部工具与 Schema
```bash
python3 mcp_client.py --list-tools
```

### 3. 调用 MCP 工具：执行 SQLite 查询
```bash
python3 mcp_client.py --call-tool "sqlite_query" --params '{"db_path": ":memory:", "query": "SELECT 1 + 1 AS result, datetime(\"now\") AS current_time;"}'
```

### 4. 调用 MCP 工具：安全数学与科学计算
```bash
python3 mcp_client.py --call-tool "safe_eval" --params '{"expression": "math.sqrt(1024) * math.sin(math.pi / 2)"}'
```

### 5. 挂载外部官方/社区 MCP Server (如 Filesystem Server)
```bash
# 挂载通过 npx 运行的官方 Filesystem MCP Server
python3 mcp_client.py --server "npx -y @modelcontextprotocol/server-filesystem /tmp" --list-tools
```
