---
title: "Sentry Sourcemap 上传脚本说明"
date: 2026-01-19
draft: false
description: ""
tags: []
categories: ["笔记"]
---

本文档说明 `scripts/upload-sourcemap.js` 脚本的工作原理，以及为什么选择独立脚本而非 Vite 插件来上传 Sourcemap。

## 目录

- [1. 脚本概述](#1-脚本概述)
- [2. 脚本工作流程](#2-脚本工作流程)
- [3. 为什么使用独立脚本而非 Vite 插件](#3-为什么使用独立脚本而非-vite-插件)
- [4. 使用方法](#4-使用方法)
- [5. 配置说明](#5-配置说明)
- [6. 总结](#6-总结)
- [7. 完整源代码](#7-完整源代码)

---

## 1. 脚本概述

### 1.1 脚本功能

`scripts/upload-sourcemap.js` 是一个独立的 Node.js 脚本，用于将构建产物中的 Sourcemap 文件上传到 Sentry 错误监控平台。

**主要功能：**

- 创建 Sentry Release（版本）
- 注入 Debug IDs（用于关联源码）
- 上传 Sourcemap 文件到 Sentry
- 完成 Release（标记为已部署）
- 删除本地 Sourcemap 文件（防止源码泄露）

### 1.2 脚本位置

```
e:\code\DC_MES_WEB_SABER3\
├── scripts/
│   └── upload-sourcemap.js    ← 上传脚本
├── dist/
│   └── assets/
│       ├── xxx.js
│       └── xxx.js.map         ← Sourcemap 文件
└── .env.production            ← 环境变量配置
```

---

## 2. 脚本工作流程

### 2.1 执行流程图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  upload-sourcemap.js 执行流程                                                    │
│                                                                                  │
│  1️⃣ 解析命令行参数                                                              │
│     └── 获取 --mode 参数（默认 production）                                      │
│                                                                                  │
│  2️⃣ 加载环境变量                                                                │
│     └── 使用 Vite 的 loadEnv 加载对应环境的 .env 文件                           │
│                                                                                  │
│  3️⃣ 检查 dist 目录                                                              │
│     ├── 检查 dist/assets 是否存在                                               │
│     └── 检查是否有 .map 文件                                                    │
│                                                                                  │
│  4️⃣ 创建 Release                                                                │
│     └── sentry-cli releases new <release>                                       │
│                                                                                  │
│  5️⃣ 注入 Debug IDs                                                              │
│     └── sentry-cli sourcemaps inject ./dist                                     │
│     └── 在 JS 和 .map 文件中注入 debugId                                        │
│                                                                                  │
│  6️⃣ 上传 Sourcemap                                                              │
│     └── sentry-cli sourcemaps upload --release <release> ./dist                 │
│                                                                                  │
│  7️⃣ 完成 Release                                                                │
│     └── sentry-cli releases finalize <release>                                  │
│                                                                                  │
│  8️⃣ 删除本地 Sourcemap                                                          │
│     └── 删除 dist/assets/*.map 文件                                             │
│                                                                                  │
│  ✅ 完成                                                                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心代码解析

#### 命令行参数解析

```javascript
function parseArgs() {
  const args = process.argv.slice(2);
  const options = { mode: "production" };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--mode" || args[i] === "-m") {
      options.mode = args[i + 1];
      i++;
    }
  }
  return options;
}
```

#### 环境变量加载

```javascript
const { loadEnv } = require("vite");

// 加载对应环境的 .env 文件
const env = loadEnv(options.mode, rootDir, "");
Object.assign(process.env, env);
```

#### Sentry CLI 命令

```javascript
// 创建 Release
npx sentry-cli --auth-token xxx releases --org xxx --project xxx new mes_web@1.0.1-production

// 注入 Debug IDs
npx sentry-cli --auth-token xxx sourcemaps inject ./dist

// 上传 Sourcemap
npx sentry-cli --auth-token xxx sourcemaps upload --org xxx --project xxx --release xxx ./dist

// 完成 Release
npx sentry-cli --auth-token xxx releases --org xxx --project xxx finalize xxx
```

---

## 3. 为什么使用独立脚本而非 Vite 插件

### 3.1 方案对比

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  方案对比                                                                        │
│                                                                                  │
│  方案 A: Vite 插件（如 @sentry/vite-plugin）                                    │
│  ─────────────────────────────────────────────────                               │
│  vite build                                                                      │
│       │                                                                          │
│       ├── 构建代码                                                               │
│       ├── 生成 Sourcemap                                                         │
│       └── 【同步】上传 Sourcemap ← 在 closeBundle 钩子中执行                    │
│                                                                                  │
│                                                                                  │
│  方案 B: 独立脚本（当前方案）                                                    │
│  ──────────────────────────────                                                  │
│  vite build                                                                      │
│       │                                                                          │
│       ├── 构建代码                                                               │
│       └── 生成 Sourcemap                                                         │
│                                                                                  │
│  node scripts/upload-sourcemap.js                                                │
│       │                                                                          │
│       └── 【异步】上传 Sourcemap ← 构建完成后单独执行                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 选择独立脚本的原因

#### ❌ Vite 插件的问题

| 问题             | 说明                                     |
| ---------------- | ---------------------------------------- |
| **增加构建时间** | 上传操作与构建同步执行，网络慢时构建也慢 |
| **增加构建内存** | 插件需要在构建过程中维护额外状态         |
| **构建失败风险** | 网络问题导致上传失败时，整个构建也会失败 |
| **调试困难**     | 插件内的错误不易排查                     |
| **灵活性差**     | 无法单独重试上传，必须重新构建           |
| **CI/CD 复杂**   | 需要在所有环境安装完整的 Sentry 插件依赖 |

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  使用 Vite 插件时的问题场景                                                      │
│                                                                                  │
│  场景 1: 网络不稳定                                                              │
│  ─────────────────────                                                           │
│  vite build                                                                      │
│       │                                                                          │
│       ├── 构建成功 ✅                                                            │
│       └── 上传 Sourcemap...                                                      │
│           └── 网络超时 ❌                                                        │
│               └── 构建失败 💥                                                    │
│                   └── 需要重新构建（浪费 5 分钟）                                │
│                                                                                  │
│  场景 2: 内存紧张                                                                │
│  ─────────────────                                                               │
│  vite build                                                                      │
│       │                                                                          │
│       ├── 构建过程中...                                                          │
│       │   ├── 内存: 5.5GB                                                        │
│       │   └── Sentry 插件也在运行，占用额外内存                                  │
│       └── 💥 OOM (Out of Memory)                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

#### ✅ 独立脚本的优势

| 优势               | 说明                                   |
| ------------------ | -------------------------------------- |
| **构建与上传解耦** | 构建专注于构建，上传单独处理           |
| **不增加构建内存** | 构建时不加载 Sentry 相关依赖           |
| **失败可单独重试** | 上传失败不影响构建，可单独重试         |
| **灵活控制时机**   | 可以选择性上传（开发环境不上传）       |
| **易于调试**       | 脚本逻辑清晰，错误易排查               |
| **CI/CD 简单**     | 可以在不同阶段执行，甚至在不同机器执行 |

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  使用独立脚本的优势场景                                                          │
│                                                                                  │
│  场景 1: 上传失败可重试                                                          │
│  ───────────────────────                                                         │
│  vite build                                                                      │
│       └── 构建成功 ✅（产物已保存）                                              │
│                                                                                  │
│  node scripts/upload-sourcemap.js                                                │
│       └── 网络超时 ❌                                                            │
│                                                                                  │
│  node scripts/upload-sourcemap.js  ← 重试（无需重新构建）                        │
│       └── 上传成功 ✅                                                            │
│                                                                                  │
│                                                                                  │
│  场景 2: CI/CD 流水线                                                            │
│  ───────────────────                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                        │
│  │  构建阶段   │ ──→ │  部署阶段   │ ──→ │  上传阶段   │                        │
│  │  vite build │     │  deploy     │     │  upload-sm  │                        │
│  └─────────────┘     └─────────────┘     └─────────────┘                        │
│                                                                                  │
│  可以在部署成功后再上传 Sourcemap                                                │
│  避免部署失败时产生无用的 Release                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 内存优化角度

之前讨论过构建时的内存问题，独立脚本有助于内存优化：

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  构建过程内存对比                                                                │
│                                                                                  │
│  使用 Vite 插件:                                                                 │
│  ├── Vite 核心            ~500MB                                                │
│  ├── Rollup 打包          ~2GB                                                  │
│  ├── Sourcemap 生成       ~1GB                                                  │
│  └── Sentry 插件          ~200MB    ← 额外开销                                  │
│  ─────────────────────────────────                                               │
│  总计                     ~3.7GB                                                 │
│                                                                                  │
│  使用独立脚本:                                                                   │
│  构建阶段:                                                                       │
│  ├── Vite 核心            ~500MB                                                │
│  ├── Rollup 打包          ~2GB                                                  │
│  └── Sourcemap 生成       ~1GB                                                  │
│  ─────────────────────────────────                                               │
│  构建总计                 ~3.5GB                                                 │
│                                                                                  │
│  上传阶段（构建已完成，内存已释放）:                                             │
│  ├── Node.js 运行时       ~100MB                                                │
│  └── sentry-cli           ~50MB                                                 │
│  ─────────────────────────────────                                               │
│  上传总计                 ~150MB                                                 │
│                                                                                  │
│  ✅ 峰值内存减少 ~200MB                                                          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 使用方法

### 4.1 命令行使用

```bash
# 默认使用 production 环境变量
node scripts/upload-sourcemap.js

# 指定环境
node scripts/upload-sourcemap.js --mode production
node scripts/upload-sourcemap.js --mode staging
node scripts/upload-sourcemap.js -m development

# 查看帮助
node scripts/upload-sourcemap.js --help
```

### 4.2 package.json 脚本配置

```json
{
  "scripts": {
    "build:prod": "vite build --mode production",
    "upload:sourcemap": "node scripts/upload-sourcemap.js",
    "build:prod:sentry": "pnpm build:prod && pnpm upload:sourcemap"
  }
}
```

### 4.3 完整流程

```bash
# 方式 1: 分步执行
pnpm build:prod          # 先构建
pnpm upload:sourcemap    # 再上传

# 方式 2: 一键执行
pnpm build:prod:sentry   # 构建 + 上传
```

### 4.4 CI/CD 集成示例

```yaml
# GitHub Actions 示例
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pnpm install

      - name: Build
        run: pnpm build:prod

      - name: Deploy
        run: # 部署逻辑...

      # 部署成功后再上传 Sourcemap
      - name: Upload Sourcemap to Sentry
        if: success() # 只有部署成功才上传
        run: pnpm upload:sourcemap
```

---

## 5. 配置说明

### 5.1 环境变量

在 `.env.production` 文件中配置：

```bash
# Sentry 配置
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
VITE_SENTRY_ORG=your-org
VITE_SENTRY_PROJECT=mes_web
VITE_SENTRY_AUTH_TOKEN=sntrys_xxx
VITE_SENTRY_APP_VERSION=1.0.1
```

### 5.2 Release 版本格式

脚本会自动生成 Release 版本号：

```
格式: {SENTRY_PROJECT}@{SENTRY_APP_VERSION}-{mode}
示例: mes_web@1.0.1-production
```

### 5.3 注意事项

1. **Auth Token 权限**：需要 `project:releases` 权限
2. **构建顺序**：必须先构建（生成 .map 文件）再上传
3. **文件删除**：上传完成后会自动删除本地 .map 文件
4. **环境隔离**：不同环境使用不同的 Release 版本

---

## 6. 总结

### 为什么选择独立脚本？

| 考虑因素 | Vite 插件  | 独立脚本   |
| -------- | ---------- | ---------- |
| 构建时间 | 增加       | 不增加     |
| 构建内存 | 增加       | 不增加     |
| 失败影响 | 构建失败   | 不影响构建 |
| 重试能力 | 需重新构建 | 可单独重试 |
| 灵活性   | 低         | 高         |
| 调试难度 | 高         | 低         |

**核心原则**：构建和上传是两个独立的关注点，解耦后各自更加稳定可控。

---

## 7. 完整源代码

### scripts/upload-sourcemap.js

```javascript
#!/usr/bin/env node
/**
 * Sentry Sourcemap 上传脚本
 * 使用 Sentry CLI 上传 sourcemap
 *
 * 使用方法：
 * 1. 构建完成后运行: node scripts/upload-sourcemap.js
 * 2. 或在 CI/CD 中: pnpm build && pnpm upload:sourcemap
 *
 * 参考文档：https://docs.sentry.io/platforms/javascript/guides/vue/sourcemaps/uploading/cli/
 */

const { execSync } = require("child_process");
const { existsSync, rmSync, readdirSync } = require("fs");
const { join } = require("path");
const { loadEnv } = require("vite"); // 使用 Vite 的 loadEnv 加载环境变量

const rootDir = join(__dirname, ".."); // 调整为根目录
const distDir = join(rootDir, "dist");
const assetsDir = join(distDir, "assets");

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    mode: "production", // 默认值
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--mode" || arg === "-m") {
      options.mode = args[i + 1];
      i++;
    } else if (arg === "--help" || arg === "-h") {
      console.log(`
📖 使用说明:
  node scripts/upload-sourcemap.js [选项]
      `);
      process.exit(0);
    }
  }

  return options;
}

const options = parseArgs();

// 加载环境变量
// 第三个参数 '' 表示加载所有环境变量，包括 VITE_ 开头的
const env = loadEnv(options.mode, rootDir, "");
Object.assign(process.env, env);

// 获取配置（直接从环境变量读取）
const sentryConfig = ({ mode }) => {
  const SENTRY_MODE = mode;
  // 从环境变量中读取配置
  const SENTRY_AUTH_TOKEN = process.env.VITE_SENTRY_AUTH_TOKEN;
  const SENTRY_ORG = process.env.VITE_SENTRY_ORG;
  const SENTRY_PROJECT = process.env.VITE_SENTRY_PROJECT;
  const SENTRY_DSN = process.env.VITE_SENTRY_DSN;
  const SENTRY_APP_VERSION = process.env.VITE_SENTRY_APP_VERSION || "1.0.1";

  // Release 版本格式: mes_web@1.0.1-production
  const SENTRY_RELEASE = `${SENTRY_PROJECT}@${SENTRY_APP_VERSION}-${SENTRY_MODE}`;

  return {
    SENTRY_AUTH_TOKEN,
    SENTRY_ORG,
    SENTRY_PROJECT,
    SENTRY_DSN,
    SENTRY_MODE,
    SENTRY_APP_VERSION,
    SENTRY_RELEASE,
  };
};

const config = sentryConfig({ mode: options.mode });

// 检查 dist 目录
function checkDistDir() {
  if (!existsSync(assetsDir)) {
    console.error("❌ 未找到 dist/assets 目录，请先运行 pnpm build");
    process.exit(1);
  }

  const mapFiles = readdirSync(assetsDir).filter((f) => f.endsWith(".map"));
  if (mapFiles.length === 0) {
    console.error("❌ 未找到 sourcemap 文件，请确保构建时开启了 sourcemap");
    process.exit(1);
  }

  console.log(`📁 找到 ${mapFiles.length} 个 sourcemap 文件\n`);
}

// 执行命令
function runCommand(command, description) {
  console.log(`⏳ ${description}...`);
  try {
    execSync(command, { cwd: rootDir, stdio: "inherit" });
    console.log(`✅ ${description} 完成\n`);
  } catch (error) {
    console.error(`❌ ${description} 失败`);
    process.exit(1);
  }
}

// 删除 sourcemap 文件
function deleteSourcemaps() {
  console.log("🗑️  删除本地 sourcemap 文件...");
  const mapFiles = readdirSync(assetsDir).filter((f) => f.endsWith(".map"));
  mapFiles.forEach((file) => {
    rmSync(join(assetsDir, file));
  });
  console.log(`✅ 已删除 ${mapFiles.length} 个 sourcemap 文件\n`);
}

function main() {
  console.log("🚀 开始上传 Sourcemap 到 Sentry\n");
  console.log(`📋 配置信息:`);
  console.log(`   - 环境: ${options.mode}`);
  console.log(`   - 组织: ${config.SENTRY_ORG}`);
  console.log(`   - 项目: ${config.SENTRY_PROJECT}`);
  console.log(`   - 版本: ${config.SENTRY_RELEASE}\n`);

  // 检查 token 是否存在
  if (!config.SENTRY_AUTH_TOKEN) {
    console.error("❌ 错误: Sentry Auth Token 配置缺失！");
    process.exit(1);
  }

  // 1. 检查 dist 目录
  checkDistDir();

  // 构建 sentry-cli 基础命令（注意参数顺序：全局参数 -> 子命令 -> 子命令参数）
  const authToken = `--auth-token ${config.SENTRY_AUTH_TOKEN}`;
  const orgProject = `--org ${config.SENTRY_ORG} --project ${config.SENTRY_PROJECT}`;

  // 2. 创建 Release（这样 Sentry 后台就能立即看到新版本）
  runCommand(
    `npx sentry-cli ${authToken} releases ${orgProject} new ${config.SENTRY_RELEASE}`,
    "创建 Release",
  );

  // 3. 注入 Debug IDs
  runCommand(
    `npx sentry-cli ${authToken} sourcemaps inject ./dist`,
    "注入 Debug IDs",
  );

  // 4. 上传 sourcemap
  runCommand(
    `npx sentry-cli ${authToken} sourcemaps upload ${orgProject} --release ${config.SENTRY_RELEASE} ./dist`,
    "上传 Sourcemap",
  );

  // 5. 完成 Release（标记为已部署）
  runCommand(
    `npx sentry-cli ${authToken} releases ${orgProject} finalize ${config.SENTRY_RELEASE}`,
    "完成 Release",
  );

  // 6. 删除本地 sourcemap 文件（防止泄露源码）
  deleteSourcemaps();

  console.log("🎉 Sourcemap 上传完成！");
  console.log("📖 在 Sentry 项目设置 > Source Maps 中查看上传的文件");
  console.log(`📋 配置信息:`);
  console.log(`   - 环境: ${options.mode}`);
  console.log(`   - 组织: ${config.SENTRY_ORG}`);
  console.log(`   - 项目: ${config.SENTRY_PROJECT}`);
  console.log(`   - 版本: ${config.SENTRY_RELEASE}\n`);
}

main();
```

---

_文档更新时间：2026-01-19_
