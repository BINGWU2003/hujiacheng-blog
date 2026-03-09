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

`<script setup lang="ts">` 经过两步处理：

**第一步：`@vue/compiler-sfc` 编译 `<script setup>`**

```javascript
// 编译后的 script 模块
import { defineComponent as _defineComponent } from "vue";
import { ref, computed } from "vue";
import { useCounter } from "@/composables/useCounter";
import logoUrl from "@/assets/logo.png";

export default /* @__PURE__ */ _defineComponent({
  __name: "HelloWorld",
  props: {
    title: { type: String, required: true },
  },
  setup(__props) {
    const { count, increment } = useCounter();
    const doubleCount = computed(() => count.value * 2);
    return { count, increment, doubleCount };
  },
});
```

> 注意：`defineProps<Props>()` 的类型信息被编译为运行时的 `props` 选项，TypeScript 类型被移除。

**第二步：esbuild 移除 TypeScript 类型**

```javascript
// esbuild 处理后（TS → JS）
import { defineComponent } from "vue";
import { ref, computed } from "vue";
import { useCounter } from "@/composables/useCounter";
import logoUrl from "@/assets/logo.png";

export default defineComponent({
  __name: "HelloWorld",
  props: {
    title: { type: String, required: true },
  },
  setup(__props) {
    const { count, increment } = useCounter();
    const doubleCount = computed(() => count.value * 2);
    return { count, increment, doubleCount };
  },
});
```

### 2.4 阶段三：Template 编译

`@vue/compiler-dom` 将模板编译为 `render` 函数：

```javascript
import {
  toDisplayString as _toDisplayString,
  createElementVNode as _createElementVNode,
  openBlock as _openBlock,
  createElementBlock as _createElementBlock,
} from "vue";

// 静态提升：不依赖响应式数据的节点在模块作用域创建，避免重复创建
const _hoisted_1 = { class: "hello-world" };
const _hoisted_2 = ["src"]; // 动态属性的 key 列表

function render(_ctx, _cache, $props, $setup) {
  return (
    _openBlock(),
    _createElementBlock("div", _hoisted_1, [
      _createElementVNode("h1", null, _toDisplayString($props.title), 1),
      _createElementVNode(
        "p",
        { class: "count" },
        "Count: " + _toDisplayString($setup.count),
        1,
      ),
      _createElementVNode("button", { onClick: $setup.increment }, "+1"),
      _createElementVNode(
        "img",
        { src: $setup.logoUrl, alt: "Logo" },
        null,
        8,
        _hoisted_2,
      ),
    ])
  );
}
```

> [!NOTE] 模板编译优化
>
> - **静态提升**：`_hoisted_1` 等静态节点被提升到模块顶层，只创建一次
> - **PatchFlag**：末尾的数字 `1`、`8` 是更新标记，告诉 Vue 只需 diff 哪些部分
> - **Tree-flattening**：`_openBlock` + `_createElementBlock` 实现块级追踪

### 2.5 阶段四：Scoped Style 编译

```css
/* 原始 SCSS */
@use "@/styles/variables" as *;

.hello-world {
  padding: $spacing-md;
  h1 {
    color: $primary-color;
  }
}
```

**第一步：Sass 编译** — 解析变量、嵌套、函数

```css
.hello-world {
  padding: 16px;
}
.hello-world h1 {
  color: #42b883;
}
.hello-world .count {
  color: #666;
}
.hello-world button {
  background: #42b883;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.hello-world button:hover {
  background: #339068;
}
```

**第二步：Scoped 处理** — 添加 `data-v-xxxx` 属性选择器

```css
.hello-world[data-v-7a3f4c2e] {
  padding: 16px;
}
.hello-world h1[data-v-7a3f4c2e] {
  color: #42b883;
}
.hello-world .count[data-v-7a3f4c2e] {
  color: #666;
}
.hello-world button[data-v-7a3f4c2e] {
  background: #42b883;
}
.hello-world button[data-v-7a3f4c2e]:hover {
  background: #339068;
}
```

### 2.6 最终合并输出

经过上述阶段，一个 `.vue` 文件最终变为一个 JS 模块：

```javascript
// HelloWorld.vue 最终编译产物（简化）
import {
  defineComponent,
  toDisplayString,
  createElementVNode,
  openBlock,
  createElementBlock,
} from "vue";
import { useCounter } from "./composables/useCounter.js";
import logoUrl from "./assets/logo-a1b2c3d4.png";

const _hoisted_1 = { class: "hello-world" };

export default defineComponent({
  __name: "HelloWorld",
  props: { title: { type: String, required: true } },
  setup(__props) {
    const { count, increment } = useCounter();
    return (_ctx, _cache) => {
      return (
        openBlock(),
        createElementBlock("div", _hoisted_1, [
          createElementVNode("h1", null, toDisplayString(__props.title), 1),
          createElementVNode(
            "p",
            { class: "count" },
            "Count: " + toDisplayString(count.value),
            1,
          ),
          createElementVNode("button", { onClick: increment }, "+1"),
          createElementVNode("img", { src: logoUrl, alt: "Logo" }, null, 8, [
            "src",
          ]),
        ])
      );
    };
  },
});
```

CSS 则被提取到独立的 `.css` 文件中。

---

## 3. TypeScript 文件的转换

### 3.1 原始 TypeScript 文件

```typescript
// src/composables/useCounter.ts
import { ref, type Ref } from "vue";

interface CounterOptions {
  initial?: number;
  step?: number;
}

interface CounterReturn {
  count: Ref<number>;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

export function useCounter(options: CounterOptions = {}): CounterReturn {
  const { initial = 0, step = 1 } = options;
  const count = ref(initial);

  const increment = (): void => {
    count.value += step;
  };

  const decrement = (): void => {
    count.value -= step;
  };

  const reset = (): void => {
    count.value = initial;
  };

  return { count, increment, decrement, reset };
}
```

### 3.2 esbuild 转换（仅移除类型，不做类型检查）

```javascript
// esbuild 输出
import { ref } from "vue";

export function useCounter(options = {}) {
  const { initial = 0, step = 1 } = options;
  const count = ref(initial);

  const increment = () => {
    count.value += step;
  };

  const decrement = () => {
    count.value -= step;
  };

  const reset = () => {
    count.value = initial;
  };

  return { count, increment, decrement, reset };
}
```

> [!IMPORTANT] esbuild 做了什么
>
> - ✅ 移除 `interface`、`type`、类型注解（`: Ref<number>`、`: void`）
> - ✅ 移除 `type` 前缀导入（`type Ref`）
> - ❌ **不做类型检查**（`tsc --noEmit` 需要单独运行）
> - ❌ **不做 enum 内联**（`const enum` 除外）

### 3.3 Rollup Tree Shaking 后

假设项目中只使用了 `useCounter` 的 `count` 和 `increment`：

```javascript
// Tree Shaking 后，decrement 和 reset 仍然保留
// 因为它们在 return 对象中被引用，Rollup 无法确定外部是否使用
export function useCounter(options = {}) {
  const { initial = 0, step = 1 } = options;
  const count = ref(initial);
  const increment = () => {
    count.value += step;
  };
  const decrement = () => {
    count.value -= step;
  };
  const reset = () => {
    count.value = initial;
  };
  return { count, increment, decrement, reset };
}
```

> ⚠️ 对象返回值中的属性无法被 Tree Shake，因为它们是动态可达的。只有顶层 `export` 的未引用绑定才会被移除。

---

## 4. CSS/SCSS 的处理流程

### 4.1 SCSS 源文件

```scss
// src/styles/variables.scss
$primary-color: #42b883;
$secondary-color: #35495e;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;

// src/styles/main.scss
@use "variables" as *;

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: $secondary-color;
  line-height: 1.6;
}

:root {
  --primary: #{$primary-color};
  --spacing: #{$spacing-md};
}
```

### 4.2 Sass 编译

```css
/* Sass 输出：变量内联，嵌套展开 */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #35495e;
  line-height: 1.6;
}

:root {
  --primary: #42b883;
  --spacing: 16px;
}
```

### 4.3 PostCSS 处理（如已配置）

```css
/* PostCSS + autoprefixer 输出 */
*,
*::before,
*::after {
  -webkit-box-sizing: border-box;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
/* ... */
```

### 4.4 最终压缩

```css
/* 生产构建最终输出（单行压缩） */
*,
::before,
::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family:
    -apple-system,
    BlinkMacSystemFont,
    Segoe UI,
    Roboto,
    sans-serif;
  color: #35495e;
  line-height: 1.6;
}
:root {
  --primary: #42b883;
  --spacing: 16px;
}
```

> 多个组件的 Scoped CSS 会被合并到同一个 `.css` chunk 中，按模块被引入的顺序排列。

---

## 5. 静态资源的处理

### 5.1 导入方式与最终产物对照

```typescript
// 源码中的导入方式
import logoUrl from "./assets/logo.png"; // → 返回 URL 字符串
import iconRaw from "./assets/icon.svg?raw"; // → 返回 SVG 文本内容
import styles from "./styles/mod.module.css"; // → 返回 CSS Modules 对象
```

### 5.2 小文件 → Base64 内联

默认阈值为 **4KB**（`assetsInlineLimit: 4096`）。

```javascript
// 源码
import smallIcon from "./assets/tiny-icon.png"; // 2KB 文件

// 构建后
const smallIcon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...";
```

> 内联减少 HTTP 请求，但会增大 JS bundle 体积约 33%（Base64 编码膨胀）。

### 5.3 大文件 → 独立输出 + 内容哈希

```javascript
// 源码
import logo from "./assets/logo.png"; // 50KB 文件

// 构建后
const logo = "/assets/logo-a1b2c3d4.png";
// 文件被复制到 dist/assets/logo-a1b2c3d4.png
```

文件名中的哈希值基于文件内容生成，内容不变则哈希不变，可实现**强缓存**。

### 5.4 特殊资源处理

| 导入后缀  | 行为                   | 示例                               |
| --------- | ---------------------- | ---------------------------------- |
| 默认      | 返回解析后的 URL       | `import img from './a.png'`        |
| `?url`    | 强制返回 URL（不内联） | `import url from './a.svg?url'`    |
| `?raw`    | 返回原始文件文本内容   | `import svg from './a.svg?raw'`    |
| `?inline` | 强制内联为 Base64      | `import b64 from './a.png?inline'` |
| `?worker` | 作为 Web Worker 导入   | `import W from './w.js?worker'`    |

---

## 6. 代码分割与 Chunk 生成

### 6.1 自动分割：动态导入

```typescript
// src/router/index.ts
const routes = [
  { path: "/", component: () => import("../views/Home.vue") },
  { path: "/about", component: () => import("../views/About.vue") },
];
```

每个 `import()` 调用生成一个独立异步 chunk：

```
dist/assets/
├── index-a1b2c3d4.js        # 入口 chunk（包含 router、App.vue）
├── Home-b2c3d4e5.js         # Home 页面 chunk
├── About-c3d4e5f6.js        # About 页面 chunk
└── vendor-vue-d4e5f6g7.js   # Vue 运行时（manualChunks 或自动提取）
```

### 6.2 Vendor 分离（manualChunks）

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ["vue", "vue-router"],
          lodash: ["lodash-es"],
        },
      },
    },
  },
});
```

效果：

```
dist/assets/
├── index-xxxx.js        # 业务代码
├── vue-xxxx.js          # Vue + Vue Router（不常变动，长缓存）
├── lodash-xxxx.js       # lodash（不常变动，长缓存）
└── About-xxxx.js        # 异步页面
```

### 6.3 Chunk 之间的依赖关系

```
index.html
  └─→ index-xxxx.js（入口）
        ├─→ vue-xxxx.js（同步依赖，modulepreload）
        ├─→ lodash-xxxx.js（同步依赖，modulepreload）
        └─→ About-xxxx.js（动态依赖，用户导航时加载）
              └─→ vue-xxxx.js（共享依赖，已缓存）
```

---

## 7. 最终产物结构

### 7.1 dist 目录

```
dist/
├── index.html                          # 注入了资源引用的 HTML
├── assets/
│   ├── index-a1b2c3d4.js              # 主入口 JS
│   ├── index-a1b2c3d4.css             # 主样式
│   ├── vendor-vue-e5f6g7h8.js         # Vue 运行时
│   ├── About-i9j0k1l2.js             # 异步页面 chunk
│   ├── About-i9j0k1l2.css            # 异步页面样式
│   └── logo-m3n4o5p6.png             # 静态资源
└── favicon.ico
```

### 7.2 HTML 注入

**构建前**：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>My App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

**构建后**：

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
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

> [!NOTE] HTML 注入的资源
>
> 1. **主入口 JS**：`<script type="module">` 异步加载
> 2. **modulepreload**：预加载关键依赖（vendor chunk），提升加载速度
> 3. **CSS**：同步加载，避免 FOUC（无样式内容闪烁）
> 4. 原始的 `<script src="/src/main.ts">` 被移除

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
