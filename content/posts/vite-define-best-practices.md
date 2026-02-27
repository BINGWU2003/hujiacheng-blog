---
title: "深度解析：Vite 配置中 `define` 的使用场景与实战指南"
date: 2026-02-27
draft: false
description: ""
tags: ["tsconfig", "Vite"]
categories: ["笔记"]
---

## 📌 1. 核心原理：什么是静态替换？

在 Vite (底层依赖 esbuild 和 Rollup) 中，`define` 的本质是**全局常量静态替换**。它不是在浏览器里挂载一个 `window.XXX` 变量，而是在**编译打包阶段**，像“查找并替换”一样，直接把代码里的标识符替换成具体的值。

**🔍 编译前后的直观对比：**
假设我们在 `vite.config.ts` 中配置了 `__APP_VERSION__: '"20260227.1200.abc1234"'`。

- **开发者的源码 (编译前)：**

```javascript
console.log("当前系统版本:", __APP_VERSION__);
```

- **Vite 打包后的产物 (编译后)：**

```javascript
// 变量名直接消失，变成了硬编码的字符串字面量
console.log("当前系统版本:", "20260227.1200.abc1234");
```

---

## 🛠️ 2. 典型配置项解析 (以 Vue-i18n 为例)

在许多使用 Vue 3 + `vue-i18n` 的项目中，常会看到如下配置，它们主要用于优化第三方库的构建体积：

```javascript
define: {
  __VUE_I18N_FULL_INSTALL__: true,  // 包含完整运行时和编译器
  __VUE_I18N_LEGACY_API__: false,   // 禁用 Vue2 语法，触发 Tree-shaking 减小体积
  __INTLIFY_PROD_DEVTOOLS__: false, // 生产环境关闭 Devtools 面板
}

```

---

## 🚀 3. 高阶实战：高频发版项目的自动化版本号注入

对于使用 CI/CD 流水线敏捷开发、高频发版的项目，每次手动修改 `package.json` 极易引发冲突。最佳实践是：**构建时根据时间戳和 Git Hash 自动生成版本号，再通过 `define` 注入到前端环境。**

### 步骤 1：编写版本号自动生成脚本

在项目根目录创建 `scripts/generate-version.js`，该脚本会在打包前运行，提取时间和当前 Git 短 Hash 生成唯一标识。

```javascript
#!/usr/bin/env node
/**
 * 版本号生成脚本
 * 格式: YYYYMMDD.HHmm.git短hash (例如: 20260119.1830.abc1234)
 */
const { execSync } = require("child_process");
const { writeFileSync } = require("fs");
const { join } = require("path");

const rootDir = join(__dirname, "..");
const versionFile = join(rootDir, ".version");

function getTimestamp() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  const hour = String(now.getHours()).padStart(2, "0");
  const minute = String(now.getMinutes()).padStart(2, "0");
  return `${year}${month}${day}.${hour}${minute}`;
}

function getGitHash() {
  try {
    return execSync("git rev-parse --short HEAD", {
      cwd: rootDir,
      encoding: "utf-8",
    }).trim();
  } catch {
    return "local";
  }
}

function main() {
  const version = `${getTimestamp()}.${getGitHash()}`;
  writeFileSync(versionFile, version, "utf-8");
  console.log(`✅ 版本号已生成: ${version} 并写入 .version 文件`);
}

main();
```

### 步骤 2：配置 `package.json` 执行构建钩子

让项目在执行 `build` 之前，先自动跑一遍上面的生成脚本：

```json
{
  "scripts": {
    "prebuild": "node scripts/generate-version.js",
    "build": "vite build"
  }
}
```

### 步骤 3：编写版本读取工具

由于 Vite 配置是基于 ESM 的，我们需要一个简单的工具来读取刚才生成的 `.version` 文件内容：

```javascript
// src/utils/readVersion.mjs
import { readFileSync, existsSync } from "fs";
import { join } from "path";

export function readVersion() {
  const versionFile = join(process.cwd(), ".version");
  if (existsSync(versionFile)) {
    return readFileSync(versionFile, "utf-8").trim();
  }
  return "dev";
}
```

### 步骤 4：在 `vite.config.ts` 中完成 `define` 注入

将读取到的版本号字符串，通过 `define` 正式注入！

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import { readVersion } from "./src/utils/readVersion.mjs";

export default defineConfig({
  define: {
    // 注入业务变量
    __APP_VERSION__: JSON.stringify(readVersion()),
  },
});
```

---

## 💻 4. 业务代码使用与 TS 类型补全

### 4.1 消除 TypeScript 报错 (前置工作)

因为 `__APP_VERSION__` 是静态替换的，TS 编译器并不知道它的存在。必须在 `src/vite-env.d.ts` 中进行全局声明：

```typescript
// src/vite-env.d.ts
/// <reference types="vite/client" />

declare const __VUE_I18N_FULL_INSTALL__: boolean;
declare const __VUE_I18N_LEGACY_API__: boolean;
declare const __INTLIFY_PROD_DEVTOOLS__: boolean;
declare const __APP_VERSION__: string;
```

### 4.2 在 Vue 组件 / Sentry 中直接使用

无需 `import`，任何地方都能直接用：

```html
<template>
  <div class="footer">
    <span class="version-tag">系统当前版本: v{{ currentVersion }}</span>
  </div>
</template>

<script setup lang="ts">
  import { ref } from "vue";
  const currentVersion = ref(__APP_VERSION__);
</script>
```

```typescript
// Sentry 监控初始化
Sentry.init({
  dsn: "your-dsn",
  release: __APP_VERSION__, // 报错时精准关联到具体的 Git commit 和时间
});
```

---

## 💡 5. 进阶认知：`define` vs `import.meta.env`

| 特性         | `define`                                        | `import.meta.env` (.env 文件)                  |
| ------------ | ----------------------------------------------- | ---------------------------------------------- |
| **设计初衷** | 替换任意全局常量、第三方库的特性开关。          | 注入项目自身的业务环境变量 (如 API 接口地址)。 |
| **使用方式** | `__APP_VERSION__`                               | `import.meta.env.VITE_API_URL`                 |
| **数据类型** | 支持复杂类型 (布尔值、对象)，替换为 JS 表达式。 | 默认全部解析为**字符串** (String)。            |
| **是否暴露** | 可以任意命名，无限制。                          | 只有以 `VITE_` 开头的变量才会打包进源码。      |

---

## ⚠️ 6. 避坑指南：为什么字符串必须用 `JSON.stringify`？

在配置 `define` 时，如果你的值是一个字符串，**绝对不能直接赋值纯字符串**，必须使用 `JSON.stringify()` 包裹。

**这是因为 `define` 执行的是“纯代码文本替换”：**

- ❌ **错误写法：**

```javascript
define: {
  __APP_VERSION__: "1.0.0";
}
```

**编译后果：** 代码中的 `const v = __APP_VERSION__` 会被直接替换成没有引号的代码 `const v = 1.0.0`。这会引发 JS 语法错误 `SyntaxError: Unexpected number`。

- ✅ **正确写法：**

```javascript
define: {
  __APP_VERSION__: JSON.stringify("1.0.0");
}
```

**编译后果：** `JSON.stringify` 会将其转换为带有双引号的字符串 `'"1.0.0"'`。代码中的 `const v = __APP_VERSION__` 会被替换成 `const v = "1.0.0"`，这才是合法且符合预期的 JS 字符串赋值。

_(注：布尔值如 `true`/`false` 本身就是合法的 JS 表达式，因此不需要使用 stringify 进行转义。)_
