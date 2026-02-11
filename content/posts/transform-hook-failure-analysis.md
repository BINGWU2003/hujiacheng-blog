---
title: "Transform 钩子失效原因分析"
date: 2026-01-23
draft: false
description: ""
tags: []
categories: ["笔记"]
---

Transform 钩子失效原因分析：为什么所有 Chunk 都生成了 Sourcemap

## 核心问题

使用 Transform 钩子返回 `map: null` 来阻止 `node_modules` 生成 sourcemap 后，发现**所有的 chunk 都生成了 sourcemap**：

```bash
# manualChunks 配置的 vendor chunk
dist/assets/vendor-vue-C9gVCVuR.js.map          ← 生成了 ❌
dist/assets/vendor-element-4vsbiGeC.js.map      ← 生成了 ❌
dist/assets/vendor-vxe-BTD-ZBhw.js.map          ← 生成了 ❌
dist/assets/vendor-echarts-CwNDiq1b.js.map      ← 生成了 ❌

# 自动分割的第三方库 chunk
dist/assets/monaco-editor-DkVVM8E4.js.map       ← 生成了 ❌

# 业务代码 chunk
dist/assets/index-Bk8aZ-po.js.map               ← 生成了 ✅
```

**问题**：为什么 Transform 钩子对 `node_modules` 返回了 `map: null`，但所有 chunk（不管是 manualChunks 配置的还是自动分割的）都生成了 sourcemap？

---

## 根本原因：Chunk 合并会重置所有 Sourcemap 状态

### 三个阶段的状态变化

#### 阶段 1: Transform（模块级别）✅

```javascript
// Transform 钩子成功过滤
moduleMap = {
  // manualChunks: vendor-vue
  'node_modules/vue/dist/vue.esm-bundler.js': { code: '...', map: null },
  'node_modules/vue-router/dist/vue-router.esm-bundler.js': { code: '...', map: null },
  'node_modules/vuex/dist/vuex.esm-bundler.js': { code: '...', map: null },

  // manualChunks: vendor-element
  'node_modules/element-plus/es/index.mjs': { code: '...', map: null },
  'node_modules/@element-plus/icons-vue/dist/index.mjs': { code: '...', map: null },

  // 自动分割: monaco-editor
  'node_modules/monaco-editor/esm/vs/editor/editor.main.js': { code: '...', map: null },
  'node_modules/monaco-editor/esm/vs/editor/editor.api.js': { code: '...', map: null },

  // 业务代码
  'src/main.js': { code: '...', map: { /* sourcemap 数据 */ } },
  'src/views/home.vue': { code: '...', map: { /* sourcemap 数据 */ } },
}

// 统计
✅ 保留 sourcemap: 50 个文件 (业务代码)
🚫 跳过 sourcemap: 200 个文件 (第三方库)
```

#### 阶段 2: Chunk 生成（信息丢失）⚠️

```javascript
// Rollup 根据配置进行代码分割
rollupOptions: {
  output: {
    manualChunks: {
      'vendor-vue': ['vue', 'vue-router', 'vuex', 'vue-demi'],
      'vendor-element': ['element-plus', '@element-plus/icons-vue'],
      // ...
    }
  }
}

// Chunk 合并逻辑（伪代码）
function createChunk(modules, chunkName) {
  // 合并所有模块的代码
  const mergedCode = modules.map(m => m.code).join('\n');

  // ⚠️ 关键：丢弃所有模块的 sourcemap
  // 不管这些模块的 map 是 null、{ ... } 还是 undefined
  // 合并后统一重置为 undefined

  return {
    name: chunkName,
    code: mergedCode,
    map: undefined  // ← 统一重置，历史信息完全丢失
  };
}

// 所有 chunk 的状态
chunks = [
  // manualChunks 配置的
  { name: 'vendor-vue', map: undefined },       // ← 重置
  { name: 'vendor-element', map: undefined },   // ← 重置
  { name: 'vendor-vxe', map: undefined },       // ← 重置

  // 自动分割的
  { name: 'monaco-editor', map: undefined },    // ← 重置

  // 业务代码
  { name: 'index', map: undefined },            // ← 也重置了
]

// 关键问题：所有 chunk 的 map 都是 undefined
// 无法区分哪些应该有 sourcemap，哪些不应该有
```

**为什么要重置？**

Rollup 的逻辑：

- 合并前，每个模块的 sourcemap 都是针对单个文件的
- 合并后，生成了一个新的大文件，旧的 sourcemap 都无效了
- 所以全部丢弃，状态重置为 `undefined`

#### 阶段 3: Output 生成（统一生成）❌

```javascript
// Rollup 检查配置
const sourcemapConfig = viteConfig.build.sourcemap; // 'hidden'

// Rollup 的决策逻辑
if (sourcemapConfig === 'hidden' || sourcemapConfig === true) {
  for (const chunk of chunks) {
    // 检查 chunk 的 map 状态
    if (chunk.map === undefined) {
      // "这个 chunk 没有 sourcemap，我需要生成一个新的！"
      chunk.map = generateNewSourcemap(chunk.code);
    }
  }
}

// 问题：Rollup 无法知道：
// - 这个 chunk 的原始模块在 Transform 阶段返回了 map: null
// - 这个 chunk 是 vendor 还是业务代码
// - 这个 chunk 是 manualChunks 配置的还是自动分割的

// Rollup 只知道：
// - chunk.map === undefined
// - config.sourcemap === 'hidden'
// - 结论：生成 sourcemap

// 最终输出（所有 chunk 都生成了 sourcemap）
dist/assets/vendor-vue-C9gVCVuR.js.map          ← 生成了
dist/assets/vendor-element-4vsbiGeC.js.map      ← 生成了
dist/assets/vendor-vxe-BTD-ZBhw.js.map          ← 生成了
dist/assets/monaco-editor-DkVVM8E4.js.map       ← 生成了
dist/assets/index-Bk8aZ-po.js.map               ← 生成了
```

---

## 关键发现对比表

| Chunk 类型         | 配置方式     | Transform 阶段     | Chunk 阶段     | Output 阶段    | 最终结果   |
| ------------------ | ------------ | ------------------ | -------------- | -------------- | ---------- |
| **vendor-vue**     | manualChunks | map: null          | map: undefined | 生成 sourcemap | ❌ 有 .map |
| **vendor-element** | manualChunks | map: null          | map: undefined | 生成 sourcemap | ❌ 有 .map |
| **vendor-vxe**     | manualChunks | map: null          | map: undefined | 生成 sourcemap | ❌ 有 .map |
| **monaco-editor**  | 自动分割     | map: null          | map: undefined | 生成 sourcemap | ❌ 有 .map |
| **index**          | 业务代码     | 不处理（保留原始） | map: undefined | 生成 sourcemap | ✅ 有 .map |

**结论**：所有 chunk 的处理逻辑完全一样，都生成了 sourcemap！

---

## 为什么 manualChunks 和自动分割都失效？

### 原因 1: Chunk 合并的统一处理

```javascript
// 对 manualChunks 的处理
const vendorVueChunk = createChunk(
  [vue, vueRouter, vuex],  // 这些模块的 map 都是 null
  'vendor-vue'
);
// 结果: { name: 'vendor-vue', map: undefined }

// 对自动分割的处理
const monacoChunk = createChunk(
  [monacoEditor1, monacoEditor2, ...],  // 这些模块的 map 也是 null
  'monaco-editor'
);
// 结果: { name: 'monaco-editor', map: undefined }

// 两者的结果完全一样！
```

### 原因 2: Output 阶段的统一逻辑

```javascript
// Rollup 在 Output 阶段不区分 chunk 的来源
function generateOutput(chunks, config) {
  for (const chunk of chunks) {
    // 不关心这个 chunk 是：
    // - manualChunks 配置的
    // - 自动分割的
    // - 业务代码

    // 只关心：
    // - chunk.map 是否为 undefined
    // - config.sourcemap 的值

    if (chunk.map === undefined && config.sourcemap === "hidden") {
      chunk.map = generateNewSourcemap(chunk.code);
    }
  }
}
```

### 原因 3: 没有元数据传递机制

```javascript
// Transform 阶段的信息
module.map = null; // "我不要 sourcemap"

// Chunk 阶段
chunk.map = undefined; // "我没有 sourcemap"

// 问题：Rollup 无法区分：
// - undefined: 从未生成过 sourcemap
// - null: 明确不要 sourcemap

// 如果有元数据机制（假设）
chunk = {
  name: "vendor-vue",
  code: "...",
  map: undefined,
  metadata: {
    originalMapStatus: "null", // ← 记录原始状态
    source: "manualChunks", // ← 记录来源
    shouldGenerateSourcemap: false, // ← 记录意图
  },
};

// 但实际上 Rollup 没有这个机制
// 所有信息在 chunk 合并时都丢失了
```

---

## 完整构建流程示例

```javascript
// ============================================
// 阶段 1: Transform（模块级别）
// ============================================

// 处理 Vue 相关的模块
transform(code, id: 'node_modules/vue/dist/vue.esm-bundler.js')
→ 返回 { code, map: null }  ✅

transform(code, id: 'node_modules/vue-router/dist/vue-router.esm-bundler.js')
→ 返回 { code, map: null }  ✅

// 处理 Element Plus 相关的模块
transform(code, id: 'node_modules/element-plus/es/index.mjs')
→ 返回 { code, map: null }  ✅

// 处理 Monaco Editor 相关的模块
transform(code, id: 'node_modules/monaco-editor/esm/vs/editor/editor.main.js')
→ 返回 { code, map: null }  ✅

// 处理业务代码（当前插件不处理，由其他插件如 vite:esbuild 生成 sourcemap）
transform(code, id: 'src/main.js')
→ 返回 null (不做转换)  ✅

// ============================================
// 阶段 2: Chunk 生成（关键阶段）
// ============================================

// Chunk 1: vendor-vue (manualChunks 配置)
const vendorVueModules = [
  'node_modules/vue/dist/vue.esm-bundler.js',           // map: null
  'node_modules/vue-router/dist/vue-router.esm-bundler.js', // map: null
  'node_modules/vuex/dist/vuex.esm-bundler.js',         // map: null
  // ... 20+ 个文件
];

const vendorVueChunk = {
  name: 'vendor-vue',
  code: mergeModules(vendorVueModules),
  map: undefined  // ← 关键：丢弃所有中间 sourcemap
};

// Chunk 2: monaco-editor (自动分割)
const monacoEditorModules = [
  'node_modules/monaco-editor/esm/vs/editor/editor.main.js', // map: null
  'node_modules/monaco-editor/esm/vs/editor/editor.api.js',  // map: null
  // ... 100+ 个文件
];

const monacoEditorChunk = {
  name: 'monaco-editor',
  code: mergeModules(monacoEditorModules),
  map: undefined  // ← 同样丢弃了所有中间 sourcemap
};

// Chunk 3: index (业务代码)
const indexModules = [
  'src/main.js',           // map: { /* 有 sourcemap */ }
  'src/views/home.vue',    // map: { /* 有 sourcemap */ }
  // ... 100+ 个业务文件
];

const indexChunk = {
  name: 'index',
  code: mergeModules(indexModules),
  map: undefined  // ← 即使原始模块有 sourcemap，合并后也重置为 undefined
};

// ⚠️ 关键发现：所有 chunk 的 map 都是 undefined
chunks = [
  { name: 'vendor-vue', map: undefined },
  { name: 'vendor-element', map: undefined },
  { name: 'monaco-editor', map: undefined },
  { name: 'index', map: undefined },
];

// ============================================
// 阶段 3: Output 生成（问题爆发）
// ============================================

// Rollup 检查配置
if (sourcemapConfig === 'hidden') {
  for (const chunk of chunks) {
    if (chunk.map === undefined) {
      // 重新生成 sourcemap
      chunk.map = generateSourcemap(chunk.code);

      // 输出文件
      writeFile(`dist/assets/${chunk.name}.js`, chunk.code);
      writeFile(`dist/assets/${chunk.name}.js.map`, chunk.map);
    }
  }
}

// 最终输出（所有 chunk 都生成了 sourcemap）
writeFile('dist/assets/vendor-vue-C9gVCVuR.js.map', ...);       // ← 生成了
writeFile('dist/assets/vendor-element-4vsbiGeC.js.map', ...);   // ← 生成了
writeFile('dist/assets/monaco-editor-DkVVM8E4.js.map', ...);    // ← 生成了
writeFile('dist/assets/index-Bk8aZ-po.js.map', ...);            // ← 生成了
```

---

## 数据流对比

### ❌ Transform 钩子（失败）

```
Transform 阶段
├─ vendor-vue 的模块
│  ├─ vue.esm.js          → map: null ✅
│  ├─ vue-router.esm.js   → map: null ✅
│  └─ vuex.esm.js         → map: null ✅
├─ vendor-element 的模块
│  └─ element-plus.mjs    → map: null ✅
└─ monaco-editor 的模块
   └─ editor.main.js      → map: null ✅

        ↓ Chunk 合并（信息丢失）

Chunk 阶段
├─ vendor-vue          → map: undefined ⚠️
├─ vendor-element      → map: undefined ⚠️
└─ monaco-editor       → map: undefined ⚠️

        ↓ Output 生成（配置生效）

Output 阶段
检查: sourcemap: 'hidden' ✅
所有 chunk.map === undefined
        ↓
为所有 chunk 生成 sourcemap
├─ vendor-vue.js.map          ❌
├─ vendor-element.js.map      ❌
└─ monaco-editor.js.map       ❌
```

### ✅ GenerateBundle 钩子（成功）

```
Transform 阶段
└─ 正常处理（不过滤）

        ↓

Chunk 阶段
└─ 正常合并

        ↓

Output 阶段
└─ 生成所有 sourcemap
   ├─ vendor-vue.js.map
   ├─ vendor-element.js.map
   └─ monaco-editor.js.map

        ↓ GenerateBundle 钩子（关键）

删除不需要的 sourcemap
├─ delete vendor-vue.js.map       ✅
├─ delete vendor-element.js.map   ✅
├─ delete monaco-editor.js.map    ✅
└─ 保留 index.js.map              ✅

        ↓

最终输出
└─ 只有 index.js.map
```

---

## 正确的解决方案

### 使用 GenerateBundle 钩子

```javascript
// vite/plugins/sourcemap-output-filter.js
export default function createSourcemapOutputFilter(options = {}) {
  const { verbose = false } = options;

  return {
    name: "sourcemap-output-filter",
    apply: "build",
    enforce: "post",

    generateBundle(outputOptions, bundle) {
      // 定义需要排除的 chunk 模式
      const excludePatterns = [
        /^vendor-/, // 所有 manualChunks 的 vendor
        /^monaco-editor/, // 自动分割的 monaco-editor
      ];

      let deletedCount = 0;
      let keptCount = 0;

      for (const fileName in bundle) {
        const file = bundle[fileName];

        if (file.type === "chunk") {
          const shouldExclude = excludePatterns.some((pattern) =>
            pattern.test(file.name),
          );

          if (shouldExclude) {
            // 删除 sourcemap 文件
            const mapFileName = `${fileName}.map`;
            if (bundle[mapFileName]) {
              delete bundle[mapFileName];
              deletedCount++;

              if (verbose) {
                console.log(`[sourcemap-filter] 删除: ${mapFileName}`);
              }
            }

            // 移除 sourceMappingURL 注释
            if (file.code) {
              file.code = file.code.replace(
                /\/\/# sourceMappingURL=.*\.map/g,
                "",
              );
            }
          } else {
            // 保留业务代码的 sourcemap
            const mapFileName = `${fileName}.map`;
            if (bundle[mapFileName]) {
              keptCount++;

              if (verbose) {
                console.log(`[sourcemap-filter] 保留: ${mapFileName}`);
              }
            }
          }
        }
      }

      if (verbose) {
        console.log(`\n[sourcemap-filter] 统计:`);
        console.log(`  删除: ${deletedCount} 个 sourcemap`);
        console.log(`  保留: ${keptCount} 个 sourcemap\n`);
      }
    },
  };
}
```

### 最终效果

```bash
# 所有 vendor chunk 和第三方库的 sourcemap 都被删除
dist/assets/vendor-vue-C9gVCVuR.js           ← 没有 .map ✅
dist/assets/vendor-element-4vsbiGeC.js       ← 没有 .map ✅
dist/assets/vendor-vxe-BTD-ZBhw.js           ← 没有 .map ✅
dist/assets/monaco-editor-DkVVM8E4.js        ← 没有 .map ✅

# 只有业务代码保留 sourcemap
dist/assets/index-Bk8aZ-po.js.map            ← 保留 ✅
```

---

## 总结

### Transform 钩子失效的根本原因

1. **所有 chunk 的状态都一样**
   - 不管是 manualChunks 配置的还是自动分割的
   - 不管原始模块有没有 sourcemap
   - 合并后都变成 `map: undefined`

2. **Chunk 合并会重置所有 Sourcemap 状态**

   ```javascript
   // Transform 阶段
   module1: { code: '...', map: null }      // 明确不要 sourcemap
   module2: { code: '...', map: { ... } }   // 有 sourcemap
   module3: { code: '...', map: null }      // 明确不要 sourcemap

   // Chunk 合并后
   chunk: {
     code: module1.code + module2.code + module3.code,
     map: undefined  // ← 所有信息都丢失，统一重置为 undefined
   }
   ```

3. **Output 阶段只看配置，不看历史**

   ```javascript
   // Rollup 的决策逻辑
   if (config.sourcemap === "hidden") {
     for (const chunk of chunks) {
       if (chunk.map === undefined) {
         // "没有 sourcemap？那我生成一个！"
         chunk.map = generateNewSourcemap(chunk.code);
       }
     }
   }
   ```

4. **没有元数据传递机制**
   - Transform 阶段的 `map: null` 无法传递到 Output 阶段
   - Chunk 合并会清除所有历史信息
   - Output 阶段无法知道哪些 chunk 应该有 sourcemap

### 唯一的解决方案

**使用 `generateBundle` 钩子在 Output 阶段直接删除不需要的 sourcemap 文件！**

```javascript
generateBundle(outputOptions, bundle) {
  // 在这个时机：
  // ✅ sourcemap 已经生成
  // ✅ 可以看到所有 chunk 的名称
  // ✅ 可以直接删除文件

  for (const fileName in bundle) {
    if (shouldExclude(fileName)) {
      delete bundle[`${fileName}.map`];  // 真正删除
    }
  }
}
```

这是唯一能真正控制最终 sourcemap 输出的方法！🎯

---

**文档版本：** 1.0
**最后更新：** 2026-01-23
**适用 Vite 版本：** 5.x+
