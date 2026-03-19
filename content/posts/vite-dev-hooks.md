---
title: "Vite Dev 模式下的插件钩子执行详解"
date: 2026-03-19
draft: false
description: "深入剖析 Vite 启动开发服务器（vite dev）时所触发的插件钩子，涵盖钩子类型、执行时机、执行顺序及与构建模式的差异对比"
tags: ["Vite", "插件", "前端工程化", "开发工具"]
categories: ["笔记"]
---

本文详细介绍 Vite 在 `dev` 模式（`vite dev` / `vite serve`）下，插件系统会触发哪些钩子、触发时机及执行顺序。

## 目录

- [1. Dev 模式与 Build 模式的核心差异](#1-dev-模式与-build-模式的核心差异)
- [2. 钩子执行总览](#2-钩子执行总览)
- [3. 服务器启动阶段](#3-服务器启动阶段)
- [4. 模块请求阶段（按需触发）](#4-模块请求阶段按需触发)
- [5. HTML 转换阶段](#5-html-转换阶段)
- [6. HMR 热更新阶段](#6-hmr-热更新阶段)
- [7. 服务器关闭阶段](#7-服务器关闭阶段)
- [8. Dev 模式不会触发的钩子](#8-dev-模式不会触发的钩子)
- [9. 钩子执行顺序示例](#9-钩子执行顺序示例)
- [10. 实用插件示例](#10-实用插件示例)
- [11. 总结](#11-总结)

---

## 1. Dev 模式与 Build 模式的核心差异

Vite dev 模式启动的是一个基于 **原生 ESM** 的开发服务器，而不是像 build 模式那样将整个项目打包成 bundle。

| 特性 | Dev 模式 | Build 模式 |
|------|----------|-----------|
| 底层引擎 | 原生 ESM + esbuild（依赖预构建） | Rollup |
| 模块处理方式 | 按需（浏览器请求时）处理 | 全量分析、打包 |
| Rollup 完整管线 | 不执行（无 chunk 生成） | 完整执行 |
| HMR 相关钩子 | 触发 | 不触发 |
| 服务器相关钩子 | 触发 | 不触发 |
| chunk 相关钩子 | 不触发 | 触发 |

---

## 2. 钩子执行总览

```
vite dev 启动
  ↓
【启动阶段】
config          → 修改/合并用户配置
configResolved  → 读取最终配置（只读）
configureServer → 注册自定义中间件
options         → 修改 Rollup/Vite 内部选项
buildStart      → 服务器就绪，开始处理模块

  ↓（浏览器请求模块时，每个模块触发一次）

【模块请求阶段】
resolveId       → 解析模块路径
load            → 加载模块内容
transform       → 转换模块代码

  ↓（浏览器请求 HTML 时）

【HTML 处理阶段】
transformIndexHtml → 转换 index.html

  ↓（文件变更时）

【HMR 阶段】
hotUpdate / handleHotUpdate → 处理热更新

  ↓（执行 Ctrl+C 关闭服务器时）

【关闭阶段】
buildEnd        → 模块图销毁前
closeBundle     → 服务器完全关闭后
```

---

## 3. 服务器启动阶段

### 3.1 `config`

**时机**：读取并合并所有插件配置之前。

```ts
{
  name: 'my-plugin',
  config(userConfig, env) {
    // env.command === 'serve' 时为 dev 模式
    if (env.command === 'serve') {
      return {
        resolve: {
          alias: { '@': '/src' }
        }
      }
    }
  }
}
```

- 可返回部分配置对象，Vite 会深度合并
- 此时其他插件的配置尚未完全合并

### 3.2 `configResolved`

**时机**：所有插件的 `config` 钩子执行完毕、配置最终确定后。

```ts
{
  name: 'my-plugin',
  configResolved(resolvedConfig) {
    // 只读访问最终配置
    console.log('根目录：', resolvedConfig.root)
    console.log('模式：', resolvedConfig.command) // 'serve'
    console.log('插件列表：', resolvedConfig.plugins.map(p => p.name))
  }
}
```

- 适合读取最终配置、存储供后续钩子使用
- **不能**修改配置（只读）

### 3.3 `configureServer`（Vite 专属）

**时机**：开发服务器创建完成后、内部中间件安装之前。

```ts
{
  name: 'my-plugin',
  configureServer(server) {
    // 在内部中间件之前添加自定义中间件
    server.middlewares.use('/api', (req, res) => {
      res.end('mock data')
    })

    // 返回函数则在内部中间件之后执行
    return () => {
      server.middlewares.use((req, res, next) => {
        // 后置中间件
        next()
      })
    }
  }
}
```

- `server` 对象提供 `watcher`、`ws`（WebSocket）、`moduleGraph` 等
- 只在 dev 模式触发，build 模式对应的是 `configurePreviewServer`

### 3.4 `options`

**时机**：Vite 初始化内部 Rollup 兼容选项时（服务器启动前）。

```ts
{
  name: 'my-plugin',
  options(rollupOptions) {
    // 可修改 input、external 等选项
    return {
      ...rollupOptions,
      external: ['lodash']
    }
  }
}
```

- dev 模式下仅作为插件钩子执行，并不真正驱动 Rollup 打包

### 3.5 `buildStart`

**时机**：服务器完成初始化、准备好接收请求时。

```ts
{
  name: 'my-plugin',
  buildStart(options) {
    console.log('dev server 已就绪，开始监听模块请求')
    // 适合初始化插件内部状态
  }
}
```

---

## 4. 模块请求阶段（按需触发）

> 每当浏览器请求一个模块（`.js`、`.ts`、`.vue`、`.css` 等）时，以下三个钩子按顺序触发。

### 4.1 `resolveId`

**时机**：解析 `import` 语句中的模块 ID 时。

```ts
{
  name: 'my-plugin',
  resolveId(source, importer, options) {
    // source: 导入路径，如 'lodash' 或 './utils'
    // importer: 发起导入的文件路径
    if (source === 'virtual:my-module') {
      return '\0virtual:my-module' // \0 前缀表示虚拟模块
    }
    return null // 返回 null 则交给下一个插件处理
  }
}
```

- 返回解析后的绝对路径，或 `null` 跳过
- 可用于创建**虚拟模块**

### 4.2 `load`

**时机**：`resolveId` 确定路径后，读取模块内容时。

```ts
{
  name: 'my-plugin',
  load(id) {
    if (id === '\0virtual:my-module') {
      // 返回虚拟模块的代码
      return `export const msg = 'Hello from virtual module'`
    }
    return null // 返回 null 则由 Vite 默认读取文件内容
  }
}
```

- 适合为虚拟模块提供内容，或拦截特定文件的加载

### 4.3 `transform`

**时机**：模块内容加载完成后，发送给浏览器之前。

```ts
{
  name: 'my-plugin',
  transform(code, id) {
    if (id.endsWith('.custom')) {
      const transformed = myCompiler(code)
      return {
        code: transformed,
        map: null // source map
      }
    }
    return null // 不处理则返回 null
  }
}
```

- **每个模块每次请求都会执行**（有缓存机制，未变更的模块不会重复 transform）
- 是最常用的钩子，用于编译 `.vue`、`.tsx`、自定义语言等

---

## 5. HTML 转换阶段

### 5.1 `transformIndexHtml`（Vite 专属）

**时机**：浏览器请求 `index.html` 时。

```ts
{
  name: 'my-plugin',
  transformIndexHtml(html) {
    // 简单字符串替换
    return html.replace('<title>App</title>', '<title>My App</title>')
  }
}
```

也可以返回标签注入描述对象：

```ts
{
  name: 'my-plugin',
  transformIndexHtml(html) {
    return {
      html,
      tags: [
        {
          tag: 'script',
          attrs: { src: '/analytics.js' },
          injectTo: 'body'
        }
      ]
    }
  }
}
```

- 可注入 `<script>`、`<link>`、`<meta>` 等标签
- 在 dev 和 build 模式下都会触发

---

## 6. HMR 热更新阶段

### 6.1 `hotUpdate`（Vite 5+ 推荐）

**时机**：检测到文件变更，即将向客户端发送 HMR 更新时。

```ts
{
  name: 'my-plugin',
  hotUpdate(ctx) {
    // ctx.file: 变更的文件路径
    // ctx.timestamp: 变更时间戳
    // ctx.modules: 受影响的模块数组
    // ctx.server: ViteDevServer 实例
    // ctx.read(): 读取文件新内容

    if (ctx.file.endsWith('.json')) {
      // 自定义 HMR 逻辑：向客户端发送自定义事件
      ctx.server.hot.send({
        type: 'custom',
        event: 'json-update',
        data: { file: ctx.file }
      })
      return [] // 返回空数组表示不需要默认 HMR 处理
    }
  }
}
```

### 6.2 `handleHotUpdate`（旧版，Vite 4 及以前）

```ts
{
  name: 'my-plugin',
  handleHotUpdate(ctx) {
    // 与 hotUpdate 类似，但参数结构略有不同
    // Vite 5 中已被 hotUpdate 取代
    if (ctx.file.endsWith('.custom')) {
      ctx.server.ws.send({ type: 'full-reload' })
      return []
    }
  }
}
```

> **注意**：Vite 5 推荐使用 `hotUpdate`，`handleHotUpdate` 仍可用但已被标记为废弃。

---

## 7. 服务器关闭阶段

### 7.1 `buildEnd`

**时机**：服务器关闭、模块图即将销毁时（`Ctrl+C` 后触发）。

```ts
{
  name: 'my-plugin',
  buildEnd(error) {
    if (error) {
      console.error('服务器异常关闭：', error)
    }
    // 清理资源
  }
}
```

### 7.2 `closeBundle`

**时机**：服务器完全关闭后的最后清理阶段。

```ts
{
  name: 'my-plugin',
  closeBundle() {
    // 释放文件句柄、关闭数据库连接等
    console.log('dev server 已关闭')
  }
}
```

---

## 8. Dev 模式不会触发的钩子

以下钩子属于 Rollup 打包阶段的专属钩子，**dev 模式下不会触发**：

| 钩子 | 原因 |
|------|------|
| `moduleParsed` | Rollup 解析 AST 时触发，dev 不完整运行 Rollup |
| `renderStart` | chunk 渲染开始时触发，dev 无 chunk 生成 |
| `renderChunk` | 每个 chunk 渲染时触发，dev 无 chunk |
| `augmentChunkHash` | 计算 chunk hash 时触发，dev 无 chunk |
| `generateBundle` | bundle 生成时触发，dev 无 bundle |
| `writeBundle` | bundle 写入磁盘时触发，dev 无写入 |
| `banner` / `footer` / `intro` / `outro` | chunk 头尾内容注入，dev 无 chunk |

---

## 9. 钩子执行顺序示例

以一次完整的 dev server 启动 + 首次请求为例：

```
1. config            ← 所有插件按顺序执行
2. configResolved    ← 所有插件按顺序执行
3. configureServer   ← 所有插件按顺序执行
4. options           ← 所有插件按顺序执行
5. buildStart        ← 所有插件按顺序执行

[浏览器请求 index.html]
6. transformIndexHtml

[浏览器请求 main.ts]
7. resolveId('main.ts')
8. load('/path/to/main.ts')
9. transform(code, '/path/to/main.ts')

[浏览器请求 App.vue]
10. resolveId('App.vue')
11. load('/path/to/App.vue')
12. transform(code, '/path/to/App.vue')

[文件变更触发 HMR]
13. hotUpdate(ctx)

[Ctrl+C 关闭服务器]
14. buildEnd
15. closeBundle
```

### 多个插件的钩子顺序

- **默认顺序**：按插件数组顺序依次执行
- **`enforce: 'pre'`**：插件钩子提前到普通插件之前执行
- **`enforce: 'post'`**：插件钩子推迟到普通插件之后执行

```
enforce: 'pre' 插件
  ↓
Vite 内置插件
  ↓
普通插件（无 enforce）
  ↓
enforce: 'post' 插件
```

---

## 10. 实用插件示例

### 示例：Dev 模式下注入环境变量

```ts
import type { Plugin } from 'vite'

function envInjectPlugin(): Plugin {
  let isDev = false

  return {
    name: 'env-inject',

    config(_, { command }) {
      isDev = command === 'serve'
    },

    configResolved(config) {
      console.log(`[env-inject] 运行模式: ${config.command}`)
    },

    transform(code, id) {
      if (!isDev) return null
      if (!id.endsWith('.ts') && !id.endsWith('.js')) return null

      // 开发模式下注入调试信息
      return code.replace(
        '__DEV_FILE__',
        JSON.stringify(id.replace(process.cwd(), ''))
      )
    }
  }
}
```

### 示例：自定义 HMR 通知

```ts
import type { Plugin } from 'vite'

function hmrNotifyPlugin(): Plugin {
  return {
    name: 'hmr-notify',

    hotUpdate(ctx) {
      const affectedModules = ctx.modules.map(m => m.id)
      console.log(`[HMR] 文件变更: ${ctx.file}`)
      console.log(`[HMR] 影响模块: ${affectedModules.join(', ')}`)

      // 不阻断默认 HMR 流程
      return ctx.modules
    }
  }
}
```

---

## 11. 总结

| 阶段 | 钩子 | 触发次数 | Vite 专属 |
|------|------|----------|-----------|
| 启动 | `config` | 1 次 | 是 |
| 启动 | `configResolved` | 1 次 | 是 |
| 启动 | `configureServer` | 1 次 | 是 |
| 启动 | `options` | 1 次 | 否（Rollup 兼容） |
| 启动 | `buildStart` | 1 次 | 否（Rollup 兼容） |
| 模块请求 | `resolveId` | 每模块 1 次 | 否（Rollup 兼容） |
| 模块请求 | `load` | 每模块 1 次 | 否（Rollup 兼容） |
| 模块请求 | `transform` | 每模块 1 次 | 否（Rollup 兼容） |
| HTML | `transformIndexHtml` | 每次请求 HTML | 是 |
| HMR | `hotUpdate` | 每次文件变更 | 是（Vite 5+） |
| HMR | `handleHotUpdate` | 每次文件变更 | 是（已废弃） |
| 关闭 | `buildEnd` | 1 次 | 否（Rollup 兼容） |
| 关闭 | `closeBundle` | 1 次 | 否（Rollup 兼容） |

Dev 模式下，插件与 Vite 的交互核心是：**启动时配置服务器、按需拦截模块请求、响应文件变更触发 HMR**。理解这条主线，就能灵活编写服务于开发体验的 Vite 插件。
