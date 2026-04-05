---
title: "Rollup / Vite 插件钩子：moduleParsed 深度解析"
date: 2026-04-05
draft: false
description: ""
tags: ["Vite", "Rollup", "前端工程化"]
categories: ["笔记"]
---

## 目录

1. [定位：moduleParsed 是什么](#一定位moduleparsed-是什么)
2. [触发时机与执行顺序](#二触发时机与执行顺序)
3. [moduleInfo 完整结构](#三moduleinfo-完整结构)
4. [核心产物逐字段解析](#四核心产物逐字段解析)
5. [AST 结构详解](#五ast-结构详解)
6. [与相邻钩子的接力关系](#六与相邻钩子的接力关系)
7. [Rollup 内部拿这些数据做了什么](#七rollup-内部拿这些数据做了什么)
8. [内存占用分析](#八内存占用分析)
9. [实际应用场景](#九实际应用场景)
10. [常见误区](#十常见误区)

---

## 一、定位：moduleParsed 是什么

`moduleParsed` 是一个**纯通知钩子**，它本身不生成任何东西，也不允许你修改任何数据。

它的语义是：

> "Rollup 已经完整解析了这个模块，包括 AST 生成和 import/export 静态分析，现在把结果告诉你。"

与 `transform`（可以修改代码）、`renderChunk`（可以修改 chunk）不同，`moduleParsed` 是**只读的观察窗口**，你能拿到数据，但不能在此修改它。

```js
// Rollup 插件 API 类型定义
interface Plugin {
  moduleParsed(moduleInfo: ModuleInfo): void  // 返回值被忽略
}
```

---

## 二、触发时机与执行顺序

### 2.1 在整个钩子链中的位置

```
resolveId        → 解析模块路径
    ↓
load             → 读取模块内容（源码字符串）
    ↓
transform        → 转换代码（TS→JS、SFC→JS 等）
    ↓
【Rollup 内部】   → acorn 解析 AST
【Rollup 内部】   → 扫描 AST，提取 import/export
【Rollup 内部】   → 更新 ModuleGraph
    ↓
moduleParsed     ← 你在这里拿到完整解析结果 ✅
    ↓
（继续解析下一个模块，或进入 buildEnd）
```

### 2.2 触发频率

**每个模块触发一次**，包括：

- 你自己写的源码文件（`.ts`、`.vue`、`.css` 等）
- `node_modules` 中被直接引用的第三方包
- 虚拟模块（插件通过 `load` 钩子动态生成的模块）

一个中型项目（500 个模块）会触发 500 次 `moduleParsed`。

### 2.3 并发行为

`moduleParsed` 是**并发触发**的，Rollup 并行解析多个模块，不保证触发顺序与 import 顺序一致。如果你的插件逻辑依赖多个模块的解析结果，需要自己收集并在 `buildEnd` 里汇总处理：

```js
// ✅ 正确：收集后在 buildEnd 汇总
const allModules = new Map()

{
  moduleParsed(moduleInfo) {
    allModules.set(moduleInfo.id, moduleInfo)  // 先收集
  },
  buildEnd() {
    // 所有模块都解析完了，在这里做全局分析
    analyzeAll(allModules)
  }
}
```

---

## 三、moduleInfo 完整结构

```ts
interface ModuleInfo {
  // ── 基本标识 ──────────────────────────────────────────
  id: string
  code: string | null
  ast: AcornNode | null

  // ── import 关系 ───────────────────────────────────────
  importedIds: readonly string[]
  dynamicallyImportedIds: readonly string[]
  importedIdResolutions: readonly ResolvedId[]
  dynamicallyImportedIdResolutions: readonly ResolvedId[]

  // ── export 分析 ───────────────────────────────────────
  exports: readonly string[]
  exportedBindings: Record<string, string[]> | null

  // ── 模块性质标记 ──────────────────────────────────────
  isEntry: boolean
  isExternal: boolean
  isIncluded: boolean | null
  hasDefaultExport: boolean | null
  syntheticNamedExports: boolean | string

  // ── 副作用与 Tree Shaking ─────────────────────────────
  moduleSideEffects: boolean | 'no-treeshake'

  // ── 自定义元数据 ──────────────────────────────────────
  meta: CustomPluginOptions

  // ── 其他 ─────────────────────────────────────────────
  implicitlyLoadedAfterOneOf: readonly string[]
  implicitlyLoadedBefore: readonly string[]
}
```

---

## 四、核心产物逐字段解析

### 4.1 `id` —— 模块的唯一标识

```js
id: '/project/src/utils/index.ts'
```

模块的**绝对路径**，是 `resolveId` 钩子返回的结果。在整个构建过程中作为模块的唯一 key 使用。

虚拟模块的 id 通常以 `\0` 开头（Rollup 约定的虚拟模块前缀）：

```js
id: '\0virtual:my-plugin-module'
```

---

### 4.2 `code` —— 转换后的模块源码

```js
code: `
  import { helper } from '/project/src/helper.ts';
  export const add = (a, b) => a + b;
  export const utils = helper();
`
```

这是经过**所有 transform 插件处理之后**的最终代码字符串，不是你原始写的 TypeScript 或 Vue SFC，而是已经：

- TypeScript 编译为 JavaScript
- Vue SFC 拆解为纯 JS
- CSS Modules 转换完成
- import 路径替换完毕

的结果。此时 `code` 是合法的 ESM JavaScript，可以被 acorn 直接解析。

---

### 4.3 `ast` —— 模块的完整 AST ⭐

```js
ast: {
  type: 'Program',
  start: 0,
  end: 284,
  body: [
    {
      type: 'ImportDeclaration',
      source: { type: 'Literal', value: '/project/src/helper.ts' },
      specifiers: [ ... ]
    },
    {
      type: 'ExportNamedDeclaration',
      declaration: {
        type: 'VariableDeclaration',
        declarations: [ ... ]
      }
    }
  ],
  sourceType: 'module'
}
```

这是 Rollup 用 **acorn** 解析 `code` 后生成的完整 ESTree 格式 AST。是 moduleParsed 阶段**内存占用最大**的字段，也是后续所有静态分析的数据来源。

**AST 的内存放大效应：**

```
code 字符串大小  →  ast 对象内存占用（粗略估算）
   1 KB         →   8~15 KB
  10 KB         →  80~150 KB
  50 KB         →  400~800 KB
```

AST 节点是包含大量字段的嵌套 JS 对象（每个节点都有 `type`、`start`、`end`、`loc` 等），内存密度远高于原始字符串。

---

### 4.4 `importedIds` —— 静态依赖列表

```js
importedIds: [
  '/project/src/helper.ts',
  '/project/node_modules/lodash-es/lodash.js',
  '/project/src/styles/base.css'
]
```

该模块所有**静态 `import` 语句**引用的模块 id 列表，已经是 resolveId 解析后的绝对路径。

对应源码中的：

```js
import { helper } from './helper'           // → /project/src/helper.ts
import _ from 'lodash-es'                  // → /project/node_modules/...
import '/styles/base.css'                  // → /project/src/styles/base.css
```

---

### 4.5 `dynamicallyImportedIds` —— 动态依赖列表

```js
dynamicallyImportedIds: [
  '/project/src/pages/About.vue',
  '/project/src/pages/Profile.vue'
]
```

该模块所有 **`import()` 动态调用**引用的模块 id 列表。

对应源码中的：

```js
const About = () => import('./pages/About.vue')
const Profile = () => import('./pages/Profile.vue')
```

**这个字段对 chunk 划分至关重要**——Rollup 正是通过扫描所有模块的 `dynamicallyImportedIds`，决定哪些模块要被拆分为独立 chunk。

---

### 4.6 `importedIdResolutions` —— 带元信息的依赖解析结果

```js
importedIdResolutions: [
  {
    id: '/project/src/helper.ts',
    external: false,
    resolvedBy: 'vite:resolve',   // 是哪个插件解析的
    assertions: {},
    meta: {}
  }
]
```

与 `importedIds` 一一对应，但包含更丰富的元信息。`importedIds` 只是路径字符串数组，这里提供了完整的解析上下文。

---

### 4.7 `exports` —— 模块导出列表

```js
exports: ['add', 'subtract', 'default']
```

该模块**导出的所有名称**，包含 `default`（如果有默认导出）。这是 Tree Shaking 的直接依据——Rollup 会对照这个列表和其他模块的 import，判断哪些 export 从未被使用。

---

### 4.8 `exportedBindings` —— export 来源追踪

```js
exportedBindings: {
  // key 是来源模块，value 是从该来源 re-export 的名称列表
  null: ['add', 'subtract'],           // null 表示本模块自己定义的
  './helper': ['helperFn'],            // 从 ./helper re-export 的
  'lodash-es': ['debounce']            // 从 lodash-es re-export 的
}
```

比 `exports` 更细粒度，追踪每个 export 的**原始来源**。对分析 re-export 链路和 Tree Shaking 精度特别有用。

---

### 4.9 `isEntry` —— 是否是入口模块

```js
isEntry: true   // 对应 vite.config 中 build.rollupOptions.input 指定的模块
isEntry: false  // 被其他模块 import 的普通模块
```

入口模块会被强制包含在产物中（即使没有被 import），其 export 也不会被 Tree Shaking 移除。

---

### 4.10 `isExternal` —— 是否是外部模块

```js
isExternal: true   // 被标记为 external，不会打包进产物
isExternal: false  // 正常打包
```

对应 `rollupOptions.external` 配置，或插件在 `resolveId` 中返回 `{ external: true }`。

---

### 4.11 `moduleSideEffects` —— 副作用标记

```js
moduleSideEffects: true          // 有副作用，必须保留
moduleSideEffects: false         // 无副作用，未被使用时可以整个移除
moduleSideEffects: 'no-treeshake' // 完全跳过 Tree Shaking
```

这是 Tree Shaking 的关键开关，来源于：

- `package.json` 的 `sideEffects` 字段
- 插件在 `resolveId` 或 `load` 中设置的 `moduleSideEffects`

---

### 4.12 `isIncluded` —— 是否会被包含进产物

```js
isIncluded: null   // 还未决定（moduleParsed 阶段通常是 null）
isIncluded: true   // 最终会被打包进产物
isIncluded: false  // 被 Tree Shaking 移除
```

在 `moduleParsed` 阶段，这个值通常是 `null`，因为 Rollup 尚未完成全局 Tree Shaking 分析。该值只有在 `buildEnd` 之后才稳定可信。

---

### 4.13 `meta` —— 跨插件自定义数据

```js
meta: {
  'my-plugin': {
    isComponent: true,
    componentName: 'MyButton'
  }
}
```

插件可以在 `resolveId`、`load`、`transform` 钩子中往 `meta` 里写入自定义数据，然后在 `moduleParsed` 里读取，实现插件间的信息传递：

```js
// 在 transform 里写入
transform(code, id) {
  return {
    code: transformedCode,
    meta: {
      'my-plugin': { isComponent: true }
    }
  }
}

// 在 moduleParsed 里读取
moduleParsed(moduleInfo) {
  const myMeta = moduleInfo.meta['my-plugin']
  if (myMeta?.isComponent) {
    // 做针对组件的处理
  }
}
```

---

## 五、AST 结构详解

### 5.1 ESTree 规范

Rollup 使用 acorn 生成符合 **ESTree 规范**的 AST，每个节点的基础结构：

```ts
interface Node {
  type: string    // 节点类型，如 'ImportDeclaration'、'ExportNamedDeclaration'
  start: number   // 在源码字符串中的起始字符偏移量
  end: number     // 在源码字符串中的结束字符偏移量
  loc: {          // 行列位置信息
    start: { line: number; column: number }
    end: { line: number; column: number }
  }
}
```

### 5.2 常见节点类型速查

**import 语句：**

```js
// 源码：import { add } from './utils'
{
  type: 'ImportDeclaration',
  specifiers: [
    {
      type: 'ImportSpecifier',
      imported: { type: 'Identifier', name: 'add' },
      local: { type: 'Identifier', name: 'add' }
    }
  ],
  source: { type: 'Literal', value: './utils', raw: "'./utils'" }
}
```

**命名导出：**

```js
// 源码：export const add = (a, b) => a + b
{
  type: 'ExportNamedDeclaration',
  declaration: {
    type: 'VariableDeclaration',
    kind: 'const',
    declarations: [
      {
        type: 'VariableDeclarator',
        id: { type: 'Identifier', name: 'add' },
        init: { type: 'ArrowFunctionExpression', ... }
      }
    ]
  }
}
```

**动态 import：**

```js
// 源码：import('./pages/About.vue')
{
  type: 'ImportExpression',
  source: { type: 'Literal', value: './pages/About.vue' }
}
```

### 5.3 Rollup 如何从 AST 提取 importedIds

Rollup 解析完 AST 后，遍历所有节点，找出这两类节点：

```
ImportDeclaration（静态 import）→ 加入 importedIds
ImportExpression（动态 import()）→ 加入 dynamicallyImportedIds
```

这个过程完全基于 AST 静态分析，**不执行任何代码**，所以条件动态 import 的路径如果是变量，Rollup 无法静态分析：

```js
// ✅ 可以静态分析
import('./pages/About.vue')

// ❌ 无法静态分析，Rollup 会警告
const page = 'About'
import(`./pages/${page}.vue`)  // 路径是动态拼接的
```

---

## 六、与相邻钩子的接力关系

### 6.1 完整数据流

```
transform 产出
└── code（转换后的 JS 字符串）
        ↓
        Rollup 内部：acorn.parse(code)
        ↓
        生成 ast
        ↓
        Rollup 内部：遍历 ast，提取所有 import/export
        ↓
        生成 importedIds、dynamicallyImportedIds、exports
        ↓
        更新 ModuleGraph（连接依赖边）
        ↓
moduleParsed 接收
└── moduleInfo（包含上面所有产物）
```

### 6.2 为什么不能在 moduleParsed 里修改代码

`moduleParsed` 触发时，`code` 已经被 acorn 解析为 `ast`，如果允许修改 `code`，就意味着 `ast` 和 `importedIds` 等需要重新生成，会破坏整个解析流程的一致性。

**想修改代码必须在 `transform` 里做**，那是代码修改的正确时机：

```
可以修改代码 ✅         只读观察 ❌
     ↓                      ↓
  transform            moduleParsed
```

### 6.3 moduleParsed 和 buildEnd 的关系

`moduleParsed` 是模块级别的逐个触发，`buildEnd` 是所有模块都解析完毕后触发一次：

```
moduleParsed(moduleA)  ─┐
moduleParsed(moduleB)  ─┤ 并发，顺序不定
moduleParsed(moduleC)  ─┘
        ↓ 全部完成
    buildEnd()         ← 这里才能做全局分析
```

需要**跨模块**分析的逻辑（如循环依赖检测、全局依赖图构建）应该放在 `buildEnd`，而不是 `moduleParsed`。

---

## 七、Rollup 内部拿这些数据做了什么

`moduleParsed` 触发之后（或者说 Rollup 内部完成解析后），这些数据被用于：

### 7.1 构建完整的模块依赖图

```
模块 A：importedIds = [B, C]
模块 B：importedIds = [D]
模块 C：importedIds = [D]

Rollup 构建出：
    A
   / \
  B   C
   \ /
    D
```

这张图是 Tree Shaking 和 chunk 划分的基础数据结构。

### 7.2 发现新的待解析模块

每个模块的 `importedIds` 里，可能有尚未解析的模块。Rollup 会把它们加入解析队列，触发对应的 `resolveId → load → transform → moduleParsed` 流程，递归直到所有依赖都被解析完毕。

```
入口 main.ts 解析完 → 发现 importedIds 有 utils.ts
    ↓
对 utils.ts 触发 resolveId → load → transform → moduleParsed
    ↓
utils.ts 解析完 → 发现 importedIds 有 helper.ts
    ↓
对 helper.ts 触发 ...
    ↓
直到所有模块解析完毕 → buildEnd
```

### 7.3 标记 chunk 分割点

所有模块的 `dynamicallyImportedIds` 被收集起来，作为 chunk 分割的候选点。这是 Rollup 自动代码分割的核心依据：

```
发现 main.ts 有：dynamicallyImportedIds = ['About.vue', 'Profile.vue']
    ↓
标记 About.vue 和 Profile.vue 为独立 chunk 入口
    ↓
最终输出：About-xxx.js、Profile-xxx.js
```

### 7.4 为 Tree Shaking 准备数据

每个模块的 `exports` 和 `moduleSideEffects` 被记录下来，在 `buildEnd` 阶段做全局可达性分析时使用：

```
模块 utils.ts 有：
  exports: ['add', 'subtract', 'multiply']
  moduleSideEffects: false

main.ts 只 import 了 { add }

→ buildEnd 分析：subtract 和 multiply 未被任何模块 import
→ 标记为"未使用"，从产物中移除
```

---

## 八、内存占用分析

### 8.1 moduleParsed 阶段内存构成

```
moduleParsed 时内存中存在：

已解析模块的 AST（最大头）
├── 每个节点是独立 JS 对象
├── 节点间有父子指针引用
└── 内存放大系数：源码 1KB → AST 8~15KB

importedIds 字符串数组
└── 通常几十到几百个路径字符串，占用较小

ModuleGraph 中的连接边
├── importers: Set<ModuleNode>（谁引用了我）
└── importedModules: Set<ModuleNode>（我引用了谁）
    ↑ 双向引用，导致整个图无法被部分 GC 回收

code 字符串
└── transform 后的源码，已存在于内存中（非新增）
```

### 8.2 为什么 ModuleGraph 的内存无法提前释放

双向引用形成了"引用环"：

```
ModuleNode(A).importedModules → ModuleNode(B)
ModuleNode(B).importers       → ModuleNode(A)
```

V8 的 GC 无法判断哪个节点可以被回收，整张图必须作为一个整体常驻内存，直到 `closeBundle` 之后 Rollup 主动断开引用，GC 才能批量回收。

### 8.3 各项数据的存活周期

```
数据                   创建时机       释放时机
──────────────────────────────────────────────
code 字符串            transform      closeBundle 后 GC
ast 对象               moduleParsed   buildEnd 后可能释放
importedIds 数组       moduleParsed   closeBundle 后 GC
ModuleGraph 节点       resolveId      closeBundle 后 GC
```

**ast 是最短命的大对象**：Rollup 在完成 import/export 提取后，理论上就不再需要 AST 了，但因为 ModuleGraph 可能持有引用，实际释放时间不确定。

### 8.4 内存增量估算（中型项目，500 模块）

```
moduleParsed 阶段自身带来的增量：
  AST 对象（500 模块 × 平均 100KB）  ≈ +50 MB
  importedIds 字符串数组              ≈ +5 MB
  ModuleGraph 新增的边               ≈ +10 MB

累计存量（非 moduleParsed 新增，但此时存活）：
  所有模块的 code 字符串             ≈ 50~200 MB
  已有 ModuleGraph 节点              ≈ 30~100 MB
```

`moduleParsed` 阶段的内存不是最高峰，但它是**内存持续增长期**，每解析完一个模块就往 ModuleGraph 里添加新节点和新边。

---

## 九、实际应用场景

### 9.1 循环依赖检测

```js
function circularDepPlugin() {
  const depGraph = new Map()   // id → importedIds[]
  const visited = new Set()

  function hasCycle(id, chain = []) {
    if (chain.includes(id)) return chain.slice(chain.indexOf(id))
    if (visited.has(id)) return null
    visited.add(id)
    for (const dep of (depGraph.get(id) || [])) {
      const cycle = hasCycle(dep, [...chain, id])
      if (cycle) return cycle
    }
    return null
  }

  return {
    name: 'circular-dep-check',
    moduleParsed(moduleInfo) {
      // 收集依赖关系
      depGraph.set(moduleInfo.id, moduleInfo.importedIds)
    },
    buildEnd() {
      // 所有模块解析完毕，做全局环检测
      visited.clear()
      for (const id of depGraph.keys()) {
        const cycle = hasCycle(id)
        if (cycle) {
          this.warn(`循环依赖: ${cycle.join(' → ')} → ${cycle[0]}`)
        }
      }
    }
  }
}
```

### 9.2 依赖关系可视化报告

```js
function depReportPlugin() {
  const modules = []

  return {
    name: 'dep-report',
    moduleParsed(moduleInfo) {
      // 只收集项目自身的模块，过滤 node_modules
      if (!moduleInfo.id.includes('node_modules')) {
        modules.push({
          id: moduleInfo.id.replace(process.cwd(), ''),
          imports: moduleInfo.importedIds
            .filter(id => !id.includes('node_modules'))
            .map(id => id.replace(process.cwd(), '')),
          dynamicImports: moduleInfo.dynamicallyImportedIds
            .map(id => id.replace(process.cwd(), '')),
          exports: moduleInfo.exports,
          isEntry: moduleInfo.isEntry
        })
      }
    },
    generateBundle() {
      const report = JSON.stringify(modules, null, 2)
      this.emitFile({
        type: 'asset',
        fileName: 'dep-report.json',
        source: report
      })
    }
  }
}
```

### 9.3 检测未使用的 export

```js
function unusedExportPlugin() {
  const allExports = new Map()   // id → Set<exportName>
  const usedExports = new Map()  // id → Set<exportName>

  return {
    name: 'unused-export',
    moduleParsed(moduleInfo) {
      // 记录每个模块的 export
      allExports.set(moduleInfo.id, new Set(moduleInfo.exports))

      // 记录每个模块实际被使用的 import
      for (const resolution of moduleInfo.importedIdResolutions) {
        // 通过 importedIdResolutions 可以进一步分析具体用了哪些名称
        // 实际实现需要结合 AST 分析 specifiers
      }
    },
    buildEnd() {
      for (const [id, exports] of allExports) {
        const used = usedExports.get(id) || new Set()
        const unused = [...exports].filter(e => !used.has(e) && e !== 'default')
        if (unused.length > 0) {
          console.warn(`[unused-export] ${id}: ${unused.join(', ')}`)
        }
      }
    }
  }
}
```

### 9.4 按模块体积排序报告

```js
function moduleSizePlugin() {
  const sizes = []

  return {
    name: 'module-size',
    moduleParsed(moduleInfo) {
      if (moduleInfo.code && !moduleInfo.id.includes('node_modules')) {
        sizes.push({
          id: moduleInfo.id.replace(process.cwd(), ''),
          size: moduleInfo.code.length,
          imports: moduleInfo.importedIds.length,
          exports: moduleInfo.exports.length
        })
      }
    },
    buildEnd() {
      sizes.sort((a, b) => b.size - a.size)
      console.log('\n模块体积 TOP 10：')
      sizes.slice(0, 10).forEach((m, i) => {
        const kb = (m.size / 1024).toFixed(1)
        console.log(`  ${i + 1}. ${m.id} (${kb} KB)`)
      })
    }
  }
}
```

### 9.5 读取其他插件写入的 meta 数据

```js
// 插件 A：在 transform 里标记组件信息
{
  transform(code, id) {
    if (id.endsWith('.vue')) {
      return {
        code: transformVue(code),
        meta: {
          'vue-analyzer': {
            isComponent: true,
            componentName: extractName(code)
          }
        }
      }
    }
  }
}

// 插件 B：在 moduleParsed 里消费插件 A 的元数据
{
  moduleParsed(moduleInfo) {
    const vueMeta = moduleInfo.meta['vue-analyzer']
    if (vueMeta?.isComponent) {
      componentRegistry.set(moduleInfo.id, vueMeta.componentName)
    }
  }
}
```

---

## 十、常见误区

### 误区一：以为 moduleParsed 可以修改代码

```js
// ❌ 错误，moduleParsed 的返回值被 Rollup 忽略
moduleParsed(moduleInfo) {
  moduleInfo.code = moduleInfo.code.replace('foo', 'bar')  // 无效
  return { code: '...' }  // 也无效
}

// ✅ 正确，在 transform 里修改
transform(code, id) {
  return { code: code.replace('foo', 'bar') }
}
```

### 误区二：在 moduleParsed 里做跨模块分析

```js
// ❌ 错误：此时其他模块可能还没解析完
moduleParsed(moduleInfo) {
  // 检查 helper.ts 是否也导出了某个名称
  // helper.ts 可能此时还没有触发 moduleParsed！
  const helperInfo = getModuleInfo('helper.ts')  // 可能是 null
}

// ✅ 正确：在 buildEnd 里做，那时所有模块都解析完了
buildEnd() {
  const helperInfo = this.getModuleInfo('helper.ts')  // 这时才可靠
}
```

### 误区三：用 `isIncluded` 判断模块是否被 Tree Shaking

```js
// ❌ 在 moduleParsed 里，isIncluded 通常是 null
moduleParsed(moduleInfo) {
  if (moduleInfo.isIncluded === false) {
    // 这个判断在 moduleParsed 阶段不可靠
  }
}

// ✅ isIncluded 在 buildEnd 之后才稳定
buildEnd() {
  for (const id of this.getModuleIds()) {
    const info = this.getModuleInfo(id)
    if (info.isIncluded === false) {
      // 这里才是准确的
    }
  }
}
```

### 误区四：在 moduleParsed 里缓存大对象导致内存泄漏

```js
const cache = new Map()

// ❌ 缓存了完整的 moduleInfo（包含 ast 和 code 字符串）
moduleParsed(moduleInfo) {
  cache.set(moduleInfo.id, moduleInfo)  // ast 是巨大对象，这样会阻止 GC
}

// ✅ 只缓存需要的轻量数据
moduleParsed(moduleInfo) {
  cache.set(moduleInfo.id, {
    imports: moduleInfo.importedIds,   // 只要路径字符串
    exports: moduleInfo.exports        // 只要导出名称
    // 不缓存 ast 和 code
  })
}
```

---

## 总结

| 维度 | 说明 |
|------|------|
| **本质** | 只读通知钩子，不能修改数据 |
| **触发时机** | 每个模块的 transform 完成且 acorn 解析 AST 之后 |
| **核心产物** | AST、importedIds、dynamicallyImportedIds、exports |
| **最大内存** | AST 对象（源码 1KB → AST 约 8~15KB） |
| **主要用途** | 依赖分析、循环检测、体积统计、读取 meta 数据 |
| **不能做的事** | 修改代码、可靠地跨模块分析、信任 isIncluded |
| **跨模块分析** | 收集数据，在 buildEnd 里汇总处理 |

`moduleParsed` 是整个构建流程中**信息最丰富的观察窗口**，你能在这里看到 Rollup 对每个模块"理解"的全貌——不只是代码本身，还有它的依赖关系、导出内容和在整个模块图中的位置。
