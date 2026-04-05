---
title: "Vite 打包阶段钩子内存占用深度分析"
date: 2026-04-05
draft: false
description: ""
tags: ["Vite", "Rollup", "前端工程化"]
categories: ["笔记"]
---

## 目录

1. [核心概念：模块 vs Chunk](#一核心概念模块-vs-chunk)
2. [Vite 打包流程总览](#二vite-打包流程总览)
3. [各钩子内存详解](#三各钩子内存详解)
4. [内存峰值时序图](#四内存峰值时序图)
5. [各钩子横向对比](#五各钩子横向对比)
6. [renderChunk OOM 专题分析](#六renderchunk-oom-专题分析)
7. [内存监控插件实现](#七内存监控插件实现)
8. [优化策略](#八优化策略)
9. [V8 GC 机制与内存行为的关系](#九v8-gc-机制与内存行为的关系)
10. [常见问题排查](#十常见问题排查)

---

## 一、核心概念：模块 vs Chunk

理解钩子内存分布之前，必须先搞清楚这两个概念的边界。

### 模块（Module）—— 输入单元

模块就是你源码里写的每一个文件，是打包的**输入**：

```
src/main.ts         ← 模块
src/App.vue         ← 模块
src/utils/index.ts  ← 模块
node_modules/vue    ← 模块（第三方）
```

### Chunk —— 输出单元

Chunk 是打包后输出到 `dist` 目录的 `.js` 文件，是打包的**输出**：

```
dist/assets/
├── index-Dg3k9xQp.js     ← chunk（入口 chunk）
├── vendor-BHp2mNkL.js    ← chunk（第三方库 chunk）
└── About-C7xQpLmN.js     ← chunk（懒加载路由 chunk）
```

**多个模块合并进一个 chunk，一个模块也可能被拆成独立 chunk。**

### 两者的流向关系

```
源码模块（N 个）
    ↓  transform（逐个处理，一对一）
    ↓
已转换模块
    ↓  Rollup 分析 import 关系，决定合并/拆分策略
    ↓
Chunk（M 个，M << N）
    ↓  renderChunk（逐个处理，一对一）
    ↓
最终产物
```

**transform 处理的是模块，renderChunk 处理的是 chunk，这是两个完全不同层面的操作。**

---

### Chunk 产生的三种方式

**1. 动态 import —— 自动拆分**

```js
// 路由懒加载，About 页面自动生成独立 chunk
const About = () => import('./pages/About.vue')
```

**2. manualChunks —— 手动拆分**

```js
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        vendor: ['vue', 'vue-router', 'pinia']  // → vendor-xxx.js
      }
    }
  }
}
```

**3. 多入口 —— 各自独立 chunk**

```js
build: {
  rollupOptions: {
    input: {
      main: 'index.html',
      admin: 'admin.html'
    }
  }
}
```

### 分包的意义不只是缓存

分包通常被认为是为了**浏览器缓存**（改了业务代码，vendor chunk 不变，用户无需重新下载）。但从构建侧看，分包同样是**内存保护机制**——把 renderChunk 一次性的大内存爆发，拆成多次可控的小波动，这在后面的 OOM 分析中会详细展开。

---

## 二、Vite 打包流程总览

Vite 的生产打包本质是调用 Rollup，整体分为两大阶段：

```
┌─────────────────────────────────────────────────────┐
│  Build 阶段（模块维度）                               │
│  options → buildStart → resolveId → load            │
│  → transform → moduleParsed → buildEnd              │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Output 阶段（chunk 维度）                            │
│  renderStart → renderChunk → generateBundle         │
│  → writeBundle → closeBundle                        │
└─────────────────────────────────────────────────────┘
```

Build 阶段以**模块**为处理单位，Output 阶段以 **chunk** 为处理单位。两个阶段的内存行为有本质差异。

---

## 三、各钩子内存详解

### 3.1 `options`

**触发时机：** Rollup 实例化之前，最先执行，用于修改最终配置。

**内存占用：** < 5 MB

**内存构成：**

```
Node.js 进程基础 RSS          30~50 MB
Vite 本身加载（esm/cjs）      10~20 MB
rollup options 对象            < 1 MB
```

**为什么这么低：** 此阶段仅在 JS 堆里构造一个普通配置对象，无 AST，无模块图，数据量极小。

---

### 3.2 `buildStart`

**触发时机：** Rollup 开始构建前，插件可在此初始化缓存、读取外部配置。

**内存占用：** 自身 < 10 MB，插件副作用可能拉高至 50~200 MB。

**典型危险写法：**

```js
buildStart() {
  // ❌ 一次性读取所有依赖元信息进内存
  this.cache = fs.readdirSync('node_modules')
    .map(pkg => readPackageJson(pkg))  // 可能 10 万+ 文件条目
}
```

**底层原因：** buildStart 是同步执行的钩子队列，大量对象在此创建后立即晋升老生代，GC 压力从这里开始积累。

---

### 3.3 `resolveId` ⭐ 第一个内存增长期

**触发时机：** 每遇到一个 `import` 语句触发一次，将模块标识符解析为绝对路径。

**内存占用（中型项目，约 500 模块）：**

| 阶段 | 内存增量 |
|------|---------|
| 前 100 个模块 | +20~40 MB |
| 前 500 个模块 | +80~150 MB |
| 含大量第三方库 | +200~400 MB |

**内存构成：**

```
resolveId 每次调用产生：
├── 路径字符串缓存（模块 ID → 绝对路径映射表）
├── 插件 resolve 结果对象 { id, external, resolvedBy }
├── 文件系统 stat 缓存（避免重复 IO）
└── ModuleNode 对象（Vite ModuleGraph 中的节点）
```

**调用次数放大效应：**

```
500 个模块 × 5 个插件 = 2500 次 resolveId 调用
```

每次调用都可能产生新的缓存条目，累积效应显著。

**ModuleGraph 节点结构（Vite 源码）：**

```ts
class ModuleNode {
  url: string                      // 原始 URL
  id: string | null                // 解析后绝对路径
  importers: Set<ModuleNode>       // 谁引用了我（双向引用）
  importedModules: Set<ModuleNode> // 我引用了谁（双向引用）
  transformResult: TransformResult // 转换结果缓存 ← 主要内存大户
}
```

双向引用意味着 GC 无法轻易回收任何节点，整个图常驻内存直到 `buildEnd`。

---

### 3.4 `load`

**触发时机：** 模块路径确定后，读取模块内容（默认行为是 `fs.readFile`）。

**内存占用：** 累计 50~200 MB（中型项目）

**为什么源码需要全部驻留内存：**

Rollup 采用**并发解析**策略，load + transform 是并行执行的，同一时刻可能有数十个模块的源码字符串同时存在于堆中：

```
t=0  load(moduleA) → 50KB 字符串，等待 transform
t=0  load(moduleB) → 30KB 字符串，等待 transform
t=0  load(moduleC) → 100KB 字符串，等待 transform
... 全部并发，字符串同时在堆里
```

---

### 3.5 `transform` ⭐ 内存峰值最高点

**触发时机：** 模块内容加载后，对代码进行转换（TS 编译、Vue SFC 解析、CSS 处理等）。

**内存占用（典型项目）：**

| 项目规模 | transform 阶段峰值 |
|---------|-----------------|
| 小型（< 100 模块） | 100~200 MB |
| 中型（500 模块） | 300~600 MB |
| 大型（2000+ 模块） | 800 MB ~ 2 GB |

**内存构成（最复杂的阶段）：**

```
transform 内存 =
  原始源码字符串（来自 load）
+ AST 对象（acorn 解析，1KB 源码 ≈ 8~15KB AST）
+ sourcemap 对象（每个模块维护完整 mappings 数组）
+ 插件处理中间结果（esbuild/babel/swc 内部表示）
+ 转换后的输出代码字符串
+ 各插件的 ctx 上下文对象
```

**AST 内存放大效应（关键）：**

```
源码大小  →  AST 内存占用（粗略估算）
 10 KB   →   80~150 KB
 50 KB   →   400~800 KB
200 KB   →   1.6~3 MB
```

AST 节点是树状 JS 对象，每个节点含 `type`、`start`、`end`、`loc`（行列信息）等字段，内存密度远高于原始字符串。

**Vue SFC 的额外开销：**

```
.vue 文件 transform 产生：
├── template AST（vue-template-compiler 解析）
├── script AST（ts → js）
├── style 处理（postcss AST）
├── 各块的 sourcemap
└── 最终合并的输出代码

一个 200 行的 .vue 文件可能产生 2~5 MB 临时对象
```

**不同转换工具的内存差异：**

| 转换工具 | 100 模块内存增量 | 原因 |
|---------|---------------|------|
| esbuild（Go） | +30~80 MB | Go 进程独立内存，IPC 通信 |
| Babel（JS） | +150~300 MB | 直接在 Node.js 堆构建 AST |
| swc（Rust WASM） | +50~120 MB | WASM 线性内存 + JS 堆结果对象 |

**transform 看起来平稳的原因（测量盲区）：**

transform 阶段用 `heapUsed` 测量往往显示"平稳"，实际上内存在持续增长，只是增长的是老生代里的隐性积累。模块转换完毕后，AST 临时对象虽然被 GC 回收了，但**转换后的代码字符串全部留下来**，悄悄堆积在老生代等待 Rollup 合并，这部分在 transform 阶段结束前不会释放。

---

### 3.6 `moduleParsed`

**触发时机：** 每个模块被完整解析（含 import/export 分析）后触发。

**内存占用：** +10~50 MB 增量

此时 Rollup 将模块加入有向图结构。所有模块的 import/export 关系形成双向引用图，整体作为一个整体常驻内存，GC 无法局部回收。

---

### 3.7 `buildEnd` ⭐ 第二高峰

**触发时机：** 所有模块解析完成，Rollup 内部完成 Tree Shaking、作用域分析、chunk 划分之后触发。

**内存占用：** 在 transform 峰值基础上额外 +50~200 MB

**额外增加的内存：**

```
├── Scope 分析结果（每个变量的 binding 信息）
├── Tree Shaking 标记集合（哪些 export 被使用）
├── Chunk 分组信息（模块 → chunk 映射）
├── 循环依赖检测结果
└── 动态 import 分析图
```

**Tree Shaking 的内存代价：**

Tree Shaking 需要对每个 export 做可达性分析（图的 DFS），需要在内存中维护已标记集合、待处理队列、副作用分析结果。大型 monorepo 在此阶段可能消耗 500 MB ~ 1.5 GB。

---

### 3.8 `renderStart`

**触发时机：** Output 阶段开始，renderChunk 之前触发一次。

**内存占用：** 自身增量极小，是 Build → Output 阶段切换的信号。

---

### 3.9 `renderChunk` ⭐ 最容易 OOM 的阶段

**触发时机：** 每个 chunk 代码生成后触发，用于对 chunk 进行二次处理（压缩、混淆、banner 注入等）。

**内存占用：** +100~500 MB（无分包时更高）

**内存构成：**

```
renderChunk 内存 =
  当前 chunk 的完整代码字符串
+ 对应 sourcemap 对象（通常是代码体积的 1.5~3 倍）
+ 压缩插件的处理中间产物
+ 其余 chunk 同时在内存中（并发执行）
```

**sourcemap 为什么比代码还大：**

```
一个 500KB 的输出 chunk：
  code:             500 KB
  map.mappings:     ~800 KB ~ 1.5 MB（Base64 VLQ 编码）
  map.sourcesContent: 所有原始源码内容（!）← 等于源码双份拷贝
```

**和 transform 的关键区别：**

| | transform | renderChunk |
|---|---|---|
| 处理单位 | 单个模块文件 | 整个 chunk（已合并） |
| 触发次数 | 模块数量次（上百次） | chunk 数量次（几个） |
| 单次输入大小 | 小（单文件） | 大（多文件合并后） |
| GC 介入机会 | 模块间隙可介入 | 大块连续处理，几乎没有 |
| 能否知道 chunk 归属 | ❌ | ✅ |

**压缩插件在此处的内存放大：**

terser（纯 JS 实现）在 renderChunk 里需要：

```
原始 chunk 字符串
  → 重新 parse AST（又一次！chunk 比单模块大 10~100 倍）
  → 压缩/混淆变换
  → 重新生成代码字符串
  → 重新生成 sourcemap

高峰期同时在内存：原始代码 + AST + 压缩后代码 + 两份 sourcemap
```

一个 1MB 的 chunk 经 terser 处理，临时内存峰值约 +15~30 MB。多 chunk 并发叠加极易 OOM。

---

### 3.10 `generateBundle`

**触发时机：** 所有 chunk 代码生成后，写入文件系统前触发。此时拿到完整的 `bundle` 对象。

**内存占用：** +100~500 MB

**bundle 对象结构：**

```ts
type OutputBundle = {
  [fileName: string]: OutputChunk | OutputAsset
}

interface OutputChunk {
  code: string       // 完整输出代码
  map: SourceMap     // sourcemap（含 sourcesContent）
  modules: { ... }   // 包含的所有模块信息
  imports: string[]
  dynamicImports: string[]
}
```

这是整个构建过程中**单个对象体积最大**的时刻，所有 chunk 的代码和 sourcemap 同时存在于一个对象里。

---

### 3.11 `writeBundle`

**触发时机：** 所有文件写入磁盘后触发，bundle 对象仍然存在。

**内存占用：** ≈ 持平，写文件使用 Node.js 流式 `fs.writeFile`，不额外占用大量内存。

---

### 3.12 `closeBundle`

**触发时机：** Rollup 完成所有工作，即将关闭时触发。

**内存变化：** -60~80%（大幅释放）

Rollup 释放模块图引用，V8 GC 随后回收大量老生代对象。**若此阶段内存未明显下降**，常见原因：

- 插件在全局变量上缓存了 `bundle` 或模块引用
- 第三方插件存在内存泄漏
- Worker 线程未被正确关闭（esbuild worker pool）

---

## 四、内存峰值时序图

```
内存 (MB)
 ^
 |                         ★ buildEnd（次高峰）
1200|                      /‾‾‾‾\
    |                     /      \
1000|          ★ transform（最高峰）\
    |          /‾‾‾‾‾‾‾‾‾\        \
 800|         /            \        renderChunk
    |        /              \      /‾‾‾\
 600|  resolveId          moduleParsed   \
    |  /‾‾‾\                              \
 400| /      \                          generateBundle
    |/        load                              \
 200|                                        writeBundle
    |                                                 \
   0+-----------------------------------------------------> 时间
   options  buildStart                          closeBundle
```

---

## 五、各钩子横向对比

| 钩子 | 典型内存增量 | 峰值特征 | 主要内存来源 | GC 介入机会 |
|------|------------|---------|------------|-----------|
| `options` | < 5 MB | 无 | 配置对象 | 充分 |
| `buildStart` | < 10 MB | 低 | 插件初始化 | 充分 |
| `resolveId` | +80~400 MB | 中高 | ModuleGraph、路径缓存 | 有限 |
| `load` | +50~200 MB | 中 | 源码字符串 | 模块间隙 |
| `transform` | +200MB~1GB | **最高峰** | AST + sourcemap + 中间结果 | 模块间隙 |
| `moduleParsed` | +10~50 MB | 中 | 模块图节点 | 极少 |
| `buildEnd` | +50~200 MB | **次高峰** | Tree Shaking、Scope 分析 | 极少 |
| `renderStart` | < 5 MB | 无 | 无 | 充分 |
| `renderChunk` | +100~500 MB | 高，**最易 OOM** | chunk 代码 + sourcemap + 压缩 | 几乎没有 |
| `generateBundle` | +100~500 MB | 高 | bundle 对象（所有 chunk） | 极少 |
| `writeBundle` | ≈ 0 | 持平 | 流式写文件 | 有 |
| `closeBundle` | -600~1000 MB | 大幅释放 | GC 回收模块图 | 充分 |

---

## 六、renderChunk OOM 专题分析

### 6.1 为什么 transform 没问题但 renderChunk 爆了

这是实际工程中最常见的 OOM 模式，原因是多层叠加的：

**原因一：GC 介入时机不同**

transform 是逐模块处理，每处理完一个模块，临时 AST 对象失去引用，V8 的 Minor GC 有机会在模块间隙回收：

```
transform(moduleA) → AST 创建 → 转换完 → AST 失去引用 → [GC 可能介入]
transform(moduleB) → AST 创建 → ...
```

renderChunk 处理的是**已合并的大字符串**，整个过程连续，GC 根本插不进来，内存只能单调增长。

**原因二：transform 阶段存在测量盲区**

用 `heapUsed` 在钩子入口记录，看到的 transform 阶段"平稳"，实际上：

- 模块 AST 临时对象确实被 GC 回收了
- 但**转换后的代码字符串全部留下来**（要给 Rollup 合并用）
- 这部分隐性积累在老生代里，GC 阈值未触发，heapUsed 不反映

到 renderChunk 时，所有模块转换结果字符串（全部存活）+ chunk 合并大字符串（新增）+ 压缩插件处理 = 爆了。

**原因三：没有分包，单个 chunk 体积过大**

```
没分包：
  500个模块 → 全部合并 → renderChunk 拿到 3MB 字符串
                          + 对应 sourcemap（6~9MB）
                          + terser 重新 parse 的 AST
                          = 单次峰值极高

分包后：
  500个模块 → 拆成 10 个 chunk → renderChunk 每次 300KB
                                  峰值只有原来的 1/10
                                  处理完一个可以部分释放
```

### 6.2 分包为什么能从根本上解决

本质是把一次**大内存爆发**拆成**多次可控的小波动**：

```
没分包的内存曲线：
           renderChunk
               ★ OOM
              /
____________/

分包后的内存曲线：
     chunk1  chunk2  chunk3  chunk4
       ↑       ↑       ↑       ↑
___/‾\_/‾\_/‾\_/‾\___   平稳波动，不超阈值
```

每个小 chunk 处理完，字符串对象失去引用，GC 有机会回收，下一个 chunk 处理时内存已部分释放，不会无限叠加。

**分包不只是运行时缓存优化，也是构建时的内存保护机制。**

---

## 七、内存监控插件实现

### 7.1 基础版（常见问题版本分析）

以下是一个常见的基础监控插件，存在几个关键缺陷：

```js
// ❌ 存在测量盲区的版本
export default function createMemoryMonitorPlugin() {
  let timer = null;
  return {
    buildStart() {
      // 问题1：500ms 轮询，短于 chunk 处理时间则漏掉峰值
      timer = setInterval(() => { /* ... */ }, 500);

      // 问题2：OOM 时 exit 事件不触发（abort 信号，非正常退出）
      process.once("exit", () => { /* 这行 OOM 时写不进去 */ });
    },
    renderChunk(_code, chunk) {
      phase = `renderChunk:${chunk.fileName}`;
      // 问题3：只更新 phase，没有记录内存，OOM 时日志空白
    },
  };
}
```

**三个关键缺陷：**

| 缺陷 | 影响 | 原因 |
|------|------|------|
| 500ms 轮询 | 漏掉短暂峰值 | chunk 处理可能只需 50ms，已经崩了才到下次 interval |
| renderChunk 无记录 | OOM 时日志空白 | 只改了 phase 变量，没有写日志 |
| `process.once('exit')` | OOM 时不触发 | OOM 触发 SIGABRT，不走 exit 事件 |

### 7.2 改进版（生产可用）

```js
import { resolve } from "path";
import fs from "fs";

export default function createMemoryMonitorPlugin() {
  const logFile = resolve(process.cwd(), "build-memory.log");
  let phase = "init";
  let peak = 0;
  let peakPhase = "init";
  let timer = null;

  const write = (msg) => fs.appendFileSync(logFile, msg + "\n");
  const mb = () => process.memoryUsage().heapUsed / 1024 / 1024;
  const rss = () => process.memoryUsage().rss / 1024 / 1024;

  const snapshot = (label) => {
    const cur = mb();
    const r = rss();
    write(`[${label}] heap: ${cur.toFixed(1)} MB | rss: ${r.toFixed(1)} MB`);
    if (cur > peak) {
      peak = cur;
      peakPhase = label;
    }
    return cur;
  };

  // 兜底：OOM 前尽量记录（捕获 uncaughtException）
  process.on("uncaughtException", (err) => {
    write(`\n[!!! 崩溃] 阶段: ${phase} | heap: ${mb().toFixed(1)} MB`);
    write(`[!!! 错误] ${err.message}`);
  });

  return {
    name: "memory-monitor",

    buildStart() {
      phase = "buildStart";
      peak = 0;
      fs.writeFileSync(logFile, `=== 构建开始 ${new Date().toLocaleString()} ===\n`);

      // 改为 100ms，更容易捕捉短暂峰值
      timer = setInterval(() => {
        const cur = mb();
        if (cur > peak) {
          peak = cur;
          peakPhase = phase;
          write(`[峰值更新] ${phase} | heap: ${cur.toFixed(1)} MB | rss: ${rss().toFixed(1)} MB`);
        }
      }, 100);

      snapshot("buildStart");
    },

    buildEnd() {
      phase = "buildEnd";
      snapshot("buildEnd");
    },

    renderStart() {
      phase = "renderStart";
      snapshot("renderStart");
    },

    renderChunk(code, chunk) {
      // 关键改进：每个 chunk 记录大小 + 处理前内存
      phase = `renderChunk:${chunk.fileName}`;
      const sizeKB = (code.length / 1024).toFixed(1);
      snapshot(`renderChunk:${chunk.fileName}(${sizeKB}KB)`);
    },

    generateBundle() {
      phase = "generateBundle";
      snapshot("generateBundle");
    },

    writeBundle() {
      phase = "writeBundle";
      snapshot("writeBundle");
    },

    closeBundle() {
      clearInterval(timer);
      snapshot("closeBundle");
      write(`\n[最终峰值] ${peak.toFixed(1)} MB | 阶段: ${peakPhase}`);
      console.log(`\n[内存峰值] ${peak.toFixed(1)} MB | 阶段: ${peakPhase}`);
    },
  };
}
```

### 7.3 改进对比

| | 原版 | 改进版 |
|---|---|---|
| 轮询频率 | 500ms | 100ms |
| renderChunk 记录 | ❌ 只改 phase | ✅ 每个 chunk 记录大小 + 内存 |
| OOM 兜底 | exit 事件，OOM 不触发 | uncaughtException 捕获 |
| RSS 记录 | ❌ | ✅（更能反映真实内存压力） |
| 峰值定位 | 只有数值 | 数值 + 具体是哪个 chunk |

### 7.4 日志解读示例

```
=== 构建开始 2025/4/5 10:23:11 ===
[buildStart]    heap: 85.2 MB  | rss: 120.1 MB
[buildEnd]      heap: 980.4 MB | rss: 1240.3 MB
[renderStart]   heap: 982.1 MB | rss: 1241.0 MB
[renderChunk:vendor-BHp2mNkL.js(2048.3KB)]   heap: 1124.7 MB | rss: 1420.5 MB
[峰值更新] renderChunk:vendor-BHp2mNkL.js | heap: 1380.2 MB | rss: 1650.1 MB
[renderChunk:index-Dg3k9xQp.js(312.1KB)]     heap: 890.3 MB  | rss: 1180.2 MB
[generateBundle] heap: 920.1 MB | rss: 1200.4 MB
[closeBundle]    heap: 312.1 MB | rss: 480.3 MB

[最终峰值] 1380.2 MB | 阶段: renderChunk:vendor-BHp2mNkL.js(2048.3KB)
```

通过 chunk 文件名和大小，可以精确定位到是 `vendor` 这个 2MB 的大 chunk 触发了峰值。

---

## 八、优化策略

### 8.1 分包（最有效）

```js
// vite.config.ts
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // 按包名分包，而非打成一个 vendor
            return id.match(/node_modules\/([^/]+)/)?.[1]
          }
        }
      }
    }
  }
}
```

**效果：** renderChunk 内存峰值降低 50~80%，是解决 renderChunk OOM 最直接的手段。

### 8.2 关闭 sourcemap（第二有效）

```js
export default {
  build: {
    sourcemap: false,  // 生产环境通常不需要，内存减少 30~50%
  }
}
```

sourcemap 的 `sourcesContent` 字段会把所有原始源码再存一份，关闭后内存收益显著。

### 8.3 使用 esbuild 替代 terser

```js
export default {
  build: {
    minify: 'esbuild',  // Vite 默认值，不要手动改成 'terser'
  }
}
```

esbuild 在 Go 进程中完成压缩，JS 堆只需承接输入输出字符串，不持有 AST，内存节省 50% 以上。

### 8.4 若必须用 terser，限制并发数

```js
import { terser } from 'rollup-plugin-terser'
export default {
  plugins: [
    terser({
      maxWorkers: 2  // 防止多 chunk 同时压缩叠加
    })
  ]
}
```

### 8.5 提高 Node.js 堆上限（治标）

```json
// package.json
{
  "scripts": {
    "build": "node --max-old-space-size=4096 node_modules/.bin/vite build"
  }
}
```

这只是缓解，不能替代分包等根本性优化。

### 8.6 插件编写规范（防止内存泄漏）

```js
export function myPlugin() {
  let cache = new Map()

  return {
    name: 'my-plugin',
    buildStart() {
      cache.clear()  // 每次构建重置，避免多次 build 累积
    },
    transform(code, id) {
      const result = heavyTransform(code)
      cache.set(id, result.summary)  // 只缓存摘要，不缓存完整 AST
      return result.code
    },
    renderChunk(code) {
      // ❌ 不要对大字符串做全量正则或重新 parse AST
      // ✅ 只做轻量的字符串替换
      return code.replace(/process\.env\.NODE_ENV/g, '"production"')
    },
    closeBundle() {
      cache.clear()
      cache = null  // 断开引用，让 GC 彻底回收
    }
  }
}
```

---

## 九、V8 GC 机制与内存行为的关系

### 9.1 V8 堆结构

```
V8 堆：
┌──────────────────────────────────────┐
│  New Space（新生代）1~8 MB            │
│  Scavenger GC，高频，速度快            │
│  存放：短命临时对象（AST 节点等）       │
├──────────────────────────────────────┤
│  Old Space（老生代）受 max-old-space  │
│  Mark-Sweep-Compact，低频，速度慢     │
│  存放：ModuleGraph、chunk code 字符串 │
└──────────────────────────────────────┘
```

### 9.2 为什么 Vite 打包内存高

**根本原因是三点叠加：**

1. **模块 AST 存活时间长**（resolveId → closeBundle 全程存在）→ 晋升老生代
2. **老生代 GC 触发慢**（默认阈值约 1.4 GB），构建结束前基本不主动回收
3. **chunk code + sourcemap 字符串体积大**，直接进老生代，且被 bundle 对象持有引用无法回收

### 9.3 为什么 heapUsed 低不代表内存压力低

`heapUsed` 是 GC 上次运行后的存活对象大小。如果老生代 GC 没有触发，大量对象虽然已经无用，但仍然计入 heapUsed。真实内存压力应结合 `rss`（操作系统层面的物理内存）一起看：

```js
const { heapUsed, rss, external, arrayBuffers } = process.memoryUsage()
// heapUsed：V8 堆中已使用的内存
// rss：进程占用的物理内存总量（包含 heapUsed + native + stack）
// external：C++ 对象（Buffer 等）占用的内存
// arrayBuffers：ArrayBuffer 分配的内存
```

renderChunk 阶段 `rss` 往往比 `heapUsed` 更能体现真实压力，因为 esbuild 等工具通过 `external` 占用内存，不反映在 `heapUsed` 里。

---

## 十、常见问题排查

### 10.1 OOM Crash 定位

```bash
# 在堆快照触发点附近生成快照
node --max-old-space-size=8192 \
     --heapsnapshot-near-heap-limit=3 \
     node_modules/.bin/vite build
```

生成的 `.heapsnapshot` 文件用 Chrome DevTools > Memory > Load Snapshot 分析。

### 10.2 常见内存问题对照表

| 现象 | 可能原因 | 排查方法 |
|------|---------|---------|
| renderChunk OOM，transform 正常 | 没有分包，单 chunk 过大 | 查看各 chunk 大小，添加 manualChunks |
| buildEnd 后内存不释放 | Tree Shaking 分析结果常驻 | 正常现象，closeBundle 后会释放 |
| closeBundle 后内存仍高 | 插件全局变量持有 bundle 引用 | 逐一禁用插件，二分法定位 |
| heapUsed 平稳但 rss 持续增长 | esbuild/native 插件内存泄漏 | 关注 `external` 指标 |
| 多次 build 内存累加 | 插件 buildStart 未重置缓存 | 检查插件的 buildStart 是否有 clear() |

### 10.3 Monorepo 构建内存翻倍

**原因：** 每个子包独立构建时各自加载一份 Vite 实例和插件链。

**解法：**
- 使用 Turborepo 构建缓存复用 transform 结果
- 将公共插件提取到 workspace root，避免重复实例化
- 考虑使用 Vite 的 `lib` 模式 + 统一入口构建

---

## 参考资料

- [Rollup 官方文档 - Plugin Hooks](https://rollupjs.org/plugin-development/)
- [Vite 源码 - ModuleGraph](https://github.com/vitejs/vite/blob/main/packages/vite/src/node/moduleGraph.ts)
- [V8 垃圾回收机制详解](https://v8.dev/blog/trash-talk)
- [Node.js 内存分析指南](https://nodejs.org/en/docs/guides/diagnostics/memory)
