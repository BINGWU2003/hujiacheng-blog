---
title: "Vite 环境变量与 TypeScript 配置实战笔记"
date: 2026-02-25
draft: false
description: ""
tags: ["Vite", "TypeScript"]
categories: ["笔记"]
---

## 1. 环境变量文件的加载与优先级

在 Vite 中，环境变量文件的加载遵循**“特定模式优先于通用配置”**的原则。如果多个文件中存在同名变量，高优先级的会覆盖低优先级的文件。

**优先级顺序（由高到低）：**

1. `.env.[mode].local` (最高优先级，如 `.env.development.local`，本地覆盖，不提交 Git)
2. `.env.[mode]` (如 `.env.development`，特定模式配置)
3. `.env.local` (通用本地覆盖，不提交 Git)
4. `.env` (最低优先级，所有模式都会加载的默认配置)

> **💡 结论：** 在 `dev`（开发）模式下，`.env.development` 中的同名变量会直接覆盖 `.env` 中的变量。

## 2. 如何读取环境变量

读取方式取决于代码运行的环境（客户端业务代码 vs Node.js 配置文件）。

### 2.1 在客户端代码中读取 (Vue / React / TS 文件)

使用 Vite 注入的 `import.meta.env` 对象读取。

- **安全限制：** 只有以 `VITE_` 开头的变量才会被暴露给客户端代码，防止敏感信息泄漏。
- **常用内置变量：**
- `import.meta.env.MODE`: 当前运行模式 (如 `'development'`)
- `import.meta.env.PROD`: 是否为生产环境 (boolean)
- `import.meta.env.DEV`: 是否为开发环境 (boolean)
- `import.meta.env.BASE_URL`: 部署的基础路径

```typescript
// 示例：在业务代码中直接读取
const apiUrl = import.meta.env.VITE_API_URL;
```

### 2.2 在 Vite 配置文件中读取 (`vite.config.ts`)

`vite.config.ts` 运行在 Node.js 环境中，此时 Vite 尚未启动完成，不能使用 `import.meta.env`，必须使用 `loadEnv` 函数手动加载。

```typescript
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // 加载环境变量 (参数: 模式, 根目录, 前缀)
  // 前缀传 '' 表示加载所有变量（包括系统变量），默认只加载 VITE_ 开头
  const env = loadEnv(mode, process.cwd(), "");

  return {
    // 可以在这里使用 env.VITE_API_URL 配置 proxy 等
  };
});
```

## 3. TypeScript 类型提示配置 (核心)

为了在输入 `import.meta.env.` 时获得 IDE 的智能提示（防拼写错误），需要通过扩展全局接口来标注其类型，并确保 TS 配置正确。

### 3.1 编写声明文件 (`vite-env.d.ts`)

在 `src/` 目录下创建或修改 `vite-env.d.ts`，扩展 Vite 内置的类型接口：

```typescript
/// <reference types="vite/client" />

// 1. 定义你自己的环境变量接口
interface ImportMetaEnv {
  /** * API 请求的基础路径
   * @example 'https://api.myapp.com'
   */
  readonly VITE_API_URL: string;

  /** 应用标题 */
  readonly VITE_APP_TITLE: string;
}

// 2. 标注 import.meta 的类型：将自定义接口合并到 ImportMeta 中
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

### 3.2 客户端代码中的类型提示与 `tsconfig` 排错

完成上述 `3.1` 的配置后，在你的 Vue/React 组件中，输入 `import.meta.env.` 时 IDE 就会自动补全 `VITE_API_URL`，且打错字会直接报错拦截。

**⚠️ 排错：如果业务代码里 `import.meta.env` 依然没有类型提示怎么办？**
这通常是因为 TS 编译器没有加载到你的 `.d.ts` 声明文件。你需要检查针对业务代码的 TS 配置文件（通常是 `tsconfig.json` 或较新模板中的 `tsconfig.app.json`），确保它的 `include` 数组包含了你的声明文件：

```json
// tsconfig.json 或 tsconfig.app.json
{
  "compilerOptions": { ... },
  // 必须包含 src 目录下的文件，以及你的声明文件
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "src/vite-env.d.ts"]
}

```

### 3.3 解决 `vite.config.ts` 中的 TS 报错 (ts2552)

在 `vite.config.ts`（Node环境）中复用 `ImportMetaEnv` 类型时，如果出现“找不到名称 ImportMetaEnv”的报错，是因为配置文件的 TS 作用域没有涵盖 `src/` 目录。

**解决方案：**
修改根目录下的 `tsconfig.node.json`，在 `include` 中加入声明文件路径：

```json
// tsconfig.node.json
{
  "compilerOptions": { ... },
  "include": ["vite.config.ts", "src/vite-env.d.ts"]
}

```

## 4. `vite.config.ts` 中的进阶避坑指南

### 4.1 给 `loadEnv` 增加类型提示

`loadEnv` 默认返回普通对象，可以通过类型断言获得提示：

```typescript
// 方式一：复用客户端声明 (会有内置变量提示，但易踩坑，见 4.2)
const env = loadEnv(mode, process.cwd(), "") as ImportMetaEnv;

// 方式二：单独定义普通 Interface (推荐，更严谨)
interface ViteEnv {
  VITE_API_URL: string;
}
const env = loadEnv(mode, process.cwd(), "") as unknown as ViteEnv;
```

### 4.2 ⚠️ 避坑：为什么 `loadEnv` 拿不到 `MODE`？

**现象：** 使用 `as ImportMetaEnv` 后，输入 `env.MODE` 有 TS 提示，但打印出来却是 `undefined`。
**原因：** `loadEnv` 的唯一作用是**读取硬盘上的 `.env` 文件**。而 `MODE`、`DEV` 等内置变量是 Vite 在编译时动态注入到业务代码里的，根本不在 `.env` 文件中。
**正解：** 在配置文件中，直接使用 `defineConfig` 回调参数提供的 `mode`。

```typescript
export default defineConfig(({ mode }) => {
  console.log("当前模式:", mode);
  const isDev = mode === "development";

  const env = loadEnv(mode, process.cwd(), "");
  // ...
});
```
