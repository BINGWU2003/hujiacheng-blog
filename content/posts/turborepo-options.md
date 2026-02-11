---
title: "Turborepo 配置选项"
date: 2025-11-10
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 Turborepo

[Turborepo](https://turborepo.com/) 是一个高性能的 JavaScript 和 TypeScript 项目构建系统，专为 Monorepo 设计。它通过智能缓存和任务编排，极大提升构建速度。

```bash
# 安装 Turborepo
npm install -g turbo

# 初始化配置
turbo init

# 运行构建
turbo run build
```

> [!TIP] 版本说明
> 本文档基于 **Turborepo 2.x** 编写。Turborepo 2.0 引入了重大变更，包括将 `pipeline` 重命名为 `tasks`。
>
> **Turborepo 1.x vs 2.x 主要区别**：
>
> - ✅ **Turborepo 2.x**（推荐）：
> - 使用 `tasks` 替代 `pipeline` 配置任务
> - 改进的 UI 模式（`--ui` 标志）
> - 更好的错误信息和日志输出
> - 支持任务标签（tags）用于分组执行
> - 移除了一些已废弃的选项
> - ⚠️ **Turborepo 1.x**（本文档部分兼容）：
> - 使用 `pipeline` 配置任务
> - 基础的日志输出
> - 仍被广泛使用但不再推荐
>
> **迁移提示**：
>
> - 如果使用 Turborepo 1.x，将文档中的 `tasks` 替换为 `pipeline` 即可
> - Turborepo 2.x 向后兼容 `pipeline`，但建议迁移到 `tasks`
> - 配置选项大部分保持一致，迁移成本较低

> [!WARNING] 注意事项
>
> - 本文档主要适用于 Turborepo 2.x，但大部分配置与 1.x 兼容
> - Turborepo 的配置选项可能随版本更新而变化
> - 建议参考 [官方文档](https://turbo.build/repo/docs) 获取最新信息
> - 本文档为了兼容性，在示例中同时展示 `tasks` 和 `pipeline` 用法

### 核心特性

- ⚡ **智能缓存**：从不重复执行相同的工作
- 🔗 **任务编排**：自动处理包之间的依赖关系
- 🚀 **并行执行**：充分利用多核 CPU
- ☁️ **远程缓存**：团队共享构建缓存
- 📊 **增量构建**：只构建改变的包

## 为什么需要 Turborepo

### 传统 Monorepo 的问题

没有 Turborepo 时，Monorepo 项目面临诸多问题：

```bash
# ❌ 传统方式：手动管理构建顺序
cd packages/shared && npm run build    # 30秒
cd ../ui && npm run build              # 20秒
cd ../../apps/web && npm run build     # 40秒
# 总耗时：90秒

# ❌ 如果顺序错了
cd apps/web && npm run build
# 错误：Cannot find module '@my-monorepo/shared'

# ❌ 即使代码未改变，也要重新构建
npm run build  # 每次都是 90秒
```

**问题**：

- ❌ 需要手动记住构建顺序
- ❌ 顺序错误导致构建失败
- ❌ 未改变的代码也重新构建
- ❌ 无法并行构建
- ❌ CI/CD 时间过长

### 使用 Turborepo 后

```bash
# ✅ 使用 Turborepo：自动处理一切
turbo run build

# 第一次构建
# ✓ shared 构建（30秒）
# ✓ ui 构建（20秒） - 等 shared 完成
# ✓ web 构建（40秒）- 等 ui 完成
# 总耗时：90秒

# 第二次构建（代码未改变）
turbo run build
# ⚡ shared 缓存命中，跳过
# ⚡ ui 缓存命中，跳过
# ⚡ web 缓存命中，跳过
# 总耗时：< 1秒！节省 89秒！

# 只修改了 shared 包
turbo run build
# ✓ shared 重新构建（30秒）
# ✓ ui 重新构建（20秒） - 依赖 shared
# ✓ web 重新构建（40秒）- 依赖 ui
# ⚡ docs 缓存命中，跳过 - 不依赖 shared
# 智能判断，增量构建！
```

**效果**：

- ✅ 自动分析依赖关系
- ✅ 智能缓存，避免重复构建
- ✅ 增量构建，只构建改变的包
- ✅ 并行执行，提高效率
- ✅ CI/CD 时间大幅缩短

## 安装

### 基础安装

```bash
# 使用 npm
npm install -D turbo

# 使用 yarn
yarn add -D turbo

# 使用 pnpm（推荐）
pnpm add -D turbo

# 全局安装
npm install -g turbo
```

### 初始化配置

```bash
# 在已有项目中初始化
turbo init

# 会创建 turbo.json 配置文件
```

### 快速开始（新项目）

```bash
# 使用官方模板创建项目
npx create-turbo@latest my-monorepo

# 选择包管理器
# > pnpm (推荐)
#   npm
#   yarn
```

## 配置文件

### 支持的配置文件格式

Turborepo 使用 `turbo.json` 作为配置文件：

```bash
# 根目录配置文件
turbo.json

# 包级别配置文件（可选）
packages/web/turbo.json
apps/docs/turbo.json
```

**推荐**：只在根目录使用一个 `turbo.json`。

### 基础结构

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    // 任务配置（Turborepo 2.x）
  },
  // "pipeline": {} // Turborepo 1.x 使用此项
  "globalEnv": [],
  "globalDependencies": []
}
```

## 一、核心配置选项

### 1.1 $schema

**作用**：指定 JSON Schema，提供 IDE 自动补全和验证。

```json
{
  "$schema": "https://turbo.build/schema.json"
}
```

**影响对比**：

```json
// ❌ 不配置 $schema
{
  "tasks": {
    "build": {
      "dependson": ["^build"]  // 拼写错误，但不提示
    }
  }
}

// ✅ 配置 $schema
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"]  // IDE 会标红和自动补全，避免拼写错误
    }
  }
}
```

**好处**：

- ✅ IDE 自动补全
- ✅ 配置验证
- ✅ 悬停提示
- ✅ 减少拼写错误

### 1.2 tasks / pipeline

**作用**：定义任务及其依赖关系（Turborepo 的核心配置）。

> [!TIP] 配置键名变更
>
> - **Turborepo 2.x**：使用 `"tasks"` 键
> - **Turborepo 1.x**：使用 `"pipeline"` 键
> - 两者功能完全相同，只是键名不同

```json
// Turborepo 2.x（推荐）
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}

// Turborepo 1.x（仍然支持）
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    }
  }
}
```

**tasks/pipeline 是什么**：

```
tasks/pipeline = 任务配置

定义了项目中所有可执行的任务，以及它们之间的关系：
- 哪些任务需要先执行
- 哪些输出需要缓存
- 哪些任务可以并行
```

**影响对比**：

```bash
# ❌ 不配置 tasks
turbo run build
# 错误：No "build" task found in tasks

# ✅ 配置 tasks
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}

turbo run build
# ✓ 按依赖顺序执行所有包的 build 任务
```

### 1.3 dependsOn（任务依赖）

**作用**：指定任务的依赖关系。

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build", "^build"]
    },
    "deploy": {
      "dependsOn": ["build", "test"]
    }
  }
}
```

**符号说明**：

| 符号    | 含义                | 示例                      |
| ------- | ------------------- | ------------------------- |
| `^task` | 先执行依赖包的 task | `^build` - 先构建依赖的包 |
| `task`  | 先执行当前包的 task | `build` - 先构建当前包    |
| 无前缀  | 当前包的其他任务    | `lint` - 当前包的 lint    |

**详细示例**：

#### 示例 1：`dependsOn: ["^build"]`

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    }
  }
}
```

**项目结构**：

```
packages/
├── shared/      (无依赖)
├── ui/          (依赖 shared)
└── web/         (依赖 ui 和 shared)
```

**执行 `turbo run build` 时**：

```
1. shared 先构建（无依赖）
   ↓
2. ui 构建（等 shared 构建完成）
   ↓
3. web 构建（等 ui 构建完成）
```

#### 示例 2：`dependsOn: ["build"]`

```json
{
  "tasks": {
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

**含义**：先执行当前包的 `build`，再执行 `test`

```
执行 turbo run test：

packages/shared:
  1. 先执行 shared 的 build
  2. 再执行 shared 的 test

packages/ui:
  1. 先执行 ui 的 build
  2. 再执行 ui 的 test
```

#### 示例 3：`dependsOn: ["^build", "build"]`

```json
{
  "tasks": {
    "test": {
      "dependsOn": ["^build", "build"]
    }
  }
}
```

**含义**：先构建依赖的包，再构建当前包，最后测试

```
执行 turbo run test（以 web 包为例）：

1. 构建 shared（web 的依赖）
   ↓
2. 构建 ui（web 的依赖）
   ↓
3. 构建 web（当前包）
   ↓
4. 测试 web（当前包）
```

#### 示例 4：多任务依赖

```json
{
  "tasks": {
    "deploy": {
      "dependsOn": ["build", "test", "lint"]
    }
  }
}
```

**含义**：部署前必须完成构建、测试和代码检查

```
执行 turbo run deploy：

1. build、test、lint 并行执行
   ↓
2. 全部完成后，执行 deploy
```

**影响对比**：

```json
// ❌ 不配置 dependsOn
{
  "tasks": {
    "build": {},
    "test": {}
  }
}

// 执行：turbo run test
// 问题：test 可能在 build 之前执行，导致失败

// ✅ 配置 dependsOn
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"]
    }
  }
}

// 执行：turbo run test
// ✓ 保证先 build，再 test
```

### 1.4 outputs（输出缓存）

**作用**：指定任务的输出目录，用于缓存。

```json
{
  "tasks": {
    "build": {
      "outputs": ["dist/**", ".next/**", "build/**"]
    },
    "test": {
      "outputs": ["coverage/**"]
    }
  }
}
```

**Glob 模式**：

```json
{
  "tasks": {
    "build": {
      "outputs": [
        "dist/**", // dist 下所有文件
        ".next/**", // .next 下所有文件
        "!**/*.map", // 排除 .map 文件
        "build/**/*.js", // build 下所有 .js 文件
        ".vitepress/dist/**" // VitePress 输出
      ]
    }
  }
}
```

**影响对比**：

```bash
# 第一次构建
turbo run build
# ✓ shared 构建 → 生成 dist/
# ✓ Turborepo 缓存 dist/ 到 .turbo/cache/

# 修改了 shared/src/index.ts
turbo run build
# ✓ shared 代码改变 → 重新构建
# ✓ Turborepo 更新缓存

# 代码未改变
turbo run build
# ⚡ 检测到无变化
# ⚡ 从缓存恢复 dist/
# ⚡ 跳过构建，< 1秒完成
```

**缓存机制**：

```
构建流程：
1. Turborepo 计算输入哈希
   - 源代码文件
   - package.json
   - 依赖的包

2. 检查缓存
   - 哈希值匹配 → 恢复缓存
   - 哈希值不匹配 → 执行构建

3. 执行构建后
   - 保存 outputs 到缓存
   - 记录哈希值
```

**不配置 outputs 的影响**：

```json
// ❌ 不配置 outputs
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"]
      // 没有 outputs
    }
  }
}

// 问题：
// - 每次都重新构建
// - 无法利用缓存
// - 构建时间没有优化

// ✅ 配置 outputs
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}

// 优势：
// - 自动缓存构建结果
// - 未改变的代码跳过构建
// - 大幅节省时间
```

### 1.5 cache（是否缓存）

**作用**：控制任务是否使用缓存。

```json
{
  "tasks": {
    "build": {
      "cache": true, // 默认值，使用缓存
      "outputs": ["dist/**"]
    },
    "dev": {
      "cache": false // 不缓存（开发服务器）
    },
    "lint": {
      "cache": true // 缓存（加速 lint）
    }
  }
}
```

**影响对比**：

```json
// build 任务（cache: true）
{
  "tasks": {
    "build": {
      "cache": true,
      "outputs": ["dist/**"]
    }
  }
}

// 执行 turbo run build
// 第一次：90秒（实际构建）
// 第二次：< 1秒（使用缓存）✅

// dev 任务（cache: false）
{
  "tasks": {
    "dev": {
      "cache": false
    }
  }
}

// 执行 turbo run dev
// 每次都启动新的开发服务器
// 不使用缓存（符合预期）✅
```

**何时设置 `cache: false`**：

```json
{
  "tasks": {
    // ✅ 需要缓存的任务
    "build": { "cache": true },
    "test": { "cache": true },
    "lint": { "cache": true },

    // ❌ 不需要缓存的任务
    "dev": { "cache": false }, // 开发服务器
    "start": { "cache": false }, // 启动服务
    "clean": { "cache": false } // 清理任务
  }
}
```

### 1.6 persistent（持续运行）

**作用**：标记任务是否持续运行（如开发服务器）。

```json
{
  "tasks": {
    "dev": {
      "cache": false,
      "persistent": true // 持续运行，不会自动结束
    },
    "build": {
      "persistent": false // 默认值，构建完成后结束
    }
  }
}
```

**影响对比**：

```bash
# persistent: false（默认）
turbo run build
# ✓ 构建完成
# ✓ 任务结束
# ✓ 返回命令行

# persistent: true
turbo run dev
# ✓ 启动开发服务器
# ⏳ 持续运行...
# ⏳ 不会自动结束
# 需要 Ctrl+C 停止
```

**常见持续运行任务**：

```json
{
  "tasks": {
    "dev": {
      "cache": false,
      "persistent": true
    },
    "start": {
      "cache": false,
      "persistent": true
    },
    "preview": {
      "cache": false,
      "persistent": true
    },
    "watch": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### 1.7 inputs（输入文件）

**作用**：指定影响任务的输入文件，用于计算缓存哈希。

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "src/**", // src 下所有文件
        "package.json", // package.json
        "tsconfig.json", // tsconfig.json
        "!**/*.test.ts", // 排除测试文件
        "!**/*.spec.ts" // 排除 spec 文件
      ],
      "outputs": ["dist/**"]
    }
  }
}
```

**默认 inputs**：

```json
// 如果不指定 inputs，默认包含：
{
  "inputs": [
    "**/*", // 包目录下所有文件
    "!node_modules/**", // 排除 node_modules
    "!dist/**", // 排除输出目录
    "!.turbo/**" // 排除 turbo 缓存
  ]
}
```

**影响对比**：

```json
// ❌ 不配置 inputs（使用默认值）
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}

// 修改了 README.md
turbo run build
// ⚠️ 触发重新构建（README 不影响构建，但被包含在 inputs）

// ✅ 配置 inputs（精确控制）
{
  "tasks": {
    "build": {
      "inputs": ["src/**", "package.json", "tsconfig.json"],
      "outputs": ["dist/**"]
    }
  }
}

// 修改了 README.md
turbo run build
// ✅ 使用缓存（README 不在 inputs 中）

// 修改了 src/index.ts
turbo run build
// ✓ 重新构建（src 在 inputs 中）
```

**最佳实践**：

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "src/**/*.ts",
        "src/**/*.tsx",
        "!src/**/*.test.ts",
        "!src/**/*.spec.ts",
        "package.json",
        "tsconfig.json"
      ],
      "outputs": ["dist/**"]
    },
    "test": {
      "inputs": ["src/**/*.ts", "src/**/*.test.ts", "package.json"]
    },
    "lint": {
      "inputs": ["src/**/*.ts", "src/**/*.tsx", ".eslintrc.js"]
    }
  }
}
```

### 1.8 env（环境变量）

**作用**：指定影响任务的环境变量（用于缓存计算）。

```json
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV", "API_URL"],
      "outputs": ["dist/**"]
    }
  }
}
```

**影响对比**：

```bash
# ❌ 不配置 env
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}

NODE_ENV=development turbo run build
# ✓ 构建并缓存

NODE_ENV=production turbo run build
# ⚠️ 使用缓存（错误！环境变量变了，但使用了开发环境的缓存）

# ✅ 配置 env
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV"],
      "outputs": ["dist/**"]
    }
  }
}

NODE_ENV=development turbo run build
# ✓ 构建并缓存（development）

NODE_ENV=production turbo run build
# ✓ 重新构建（环境变量改变，缓存失效）
```

**常用环境变量**：

```json
{
  "tasks": {
    "build": {
      "env": [
        "NODE_ENV", // 环境（development/production）
        "API_URL", // API 地址
        "PUBLIC_KEY", // 公钥
        "VITE_*", // Vite 环境变量（通配符）
        "NEXT_PUBLIC_*" // Next.js 公共环境变量
      ],
      "outputs": ["dist/**"]
    }
  }
}
```

### 1.9 outputLogs（输出日志模式）

**作用**：控制任务的日志输出方式。

> [!TIP] 配置键名变更
>
> - **Turborepo 2.x**：使用 `outputLogs` 配置
> - **Turborepo 1.x**：使用 `outputMode` 配置
> - 命令行仍可使用 `--output-logs` 标志

```json
{
  "tasks": {
    "build": {
      "outputLogs": "hash-only"
    },
    "dev": {
      "outputLogs": "full"
    },
    "test": {
      "outputLogs": "new-only"
    }
  }
}
```

**可选值**：

| 值            | 说明           | 适用场景         |
| ------------- | -------------- | ---------------- |
| `full`        | 显示完整输出   | 开发服务器、调试 |
| `hash-only`   | 只显示任务哈希 | 构建、简洁输出   |
| `new-only`    | 只显示新的输出 | 测试、增量日志   |
| `errors-only` | 只显示错误     | CI/CD、生产构建  |
| `none`        | 不显示输出     | 静默模式         |

**影响对比**：

```bash
# outputLogs: "full"
turbo run build --output-logs=full

# 输出：
# packages/shared:
#   ✓ Building...
#   ✓ Compiled successfully
#   ✓ dist/index.js created
#   ✓ dist/index.d.ts created

# outputLogs: "hash-only"
turbo run build --output-logs=hash-only

# 输出：
# packages/shared: cache miss, executing abc123def

# outputLogs: "errors-only"
turbo run build --output-logs=errors-only

# 输出：
# （只有错误时才显示）
```

### 1.10 globalEnv

**作用**：定义全局环境变量（影响所有任务的缓存）。

```json
{
  "globalEnv": ["NODE_ENV", "CI"],
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}
```

**影响对比**：

```json
// ❌ 不配置 globalEnv
{
  "tasks": {
    "build": { "outputs": ["dist/**"] },
    "test": {},
    "lint": {}
  }
}

NODE_ENV=production turbo run build
# build 使用 production 环境

NODE_ENV=development turbo run build
# ⚠️ 可能使用缓存（NODE_ENV 未被追踪）

// ✅ 配置 globalEnv
{
  "globalEnv": ["NODE_ENV"],
  "tasks": {
    "build": { "outputs": ["dist/**"] },
    "test": {},
    "lint": {}
  }
}

NODE_ENV=production turbo run build
# ✓ 构建（production 环境）

NODE_ENV=development turbo run build
# ✓ 重新构建（NODE_ENV 改变，所有缓存失效）
```

**与 `env` 的区别**：

```json
{
  // globalEnv：影响所有任务
  "globalEnv": ["NODE_ENV", "CI"],

  "tasks": {
    "build": {
      // env：只影响 build 任务
      "env": ["API_URL"],
      "outputs": ["dist/**"]
    },
    "test": {
      // test 任务不受 API_URL 影响
      // 但受 NODE_ENV 和 CI 影响（globalEnv）
    }
  }
}
```

### 1.11 globalDependencies

**作用**：定义全局依赖文件（这些文件改变会使所有缓存失效）。

```json
{
  "globalDependencies": [".env", ".env.local", "tsconfig.json", ".eslintrc.js"],
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}
```

**影响对比**：

```bash
# ✅ 配置 globalDependencies
{
  "globalDependencies": ["tsconfig.json"],
  "tasks": {
    "build": { "outputs": ["dist/**"] }
  }
}

# 第一次构建
turbo run build
# ✓ 所有包构建完成，缓存

# 修改 tsconfig.json
turbo run build
# ✓ 所有包重新构建（globalDependencies 改变）

# 修改某个包的代码
turbo run build
# ✓ 只重新构建该包及其依赖（正常的增量构建）
```

**常用全局依赖**：

```json
{
  "globalDependencies": [
    // 环境配置
    ".env",
    ".env.local",
    ".env.production",

    // TypeScript 配置
    "tsconfig.json",
    "tsconfig.base.json",

    // 代码规范
    ".eslintrc.js",
    ".prettierrc",

    // 包管理
    "pnpm-workspace.yaml",
    "package.json" // 根目录的 package.json
  ]
}
```

## 二、完整推荐配置

### 2.1 基础 Monorepo 配置

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", "build/**"]
    },
    "lint": {
      "outputs": []
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### 2.2 完整配置（推荐）

```json
{
  "$schema": "https://turbo.build/schema.json",

  "globalEnv": ["NODE_ENV", "CI"],

  "globalDependencies": [".env", "tsconfig.json", ".eslintrc.js"],

  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": [
        "src/**/*.ts",
        "src/**/*.tsx",
        "!src/**/*.test.ts",
        "!src/**/*.spec.ts",
        "package.json",
        "tsconfig.json"
      ],
      "outputs": ["dist/**", ".next/**", ".vitepress/dist/**"],
      "env": ["API_URL", "PUBLIC_KEY"]
    },

    "dev": {
      "cache": false,
      "persistent": true,
      "outputLogs": "full"
    },

    "preview": {
      "cache": false,
      "persistent": true
    },

    "lint": {
      "dependsOn": ["^build"],
      "inputs": ["src/**/*.ts", "src/**/*.tsx", ".eslintrc.js"],
      "outputs": []
    },

    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**/*.ts", "src/**/*.test.ts", "src/**/*.spec.ts"],
      "outputs": ["coverage/**"]
    },

    "type-check": {
      "dependsOn": ["^build"],
      "inputs": ["src/**/*.ts", "src/**/*.tsx", "tsconfig.json"],
      "outputs": []
    },

    "clean": {
      "cache": false
    }
  }
}
```

### 2.3 Vite + Vue 3 项目配置

```json
{
  "$schema": "https://turbo.build/schema.json",

  "globalEnv": ["NODE_ENV"],

  "globalDependencies": ["tsconfig.json", "vite.config.ts"],

  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": [
        "src/**",
        "public/**",
        "index.html",
        "vite.config.ts",
        "package.json"
      ],
      "outputs": ["dist/**"],
      "env": ["VITE_*"]
    },

    "dev": {
      "cache": false,
      "persistent": true,
      "outputLogs": "full"
    },

    "preview": {
      "cache": false,
      "persistent": true
    },

    "lint": {
      "inputs": ["src/**/*.{ts,tsx,vue}", ".eslintrc.js"],
      "outputs": []
    },

    "lint:css": {
      "inputs": ["src/**/*.{css,scss,vue}", ".stylelintrc.js"],
      "outputs": []
    },

    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**", "vitest.config.ts"],
      "outputs": ["coverage/**"]
    },

    "type-check": {
      "dependsOn": ["^build"],
      "inputs": ["src/**/*.{ts,vue}", "tsconfig.json"],
      "outputs": []
    }
  }
}
```

### 2.4 Next.js 项目配置

```json
{
  "$schema": "https://turbo.build/schema.json",

  "globalEnv": ["NODE_ENV"],

  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**"],
      "env": ["NEXT_PUBLIC_*"]
    },

    "dev": {
      "cache": false,
      "persistent": true
    },

    "start": {
      "dependsOn": ["build"],
      "cache": false,
      "persistent": true
    },

    "lint": {
      "dependsOn": ["^build"],
      "outputs": []
    },

    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    }
  }
}
```

### 2.5 库开发配置

```json
{
  "$schema": "https://turbo.build/schema.json",

  "globalDependencies": ["tsconfig.json", "tsconfig.base.json"],

  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": [
        "src/**",
        "!src/**/*.test.ts",
        "!src/**/*.spec.ts",
        "package.json",
        "tsconfig.json",
        "vite.config.ts"
      ],
      "outputs": ["dist/**", "*.d.ts"]
    },

    "dev": {
      "dependsOn": ["^build"],
      "cache": false,
      "persistent": true
    },

    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**", "vitest.config.ts"],
      "outputs": ["coverage/**"]
    },

    "lint": {
      "inputs": ["src/**", ".eslintrc.js"]
    },

    "type-check": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "tsconfig.json"]
    },

    "prepublishOnly": {
      "dependsOn": ["build", "test", "lint"],
      "cache": false
    }
  }
}
```

## 三、常用命令

### 3.1 基础命令

```bash
# 运行单个任务
turbo run build

# 运行多个任务
turbo run build test lint

# 简写（不需要 run）
turbo build
turbo test
```

### 3.2 过滤选项

```bash
# 只构建特定包
turbo run build --filter=@my-monorepo/web

# 构建包及其依赖
turbo run build --filter=@my-monorepo/web...

# 构建包及其依赖者
turbo run build --filter=...@my-monorepo/shared

# 多个过滤条件
turbo run build --filter=@my-monorepo/web --filter=@my-monorepo/api

# 排除特定包
turbo run build --filter=!@my-monorepo/docs
```

### 3.3 缓存控制

```bash
# 强制重新执行（忽略缓存）
turbo run build --force

# 不写入缓存（但可读取）
turbo run build --no-cache

# 清理本地缓存
rm -rf .turbo

# 查看缓存使用情况
turbo run build --summarize
```

### 3.4 输出控制

```bash
# 显示完整输出
turbo run build --output-logs=full

# 只显示错误
turbo run build --output-logs=errors-only

# 只显示哈希
turbo run build --output-logs=hash-only

# 静默模式
turbo run build --output-logs=none
```

### 3.5 并行控制

```bash
# 限制并发数
turbo run build --concurrency=4

# 串行执行（不并行）
turbo run build --concurrency=1

# 使用所有 CPU 核心
turbo run build --concurrency=100%
```

### 3.6 调试和分析

```bash
# 显示执行计划
turbo run build --dry-run

# 生成依赖图
turbo run build --graph

# 生成 HTML 依赖图
turbo run build --graph=graph.html

# 显示详细日志
turbo run build --verbose

# 查看缓存信息
turbo run build --summarize
```

### 3.7 远程缓存

```bash
# 登录到远程缓存（Vercel）
turbo login

# 链接项目
turbo link

# 使用远程缓存构建
turbo run build

# 查看远程缓存使用情况
turbo run build --summarize
```

### 3.8 全局配置

```bash
# 查看 Turborepo 版本
turbo --version

# 更新 Turborepo
npm install -g turbo@latest

# 查看帮助
turbo --help
turbo run --help
```

## 四、常见问题和最佳实践

### 4.1 缓存未命中的原因

**问题**：每次都重新构建，缓存不生效。

**排查步骤**：

```bash
# 1. 查看详细日志
turbo run build --verbose

# 2. 查看缓存摘要
turbo run build --summarize

# 3. 检查 outputs 配置
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]  // 确保路径正确
    }
  }
}

# 4. 检查环境变量
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV"],  // 确保包含影响构建的环境变量
      "outputs": ["dist/**"]
    }
  }
}
```

**常见原因**：

```json
// ❌ 原因 1：outputs 路径错误
{
  "tasks": {
    "build": {
      "outputs": ["build/**"]  // 实际输出在 dist/
    }
  }
}

// ✅ 修复
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}

// ❌ 原因 2：缺少环境变量配置
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
      // 缺少 env: ["NODE_ENV"]
    }
  }
}

// ✅ 修复
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV"],
      "outputs": ["dist/**"]
    }
  }
}

// ❌ 原因 3：inputs 太宽泛
{
  "tasks": {
    "build": {
      "inputs": ["**/*"],  // 包含所有文件，包括 README、测试等
      "outputs": ["dist/**"]
    }
  }
}

// ✅ 修复
{
  "tasks": {
    "build": {
      "inputs": [
        "src/**",
        "package.json",
        "tsconfig.json"
      ],
      "outputs": ["dist/**"]
    }
  }
}
```

### 4.2 依赖顺序错误

**问题**：构建失败，提示找不到依赖的包。

**错误示例**：

```bash
# 执行构建
turbo run build

# 错误信息
Error: Cannot find module '@my-monorepo/shared'
```

**原因和解决方案**：

```json
// ❌ 错误：缺少 dependsOn
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
      // 没有 dependsOn
    }
  }
}

// 结果：web 可能在 shared 之前构建，导致找不到模块

// ✅ 正确：添加 dependsOn
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],  // 先构建依赖的包
      "outputs": ["dist/**"]
    }
  }
}

// 结果：
// 1. shared 先构建
// 2. ui 构建（等 shared 完成）
// 3. web 构建（等 ui 完成）
```

### 4.3 开发服务器冲突

**问题**：多个包的开发服务器端口冲突。

**解决方案**：

```json
// 方案 1：不同的端口
// packages/web/package.json
{
  "scripts": {
    "dev": "vite --port 3000"
  }
}

// packages/admin/package.json
{
  "scripts": {
    "dev": "vite --port 3001"
  }
}

// 方案 2：使用 filter
turbo run dev --filter=@my-monorepo/web
turbo run dev --filter=@my-monorepo/admin

// 方案 3：配置 persistent
{
  "tasks": {
    "dev": {
      "cache": false,
      "persistent": true  // 允许多个持续运行的任务
    }
  }
}
```

### 4.4 环境变量不生效

**问题**：改变环境变量后，仍使用旧的缓存。

**解决方案**：

```json
// ❌ 错误：未配置 env
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    }
  }
}

NODE_ENV=production turbo run build
# ⚠️ 可能使用 development 的缓存

// ✅ 正确：配置 env
{
  "tasks": {
    "build": {
      "env": ["NODE_ENV"],
      "outputs": ["dist/**"]
    }
  }
}

NODE_ENV=production turbo run build
# ✓ 正确地重新构建

// ✅ Vite/Next.js 项目
{
  "tasks": {
    "build": {
      "env": ["VITE_*", "NEXT_PUBLIC_*"],  // 使用通配符
      "outputs": ["dist/**"]
    }
  }
}
```

### 4.5 远程缓存配置

**配置远程缓存（Vercel）**：

```bash
# 1. 登录
turbo login

# 2. 链接项目
turbo link

# 3. 构建（自动使用远程缓存）
turbo run build
```

**团队协作**：

```
开发者 A：
1. turbo run build
2. 上传缓存到远程

开发者 B：
1. git pull
2. turbo run build
3. ⚡ 使用开发者 A 的远程缓存
4. 构建飞快！
```

**配置文件**：

```json
// turbo.json
{
  "remoteCache": {
    "signature": true // 启用缓存签名
  }
}
```

### 4.6 CI/CD 集成

**GitHub Actions**：

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install

      - name: Build
        run: pnpm turbo run build
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ secrets.TURBO_TEAM }}

      - name: Test
        run: pnpm turbo run test
```

**配置 secrets**：

```
GitHub Repository → Settings → Secrets

添加：
- TURBO_TOKEN（从 Vercel 获取）
- TURBO_TEAM（团队 ID）
```

### 4.7 最佳实践

#### 1. 合理配置 outputs

```json
{
  "tasks": {
    "build": {
      "outputs": [
        "dist/**",
        ".next/**",
        "!.next/cache/**", // 排除 Next.js 缓存
        "build/**",
        "!**/*.map" // 排除 source map
      ]
    }
  }
}
```

#### 2. 精确配置 inputs

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "src/**/*.{ts,tsx}",
        "!src/**/*.{test,spec}.{ts,tsx}", // 排除测试文件
        "package.json",
        "tsconfig.json"
      ],
      "outputs": ["dist/**"]
    }
  }
}
```

#### 3. 合理使用 dependsOn

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"] // 先构建依赖
    },
    "test": {
      "dependsOn": ["build"] // 先构建当前包
    },
    "deploy": {
      "dependsOn": ["build", "test", "lint"] // 部署前检查
    }
  }
}
```

#### 4. 开发任务配置

```json
{
  "tasks": {
    "dev": {
      "cache": false, // 不缓存
      "persistent": true, // 持续运行
      "outputLogs": "full" // 显示完整输出
    }
  }
}
```

#### 5. 环境变量管理

```json
{
  "globalEnv": ["NODE_ENV", "CI"],
  "tasks": {
    "build": {
      "env": [
        "VITE_*", // Vite 环境变量
        "NEXT_PUBLIC_*", // Next.js 公共变量
        "API_URL" // 自定义变量
      ]
    }
  }
}
```

#### 6. 忽略不必要的输入

```json
{
  "tasks": {
    "build": {
      "inputs": [
        "src/**",
        "!**/*.md", // 忽略 Markdown
        "!**/README*", // 忽略 README
        "!**/*.test.*", // 忽略测试
        "!**/__tests__/**" // 忽略测试目录
      ]
    }
  }
}
```

## 五、性能优化

### 5.1 缓存优化

```json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": [
        "src/**",
        "!src/**/*.test.ts" // 排除测试文件，避免不必要的缓存失效
      ],
      "outputs": [
        "dist/**",
        "!**/*.map" // 排除 source map，减小缓存体积
      ]
    }
  }
}
```

### 5.2 并行优化

```bash
# 根据 CPU 核心数调整并发
turbo run build --concurrency=$(nproc)

# 或者在 package.json 中配置
{
  "scripts": {
    "build": "turbo run build --concurrency=8"
  }
}
```

### 5.3 输出优化

```json
{
  "tasks": {
    "build": {
      "outputLogs": "errors-only" // CI 环境只显示错误
    },
    "dev": {
      "outputLogs": "full" // 开发环境显示完整输出
    }
  }
}
```

### 5.4 CI/CD 优化

```yaml
# GitHub Actions
- name: Cache Turborepo
  uses: actions/cache@v3
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-turbo-

- name: Build
  run: turbo run build --cache-dir=.turbo
```

## 六、与其他工具对比

### Turborepo vs Lerna

| 特性         | Turborepo         | Lerna           |
| ------------ | ----------------- | --------------- |
| **缓存**     | ✅ 强大的增量缓存 | ❌ 无内置缓存   |
| **远程缓存** | ✅ 支持           | ❌ 不支持       |
| **任务编排** | ✅ 自动           | ⚠️ 需要手动配置 |
| **性能**     | ⚡ 非常快         | ⚠️ 较慢         |
| **学习曲线** | ⭐⭐ 简单         | ⭐⭐⭐ 中等     |
| **版本管理** | ❌ 不支持         | ✅ 支持         |

**结论**：Turborepo 专注于构建性能，Lerna 专注于版本管理。可以结合使用。

### Turborepo vs Nx

| 特性           | Turborepo | Nx            |
| -------------- | --------- | ------------- |
| **配置复杂度** | ⭐⭐ 简单 | ⭐⭐⭐⭐ 复杂 |
| **缓存**       | ✅ 优秀   | ✅ 优秀       |
| **依赖图**     | ✅ 基础   | ✅ 强大       |
| **插件生态**   | ⚠️ 有限   | ✅ 丰富       |
| **性能**       | ⚡ 极快   | ⚡ 快         |
| **适用规模**   | 中小型    | 大型          |

**结论**：Turborepo 更轻量简单，Nx 功能更强大但复杂。

## 七、总结

### 必须配置的选项

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    }
  }
}
```

### 推荐配置

```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalEnv": ["NODE_ENV"],
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"],
      "env": ["API_URL"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {}
  }
}
```

### 关键要点

1. **`dependsOn: ["^build"]`** - 保证构建顺序
2. **`outputs`** - 启用缓存
3. **`cache: false`** - 开发任务不缓存
4. **`persistent: true`** - 持续运行的任务
5. **`env`** - 追踪环境变量
6. **`inputs`** - 精确控制输入文件

### 性能收益

```
不使用 Turborepo：
- 每次构建：90秒
- 每天 10 次构建
- 浪费：15分钟/天

使用 Turborepo：
- 首次：90秒
- 缓存命中：< 1秒
- 节省：约 13分钟/天

年节省：约 78小时 = 3.25天！
```

### 学习路径

1. **入门**：从基础配置开始
2. **优化**：添加 inputs、env 等
3. **进阶**：使用远程缓存
4. **团队**：CI/CD 集成
5. **调优**：根据项目优化配置

## 参考资源

- [Turborepo 官方文档](https://turborepo.com/)
- [Turborepo GitHub](https://github.com/vercel/turbo)
- [Monorepo 最佳实践](https://monorepo.tools/)
- [Vercel 远程缓存](https://vercel.com/docs/concepts/monorepos/remote-caching)

---

🎉 掌握 Turborepo，让你的 Monorepo 构建飞起来！
