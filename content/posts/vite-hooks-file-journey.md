---
title: "Vue 项目文件的构建之旅：逐钩子追踪 Vite 打包全过程"
date: 2026-03-09
draft: false
description: "以一个 Vue 3 项目为例，逐个追踪每种文件（.vue、.ts、.scss、图片）在 Vite/Rollup 各钩子阶段中经历了什么处理、发生了什么变化、最终变成了什么样子"
tags: ["Vite", "Vue", "构建工具", "前端工程化"]
categories: ["笔记"]
---

本文以一个真实的 Vue 3 + TypeScript + SCSS 项目为样本，**逐钩子、逐文件类型**地追踪 `npm run build` 之后每个文件到底经历了什么。

> **阅读前提：** 如果你还不了解 Vite 钩子的分类和整体执行顺序，建议先阅读 [Vite 构建流程详解：从命令到产物](/posts/vite-build-process/)。

---

## 示例项目结构

```
src/
├── main.ts                  # 入口
├── App.vue                  # 根组件
├── router/index.ts          # 路由配置
├── views/
│   ├── Home.vue             # 首页（同步加载）
│   └── About.vue            # 关于页（懒加载）
├── components/
│   └── UserCard.vue         # 通用组件
├── composables/
│   └── useUser.ts           # 组合式函数
├── styles/
│   ├── _variables.scss      # SCSS 变量
│   └── global.scss          # 全局样式
├── assets/
│   ├── logo.png             # 图片（< 4KB）
│   └── banner.jpg           # 图片（> 4KB）
└── utils/
    └── format.ts            # 工具函数
```

下面我们跟着构建流程走一遍。

---

## 1. config & configResolved — 配置定型

这两个钩子处理的是**配置对象本身**，还没有开始接触任何源文件。

### 发生了什么

```
config 钩子（各插件按顺序执行）
│
├─ @vitejs/plugin-vue ──────► 注入 Vue 编译器配置、SFC 热更新选项
├─ unplugin-auto-import ────► 注入自动导入的 include/exclude 规则
├─ unplugin-vue-components ─► 注入组件解析器（如 ElementPlusResolver）
└─ vite-plugin-compression ─► 注入压缩算法和阈值配置
│
▼
configResolved 钩子
│
└─ 各插件拿到最终冻结的配置，缓存供后续使用
   例如：config.build.outDir = 'dist'
         config.build.sourcemap = 'hidden'
         config.resolve.alias = { '@': '/src' }
```

### 对文件的影响

**没有直接处理任何文件。** 但这里确定了：

- 路径别名映射（`@` → `/src`）—— 会影响后面 `resolveId` 怎么解析导入
- sourcemap 策略 —— 影响 `transform` 和 `renderChunk` 阶段的输出
- 压缩配置 —— 影响 `generateBundle` 阶段的产物

---

## 2. options & buildStart — 构建启动

### options

Rollup 接收输入选项，确认入口文件。对于 Vite 项目来说：

```
输入：整个 Rollup 选项对象
处理：确认 input = 'index.html'（Vite 默认以 HTML 为入口）
输出：修正后的选项对象
```

### buildStart

各插件做初始化准备，**仍未处理源文件**：

```
@vitejs/plugin-vue ──► 初始化 @vue/compiler-sfc 编译器实例
auto-import ─────────► 扫描项目已有的导入，建立映射表
```

---

## 3. resolveId — 模块路径解析

**每一条 `import` 语句**都会触发 `resolveId`。这个钩子不读取文件内容，只把导入路径翻译成文件系统的绝对路径。

### 典型示例

以 `main.ts` 的导入为起点：

```typescript
// main.ts 中的导入
import { createApp } from "vue";
import App from "./App.vue";
import router from "@/router";
import "@/styles/global.scss";
```

每一行触发一次 `resolveId`：

| 导入路径                 | resolveId 由谁处理 | 解析结果                                           |
| ------------------------ | ------------------ | -------------------------------------------------- |
| `'vue'`                  | Vite 核心          | `node_modules/vue/dist/vue.runtime.esm-bundler.js` |
| `'./App.vue'`            | Vite 核心          | `/src/App.vue`                                     |
| `'@/router'`             | Alias 插件         | `/src/router/index.ts`（`@` → `/src`）             |
| `'@/styles/global.scss'` | Alias 插件         | `/src/styles/global.scss`                          |

### 虚拟模块

`auto-import` 插件会在这个阶段拦截特殊的导入：

```
导入：'vue' 中的 ref, computed（由 auto-import 注入）
处理：resolveId 返回虚拟模块 ID '\0unplugin-auto-import/...'
结果：后续 load 钩子会提供这个虚拟模块的代码
```

### 关键理解

> **resolveId 只做"翻译"**，把 `import` 里的字符串翻译成真实路径。  
> 它不读文件、不改代码，但决定了 Rollup 去哪里找这个模块。

---

## 4. load — 模块内容加载

`resolveId` 找到路径后，`load` 负责**读取内容**。大多数文件由默认加载器直接读磁盘，只有特殊文件需要插件介入。

### 各类文件的 load 行为

#### .vue 文件

Vue 插件在 `load` 阶段拦截 `.vue` 文件，将其**拆分为多个虚拟子模块**：

```
load('src/components/UserCard.vue')
│
├─ 返回主模块代码（脚本部分 + 子模块引用）
│
│  生成的代码大致如下：
│  import script from 'UserCard.vue?vue&type=script&setup=true&lang.ts'
│  import 'UserCard.vue?vue&type=style&index=0&scoped=xxx&lang.scss'
│  script.__file = 'src/components/UserCard.vue'
│  export default script
│
└─ 后续 Rollup 会对这些子模块查询串再次走 resolveId → load 流程
```

> `.vue` 文件**不是一次加载完的**，而是被拆成 script / template / style 三个虚拟子请求，每个子请求再单独走一遍 resolveId → load → transform 流程。

#### .ts 文件

```
load('src/utils/format.ts')
│
└─ 默认加载器直接读取磁盘文件内容，原样返回 TypeScript 源码
   （TypeScript → JavaScript 的转换在下一步 transform 阶段完成）
```

#### .scss 文件

```
load('src/styles/global.scss')
│
└─ 默认加载器直接读取磁盘文件内容，原样返回 SCSS 源码
```

#### 图片文件

```
load('src/assets/logo.png')  ← 小于 4KB
│
└─ Vite 资源插件返回：
   export default 'data:image/png;base64,iVBORw0KGgo...'
   （内联为 Base64 data URI）

load('src/assets/banner.jpg')  ← 大于 4KB
│
└─ Vite 资源插件返回：
   export default '/assets/banner-a1b2c3d4.jpg'
   （返回带哈希的公共路径引用，原始文件将作为 asset 输出）
```

### 虚拟模块

```
load('\0unplugin-auto-import/...')
│
└─ auto-import 插件生成并返回代码：
   export { ref, computed, watch, ... } from 'vue'
   export { useRouter, useRoute, ... } from 'vue-router'
```

---

## 5. transform — 代码转换（核心阶段）

这是构建流程中**最重要、处理最多的阶段**。每个模块加载后都会经过 `transform` 链，由多个插件**依次**处理。

### 5.1 .vue 文件（script 部分）

`<script setup lang="ts">` 会经历两次关键转换：

**原始代码：**

```vue
<script setup lang="ts">
import { ref, computed } from "vue";
import { useUser } from "@/composables/useUser";

interface Props {
  userId: number;
}

const props = defineProps<Props>();
const { user, loading } = useUser(props.userId);
const displayName = computed(() => user.value?.name ?? "匿名");
</script>
```

**第一次转换：@vue/compiler-sfc 编译 `<script setup>`**

```javascript
// TypeScript 类型提取为运行时 props 定义
// setup() 函数体自动生成
import { defineComponent as _defineComponent } from "vue";
import { ref, computed } from "vue";
import { useUser } from "@/composables/useUser";

export default /*#__PURE__*/ _defineComponent({
  __name: "UserCard",
  props: {
    userId: { type: Number, required: true }, // ← TS interface 变成了运行时声明
  },
  setup(__props) {
    const props = __props;
    const { user, loading } = useUser(props.userId);
    const displayName = computed(() => user.value?.name ?? "匿名");
    return { user, loading, displayName }; // ← 自动收集模板需要的变量
  },
});
```

**变化要点：**

- `interface Props` 消失了 → 变成运行时 `props` 选项
- `defineProps<Props>()` 消失了 → 编译器提取类型信息
- 顶层变量被包裹进 `setup()` 函数
- 返回值自动包含模板中引用的响应式变量

**第二次转换：esbuild 移除 TypeScript**

```javascript
// 所有类型注解都已移除，纯 JavaScript
import { defineComponent } from "vue";
import { ref, computed } from "vue";
import { useUser } from "@/composables/useUser";

export default defineComponent({
  __name: "UserCard",
  props: {
    userId: { type: Number, required: true },
  },
  setup(__props) {
    const props = __props;
    const { user, loading } = useUser(props.userId);
    const displayName = computed(() => user.value?.name ?? "匿名");
    return { user, loading, displayName };
  },
});
```

### 5.2 .vue 文件（template 部分）

模板被 `@vue/compiler-dom` 编译为渲染函数：

**原始模板：**

```html
<template>
  <div class="user-card">
    <span v-if="loading">加载中...</span>
    <template v-else>
      <h2>{{ displayName }}</h2>
      <img :src="avatarUrl" :alt="displayName" />
    </template>
  </div>
</template>
```

**编译后的 render 函数：**

```javascript
import {
  createElementVNode as _createElementVNode,
  toDisplayString as _toDisplayString,
  openBlock as _openBlock,
  createElementBlock as _createElementBlock,
  createCommentVNode as _createCommentVNode,
  Fragment as _Fragment,
} from "vue";

function render(_ctx, _cache, $props, $setup, $data, $options) {
  return (
    _openBlock(),
    _createElementBlock("div", { class: "user-card" }, [
      _ctx.loading
        ? _createElementVNode("span", null, "加载中...")
        : (_openBlock(),
          _createElementBlock(
            _Fragment,
            { key: 1 },
            [
              _createElementVNode(
                "h2",
                null,
                _toDisplayString(_ctx.displayName),
                1,
              ),
              _createElementVNode(
                "img",
                {
                  src: _ctx.avatarUrl,
                  alt: _ctx.displayName,
                },
                null,
                8,
                ["src", "alt"],
              ),
            ],
            64,
          )),
    ])
  );
}
```

**变化要点：**

| 模板语法                  | 编译结果                                                    |
| ------------------------- | ----------------------------------------------------------- |
| `<div class="user-card">` | `_createElementBlock("div", { class: "user-card" }, [...])` |
| `v-if="loading"`          | 三元表达式 `_ctx.loading ? ... : ...`                       |
| `{{ displayName }}`       | `_toDisplayString(_ctx.displayName)`                        |
| `:src="avatarUrl"`        | `{ src: _ctx.avatarUrl }` + patchFlag `8`                   |
| `v-else` + `<template>`   | `_Fragment` 包裹                                            |

> **patchFlag** 是 Vue 3 编译优化的核心：数字 `8` 表示"只有 props 是动态的"，运行时 diff 可以跳过静态属性检查。`1` 对应 `TEXT`，`64` 对应 `STABLE_FRAGMENT`。

### 5.3 .vue 文件（style 部分）

**原始样式（Scoped SCSS）：**

```scss
<style scoped lang="scss">
@use '@/styles/variables' as *;

.user-card {
  padding: $spacing-md;

  h2 {
    color: $primary-color;
  }
}
</style>
```

**转换过程（3步）：**

```
步骤 1：SCSS → CSS（Sass 预处理器）
─────────────────────────────────
.user-card {
  padding: 16px;          /* $spacing-md 被替换为具体值 */
}
.user-card h2 {
  color: #409eff;         /* $primary-color 被替换 */
}

步骤 2：添加 scoped 属性选择器（Vue 插件）
─────────────────────────────────
.user-card[data-v-7a8b9c0d] {
  padding: 16px;
}
.user-card h2[data-v-7a8b9c0d] {     /* 每个选择器都追加了 scoped 哈希 */
  color: #409eff;
}

步骤 3：转换为 JS 模块（Vite CSS 插件）
─────────────────────────────────
// 在构建模式下，CSS 被提取为独立文件
// 此处生成一个空的 JS 模块，CSS 内容记录到 Rollup 的 asset 中
export default {}
```

> **scoped 的本质：** Vue 编译器给当前组件的每个 DOM 元素添加 `data-v-7a8b9c0d` 属性，同时给 CSS 选择器追加 `[data-v-7a8b9c0d]`，实现样式隔离。这个哈希值基于文件路径生成。

### 5.4 .ts 文件

**原始代码：**

```typescript
// src/utils/format.ts
export function formatDate(date: Date, format: string = "YYYY-MM-DD"): string {
  const year: number = date.getFullYear();
  const month: string = String(date.getMonth() + 1).padStart(2, "0");
  const day: string = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export const VERSION: string = "1.0.0";
```

**esbuild transform 后：**

```javascript
// 所有类型注解被移除，逻辑代码不变
export function formatDate(date, format = "YYYY-MM-DD") {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export const VERSION = "1.0.0";
```

**变化要点：**

- 类型注解（`: Date`、`: string`、`: number`）全部移除
- 逻辑代码**完全不变** —— esbuild 只做类型擦除，不做降级编译
- 如果配置了 `target: 'es2015'`，模板字符串等语法也会被降级

### 5.5 路由文件（懒加载 → 动态 import）

**原始代码：**

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Home }, // 同步
    { path: "/about", component: () => import("@/views/About.vue") }, // 懒加载
  ],
});
```

**transform 后（类型擦除 + 路径解析完成）：**

```javascript
import { createRouter, createWebHistory } from "vue-router";
import Home from "/src/views/Home.vue"; // 别名已解析

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Home },
    { path: "/about", component: () => import("/src/views/About.vue") },
    // ↑ 动态 import() 保留，Rollup 后续会把 About.vue 分割为独立 chunk
  ],
});
```

> **动态 `import()` 是代码分割的信号。** Rollup 看到它后会将 `About.vue` 及其依赖树打包为独立的异步 chunk。

---

## 6. moduleParsed — 模块解析完成

每个模块**完成 transform 之后**，Rollup 会解析其 AST，提取导入导出信息，然后触发 `moduleParsed`。

### 发生了什么

```
moduleParsed('src/main.ts')
│
├─ 静态导入：
│  ├─ 'vue'                    → 标记为依赖
│  ├─ './App.vue'              → 标记为依赖
│  ├─ '@/router'               → 标记为依赖
│  └─ '@/styles/global.scss'   → 标记为依赖
│
├─ 动态导入：无
│
└─ 导出：无（入口文件通常不导出）

moduleParsed('src/router/index.ts')
│
├─ 静态导入：
│  ├─ 'vue-router'
│  └─ '@/views/Home.vue'
│
├─ 动态导入：
│  └─ '@/views/About.vue'   ← 标记为代码分割点！
│
└─ 导出：router 实例
```

### 对文件的影响

**不修改任何代码。** 构建的是一张**模块依赖图**：

```
main.ts
├── vue (外部依赖)
├── App.vue
│   ├── UserCard.vue
│   │   ├── useUser.ts
│   │   └── _variables.scss
│   └── router/index.ts
│       ├── vue-router (外部依赖)
│       ├── Home.vue (同步)
│       └── About.vue (异步 → 分割点)
├── global.scss
└── logo.png / banner.jpg
```

这张图决定了接下来**哪些模块打进同一个 chunk，哪些需要分割**。

---

## 7. buildEnd — 模块处理结束

所有模块都完成了 resolveId → load → transform → moduleParsed 循环后，Rollup 触发 `buildEnd`。

### 发生了什么

```
buildEnd(error?)
│
├─ 如果 error 不为空：某个模块处理失败，构建将中断
│
└─ 如果没有 error：
   ├─ 所有源文件已完成转换
   ├─ 模块依赖图已建立完毕
   ├─ 代码分割点已标记
   └─ 准备进入输出生成阶段
```

### 对文件的影响

**不修改文件。** 这是一个"检查点"钩子，用于日志记录和资源清理。

---

## 8. renderStart — 输出生成开始

进入 Rollup 的 **Output Generation** 阶段。Rollup 根据 `moduleParsed` 阶段建立的依赖图，决定如何分割 chunk。

### 发生了什么

```
renderStart(outputOptions, inputOptions)
│
├─ 确认输出格式：format = 'es'（ESM）
├─ 确认输出目录：dir = 'dist/assets'
├─ 确认文件命名：entryFileNames = '[name]-[hash].js'
│                 chunkFileNames = '[name]-[hash].js'
│                 assetFileNames = '[name]-[hash].[ext]'
│
└─ Rollup 开始按依赖图 + manualChunks 配置进行分组
```

### Chunk 分割决策

假设 `vite.config.ts` 中配置了 `manualChunks`：

```
分割结果：

chunk-1: index       ──► main.ts + App.vue + router/index.ts + Home.vue
chunk-2: about       ──► About.vue（动态导入 → 独立异步 chunk）
chunk-3: vendor-vue  ──► vue + vue-router（manualChunks 配置）
chunk-4: vendor-ui   ──► element-plus 相关（如果有）
chunk-5: UserCard    ──► 被多个路由引用时可能拆为公共 chunk
```

---

## 9. renderChunk — 逐 Chunk 处理

对**每一个**生成的 chunk 调用，此时代码已经是打包后的形态（模块已合并）。

### 输入 → 处理 → 输出

以入口 chunk 为例：

**输入（合并后的 chunk 代码片段）：**

```javascript
// 多个模块已被合并到一个文件
import { createApp as n, defineComponent as t, computed as o,
         ref as r, createElementBlock as c, ... } from './vendor-vue-Bx7K3mLd.js'

const s = t({
  __name: "UserCard",
  props: { userId: { type: Number, required: true } },
  setup(e) {
    // ...
    console.log('debug: user loaded')  // ← 遗留的 console
    return { user: a, loading: l, displayName: d }
  }
})

// ... 更多模块代码
```

**处理：esbuild minify（压缩）**

```javascript
import {
  createApp as n,
  defineComponent as t,
  computed as o,
  ref as r,
  createElementBlock as c,
} from "./vendor-vue-Bx7K3mLd.js";
const s = t({
  __name: "UserCard",
  props: { userId: { type: Number, required: !0 } },
  setup(e) {
    return { user: a, loading: l, displayName: d };
  },
});
```

**变化要点：**

- 所有空白、换行被移除
- 变量名被压缩（`createApp` → `n`）
- `console.log` 被移除（如果配置了 `drop: ['console']`）
- `required: true` → `required: !0`（更短的等效表达）
- 注释被清除

### 每个 chunk 都经历这个过程

```
renderChunk('index-a1b2c3d4.js')         → 压缩入口代码
renderChunk('about-e5f6g7h8.js')         → 压缩 About 页面代码
renderChunk('vendor-vue-Bx7K3mLd.js')    → 压缩 Vue 运行时
```

---

## 10. augmentChunkHash — 哈希计算

### 发生了什么

```
augmentChunkHash(chunkInfo)
│
├─ Rollup 根据 chunk 内容计算哈希值
├─ 插件可以额外注入影响哈希的字符串
│
└─ 最终哈希决定文件名：
   index-a1b2c3d4.js    ← 代码变了，哈希就变
   vendor-vue-Bx7K3mLd.js  ← 没改 Vue 版本，哈希不变 → 浏览器用缓存
```

> **文件名哈希是长期缓存策略的核心。** 第三方库拆成独立 chunk，版本不变则哈希不变，用户无需重新下载。

---

## 11. generateBundle — 最终产物生成

**文件写入磁盘之前的最后机会。** 所有需要输出的文件都在 `bundle` 对象中。

### bundle 中有什么

```javascript
// generateBundle(options, bundle) 中的 bundle 对象：

{
  // ── JavaScript Chunks ──
  'assets/index-a1b2c3d4.js': {
    type: 'chunk',
    code: '/* 压缩后的入口代码 */',
    fileName: 'assets/index-a1b2c3d4.js',
    isEntry: true,
    modules: {
      'src/main.ts': { ... },
      'src/App.vue': { ... },
      'src/router/index.ts': { ... },
      'src/views/Home.vue': { ... },
    }
  },

  'assets/about-e5f6g7h8.js': {
    type: 'chunk',
    code: '/* About 页面代码 */',
    isDynamicEntry: true,       // ← 懒加载入口
  },

  'assets/vendor-vue-Bx7K3mLd.js': {
    type: 'chunk',
    code: '/* Vue 运行时 */',
  },

  // ── CSS Assets ──
  'assets/index-x9y0z1w2.css': {
    type: 'asset',
    source: '.user-card[data-v-7a8b9c0d]{padding:16px}...',  // 所有组件 CSS 合并+压缩
    fileName: 'assets/index-x9y0z1w2.css',
  },

  // ── 图片 Assets ──
  'assets/banner-m3n4o5p6.jpg': {
    type: 'asset',
    source: <Buffer ...>,       // 原始二进制数据
    fileName: 'assets/banner-m3n4o5p6.jpg',
  },
  // 注意：logo.png 不在这里，因为它 < 4KB 已被内联为 Base64

  // ── Sourcemap ──
  'assets/index-a1b2c3d4.js.map': {
    type: 'asset',
    source: '{"version":3,"mappings":"..."}',
  },
}
```

### 插件在此阶段的操作

```
generateBundle(options, bundle)
│
├─ vite-plugin-compression：
│  ├─ 遍历所有 .js / .css 文件
│  ├─ 生成 .gz 压缩版本（Gzip）
│  └─ 生成 .br 压缩版本（Brotli）
│
├─ sourcemap-filter 插件（如果有）：
│  └─ 删除 node_modules 相关的 sourcemap
│
└─ rollup-plugin-visualizer（如果启用）：
   └─ 输出 stats.html 打包分析报告
```

**新增的文件（通过 `this.emitFile` 或直接加入 bundle）：**

```
assets/index-a1b2c3d4.js.gz        ← Gzip 压缩
assets/index-a1b2c3d4.js.br        ← Brotli 压缩
assets/index-x9y0z1w2.css.gz
assets/index-x9y0z1w2.css.br
assets/vendor-vue-Bx7K3mLd.js.gz
assets/vendor-vue-Bx7K3mLd.js.br
stats.html                          ← 打包分析报告
```

---

## 12. transformIndexHtml — HTML 处理

这是 **Vite 特有钩子**，专门处理 HTML 入口文件。

### 输入

```html
<!-- 原始 index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

### 输出

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My App</title>
    <!-- ▼ 自动注入 CSS -->
    <link rel="stylesheet" crossorigin href="/assets/index-x9y0z1w2.css" />
    <!-- ▼ 预加载关键 JS chunk -->
    <link
      rel="modulepreload"
      crossorigin
      href="/assets/vendor-vue-Bx7K3mLd.js"
    />
  </head>
  <body>
    <div id="app"></div>
    <!-- ▼ 原始 /src/main.ts 被替换为构建产物路径 -->
    <script type="module" crossorigin src="/assets/index-a1b2c3d4.js"></script>
  </body>
</html>
```

**变化要点：**

- `/src/main.ts` → `/assets/index-a1b2c3d4.js`（带哈希的构建产物）
- 自动注入 `<link rel="stylesheet">` 引用提取出的 CSS
- 自动注入 `<link rel="modulepreload">` 预加载关键依赖 chunk
- 添加 `crossorigin` 属性（用于 CORS）

---

## 13. writeBundle — 写入磁盘

`generateBundle` 中的所有文件被写入到 `dist/` 目录。

### 最终产物目录

```
dist/
├── index.html                           # 处理后的 HTML 入口
├── assets/
│   ├── index-a1b2c3d4.js               # 入口 + 同步路由 + 组件
│   ├── index-a1b2c3d4.js.map           # Sourcemap（hidden，不引用）
│   ├── index-a1b2c3d4.js.gz            # Gzip 压缩版
│   ├── index-a1b2c3d4.js.br            # Brotli 压缩版
│   │
│   ├── about-e5f6g7h8.js              # 懒加载的 About 页面
│   ├── about-e5f6g7h8.js.map
│   ├── about-e5f6g7h8.js.gz
│   ├── about-e5f6g7h8.js.br
│   │
│   ├── vendor-vue-Bx7K3mLd.js         # Vue 运行时
│   ├── vendor-vue-Bx7K3mLd.js.gz
│   ├── vendor-vue-Bx7K3mLd.js.br
│   │
│   ├── index-x9y0z1w2.css             # 合并的样式
│   ├── index-x9y0z1w2.css.gz
│   ├── index-x9y0z1w2.css.br
│   │
│   └── banner-m3n4o5p6.jpg            # 图片资源（> 4KB）
│
└── stats.html                          # 打包分析报告（可选）
```

---

## 14. closeBundle — 构建完成

最后一个钩子，所有文件已写入磁盘。

```
closeBundle()
│
├─ 可执行后处理操作：
│  ├─ 上传 sourcemap 到 Sentry
│  ├─ 将产物上传到 CDN
│  └─ 发送构建完成通知
│
└─ 构建流程结束
```

---

## 完整流程回顾：一个 .vue 文件的一生

以 `UserCard.vue` 为例，追踪它从源码到产物的完整旅程：

```
UserCard.vue（源码）
    │
    │  resolveId
    ├─────────────► 路径解析：'@/components/UserCard.vue' → '/src/components/UserCard.vue'
    │
    │  load
    ├─────────────► 拆分为 3 个虚拟子模块：
    │               ├─ ?vue&type=script    （脚本）
    │               ├─ ?vue&type=template  （模板）
    │               └─ ?vue&type=style     （样式）
    │
    │  transform（script）
    ├─────────────► <script setup lang="ts">
    │               → @vue/compiler-sfc 编译 setup 语法
    │               → esbuild 擦除 TypeScript 类型
    │               结果：纯 JS 的 defineComponent({...})
    │
    │  transform（template）
    ├─────────────► <template> HTML
    │               → @vue/compiler-dom 编译为 render 函数
    │               → 生成 VNode 创建代码 + patchFlags 优化标记
    │               结果：render(_ctx) { return createElementBlock(...) }
    │
    │  transform（style）
    ├─────────────► <style scoped lang="scss">
    │               → Sass 编译：SCSS → CSS，变量替换
    │               → Scoped 处理：追加 [data-v-hash] 属性选择器
    │               → 提取为独立 CSS asset
    │               结果：.user-card[data-v-7a8b9c0d] { padding: 16px }
    │
    │  moduleParsed
    ├─────────────► 分析依赖：imports useUser.ts, _variables.scss
    │               登记到模块依赖图
    │
    │  renderChunk
    ├─────────────► 与其他同步模块合并到 index chunk
    │               esbuild 压缩：变量重命名、空白移除、console 删除
    │
    │  generateBundle
    ├─────────────► JS 部分 → 存在于 index-a1b2c3d4.js 中
    │               CSS 部分 → 合并进 index-x9y0z1w2.css 中
    │               生成 .gz / .br 压缩版本
    │
    │  writeBundle
    └─────────────► 写入 dist/assets/ 目录，构建完成
```

---

## 钩子 × 文件类型 全景表

| 钩子                   | .vue（script） | .vue（template） | .vue（style）   | .ts       | .scss         | 图片       | HTML     |
| ---------------------- | -------------- | ---------------- | --------------- | --------- | ------------- | ---------- | -------- |
| **resolveId**          | 解析路径       | 解析子查询       | 解析子查询      | 解析路径  | 解析路径      | 解析路径   | —        |
| **load**               | 拆分SFC        | 返回模板         | 返回样式        | 读磁盘    | 读磁盘        | Base64/URL | —        |
| **transform**          | SFC编译→TS擦除 | 编译render函数   | SCSS→CSS→scoped | TS擦除    | SCSS→CSS→提取 | —          | —        |
| **moduleParsed**       | 分析依赖       | —                | —               | 分析依赖  | —             | —          | —        |
| **renderChunk**        | 压缩+合并      | 压缩+合并        | —               | 压缩+合并 | —             | —          | —        |
| **generateBundle**     | 输出chunk      | 输出chunk        | 输出CSS asset   | 输出chunk | 输出CSS asset | 输出asset  | —        |
| **transformIndexHtml** | —              | —                | —               | —         | —             | —          | 注入标签 |
| **writeBundle**        | 写入磁盘       | 写入磁盘         | 写入磁盘        | 写入磁盘  | 写入磁盘      | 写入磁盘   | 写入磁盘 |

---

## 结语

通过逐钩子追踪可以看到，Vite 的构建流程本质上是一条**流水线**：

1. **resolveId** — 知道文件在哪
2. **load** — 把文件读进来（.vue 会被拆分）
3. **transform** — 各种编译转换（SFC → JS、TS → JS、SCSS → CSS、模板 → render）
4. **moduleParsed** — 搞清楚谁依赖谁
5. **renderChunk** — 合并 + 压缩
6. **generateBundle** — 组装最终产物 + 额外处理（压缩、sourcemap、分析报告）
7. **writeBundle** — 写盘、结束

每种文件类型在这条流水线上的"停靠站"不同 —— `.vue` 最复杂（拆分 → 多路处理 → 合并），`.ts` 只做类型擦除，图片可能直接内联。理解了这个过程，排查构建问题时就知道该看哪个阶段、哪个插件了。
