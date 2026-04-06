---
title: "MCP完全指南"
date: 2026-04-06
draft: false
description: ""
tags: ["MCP"]
categories: ["笔记"]
---

## 目录

1. [什么是 MCP](#1-什么是-mcp)
2. [为什么需要 MCP](#2-为什么需要-mcp)
3. [核心架构](#3-核心架构)
4. [三大核心能力](#4-三大核心能力)
5. [传输层详解](#5-传输层详解)
6. [实战项目：文件系统 + 天气查询 MCP Server](#6-实战项目)
7. [进阶：在 Claude Desktop 中接入自定义 Server](#7-接入-claude-desktop)
8. [常见问题 & 最佳实践](#8-最佳实践)

---

## 1. 什么是 MCP

**MCP（Model Context Protocol）** 是 Anthropic 于 2024 年 11 月开源的一套标准协议，旨在解决 AI 大模型与外部工具、数据源之间的**集成碎片化**问题。

你可以把它理解为：

> **AI 世界的 USB-C 接口**

以前，每当你想让 AI 访问数据库、调用 API、读取文件，都需要为每个模型、每个平台单独写集成代码。MCP 定义了一套统一标准，让任意 **MCP Client**（Claude、Cursor、自定义 AI 应用）都能无缝接入任意 **MCP Server**（文件系统、数据库、GitHub、Slack……）。

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP 生态全貌                          │
│                                                             │
│  ┌──────────────┐     MCP 协议      ┌──────────────────┐   │
│  │  MCP Client  │ ◄──────────────► │   MCP Server     │   │
│  │              │                  │                  │   │
│  │  - Claude    │                  │  - 文件系统       │   │
│  │  - Cursor    │                  │  - 数据库         │   │
│  │  - 你的 App  │                  │  - GitHub API    │   │
│  └──────────────┘                  │  - Slack         │   │
│                                    │  - 你的自定义服务 │   │
│                                    └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 为什么需要 MCP

### 没有 MCP 之前的痛点

```
Claude ──► 自定义工具调用 ──► 碎片化集成代码（每次都要重写）
GPT-4 ──► Function Calling ──► 又一套不兼容的集成代码
Cursor ──► 专有扩展 API ──► 再一套……
```

**问题：**
- 开发者要为不同 AI 框架重复造轮子
- 工具提供商无法一次性支持所有 AI 平台
- 没有统一的安全、权限、上下文管理标准

### MCP 解决了什么

| 问题 | MCP 的解决方式 |
|------|--------------|
| 集成碎片化 | 一套协议，所有 Client/Server 通用 |
| 工具发现困难 | Server 自动暴露能力，Client 动态发现 |
| 上下文丢失 | Resources 机制持久化上下文 |
| 安全边界不清 | 明确的权限声明与授权流程 |
| 重复造轮子 | 生态共享，npm 上直接安装 MCP Server |

---

## 3. 核心架构

MCP 采用经典的 **Client-Server 架构**，通信基于 **JSON-RPC 2.0**。

```
┌─────────────────────────────────────────────────────────────────┐
│                         完整架构图                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Host Application                     │   │
│  │  (Claude Desktop / Cursor / 你的自定义 AI 应用)           │   │
│  │                                                         │   │
│  │   ┌───────────┐    ┌───────────┐    ┌───────────┐      │   │
│  │   │ MCP Client│    │ MCP Client│    │ MCP Client│      │   │
│  │   │     1     │    │     2     │    │     3     │      │   │
│  │   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘      │   │
│  └─────────┼───────────────┼───────────────┼─────────────┘   │
│            │               │               │                  │
│    ┌───────▼───────┐ ┌─────▼───────┐ ┌────▼────────┐        │
│    │  MCP Server A │ │ MCP Server B│ │ MCP Server C│        │
│    │  (文件系统)    │ │  (数据库)   │ │  (GitHub)   │        │
│    └───────────────┘ └─────────────┘ └─────────────┘        │
│            │               │               │                  │
│    ┌───────▼───────┐ ┌─────▼───────┐ ┌────▼────────┐        │
│    │  本地文件系统  │ │  PostgreSQL │ │  GitHub API │        │
│    └───────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 关键角色说明

| 角色 | 职责 |
|------|------|
| **Host** | 宿主应用，如 Claude Desktop。管理多个 MCP Client 实例 |
| **MCP Client** | 嵌入在 Host 中，与单个 MCP Server 保持 1:1 连接 |
| **MCP Server** | 轻量级服务，暴露工具/资源/提示词给 Client |

### 通信流程（握手 → 调用）

```
Client                          Server
  │                               │
  │──── initialize ─────────────►│  发送客户端能力 & 版本
  │◄─── initialize result ───────│  返回服务端能力 & 版本
  │                               │
  │──── initialized (通知) ──────►│  确认握手完成
  │                               │
  │──── tools/list ─────────────►│  列出所有工具
  │◄─── tools/list result ───────│  返回工具描述
  │                               │
  │──── tools/call ─────────────►│  调用具体工具
  │◄─── tools/call result ───────│  返回执行结果
  │                               │
  │──── resources/list ─────────►│  列出资源
  │◄─── resources/read result ───│  返回资源内容
```

---

## 4. 三大核心能力

MCP Server 可以向 Client 暴露三种能力：

### 4.1 Tools（工具）—— 模型发起的操作

Tools 是 MCP 最核心的能力，允许 AI 模型**执行操作**，类似 OpenAI 的 Function Calling。

```
特点：
- 由 AI 模型决定何时调用
- 有明确的输入 Schema（JSON Schema）
- 返回结构化或文本结果
- 典型场景：查询数据库、调用 API、执行命令
```

**示例工具定义：**

```json
{
  "name": "read_file",
  "description": "读取指定路径的文件内容",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "文件的绝对路径"
      }
    },
    "required": ["path"]
  }
}
```

### 4.2 Resources（资源）—— 结构化上下文

Resources 允许 Server 暴露**数据/内容**给 Client，用于丰富 AI 的上下文。

```
特点：
- 由应用层（Host）控制何时读取，而非 AI 自主决策
- 通过 URI 标识（如 file:///path/to/file）
- 支持文本和二进制内容
- 典型场景：项目文件、数据库记录、配置信息
```

**Resource URI 示例：**

```
file:///home/user/project/README.md
postgres://localhost/mydb/users/schema
github://repos/anthropics/mcp/README
```

### 4.3 Prompts（提示词模板）—— 可复用的交互模式

Prompts 允许 Server 定义**可复用的提示词模板**，供用户选择触发。

```
特点：
- 由用户主动选择（而非 AI 自主触发）
- 可接受参数，动态生成提示词
- 支持多轮对话模板
- 典型场景：代码审查模板、翻译模板、报告生成模板
```

### 三者对比

| 能力 | 控制方 | 典型用途 | 类比 |
|------|--------|----------|------|
| Tools | AI 模型 | 执行操作、获取实时数据 | 函数调用 |
| Resources | 应用/用户 | 注入背景上下文 | 文件附件 |
| Prompts | 用户 | 触发预设工作流 | 斜杠命令 |

---

## 5. 传输层详解

MCP 支持两种传输机制：

### 5.1 Stdio（标准输入输出）

```
适用场景：本地运行的 MCP Server（最常用）

Host Process
    │
    ├── 启动子进程（MCP Server）
    │       stdin  ◄─── JSON-RPC 请求
    │       stdout ───► JSON-RPC 响应
    │       stderr ───► 日志（不参与协议）
```

**特点：**
- 简单，无需网络配置
- 安全（进程隔离）
- Claude Desktop 默认使用此方式

### 5.2 SSE（Server-Sent Events）

```
适用场景：远程 MCP Server、多 Client 共享

Client ──── HTTP POST /messages ────► Server（发送请求）
Client ◄─── GET /sse （流式推送）──── Server（接收响应）
```

**特点：**
- 支持远程部署
- 多个 Client 可连接同一 Server
- 适合团队共享工具服务

---

## 6. 实战项目

### 项目目标

构建一个 MCP Server，包含以下功能：

- **Tool 1：`read_file`** - 读取本地文件
- **Tool 2：`list_directory`** - 列出目录结构
- **Tool 3：`get_weather`** - 模拟天气查询
- **Resource：`file://`** - 动态暴露文件资源

### 6.1 项目初始化

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript @types/node tsx
```

**`tsconfig.json`：**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src/**/*"]
}
```

**`package.json` 关键字段：**

```json
{
  "type": "module",
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js"
  }
}
```

### 6.2 核心代码

**`src/index.ts`：**

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import fs from "fs/promises";
import path from "path";

// ============================================================
// 1. 创建 Server 实例
// ============================================================
const server = new Server(
  {
    name: "my-mcp-server",       // Server 名称
    version: "1.0.0",            // Server 版本
  },
  {
    capabilities: {
      tools: {},        // 声明支持 Tools
      resources: {},    // 声明支持 Resources
    },
  }
);

// ============================================================
// 2. 注册 Tools 列表处理器
//    Client 调用 tools/list 时触发
// ============================================================
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "read_file",
        description: "读取指定路径的文件内容，支持文本文件",
        inputSchema: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "文件的绝对路径或相对路径",
            },
          },
          required: ["path"],
        },
      },
      {
        name: "list_directory",
        description: "列出指定目录下的文件和文件夹",
        inputSchema: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description: "目录路径，默认为当前目录",
            },
            show_hidden: {
              type: "boolean",
              description: "是否显示隐藏文件（以.开头）",
            },
          },
          required: ["path"],
        },
      },
      {
        name: "get_weather",
        description: "获取指定城市的当前天气信息（模拟数据）",
        inputSchema: {
          type: "object",
          properties: {
            city: {
              type: "string",
              description: "城市名称，如：北京、上海、深圳",
            },
            unit: {
              type: "string",
              enum: ["celsius", "fahrenheit"],
              description: "温度单位，默认摄氏度",
            },
          },
          required: ["city"],
        },
      },
    ],
  };
});

// ============================================================
// 3. 注册 Tools 调用处理器
//    Client 调用 tools/call 时触发
// ============================================================
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    // ---------- Tool: read_file ----------
    case "read_file": {
      const { path: filePath } = z
        .object({ path: z.string() })
        .parse(args);

      try {
        const absolutePath = path.resolve(filePath);
        const content = await fs.readFile(absolutePath, "utf-8");
        const stats = await fs.stat(absolutePath);

        return {
          content: [
            {
              type: "text",
              text: [
                `📄 文件：${absolutePath}`,
                `📦 大小：${stats.size} 字节`,
                `🕒 修改时间：${stats.mtime.toLocaleString("zh-CN")}`,
                `\n${"─".repeat(50)}\n`,
                content,
              ].join("\n"),
            },
          ],
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `读取文件失败：${(error as Error).message}`
        );
      }
    }

    // ---------- Tool: list_directory ----------
    case "list_directory": {
      const { path: dirPath, show_hidden = false } = z
        .object({
          path: z.string(),
          show_hidden: z.boolean().optional(),
        })
        .parse(args);

      try {
        const absolutePath = path.resolve(dirPath);
        const entries = await fs.readdir(absolutePath, { withFileTypes: true });

        const filtered = entries.filter(
          (e) => show_hidden || !e.name.startsWith(".")
        );

        // 目录在前，文件在后
        const dirs = filtered.filter((e) => e.isDirectory());
        const files = filtered.filter((e) => !e.isDirectory());

        const formatEntry = async (entry: typeof entries[0]) => {
          const entryPath = path.join(absolutePath, entry.name);
          if (entry.isDirectory()) {
            return `📁 ${entry.name}/`;
          } else {
            const stats = await fs.stat(entryPath);
            const size = formatBytes(stats.size);
            return `📄 ${entry.name} (${size})`;
          }
        };

        const lines = [
          `📂 目录：${absolutePath}`,
          `共 ${dirs.length} 个文件夹，${files.length} 个文件`,
          "─".repeat(50),
          ...(await Promise.all([...dirs, ...files].map(formatEntry))),
        ];

        return {
          content: [{ type: "text", text: lines.join("\n") }],
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `读取目录失败：${(error as Error).message}`
        );
      }
    }

    // ---------- Tool: get_weather ----------
    case "get_weather": {
      const { city, unit = "celsius" } = z
        .object({
          city: z.string(),
          unit: z.enum(["celsius", "fahrenheit"]).optional(),
        })
        .parse(args);

      // 模拟天气数据（实际项目中替换为真实 API 调用）
      const weatherData = simulateWeather(city, unit);

      return {
        content: [
          {
            type: "text",
            text: [
              `🌤️ ${city} 天气报告`,
              "─".repeat(30),
              `🌡️ 温度：${weatherData.temp}°${unit === "celsius" ? "C" : "F"}`,
              `💧 湿度：${weatherData.humidity}%`,
              `🌬️ 风速：${weatherData.windSpeed} km/h`,
              `☁️ 天气：${weatherData.condition}`,
              `👁️ 能见度：${weatherData.visibility} km`,
              `🕒 更新时间：${new Date().toLocaleString("zh-CN")}`,
            ].join("\n"),
          },
        ],
      };
    }

    default:
      throw new McpError(
        ErrorCode.MethodNotFound,
        `未知工具：${name}`
      );
  }
});

// ============================================================
// 4. 注册 Resources 列表处理器
// ============================================================
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  // 动态列出当前目录的文件作为资源
  try {
    const entries = await fs.readdir(process.cwd(), { withFileTypes: true });
    const files = entries.filter(
      (e) => !e.isDirectory() && !e.name.startsWith(".")
    );

    return {
      resources: files.map((file) => ({
        uri: `file://${path.join(process.cwd(), file.name)}`,
        name: file.name,
        description: `工作目录中的文件：${file.name}`,
        mimeType: getMimeType(file.name),
      })),
    };
  } catch {
    return { resources: [] };
  }
});

// ============================================================
// 5. 注册 Resources 读取处理器
// ============================================================
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (!uri.startsWith("file://")) {
    throw new McpError(ErrorCode.InvalidRequest, "仅支持 file:// URI");
  }

  const filePath = uri.replace("file://", "");

  try {
    const content = await fs.readFile(filePath, "utf-8");
    return {
      contents: [
        {
          uri,
          mimeType: getMimeType(filePath),
          text: content,
        },
      ],
    };
  } catch (error) {
    throw new McpError(
      ErrorCode.InternalError,
      `读取资源失败：${(error as Error).message}`
    );
  }
});

// ============================================================
// 工具函数
// ============================================================

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getMimeType(filename: string): string {
  const ext = path.extname(filename).toLowerCase();
  const mimeMap: Record<string, string> = {
    ".ts": "text/plain",
    ".js": "text/javascript",
    ".json": "application/json",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".html": "text/html",
    ".css": "text/css",
  };
  return mimeMap[ext] ?? "text/plain";
}

function simulateWeather(city: string, unit: string) {
  // 基于城市名生成确定性的模拟数据
  const hash = city.split("").reduce((a, c) => a + c.charCodeAt(0), 0);
  const conditions = ["晴天 ☀️", "多云 ⛅", "阴天 ☁️", "小雨 🌧️", "大风 💨"];

  let tempC = 15 + (hash % 20); // 15~34°C
  const temp =
    unit === "fahrenheit" ? Math.round(tempC * 1.8 + 32) : tempC;

  return {
    temp,
    humidity: 40 + (hash % 50),        // 40%~89%
    windSpeed: 5 + (hash % 30),         // 5~34 km/h
    condition: conditions[hash % conditions.length],
    visibility: 5 + (hash % 20),        // 5~24 km
  };
}

// ============================================================
// 6. 启动 Server（Stdio 传输）
// ============================================================
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // 注意：不要向 stdout 写日志（会污染 MCP 协议流）
  // 所有日志统一写到 stderr
  console.error("✅ MCP Server 已启动，等待连接...");
}

main().catch((error) => {
  console.error("❌ 启动失败：", error);
  process.exit(1);
});
```

### 6.3 代码结构说明

```
my-mcp-server/
├── src/
│   └── index.ts       # 主文件（所有逻辑）
├── package.json
├── tsconfig.json
└── dist/              # 编译输出（运行 npm run build 后生成）
```

### 6.4 本地测试

MCP 提供了官方调试工具 **MCP Inspector**：

```bash
# 安装并启动 Inspector
npx @modelcontextprotocol/inspector tsx src/index.ts
```

浏览器打开 `http://localhost:5173`，你将看到一个可视化界面：

```
┌──────────────────────────────────────────────────┐
│              MCP Inspector                        │
│                                                  │
│  📦 Server Info                                  │
│  Name: my-mcp-server  Version: 1.0.0             │
│                                                  │
│  🔧 Tools (3)                                    │
│  ├── read_file                   [Test ▶]        │
│  ├── list_directory              [Test ▶]        │
│  └── get_weather                 [Test ▶]        │
│                                                  │
│  📚 Resources (动态列出文件)                       │
│  ├── package.json                                │
│  └── tsconfig.json                              │
└──────────────────────────────────────────────────┘
```

**手动测试 get_weather：**

```json
// 输入
{ "city": "深圳", "unit": "celsius" }

// 输出
🌤️ 深圳 天气报告
──────────────────────────────
🌡️ 温度：28°C
💧 湿度：73%
🌬️ 风速：18 km/h
☁️ 天气：晴天 ☀️
👁️ 能见度：16 km
🕒 更新时间：2025/4/6 10:30:00
```

---

## 7. 接入 Claude Desktop

### 7.1 编译项目

```bash
npm run build
# 生成 dist/index.js
```

### 7.2 修改 Claude Desktop 配置

找到配置文件：

| 系统 | 路径 |
|------|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "node",
      "args": ["/绝对路径/my-mcp-server/dist/index.js"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

### 7.3 重启 Claude Desktop

重启后，你可以直接在对话中说：

```
你好，请帮我读取 /Users/me/project/README.md 的内容
```

Claude 会自动调用 `read_file` 工具，无需任何额外配置。

---

## 8. 最佳实践

### 8.1 错误处理

始终使用 `McpError` 而非普通 `Error`，让 Client 能正确解析错误类型：

```typescript
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";

// ✅ 正确
throw new McpError(ErrorCode.InvalidRequest, "路径不能为空");

// ❌ 避免
throw new Error("路径不能为空");
```

**ErrorCode 速查：**

| ErrorCode | 含义 | 使用场景 |
|-----------|------|----------|
| `InvalidRequest` | 请求参数有误 | 参数校验失败 |
| `MethodNotFound` | 方法不存在 | 未知 tool name |
| `InternalError` | 内部错误 | 文件读取失败等 |
| `InvalidParams` | 参数类型错误 | Schema 不匹配 |

### 8.2 日志规范

```typescript
// ✅ 正确：日志写到 stderr，不污染协议流
console.error("[INFO] 工具被调用:", toolName);

// ❌ 错误：不要写到 stdout，会破坏 JSON-RPC 通信
console.log("工具调用");
```

### 8.3 工具描述要写好

AI 模型根据 description 决定何时调用哪个工具：

```typescript
// ❌ 模糊的描述
{
  name: "process",
  description: "处理数据"
}

// ✅ 清晰的描述
{
  name: "search_products",
  description: "在商品数据库中搜索产品。支持按名称、品类、价格区间过滤。返回匹配产品的列表，包含ID、名称、价格和库存状态。"
}
```

### 8.4 输入验证用 Zod

```typescript
import { z } from "zod";

const InputSchema = z.object({
  path: z.string().min(1, "路径不能为空"),
  encoding: z.enum(["utf-8", "base64"]).default("utf-8"),
  max_size: z.number().int().positive().max(10 * 1024 * 1024).optional(),
});

// 在 handler 中使用
const validated = InputSchema.parse(args);  // 自动抛出类型安全的错误
```

### 8.5 安全注意事项

```typescript
// ✅ 路径遍历防护
const safePath = path.resolve(BASE_DIR, userInput);
if (!safePath.startsWith(BASE_DIR)) {
  throw new McpError(ErrorCode.InvalidRequest, "不允许访问该路径");
}

// ✅ 文件大小限制
const stats = await fs.stat(filePath);
if (stats.size > MAX_FILE_SIZE) {
  throw new McpError(ErrorCode.InvalidRequest, "文件过大");
}
```

---

## 总结

| 阶段 | 核心概念 | 你需要做的 |
|------|----------|-----------|
| 理解协议 | JSON-RPC 2.0、Client-Server | 了解握手流程 |
| 暴露工具 | `tools/list` + `tools/call` | 实现 setRequestHandler |
| 丰富上下文 | `resources/list` + `resources/read` | 暴露文件/数据源 |
| 接入宿主 | Stdio 传输 + 配置文件 | 修改 claude_desktop_config.json |

MCP 的价值在于**生态**：你写的 Server，不仅 Claude 能用，未来所有支持 MCP 的 AI 工具都能无缝接入。现在正是参与这个生态早期建设的最好时机。

---

*参考资料：[MCP 官方文档](https://modelcontextprotocol.io) · [MCP SDK on npm](https://www.npmjs.com/package/@modelcontextprotocol/sdk)*
