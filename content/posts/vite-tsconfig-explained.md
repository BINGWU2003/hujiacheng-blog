---
title: "Vite 项目 tsconfig 配置文件深度解析笔记"
date: 2026-02-25
draft: false
description: ""
tags: ["tsconfig", "Vite"]
categories: ["笔记"]
---

## 一、 核心痛点与结论：为什么要拆分 3 个文件？

在现代前端工程（如 Vite + React/Vue）中，项目实际运行在**两个完全不同的环境**中：

1. **浏览器环境 (Browser)**：业务代码（`src/` 目录下），需要认识 DOM API（如 `window`、`document`）和 JSX，但**不应该**认识 Node.js API。
2. **Node.js 环境 (Node)**：构建配置代码（如 `vite.config.ts`），需要认识 Node.js API（如 `process`、`fs`、`__dirname`），但**不应该**认识 DOM API。

**结论**：如果只用一个 `tsconfig.json`，TypeScript 会把这两套类型合并，导致“类型污染”（例如在前端代码里写 `process.env` 不报错，但运行时页面白屏崩溃）。Vite 利用 TypeScript 的 **Project References（项目引用）** 功能将其拆分，实现了**运行环境的类型隔离**。

---

## 二、 三个配置文件的具体职责

### 1. `tsconfig.json` (总指挥 / 路由中心)

- **作用**：TS 编译器的入口文件。本身不包含编译规则。
- **核心配置**：通过 `"references"` 数组，引导 TS 语言服务去加载另外两个子配置文件，建立两个独立的虚拟项目。

### 2. `tsconfig.app.json` (前端业务代码专属)

- **作用**：专门为 `src` 目录下的浏览器端代码服务。
- **核心配置**：
- `"lib": ["ES2022", "DOM", "DOM.Iterable"]`：注入浏览器 DOM 类型。
- `"types": ["vite/client"]`：注入 Vite 客户端特有类型（如 `import.meta.env`）。
- `"include": ["src", "src/vite-env.d.ts"]`：**严格圈定**管辖范围只在 `src` 目录。

### 3. `tsconfig.node.json` (Node.js 配置代码专属)

- **作用**：专门为运行在 Node.js 环境下的配置脚本服务。
- **核心配置**：
- `"lib": ["ES2023"]`：提供现代 JS 语法支持（**无 DOM**）。
- `"types": ["node"]`：注入 Node.js API 类型。
- `"include": ["vite.config.ts", "src/vite-env.d.ts"]`：圈定管辖范围。

_(注：现代配置中通常还会包含 `"moduleResolution": "bundler"` 和 `"noEmit": true` 等顺应现代打包工具的最佳实践。)_

---

## 三、 底层运行机制：TS 是如何匹配配置的？

系统内部确定一个文件该用 `app` 还是 `node` 的规则，完全依赖于**路径匹配 (Glob Matching)**。

1. **工作原理**：当在编辑器打开一个文件时，TS 语言服务（TSServer）会拿着这个文件的路径，去各个子 `tsconfig` 的 `"include"` 和 `"exclude"` 列表中进行匹配。
2. **对号入座**：哪个配置文件的 `"include"` 包含了该文件，编辑器就用哪套规则来做类型检查。
3. **纠偏误区**：Vite 在开发（`npm run dev`）或极速打包时（依赖 esbuild/SWC），**基本不看**这三个文件进行类型检查。真正的类型把关是由编辑器（VS Code）的错误提示，以及打包前的 `tsc -b` 命令来执行的。

---

## 四、 实验记录：孤儿文件与“幽灵依赖”现象

通过将 `vite.config.ts` 从 `tsconfig.node.json` 的 `include` 中移除，我们验证了以下 TS 的底层行为：

### 1. “孤儿文件”现象与 Vite 类型丢失

当文件脱离了所有 `tsconfig` 的管辖时，它会丢失项目中通过 `"types"` 或 `include` 专门引入的自定义类型。

- **表现**：`ImportMetaEnv`（属于 Vite 专属类型）立刻报错，因为孤儿文件无法访问到 `node_modules/vite/client.d.ts`。

### 2. 贪婪扫描机制与幽灵依赖 (Phantom Dependencies)

当文件脱离管辖进入“全局默认模式”时，TS 会自动扫描项目中**所有的** `@types` 目录。

- **表现**：即使在 `package.json` 中 `uninstall @types/node`，`process` 变量依然没有报错。
- **根本原因**：构建工具（如 pnpm）为了满足其他底层依赖的运行，会在 `node_modules` 深处（如 `.pnpm/@types+node...`）保留 `@types/node`。TS 顺着目录树偷偷加载了这些全局声明（如 `globals.d.ts`）。

![5e550cb6-4e8d-4f39-b4c4-dac41ab7e39a](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/typora/5e550cb6-4e8d-4f39-b4c4-dac41ab7e39a.png)

### 3. 实验反思

这个实验完美证明了配置隔离的必要性。如果不利用 `tsconfig.app.json` 强行限制 `"types": ["vite/client"]` 和 `"include"`，TS 就会把 `node_modules` 深处的 Node 类型泄漏给前端业务代码，造成极其危险的类型假象。
