---
title: "Vite 打包全流程可视化：从源码到产物"
date: 2026-02-02
draft: false
description: ""
tags: []
categories: ["笔记"]
---

本文档通过具体的项目代码示例，可视化展示 Vite 打包过程中每一步的代码转换，让你真正理解"代码是怎么变的"。

## 目录

- [1. 项目结构示例](#1-项目结构示例)
- [2. Vue SFC 文件的完整转换](#2-vue-sfc-文件的完整转换)
- [3. TypeScript 文件的转换](#3-typescript-文件的转换)
- [4. CSS/SCSS 的处理流程](#4-cssscss-的处理流程)
- [5. 静态资源的处理](#5-静态资源的处理)
- [6. 代码分割与 Chunk 生成](#6-代码分割与-chunk-生成)
- [7. 最终产物结构](#7-最终产物结构)
- [8. 完整构建流程图](#8-完整构建流程图)

---

## 1. 项目结构示例

我们以一个典型的 Vue 3 + TypeScript 项目为例：

```
src/
├── main.ts                 # 入口文件
├── App.vue                 # 根组件
├── components/
│   ├── HelloWorld.vue      # 普通组件
│   └── LazyComponent.vue   # 懒加载组件
├── composables/
│   └── useCounter.ts       # 组合式函数
├── styles/
│   ├── variables.scss      # SCSS 变量
│   └── main.scss           # 全局样式
├── assets/
│   ├── logo.png            # 图片资源
│   └── icon.svg            # SVG 图标
└── utils/
    └── helpers.ts          # 工具函数
```

---

## 2. Vue SFC 文件的完整转换

### 2.1 原始 Vue 文件

```vue
<!-- src/components/HelloWorld.vue -->
<template>
  <div class="hello-world">
    <h1>{{ title }}</h1>
    <p class="count">Count: {{ count }}</p>
    <button @click="increment">+1</button>
    <img :src="logoUrl" alt="Logo" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useCounter } from "@/composables/useCounter";
import logoUrl from "@/assets/logo.png";

interface Props {
  title: string;
}

const props = defineProps<Props>();
const { count, increment } = useCounter();

const doubleCount = computed(() => count.value * 2);
</script>

<style scoped lang="scss">
@use "@/styles/variables" as *;

.hello-world {
  padding: $spacing-md;

  h1 {
    color: $primary-color;
    font-size: 24px;
  }

  .count {
    color: #666;
  }

  button {
    background: $primary-color;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;

    &:hover {
      background: darken($primary-color, 10%);
    }
  }
}
</style>
```

### 2.2 阶段一：SFC 解析（@vitejs/plugin-vue）

Vite 使用 `@vue/compiler-sfc` 将 `.vue` 文件拆分成三个部分：

```typescript
// 解析后的 SFC 描述对象
{
  filename: '/src/components/HelloWorld.vue',
  source: '原始文件内容...',
  template: {
    type: 'template',
    content: '<div class="hello-world">...</div>',
    loc: { start: { line: 2 }, end: { line: 9 } },
    attrs: {},
    ast: { /* 模板 AST */ }
  },
  script: null,  // 没有普通 script
  scriptSetup: {
    type: 'script',
    content: "import { ref, computed } from 'vue'...",
    loc: { start: { line: 11 }, end: { line: 23 } },
    attrs: { setup: true, lang: 'ts' },
  },
  styles: [{
    type: 'style',
    content: '@use "@/styles/variables" as *;...',
    loc: { start: { line: 25 }, end: { line: 50 } },
    attrs: { scoped: true, lang: 'scss' },
    scoped: true,
    lang: 'scss'
  }],
  customBlocks: [],
  cssVars: [],
  slotted: false
}
```

### 2.3 阶段二：Script 编译

`

</body>
</html>
```

**构建后**：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My App</title>
    <script type="module" crossorigin src="/assets/index-a1b2c3d4.js"></script>
    <link
      rel="modulepreload"
      crossorigin
      href="/assets/vendor-vue-e5f6g7h8.js"
    />
    <link rel="stylesheet" crossorigin href="/assets/index-a1b2c3d4.css" />
  </head>
  <body>
    <div id="app"></div>
  </body>
</html>
```

:::info HTML 注入的资源

1. **主入口 JS**：`<script type="module">` 异步加载
2. **modulepreload**：预加载关键依赖，提升加载速度
3. **CSS**：同步加载，避免 FOUC（无样式内容闪烁）
   :::

---

## 8. 完整构建流程图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Vite Build 完整流程                                │
└─────────────────────────────────────────────────────────────────────────────┘

源文件                    处理阶段                           输出
━━━━━━                    ━━━━━━                            ━━━━

                         ┌─────────────┐
.vue 文件 ──────────────→│ Vue Plugin  │
                         │ (SFC 解析)   │
                         └──────┬──────┘
                                │
                    ┌───────────┼───────────┐
                    ↓           ↓           ↓
              ┌─────────┐ ┌─────────┐ ┌─────────┐
              │ Template│ │ Script  │ │ Style   │
              │ Compiler│ │ Compiler│ │ Compiler│
              └────┬────┘ └────┬────┘ └────┬────┘
                   │           │           │
                   ↓           ↓           ↓
              render()    JS Module    CSS Module
                   │           │           │
                   └───────────┴───────────┘
                               │
                               ↓
                    ┌─────────────────┐
.ts 文件 ──────────→│    esbuild      │────→ JS (类型已移除)
                    │ (TS → JS 转换)   │
                    └─────────────────┘
                               │
                               ↓
                    ┌─────────────────┐
.scss 文件 ────────→│   Sass/Less     │────→ CSS
                    │ (预处理器编译)   │
                    └─────────────────┘
                               │
                               ↓
                    ┌─────────────────────────────────┐
                    │           Rollup                 │
                    │  ┌─────────────────────────┐    │
                    │  │ 1. 依赖解析 (resolveId)  │    │
                    │  │ 2. 模块加载 (load)       │    │
所有模块 ──────────→│  │ 3. 模块转换 (transform)  │    │
                    │  │ 4. 依赖图构建            │    │
                    │  │ 5. Tree Shaking         │    │
                    │  │ 6. 代码分割             │    │
                    │  │ 7. Chunk 生成           │    │
                    │  └─────────────────────────┘    │
                    └─────────────────────────────────┘
                               │
                               ↓
                    ┌─────────────────┐
                    │    Minify       │
                    │ (esbuild/terser)│
                    └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ↓                     ↓
              ┌──────────┐         ┌──────────┐
              │ JS Chunks │         │CSS Chunks│
              └──────────┘         └──────────┘
                    │                     │
                    ↓                     ↓
              ┌─────────────────────────────┐
              │         dist/assets/        │
              │ ├── index-xxxx.js          │
              │ ├── index-xxxx.css         │
              │ ├── vendor-xxxx.js         │
              │ ├── About-xxxx.js          │
              │ └── ...                    │
              └─────────────────────────────┘
                               │
                               ↓
                    ┌─────────────────┐
index.html ────────→│  HTML Plugin    │────→ dist/index.html
                    │ (资源注入)       │      (带有正确的资源引用)
                    └─────────────────┘

图片/字体 ─────────→ 复制/处理/hash ──────→ dist/assets/xxx-xxxx.png
```

### 8.1 各文件类型转换速查表

| 源文件           | 处理器             | 中间产物      | 最终产物                   |
| ---------------- | ------------------ | ------------- | -------------------------- |
| `.vue`           | @vitejs/plugin-vue | JS + CSS 模块 | `.js` chunk + `.css` chunk |
| `.ts/.tsx`       | esbuild            | JS (无类型)   | 合并到 `.js` chunk         |
| `.js/.jsx`       | esbuild            | JS (转换语法) | 合并到 `.js` chunk         |
| `.scss/.sass`    | sass               | CSS           | 合并到 `.css` chunk        |
| `.less`          | less               | CSS           | 合并到 `.css` chunk        |
| `.css`           | PostCSS (可选)     | CSS           | 合并到 `.css` chunk        |
| `.png/.jpg` (大) | -                  | -             | 独立文件 + hash            |
| `.png/.jpg` (小) | -                  | base64        | 内联到 JS                  |
| `.svg`           | -                  | -             | 独立文件 或 内联           |
| `.json`          | -                  | JS 对象       | 内联到 JS                  |
| `.wasm`          | -                  | -             | 独立文件                   |

### 8.2 Vite 插件钩子执行顺序

```
构建阶段                 钩子名称              执行内容
━━━━━━                  ━━━━━━              ━━━━━━

配置阶段
  │
  ├─── config ─────────→ 修改/扩展 Vite 配置
  │
  ├─── configResolved ─→ 读取最终配置
  │
构建阶段
  │
  ├─── buildStart ────→ 构建开始，初始化资源
  │
  │    ┌─────────────────────────────────┐
  │    │  对每个模块循环执行：              │
  │    │                                  │
  │    │  resolveId ──→ 解析模块路径       │
  │    │      ↓                           │
  │    │  load ───────→ 加载模块内容       │
  │    │      ↓                           │
  │    │  transform ──→ 转换模块代码       │
  │    │      ↓                           │
  │    │  moduleParsed → 模块解析完成      │
  │    │                                  │
  │    └─────────────────────────────────┘
  │
  ├─── buildEnd ──────→ 所有模块处理完成
  │
生成阶段
  │
  ├─── renderStart ───→ 开始生成 bundle
  │
  ├─── renderChunk ───→ 处理每个 chunk
  │
  ├─── generateBundle → 生成最终 bundle
  │
  ├─── writeBundle ───→ 写入文件系统
  │
  └─── closeBundle ───→ 构建完成，清理资源
```

---

## 总结

通过本文档，你应该对 Vite 打包过程有了直观的理解：

### 核心转换过程

1. **Vue SFC**：拆分 → 编译模板/脚本/样式 → 合并为 JS 模块
2. **TypeScript**：esbuild 移除类型 → Rollup Tree Shaking → 压缩
3. **CSS/SCSS**：预处理器编译 → PostCSS → 压缩 → 提取到独立文件
4. **静态资源**：小文件内联，大文件独立输出并添加 hash

### 关键优化点

1. **静态提升**：模板中的静态内容在编译时提取
2. **Tree Shaking**：未使用的导出被移除
3. **代码分割**：动态导入自动生成独立 chunk
4. **资源优化**：小文件内联减少请求，hash 确保缓存有效

> 理解构建过程有助于编写更优化的代码，也能更好地排查构建问题。
