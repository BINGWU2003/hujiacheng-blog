---
title: "Sourcemap Filter 插件文档"
date: 2026-01-20
draft: false
description: ""
tags: []
categories: ["笔记"]
---

`sourcemap-filter.js` 是一个 Vite 插件，用于在构建时 **精细化过滤 Sourcemap**，只为业务代码生成 Sourcemap，排除 `node_modules` 和第三方库。

## 解决的问题

在大型项目中，完整生成所有文件的 Sourcemap 会导致：

- **内存占用过高**：可能超出 Node.js 默认的 4GB 限制
- **构建时间过长**：处理大量第三方库的 Sourcemap 耗时
- **文件体积膨胀**：Sourcemap 文件过大

## 解决方案

通过选择性生成 Sourcemap：

- ✅ **业务代码**：保留 Sourcemap，用于错误堆栈还原
- 🚫 **node_modules**：不生成 Sourcemap，节省内存

---

## 工作原理

```
构建流程
   │
   ▼
┌─────────────────────────────────────────────────┐
│  Vite transform 阶段                              │
│                                                   │
│  对每个模块判断：                                  │
│  ├─ node_modules/* → 返回 { code, map: null }    │
│  │                    (不生成 sourcemap)          │
│  │                                                │
│  ├─ 匹配业务模式 → 返回 null                       │
│  │                 (使用默认 sourcemap 生成)       │
│  │                                                │
│  └─ 其他文件 → 返回 { code, map: null }           │
│                (不生成 sourcemap)                 │
└─────────────────────────────────────────────────┘
```

### 核心逻辑

1. **排除 node_modules**：任何包含 `node_modules` 路径的文件都不生成 Sourcemap
2. **模式匹配**：只有匹配 `allowedPatterns` 的业务文件才保留 Sourcemap
3. **返回值控制**：
   - `return { code, map: null }` → 不生成 Sourcemap
   - `return null` → 使用默认的 Sourcemap 生成逻辑

---

## 配置选项

| 选项       | 类型       | 默认值  | 说明                              |
| ---------- | ---------- | ------- | --------------------------------- |
| `patterns` | `RegExp[]` | 见下方  | 允许生成 Sourcemap 的文件路径模式 |
| `verbose`  | `boolean`  | `false` | 是否输出详细日志                  |

### 默认的业务文件模式

```javascript
const defaultPatterns = [
  /\/src\/views\/.*\.(vue|js|ts|jsx|tsx)$/, // 业务页面
  /\/src\/components\/.*\.(vue|js|ts|jsx|tsx)$/, // 业务组件
  /\/src\/utils\/.*\.(js|ts)$/, // 工具函数
  /\/src\/option\/.*\.(js|ts)$/, // 配置项
  /\/src\/api\/.*\.(js|ts)$/, // API 接口
  /\/src\/store\/.*\.(js|ts)$/, // 状态管理
  /\/src\/router\/.*\.(js|ts)$/, // 路由配置
  /\/src\/hooks\/.*\.(js|ts)$/, // 钩子函数
  /\/src\/main\.[jt]s$/, // 主入口
  /\/src\/App\.vue$/, // 根组件
];
```

---

## 使用方式

### 在 vite/plugins/index.js 中注册

```javascript
import createSourcemapFilter from "./sourcemap-filter.js";

export default function createVitePlugins(env, isBuild) {
  const vitePlugins = [];

  if (isBuild) {
    // 只在构建时启用
    vitePlugins.push(createSourcemapFilter());
  }

  return vitePlugins;
}
```

### 自定义配置

```javascript
// 自定义模式
vitePlugins.push(
  createSourcemapFilter({
    patterns: [
      /\/src\/views\//, // 只保留 views 目录
      /\/src\/components\//, // 和 components 目录
    ],
    verbose: true, // 输出详细日志
  }),
);
```

---

## 构建输出示例

```
📊 [Sourcemap Filter] 统计信息:
   ✅ 保留 sourcemap: 156 个文件
   🚫 跳过 sourcemap: 1842 个文件
   💾 预计节省内存: ~92%
```

---

## Vite 插件 enforce 配置说明

| enforce 值    | 执行时机           | 是否适用                             |
| ------------- | ------------------ | ------------------------------------ |
| `'pre'`       | 在 Vue/TS 编译之前 | ❌ 不适用：此时 `.vue` 文件还未转换  |
| 不设置 (默认) | 在默认阶段执行     | ✅ 推荐：Vue/TS 已转换完成           |
| `'post'`      | 在所有插件之后     | ✅ 可用：但对 sourcemap 过滤效果相同 |

**当前配置**：使用默认顺序（不设置 `enforce`）

---

## 内存优化效果

| 场景             | 不使用插件 | 使用插件 | 节省 |
| ---------------- | ---------- | -------- | ---- |
| Sourcemap 文件数 | ~2000 个   | ~150 个  | 92%  |
| 内存峰值         | ~6GB       | ~3GB     | 50%  |
| 构建时间         | ~180s      | ~120s    | 33%  |

_注：数据为估算值，实际效果因项目而异_

---

## 完整源代码

```javascript
/**
 * Vite 插件：精细化过滤 sourcemap
 * 只为业务代码生成 sourcemap，排除 node_modules 和第三方库
 * 这样可以在满足 4G/6G 内存限制的同时，保证业务报错的可追溯性
 */
export default function createSourcemapFilter(options = {}) {
  // 定义允许生成 sourcemap 的业务文件夹或文件模式
  const defaultPatterns = [
    /\/src\/views\/.*\.(vue|js|ts|jsx|tsx)$/, // 所有业务页面
    /\/src\/components\/.*\.(vue|js|ts|jsx|tsx)$/, // 业务公共组件
    /\/src\/utils\/.*\.(js|ts)$/, // 工具函数
    /\/src\/option\/.*\.(js|ts)$/, // 配置项 (如 Avue 配置)
    /\/src\/api\/.*\.(js|ts)$/, // API 接口
    /\/src\/store\/.*\.(js|ts)$/, // 状态管理
    /\/src\/router\/.*\.(js|ts)$/, // 路由配置
    /\/src\/hooks\/.*\.(js|ts)$/, // 钩子函数
    /\/src\/main\.[jt]s$/, // 应用主入口
    /\/src\/App\.vue$/, // 应用根组件
  ];

  const allowedPatterns = options.patterns || defaultPatterns;
  const verbose = options.verbose || false;

  let filteredCount = 0;
  let allowedCount = 0;

  return {
    name: "sourcemap-filter-business-only",
    // enforce 配置说明:
    // ❌ 'pre': 在 Vue/TS 编译之前执行
    //   问题：此时 .vue 文件还未转换，sourcemap 还未生成，过早介入无意义
    //
    // ✅ 不设置 (undefined): 在默认阶段执行 【推荐】
    //   优势：Vue/TS 已转换完成，sourcemap 正在生成阶段，正好可以过滤
    //
    // ✅ 'post': 在所有插件之后执行
    //   优势：确保看到最终代码，但对 sourcemap 过滤来说和默认效果相同
    //
    // 当前配置：使用默认顺序（不设置 enforce）
    apply: "build",

    transform(code, id) {
      // 排除 node_modules
      if (id.includes("node_modules")) {
        filteredCount++;
        if (verbose) {
          console.log(`🚫 [Sourcemap Filter] 跳过 node_modules: ${id}`);
        }
        return { code, map: null };
      }

      // 标准化路径（统一使用正斜杠）
      const normalizedId = id.replace(/\\/g, "/");

      // 检查是否匹配允许的模式
      const isAllowed = allowedPatterns.some((pattern) =>
        pattern.test(normalizedId),
      );

      if (!isAllowed) {
        filteredCount++;
        if (verbose) {
          console.log(`🚫 [Sourcemap Filter] 跳过非业务代码: ${normalizedId}`);
        }
        // 对于不匹配的非业务代码，不生成 sourcemap 映射，节省内存
        return { code, map: null };
      }

      allowedCount++;
      if (verbose) {
        console.log(`✅ [Sourcemap Filter] 保留业务代码: ${normalizedId}`);
      }

      // 业务核心代码，保留 sourcemap 用于报错定位
      // 返回 null 表示继续使用默认的 sourcemap 生成逻辑
      return null;
    },

    buildEnd() {
      // 构建结束时输出统计信息
      console.log("\n📊 [Sourcemap Filter] 统计信息:");
      console.log(`   ✅ 保留 sourcemap: ${allowedCount} 个文件`);
      console.log(`   🚫 跳过 sourcemap: ${filteredCount} 个文件`);
      console.log(
        `   💾 预计节省内存: ~${Math.round((filteredCount / (allowedCount + filteredCount)) * 100)}%\n`,
      );
    },
  };
}
```

---

## 相关文件

| 文件                               | 说明                              |
| ---------------------------------- | --------------------------------- |
| `vite/plugins/sourcemap-filter.js` | 插件源文件                        |
| `vite/plugins/index.js`            | 插件注册入口                      |
| `vite.config.mjs`                  | Vite 配置 (`sourcemap: 'hidden'`) |
| `docs/vite-build-process.md`       | Vite 构建流程文档                 |

---

## 注意事项

1. **只在生产构建时启用**：通过 `apply: 'build'` 限制，开发模式不受影响
2. **路径标准化**：Windows 路径使用反斜杠 `\`，需转换为正斜杠 `/` 才能匹配正则
3. **Sentry 兼容**：只上传业务代码的 Sourcemap，可以正常定位错误
4. **按需扩展**：如需追踪其他目录（如 `src/directives`），添加对应的正则模式即可
