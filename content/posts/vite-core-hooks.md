---
title: "Vite 核心钩子完整文档"
date: 2026-04-04
draft: false
description: ""
tags: ["Vite", "插件", "前端工程化", "开发工具"]
categories: ["笔记"]
---

## 目录

1. [钩子总览与执行顺序](#一钩子总览与执行顺序)
2. [config — 修改配置](#二config--修改配置)
3. [configResolved — 读取最终配置](#三configresolved--读取最终配置)
4. [resolveId — 自定义模块路径解析](#四resolveid--自定义模块路径解析)
5. [load — 自定义模块内容加载](#五load--自定义模块内容加载)
6. [transform — 模块源码转换](#六transform--模块源码转换)
7. [generateBundle — 生成产物前处理](#七generatebundle--生成产物前处理)
8. [configureServer — 开发服务器中间件](#八configureserver--开发服务器中间件)
9. [handleHotUpdate — 自定义 HMR](#九handlehotupdate--自定义-hmr)
10. [钩子执行顺序控制](#十钩子执行顺序控制)
11. [完整插件模板](#十一完整插件模板)

---

## 一、钩子总览与执行顺序

### Dev 模式启动时

```
config
  → configResolved
    → configureServer
      → buildStart
        ↓ (每次请求某个模块)
        resolveId → load → transform
```

### Build 模式构建时

```
config
  → configResolved
    → buildStart
      → resolveId → load → transform   (每个模块)
        → moduleParsed
          → buildEnd
            → renderStart
              → renderChunk            (每个 chunk)
                → generateBundle
                  → writeBundle
                    → closeBundle
```

### 快速速查表

| 钩子 | Dev | Build | 最核心用途 |
|---|---|---|---|
| `config` | ✅ | ✅ | 动态修改 Vite 配置 |
| `configResolved` | ✅ | ✅ | 读取最终配置快照 |
| `resolveId` | ✅ | ✅ | 虚拟模块 / 路径重定向 |
| `load` | ✅ | ✅ | 自定义模块内容 |
| `transform` | ✅ | ✅ | 编译 / 转换源码 |
| `renderChunk` | ❌ | ✅ | 处理打包后的 chunk |
| `generateBundle` | ❌ | ✅ | 增删改最终产物文件 |
| `writeBundle` | ❌ | ✅ | 文件写入后的后处理 |
| `configureServer` | ✅ | ❌ | 添加开发服务器中间件 |
| `handleHotUpdate` | ✅ | ❌ | 自定义 HMR 热更新行为 |
| `transformIndexHtml` | ✅ | ✅ | 转换 index.html |

---

## 二、`config` — 修改配置

### 是什么

在 Vite 解析合并所有配置**之前**调用。每个插件都可以通过这个钩子返回一个对象，该对象会被**深度 merge** 进最终配置。是整个插件生命周期的第一个钩子。

### 函数签名

```ts
config(
  config: UserConfig,
  env: { command: 'build' | 'serve', mode: string }
): UserConfig | null | void
```

### 能做什么

- 根据 `command`（`serve` / `build`）动态切换配置
- 根据 `mode`（`development` / `production` / 自定义）注入不同参数
- 注入 `server.proxy`、`resolve.alias`、`build.rollupOptions` 等
- 动态修改 `base` 路径（常用于 CDN 部署）
- 设置 `external` 依赖（不打进 bundle 的包）

### 完整示例：多环境差异化配置插件

```ts
// vite-plugin-env-config.ts

import type { Plugin, UserConfig } from 'vite'

interface Options {
  cdnBase?: string
  apiTarget?: string
}

export default function envConfigPlugin(options: Options = {}): Plugin {
  return {
    name: 'vite-plugin-env-config',

    config(userConfig, { command, mode }) {
      console.log(`[env-config] command=${command}, mode=${mode}`)

      // ① Dev 模式：注入本地 mock 代理
      if (command === 'serve') {
        return {
          server: {
            proxy: {
              '/api': {
                target: options.apiTarget ?? 'http://localhost:3001',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/api/, '')
              }
            }
          },
          define: {
            __APP_ENV__: JSON.stringify('development')
          }
        }
      }

      // ② Build 模式：注入 CDN 路径 + 外部依赖
      if (command === 'build') {
        return {
          base: options.cdnBase ?? 'https://cdn.example.com/v1/',
          define: {
            __APP_ENV__: JSON.stringify(mode)
          },
          build: {
            rollupOptions: {
              // vue / react 不打进 bundle，运行时从 CDN 加载
              external: ['vue', 'react', 'react-dom'],
              output: {
                globals: {
                  vue: 'Vue',
                  react: 'React',
                  'react-dom': 'ReactDOM'
                },
                // 按文件类型分目录输出
                assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
                chunkFileNames: 'assets/js/[name]-[hash].js',
                entryFileNames: 'assets/js/[name]-[hash].js'
              }
            }
          }
        }
      }
    }
  }
}
```

### 实际效果

用户在 `vite.config.ts` 里只写了：

```ts
// vite.config.ts（用户写的）
export default defineConfig({
  plugins: [vue(), envConfigPlugin({ cdnBase: 'https://cdn.myapp.com/' })],
  server: { port: 5173 }
})
```

执行 `vite build` 后，最终合并得到的配置是：

```ts
// 最终配置（深度 merge 后）
{
  plugins: [...],
  server: { port: 5173 },   // 用户的保留
  base: 'https://cdn.myapp.com/',  // 插件注入的
  define: { __APP_ENV__: '"production"' },
  build: {
    rollupOptions: {
      external: ['vue', 'react', 'react-dom'],
      output: { globals: { vue: 'Vue', ... } }
    }
  }
}
```

### 注意事项

- 返回对象会被**深度 merge**，不会覆盖用户已有的配置项（比如用户设置了 `server.port`，插件返回 `{ server: { proxy: {...} } }` 不会清掉 port）
- 如果多个插件都修改了同一个字段，后面的插件会覆盖前面的（按插件数组顺序）
- 不要在 `config` 里保存配置引用，因为此时配置还没最终确定，应在 `configResolved` 里保存

---

## 三、`configResolved` — 读取最终配置

### 是什么

所有插件的 `config` 钩子都执行完、所有配置深度合并完成之后调用。此时拿到的是**最终、完全确定**的配置对象，类型为 `Readonly<ResolvedConfig>`，**不能修改**。

### 函数签名

```ts
configResolved(config: ResolvedConfig): void | Promise<void>
```

### 能做什么

- 把最终配置保存到插件外部变量，供 `transform`、`load` 等其他钩子使用
- 根据最终配置决定插件内部的行为开关
- 读取其他插件注入进来的配置
- 打印调试信息（查看 alias、plugins 等最终值）

### 完整示例：上下文感知插件

```ts
// vite-plugin-context.ts

import type { Plugin, ResolvedConfig } from 'vite'
import path from 'node:path'

// 插件内部状态（模块级变量，所有钩子共享）
let viteConfig: ResolvedConfig
let isBuild: boolean
let isSSR: boolean
let projectRoot: string
let isDev: boolean

export default function contextPlugin(): Plugin {
  return {
    name: 'vite-plugin-context',

    // ✅ 在这里保存配置
    configResolved(resolved) {
      viteConfig = resolved
      isBuild = resolved.command === 'build'
      isDev = resolved.command === 'serve'
      isSSR = !!resolved.build?.ssr
      projectRoot = resolved.root  // 绝对路径，如 /Users/me/my-app

      // 可以读取其他插件注入的 alias
      console.log('[context] resolve.alias:', resolved.resolve.alias)

      // 可以读取最终插件列表
      console.log('[context] 插件数量:', resolved.plugins.length)

      // ❌ 不能修改，这是 Readonly 类型
      // resolved.base = '/new-base/'  // TypeScript 报错
    },

    // 在 transform 里使用上面保存的变量
    transform(code, id) {
      // 只在生产非 SSR 构建中处理
      if (!isBuild || isSSR) return

      // 把绝对路径转为相对路径（用于错误提示）
      const relPath = path.relative(projectRoot, id)

      if (id.endsWith('.ts')) {
        // 生产构建时在每个 TS 模块顶部注入构建时间戳
        const timestamp = Date.now()
        return {
          code: `/* built: ${timestamp} */\n${code}`,
          map: null
        }
      }
    },

    resolveId(id) {
      // 根据当前模式决定虚拟模块的内容
      if (id === 'virtual:app-config') {
        return '\0virtual:app-config'
      }
    },

    load(id) {
      if (id === '\0virtual:app-config') {
        // 根据最终配置生成虚拟模块
        return `
          export const isDev = ${isDev}
          export const base = '${viteConfig.base}'
          export const mode = '${viteConfig.mode}'
        `
      }
    }
  }
}
```

### 转换过程

```
执行顺序：
  pluginA.config()  → 返回 { base: '/app/' }
  pluginB.config()  → 返回 { build: { sourcemap: true } }
  用户配置          → { server: { port: 8080 } }
         ↓ 深度 merge
  configResolved 拿到：
  {
    root: '/Users/me/my-app',
    base: '/app/',
    command: 'build',
    mode: 'production',
    server: { port: 8080 },
    build: { sourcemap: true, ssr: false, ... },
    resolve: { alias: { '@': '/Users/me/my-app/src' } },
    plugins: [/* 所有插件，已排序 */]
  }
```

---

## 四、`resolveId` — 自定义模块路径解析

### 是什么

每次遇到 `import` 语句，Vite 需要把 import 的路径（模块 id）解析成实际文件路径时调用。可以拦截任意 id，返回自定义路径，或者实现**虚拟模块**（不对应任何真实文件的模块）。

### 函数签名

```ts
resolveId(
  source: string,      // import 的路径，如 'vue'、'./utils'、'virtual:routes'
  importer?: string,   // 发起 import 的文件的绝对路径
  options?: { isEntry: boolean }
): string | false | null | { id: string; external?: boolean }
```

**返回值含义：**

- 返回字符串 → 这就是解析后的模块 id，Vite 会用它去调用 `load`
- 返回 `false` → 把该模块标记为 external（不打包，运行时从外部加载）
- 返回 `null` / `undefined` → 不处理，交给下一个插件或 Vite 默认逻辑

### 能做什么

- 实现虚拟模块（如 `virtual:auto-routes`、`virtual:icons`）
- 将某个模块重定向到另一个路径（如 `lodash` → `lodash-es`）
- 标记某些模块为 external（不打包）
- 根据 importer 动态决定解析结果

### 完整示例 1：虚拟模块 — 自动路由生成

```ts
// vite-plugin-auto-routes.ts

import type { Plugin } from 'vite'
import { glob } from 'fast-glob'
import path from 'node:path'

const VIRTUAL_ID = 'virtual:auto-routes'
// \0 前缀是 Rollup 社区约定，表示虚拟模块，防止其他插件误拦截
const RESOLVED_ID = '\0virtual:auto-routes'

export default function autoRoutesPlugin(): Plugin {
  return {
    name: 'vite-plugin-auto-routes',

    // Step 1: 拦截 'virtual:auto-routes' 这个特殊 id
    resolveId(id) {
      if (id === VIRTUAL_ID) {
        return RESOLVED_ID
      }
      // 其他 id 返回 undefined，Vite 继续用默认逻辑解析
    },

    // Step 2: 为虚拟 id 提供实际内容（见 load 钩子章节）
    load(id) {
      if (id !== RESOLVED_ID) return

      // 扫描 src/pages/ 目录下的所有 .vue 文件
      const pages = glob.sync('src/pages/**/*.vue', { absolute: false })

      // 生成 import 语句
      const imports = pages.map((file, i) => {
        return `import Page${i} from '/${file}'`
      }).join('\n')

      // 生成路由配置
      const routes = pages.map((file, i) => {
        // src/pages/user/[id].vue → /user/:id
        const routePath = '/' + file
          .replace('src/pages', '')
          .replace(/\.vue$/, '')
          .replace(/\/index$/, '')
          .replace(/\[(\w+)\]/g, ':$1')  // [id] → :id
          .replace(/^\//, '')

        return `{ path: '/${routePath}', component: Page${i} }`
      }).join(',\n  ')

      return `
${imports}

export default [
  ${routes}
]
      `.trim()
    }
  }
}
```

**使用效果：**

```
目录结构：
src/pages/
  index.vue
  about.vue
  user/[id].vue
  blog/[slug]/index.vue
```

```ts
// 源代码里写：
import routes from 'virtual:auto-routes'

// 等价于 Vite 动态生成了这样一个模块：
import Page0 from '/src/pages/index.vue'
import Page1 from '/src/pages/about.vue'
import Page2 from '/src/pages/user/[id].vue'
import Page3 from '/src/pages/blog/[slug]/index.vue'

export default [
  { path: '/', component: Page0 },
  { path: '/about', component: Page1 },
  { path: '/user/:id', component: Page2 },
  { path: '/blog/:slug', component: Page3 }
]
```

### 完整示例 2：路径重定向 + External 标记

```ts
// vite-plugin-resolve-override.ts

import type { Plugin } from 'vite'

export default function resolveOverridePlugin(): Plugin {
  return {
    name: 'vite-plugin-resolve-override',

    resolveId(id) {
      // ① 将 lodash 重定向到 lodash-es（支持 tree-shaking）
      // Before: import { cloneDeep } from 'lodash'
      // After:  import { cloneDeep } from 'lodash-es'
      if (id === 'lodash') {
        return { id: 'lodash-es', external: false }
      }

      // ② 将某个包标记为 external，从 CDN 加载
      // 打包产物里不会包含这个库的代码
      if (id === 'some-heavy-lib') {
        return {
          id: 'https://cdn.skypack.dev/some-heavy-lib@1.0.0',
          external: true
        }
      }

      // ③ 根据 importer 决定解析路径
      // 同一个 id，从不同文件 import 时解析到不同地方
      if (id === '@config') {
        // importer 是发起 import 的文件绝对路径
        // 这里可以根据 importer 返回不同的配置文件
      }
    }
  }
}
```

---

## 五、`load` — 自定义模块内容加载

### 是什么

`resolveId` 确定模块的 id 之后，Vite 准备读取模块内容时调用 `load`。可以返回任意字符串作为模块的代码，Vite 会把它当成 JS 模块处理。

### 函数签名

```ts
load(
  id: string  // resolveId 返回的模块 id
): string | { code: string; map?: SourceMap } | null | void
```

### 能做什么

- 配合 `resolveId` 提供虚拟模块的代码内容
- 读取非标准文件（YAML、TOML、CSV）并转成 JS
- 动态生成代码（扫描文件系统、读取数据库等）
- 在测试环境下用 mock 数据替换真实模块

### 完整示例 1：YAML 文件加载器

```ts
// vite-plugin-yaml.ts

import type { Plugin } from 'vite'
import yaml from 'js-yaml'
import fs from 'node:fs'

export default function yamlPlugin(): Plugin {
  return {
    name: 'vite-plugin-yaml',
    enforce: 'pre',

    // 让 Vite 把 .yaml/.yml 路径交给我们处理
    resolveId(id) {
      if (id.endsWith('.yaml') || id.endsWith('.yml')) {
        return id  // 直接返回原 id，让 load 来处理
      }
    },

    load(id) {
      if (!id.endsWith('.yaml') && !id.endsWith('.yml')) return

      // 读取文件原始内容
      const raw = fs.readFileSync(id, 'utf-8')

      // 解析 YAML
      const data = yaml.load(raw)

      // 转换为 JS 模块（支持具名导出和默认导出）
      const entries = Object.entries(data as Record<string, unknown>)
      const namedExports = entries
        .map(([k, v]) => `export const ${k} = ${JSON.stringify(v)}`)
        .join('\n')

      return `
${namedExports}
export default ${JSON.stringify(data)}
      `.trim()
    }
  }
}
```

**转换过程：**

```yaml
# database.yaml（原始文件）
host: localhost
port: 5432
name: myapp
pool:
  min: 2
  max: 10
```

```ts
// load 钩子返回的 JS 模块代码：
export const host = "localhost"
export const port = 5432
export const name = "myapp"
export const pool = { "min": 2, "max": 10 }
export default { host: "localhost", port: 5432, name: "myapp", pool: { min: 2, max: 10 } }

// 源代码里可以直接 import：
import config, { host, port } from './database.yaml'
console.log(host)  // "localhost"
console.log(port)  // 5432
```

### 完整示例 2：SVG 图标精灵虚拟模块

```ts
// vite-plugin-icons.ts

import type { Plugin } from 'vite'
import { glob } from 'fast-glob'
import fs from 'node:fs'
import path from 'node:path'

const VIRTUAL_ID = 'virtual:icons'
const RESOLVED_ID = '\0virtual:icons'

export default function iconsPlugin(iconDir = 'src/assets/icons'): Plugin {
  return {
    name: 'vite-plugin-icons',

    resolveId(id) {
      if (id === VIRTUAL_ID) return RESOLVED_ID
    },

    load(id) {
      if (id !== RESOLVED_ID) return

      // 扫描所有 SVG 图标文件
      const files = glob.sync(`${iconDir}/**/*.svg`)

      // 读取每个 SVG 并生成导出
      const exports = files.map((file) => {
        const name = path.basename(file, '.svg')
          .replace(/-([a-z])/g, (_, c) => c.toUpperCase())  // kebab → camelCase
        const content = fs.readFileSync(file, 'utf-8')
          .replace(/"/g, '\\"')  // 转义双引号

        return `export const ${name} = "${content}"`
      }).join('\n')

      // 同时导出图标名称列表
      const names = files.map(f => path.basename(f, '.svg'))

      return `
${exports}
export const iconNames = ${JSON.stringify(names)}
      `.trim()
    }
  }
}
```

**使用：**

```ts
// 源代码：
import { searchIcon, closeIcon } from 'virtual:icons'

// 等价于访问了扫描出来的 SVG 内容：
// searchIcon → '<svg>...</svg>' 字符串
// closeIcon  → '<svg>...</svg>' 字符串
```

---

## 六、`transform` — 模块源码转换

### 是什么

模块内容加载（`load`）之后，对每一个模块的源码执行转换。是整个 Vite 插件系统中**使用频率最高**的钩子。所有插件的 `transform` 按 `enforce` 顺序**链式执行**，上一个的输出是下一个的输入。

### 函数签名

```ts
transform(
  code: string,  // 当前模块的源码字符串
  id: string     // 模块的绝对路径（或虚拟模块 id）
): string | { code: string; map?: SourceMap } | null | void
```

### 能做什么

- 编译 TypeScript → JavaScript（剥除类型注解）
- 编译 Vue SFC / JSX → 渲染函数
- 编译 Sass / Less → CSS
- 自动注入代码（埋点、HMR 运行时、版权声明）
- 生产环境移除 `console.log` / `debugger`
- 替换环境变量 / 编译期常量

### Vite 内置 transform 链（一个 .vue 文件的完整旅程）

```
App.vue 被 import 时：

① @vitejs/plugin-vue (enforce: 'pre')
   输入: .vue 原始文件内容（含 template/script/style）
   输出: 拆成多个虚拟请求：
         App.vue?vue&type=script    → script setup 内容
         App.vue?vue&type=template  → template 编译结果
         App.vue?vue&type=style&0   → style 内容

② vite:esbuild (针对 script 部分，含 lang="ts")
   输入: TypeScript 代码（含类型注解、interface）
   输出: 纯 JavaScript（类型被剥除）

③ 用户自定义插件 (enforce: 'post')
   输入: 编译好的 JS
   输出: 注入埋点 / 移除 console 等

④ vite:import-analysis (Vite 内置，最后执行)
   输入: 含 import 语句的 JS
   输出: import 路径转为带版本号的完整 URL
         'vue' → '/node_modules/.vite/deps/vue.js?v=abc123'
```

### 完整示例 1：TypeScript 类型注解 → 纯 JS（esbuild 做的事）

**转换前（Button.tsx）：**

```tsx
interface ButtonProps {
  label: string
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  onClick: () => void
}

const variantStyles: Record<NonNullable<ButtonProps['variant']>, string> = {
  primary: 'bg-blue-500 text-white',
  secondary: 'bg-gray-200 text-gray-800',
  danger: 'bg-red-500 text-white'
}

export const Button: React.FC<ButtonProps> = ({
  label,
  variant = 'primary',
  disabled = false,
  onClick
}) => (
  <button
    className={`btn ${variantStyles[variant]} ${disabled ? 'opacity-50' : ''}`}
    onClick={onClick}
    disabled={disabled}
  >
    {label}
  </button>
)
```

**转换后（经过 esbuild transform + JSX transform）：**

```js
import { jsx as _jsx } from 'react/jsx-runtime'

// interface ButtonProps → 完全消失（纯类型，编译时抹除）
// Record<NonNullable<...>, string> → 抹除泛型，只剩运行时代码

const variantStyles = {
  primary: 'bg-blue-500 text-white',
  secondary: 'bg-gray-200 text-gray-800',
  danger: 'bg-red-500 text-white'
}

export const Button = ({
  label,
  variant = 'primary',
  disabled = false,
  onClick
}) => (
  _jsx("button", {
    className: `btn ${variantStyles[variant]} ${disabled ? 'opacity-50' : ''}`,
    onClick: onClick,
    disabled: disabled,
    children: label
  })
)
// 变化点：
// 1. interface 被完全移除
// 2. React.FC<ButtonProps> 泛型注解被移除
// 3. JSX 转为 _jsx() 函数调用
// 4. import React 被替换为 react/jsx-runtime（React 17+ 新 transform）
```

### 完整示例 2：Vue SFC 编译过程（@vitejs/plugin-vue 做的事）

**转换前（Counter.vue）：**

```vue
<template>
  <div class="counter">
    <h2>{{ title }}</h2>
    <button @click="decrement" :disabled="count <= 0">-</button>
    <span class="value">{{ count }}</span>
    <button @click="increment">+</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  max?: number
}

const props = withDefaults(defineProps<Props>(), { max: 100 })
const count = ref(0)

const increment = () => {
  if (count.value < props.max) count.value++
}
const decrement = () => {
  if (count.value > 0) count.value--
}
</script>

<style scoped>
.counter { display: flex; align-items: center; gap: 12px; }
.value { font-size: 24px; font-weight: bold; min-width: 40px; text-align: center; }
</style>
```

**转换后（plugin-vue 处理 script 部分，经过 esbuild 去类型后）：**

```js
// Counter.vue?vue&type=script&setup=true
import { ref, withDefaults, defineProps } from 'vue'

// interface Props → 消失
// withDefaults + defineProps<Props>() → 编译为运行时 props 定义

const __props = withDefaults(defineProps({
  title: { type: String, required: true },
  max: { type: Number, default: 100 }
}), { max: 100 })

const count = ref(0)

const increment = () => {
  if (count.value < __props.max) count.value++
}
const decrement = () => {
  if (count.value > 0) count.value--
}

// setup 返回值（供 template 使用）
export { count, increment, decrement }
```

**template 编译结果（Counter.vue?vue&type=template）：**

```js
import {
  createElementVNode as _createElementVNode,
  toDisplayString as _toDisplayString,
  openBlock as _openBlock,
  createElementBlock as _createElementBlock
} from 'vue'

export function render(_ctx, _cache) {
  return (_openBlock(), _createElementBlock("div", { class: "counter" }, [
    _createElementVNode("h2", null, _toDisplayString(_ctx.title), 1),
    _createElementVNode("button", {
      onClick: _cache[0] || (_cache[0] = (...args) => _ctx.decrement(...args)),
      disabled: _ctx.count <= 0
    }, "-", 8, ["disabled"]),
    _createElementVNode("span", { class: "value" },
      _toDisplayString(_ctx.count), 1),
    _createElementVNode("button", {
      onClick: _cache[1] || (_cache[1] = (...args) => _ctx.increment(...args))
    }, "+")
  ]))
}
```

**style scoped 处理（Counter.vue?vue&type=style&index=0&scoped=true）：**

```
输入: .counter { display: flex; ... }  .value { font-size: 24px; ... }

输出（浏览器实际注入的 CSS）:
  .counter[data-v-7ba5bd90] { display: flex; align-items: center; gap: 12px; }
  .value[data-v-7ba5bd90] { font-size: 24px; font-weight: bold; ... }

同时 template 里的元素被注入 data-v-7ba5bd90 属性，实现样式隔离
```

### 完整示例 3：自定义 transform — 生产环境代码清理插件

```ts
// vite-plugin-code-clean.ts

import type { Plugin } from 'vite'
import MagicString from 'magic-string'

export default function codeCleanPlugin(): Plugin {
  return {
    name: 'vite-plugin-code-clean',
    apply: 'build',      // 只在 build 模式执行
    enforce: 'post',     // 在其他插件（如 TS 编译）之后执行

    transform(code, id) {
      // 只处理 JS/TS 文件
      if (!/\.[jt]sx?$/.test(id)) return
      // 跳过 node_modules
      if (id.includes('node_modules')) return

      // 使用 MagicString 保留 sourcemap 信息
      const s = new MagicString(code)
      let changed = false

      // ① 移除 console.log / console.warn / console.info / console.debug
      // Before: console.log('debug:', someObject, anotherValue)
      // After:  (整行消失)
      code.replace(
        /^\s*console\.(log|warn|info|debug)\([\s\S]*?\);?\s*$/gm,
        (match, _type, offset) => {
          s.remove(offset, offset + match.length)
          changed = true
          return ''
        }
      )

      // ② 移除 debugger 语句
      // Before: debugger
      // After:  (消失)
      code.replace(/\bdebugger\b;?/g, (match, offset) => {
        s.remove(offset, offset + match.length)
        changed = true
        return ''
      })

      // ③ 替换 __DEV__ 标记为 false（生产环境）
      // Before: if (__DEV__) { showDevTools() }
      // After:  if (false) { showDevTools() }
      // （Rollup 的 tree-shaking 会进一步消除 if(false) 的死代码）
      code.replace(/__DEV__/g, (_match, offset) => {
        s.overwrite(offset, offset + 7, 'false')
        changed = true
        return ''
      })

      if (!changed) return null

      return {
        code: s.toString(),
        map: s.generateMap({ hires: true })
      }
    }
  }
}
```

**完整转换过程：**

```ts
// 转换前（src/utils/payment.ts）：
export async function processPayment(orderId: string, amount: number) {
  debugger  // ← 忘记删除的调试断点

  console.log('processing payment:', orderId, amount)

  if (__DEV__) {
    console.warn('DEV MODE: 跳过真实支付验证')
    return { success: true, mock: true }
  }

  const result = await callPaymentAPI(orderId, amount)
  console.info('payment result:', result)

  return result
}

// ↓↓↓ vite-plugin-code-clean transform 执行后 ↓↓↓

// 转换后：
export async function processPayment(orderId: string, amount: number) {
  // debugger 消失
  // console.log 消失

  if (false) {  // __DEV__ → false
    // console.warn 消失
    return { success: true, mock: true }
  }
  // if (false) 块会被 Rollup tree-shaking 完全消除

  const result = await callPaymentAPI(orderId, amount)
  // console.info 消失

  return result
}

// 最终 Rollup 产物（tree-shaking 后）：
export async function processPayment(orderId, amount) {
  const result = await callPaymentAPI(orderId, amount)
  return result
}
```

### 完整示例 4：自动埋点注入插件

```ts
// vite-plugin-auto-track.ts

import type { Plugin } from 'vite'

export default function autoTrackPlugin(): Plugin {
  return {
    name: 'vite-plugin-auto-track',
    enforce: 'post',
    apply: 'build',

    transform(code, id) {
      // 只处理 src/ 下的业务代码
      if (!id.includes('/src/')) return
      if (!/\.[jt]sx?$/.test(id)) return

      // 在每个导出函数的第一行注入埋点调用
      // Before:
      //   export function checkout(orderId) {
      //     processPayment(orderId)
      //   }
      //
      // After:
      //   export function checkout(orderId) {
      //     __track__('checkout', { args: [orderId] })
      //     processPayment(orderId)
      //   }

      const result = code.replace(
        /export\s+(async\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*\{/g,
        (match, asyncKw, fnName, params) => {
          const argNames = params
            .split(',')
            .map((p: string) => p.trim().split(/[\s:=]/)[0])
            .filter(Boolean)

          return `${match}
  __track__('${fnName}', { args: [${argNames.join(', ')}] })`
        }
      )

      // 在文件顶部注入 __track__ 函数引用
      if (result !== code) {
        return {
          code: `import { __track__ } from 'virtual:tracker'\n${result}`,
          map: null
        }
      }
    }
  }
}
```

---

## 七、`generateBundle` — 生成产物前处理

### 是什么

所有模块编译、所有 chunk 合并完成，即将调用 `fs.writeFile` 写入磁盘**之前**调用。拿到的 `bundle` 对象包含了所有将要输出的文件（chunk 和 asset），可以对它进行**增删改**。

### 函数签名

```ts
generateBundle(
  options: OutputOptions,   // Rollup 输出配置（dir、format 等）
  bundle: OutputBundle,     // 所有产物文件的集合
  isWrite: boolean          // 是否会真正写入磁盘
): void | Promise<void>
```

### bundle 对象结构

```ts
// bundle 是一个 Map-like 对象，key 是文件名
bundle = {
  // Chunk（JS 文件）
  'assets/index-Bq3XzYkL.js': {
    type: 'chunk',
    isEntry: true,          // 是否是入口文件
    isDynamicEntry: false,  // 是否是动态 import 的入口
    name: 'index',          // chunk 名称
    fileName: 'assets/index-Bq3XzYkL.js',
    code: '/* 打包后的 JS 代码 */',
    map: null,
    imports: ['assets/vendor-Cx9dKJqL.js'],
    exports: ['default'],
    modules: { '/src/main.ts': {...}, ... }
  },
  // Asset（非 JS 文件）
  'assets/logo-DqKz8v3n.png': {
    type: 'asset',
    fileName: 'assets/logo-DqKz8v3n.png',
    name: 'logo.png',
    source: Buffer.from('...')  // 文件内容
  }
}
```

### 能做什么

- 新增文件（`this.emitFile`）：manifest.json、version.txt、service worker 等
- 删除文件（`delete bundle[key]`）：去掉不需要的 sourcemap 等
- 修改 chunk 代码（直接修改 `chunk.code`）：注入版本号、license 声明等
- 分析产物结构，生成构建报告

### 完整示例：多功能产物处理插件

```ts
// vite-plugin-bundle-processor.ts

import type { Plugin } from 'vite'
import { createHash } from 'node:crypto'
import pkg from './package.json' assert { type: 'json' }

export default function bundleProcessorPlugin(): Plugin {
  return {
    name: 'vite-plugin-bundle-processor',

    generateBundle(options, bundle) {
      const manifest: Record<string, {
        file: string
        src?: string
        isEntry?: boolean
        imports?: string[]
      }> = {}

      const stats = {
        chunks: 0,
        assets: 0,
        totalSize: 0
      }

      for (const [fileName, file] of Object.entries(bundle)) {

        // ① 统计信息
        if (file.type === 'chunk') {
          stats.chunks++
          stats.totalSize += file.code.length

          // ② 给每个 chunk 添加版权声明头部
          // Before: (function(){...})()
          // After:
          //   /*!
          //    * MyApp v1.2.3 | MIT License
          //    * Build: 2024-01-15T10:30:00Z
          //    */
          //   (function(){...})()
          if (file.isEntry || file.isDynamicEntry) {
            file.code = [
              `/*!`,
              ` * ${pkg.name} v${pkg.version} | ${pkg.license} License`,
              ` * Build: ${new Date().toISOString()}`,
              ` * Commit: ${process.env.GIT_COMMIT ?? 'local'}`,
              ` */`,
              file.code
            ].join('\n')
          }

          // ③ 收集到 manifest
          manifest[file.name] = {
            file: fileName,
            isEntry: file.isEntry,
            imports: file.imports
          }

          // 如果有对应的源文件信息
          const srcModules = Object.keys(file.modules)
          if (srcModules.length === 1) {
            manifest[file.name].src = srcModules[0]
              .replace(process.cwd() + '/', '')
          }
        } else {
          // asset 文件
          stats.assets++
          if (file.source instanceof Uint8Array) {
            stats.totalSize += file.source.length
          } else {
            stats.totalSize += file.source.length
          }
        }

        // ④ 删除 sourcemap 文件（如果不需要）
        if (fileName.endsWith('.map') && !options.sourcemap) {
          delete bundle[fileName]
          continue
        }
      }

      // ⑤ 生成 manifest.json
      // dist/manifest.json:
      // {
      //   "main": { "file": "assets/index-Bq3X.js", "isEntry": true },
      //   "vendor": { "file": "assets/vendor-Cx9d.js" }
      // }
      this.emitFile({
        type: 'asset',
        fileName: 'manifest.json',
        source: JSON.stringify(manifest, null, 2)
      })

      // ⑥ 生成构建信息文件
      // dist/build-info.json:
      // { "version": "1.2.3", "buildTime": "...", "chunks": 3, ... }
      this.emitFile({
        type: 'asset',
        fileName: 'build-info.json',
        source: JSON.stringify({
          version: pkg.version,
          buildTime: new Date().toISOString(),
          chunks: stats.chunks,
          assets: stats.assets,
          totalSizeKB: Math.round(stats.totalSize / 1024)
        }, null, 2)
      })

      console.log(
        `\n📦 Bundle 分析：`,
        `${stats.chunks} chunks,`,
        `${stats.assets} assets,`,
        `总大小 ~${Math.round(stats.totalSize / 1024)}KB`
      )
    }
  }
}
```

**执行后的 dist/ 目录：**

```
dist/
├── assets/
│   ├── index-Bq3XzYkL.js    ← 入口 chunk（头部加了版权声明）
│   ├── vendor-Cx9dKJqL.js   ← vendor chunk
│   └── logo-DqKz8v3n.png    ← 图片 asset
├── manifest.json             ← ✨ 新增
├── build-info.json           ← ✨ 新增
└── index.html
```

---

## 八、`configureServer` — 开发服务器中间件

### 是什么

Dev 专属钩子，在开发服务器创建之后、监听请求之前调用。可以向 Vite 的 Connect 中间件栈中添加自定义中间件。

### 函数签名

```ts
configureServer(server: ViteDevServer): (() => void) | void | Promise<...>
```

**ViteDevServer 主要属性：**

```ts
interface ViteDevServer {
  config: ResolvedConfig        // 最终配置
  middlewares: Connect.Server   // Connect 中间件实例
  httpServer: http.Server       // Node.js HTTP 服务器
  watcher: chokidar.FSWatcher   // 文件监听器
  ws: WebSocketServer           // WebSocket 服务（用于 HMR）
  moduleGraph: ModuleGraph      // 模块依赖图
}
```

### 能做什么

- 添加 mock API 接口（无需启动额外的 mock server 进程）
- 添加请求日志、鉴权等中间件
- 监听文件变化，手动触发模块失效或 HMR
- 通过 WebSocket 向浏览器发送自定义消息
- 直接返回一个函数 = 后置中间件（在 Vite 内置处理之后执行）

### 完整示例：开发环境完整 mock 服务器插件

```ts
// vite-plugin-dev-server.ts

import type { Plugin } from 'vite'
import type { IncomingMessage, ServerResponse } from 'node:http'
import fs from 'node:fs'
import path from 'node:path'

// 简单的内存数据库（模拟）
const db = {
  users: [
    { id: 1, name: 'Alice', email: 'alice@example.com', role: 'admin' },
    { id: 2, name: 'Bob', email: 'bob@example.com', role: 'user' },
    { id: 3, name: 'Carol', email: 'carol@example.com', role: 'user' }
  ],
  posts: [
    { id: 1, title: 'Hello World', authorId: 1, content: 'First post!' },
    { id: 2, title: 'Second Post', authorId: 2, content: 'Another post.' }
  ]
}

type Handler = (
  req: IncomingMessage,
  res: ServerResponse,
  body?: unknown
) => void

// 定义路由表
const routes: Record<string, Record<string, Handler>> = {
  '/api/users': {
    GET: (req, res) => {
      const url = new URL(req.url!, `http://${req.headers.host}`)
      const role = url.searchParams.get('role')
      const users = role
        ? db.users.filter(u => u.role === role)
        : db.users
      res.end(JSON.stringify({ data: users, total: users.length }))
    },
    POST: (req, res, body: any) => {
      const newUser = {
        id: db.users.length + 1,
        ...body,
        createdAt: new Date().toISOString()
      }
      db.users.push(newUser)
      res.statusCode = 201
      res.end(JSON.stringify({ data: newUser }))
    }
  },
  '/api/posts': {
    GET: (_req, res) => {
      const postsWithAuthor = db.posts.map(p => ({
        ...p,
        author: db.users.find(u => u.id === p.authorId)
      }))
      res.end(JSON.stringify({ data: postsWithAuthor }))
    }
  }
}

export default function devServerPlugin(): Plugin {
  return {
    name: 'vite-plugin-dev-server',
    apply: 'serve',  // 只在 dev 模式生效

    configureServer(server) {
      // ① 添加 mock API 中间件（在 Vite 内置中间件之前执行）
      server.middlewares.use('/api', (req, res, next) => {
        // 设置 JSON 响应头
        res.setHeader('Content-Type', 'application/json')
        res.setHeader('Access-Control-Allow-Origin', '*')

        // 解析路由
        const urlPath = req.url?.split('?')[0] ?? '/'
        const fullPath = '/api' + urlPath
        const handler = routes[fullPath]?.[req.method ?? 'GET']

        if (!handler) {
          res.statusCode = 404
          res.end(JSON.stringify({ error: `${req.method} ${fullPath} not found` }))
          return
        }

        // 解析请求 body（POST/PUT/PATCH）
        if (['POST', 'PUT', 'PATCH'].includes(req.method ?? '')) {
          let body = ''
          req.on('data', chunk => { body += chunk })
          req.on('end', () => {
            try {
              handler(req, res, JSON.parse(body))
            } catch {
              res.statusCode = 400
              res.end(JSON.stringify({ error: 'Invalid JSON body' }))
            }
          })
        } else {
          handler(req, res)
        }
      })

      // ② 监听 mock 数据文件变化，自动重新加载
      const mockDir = path.resolve('src/mocks')
      if (fs.existsSync(mockDir)) {
        server.watcher.add(mockDir)
        server.watcher.on('change', (file) => {
          if (!file.startsWith(mockDir)) return
          console.log(`[mock] 数据文件变化：${file}，重新加载...`)

          // 找出所有依赖该 mock 文件的模块，让它们失效（触发 HMR）
          const affectedModules = server.moduleGraph.getModulesByFile(file)
          affectedModules?.forEach(mod => {
            server.moduleGraph.invalidateModule(mod)
          })

          // 向浏览器发送自定义事件（可选）
          server.ws.send({
            type: 'custom',
            event: 'mock-data-updated',
            data: { file: path.relative(process.cwd(), file) }
          })
        })
      }

      // ③ 返回函数 = 后置中间件（在 Vite 内置处理之后执行）
      // 适合做请求日志、404 兜底等
      return () => {
        server.middlewares.use((req, res, next) => {
          const start = Date.now()
          const url = req.url ?? '/'

          // 只记录非静态资源的请求
          if (!url.includes('.') || url.startsWith('/api')) {
            res.on('finish', () => {
              const duration = Date.now() - start
              const status = res.statusCode
              const color = status >= 400 ? '\x1b[31m' : '\x1b[32m'
              console.log(
                `${color}[${status}]\x1b[0m`,
                `${req.method} ${url}`,
                `${duration}ms`
              )
            })
          }
          next()
        })
      }
    }
  }
}
```

**实际效果：**

```
前端代码发请求：
  fetch('/api/users?role=admin')

↓ 经过 configureServer 添加的中间件处理

返回：
  HTTP 200
  Content-Type: application/json
  { "data": [{ "id": 1, "name": "Alice", "role": "admin" }], "total": 1 }

控制台输出：
  [200] GET /api/users?role=admin 2ms
```

---

## 九、`handleHotUpdate` — 自定义 HMR

### 是什么

Dev 专属钩子。当任意文件发生变化时，Vite 执行默认 HMR 逻辑**之前**调用。可以完全控制热更新行为：拦截、修改、阻止或扩展默认行为。

### 函数签名

```ts
handleHotUpdate(ctx: HmrContext): Array<ModuleNode> | void | Promise<...>

interface HmrContext {
  file: string              // 变化的文件绝对路径
  timestamp: number         // 变化发生的时间戳
  modules: Array<ModuleNode>  // 受该文件直接影响的模块列表
  read: () => string | Promise<string>  // 读取文件内容
  server: ViteDevServer     // 开发服务器实例
}
```

**返回值含义：**

- 返回模块数组 → Vite 只更新这些模块（替代默认的受影响模块列表）
- 返回空数组 `[]` → 阻止任何 HMR，浏览器什么都不做
- 返回 `undefined` / 不 `return` → 走 Vite 默认 HMR 流程

### HMR 默认流程

```
文件变化
  ↓
handleHotUpdate 调用
  ↓ (不阻止的话)
计算受影响的模块
  ↓
通过 WebSocket 发送更新信息给浏览器
  ↓
浏览器执行模块热替换
```

### 能做什么

- 修改全局 CSS 变量 / 主题文件时，强制整页刷新（局部 HMR 会导致花屏）
- 修改 i18n 翻译文件时，只重载翻译而不刷新页面（自定义 HMR 协议）
- 修改 mock 数据时，精确控制哪些业务模块需要重新执行
- 监控构建时间，修改某些性能关键文件时给出警告

### 完整示例：智能 HMR 策略插件

```ts
// vite-plugin-smart-hmr.ts

import type { Plugin } from 'vite'
import path from 'node:path'

export default function smartHMRPlugin(): Plugin {
  return {
    name: 'vite-plugin-smart-hmr',
    apply: 'serve',

    handleHotUpdate({ file, server, modules, timestamp, read }) {
      const relPath = path.relative(process.cwd(), file)

      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // 策略 1：全局样式变量 → 整页刷新
      // 原因：CSS 变量影响全局，局部 HMR 无法完整更新
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      const isGlobalStyle =
        file.includes('/styles/variables') ||
        file.includes('/styles/theme') ||
        file.endsWith('global.css') ||
        file.endsWith('global.scss')

      if (isGlobalStyle) {
        console.log(`[hmr] 全局样式变化，触发整页刷新: ${relPath}`)
        // 向浏览器发送 full-reload 指令
        server.ws.send({
          type: 'full-reload',
          path: '*'  // 重新加载所有资源
        })
        return []  // ← 阻止默认 HMR，避免重复处理
      }

      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // 策略 2：i18n 翻译文件 → 自定义更新协议
      // 原因：只需要重新加载翻译数据，不需要刷新页面
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      if (
        file.includes('/locales/') &&
        (file.endsWith('.json') || file.endsWith('.yaml'))
      ) {
        // 读取新的翻译文件内容
        const content = read()
        Promise.resolve(content).then(text => {
          let data: unknown
          try {
            data = JSON.parse(text)
          } catch {
            data = null  // yaml 格式由其他插件处理
          }

          // 发送自定义 HMR 事件给浏览器
          server.ws.send({
            type: 'custom',
            event: 'i18n-update',
            data: {
              file: relPath,
              locale: path.basename(file, path.extname(file)),
              timestamp,
              data
            }
          })

          console.log(`[hmr] i18n 翻译更新: ${relPath}`)
        })

        return []  // 阻止默认 HMR
      }

      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // 策略 3：Mock 数据文件 → 使上游模块失效
      // 原因：mock 文件本身不是 ES 模块，
      //       需要找到 import 了它的上游业务模块
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      if (file.includes('/mocks/') || file.includes('/fixtures/')) {
        const affected = new Set<(typeof modules)[0]>()

        // 遍历所有直接受影响的模块
        modules.forEach(mod => {
          // 把"导入了 mock 文件的业务模块"加入待更新列表
          mod.importers.forEach(importer => {
            affected.add(importer)
          })
        })

        console.log(
          `[hmr] Mock 数据变化，更新 ${affected.size} 个依赖模块: ${relPath}`
        )

        // 返回需要 HMR 的模块列表（替代默认的 modules）
        return [...affected]
      }

      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      // 策略 4：store 状态文件 → 发送自定义清除事件
      // ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      if (file.includes('/store/') || file.includes('/stores/')) {
        // 通知浏览器在 HMR 前清除对应 store 的状态
        server.ws.send({
          type: 'custom',
          event: 'store-hmr-before',
          data: { file: relPath }
        })

        // 走默认 HMR（不 return → 继续正常热更新）
        // 但在浏览器端可以监听 store-hmr-before 做状态清理
      }

      // 其他文件：不 return，走 Vite 默认 HMR
    }
  }
}
```

**浏览器端配套代码：**

```ts
// src/plugins/hmr-client.ts
// 在 main.ts 里 import 这个文件（只在开发模式）

if (import.meta.hot) {
  // 监听 i18n 更新事件
  import.meta.hot.on('i18n-update', ({ locale, data, timestamp }) => {
    console.log(`[i18n] 翻译更新: ${locale}`, { timestamp })
    // 只更新翻译数据，不刷新页面
    i18n.global.setLocaleMessage(locale, data)
    i18n.global.locale.value = locale  // 触发重渲染
  })

  // 监听 store HMR 前的清理事件
  import.meta.hot.on('store-hmr-before', ({ file }) => {
    console.log(`[store] 状态文件变化，清理状态: ${file}`)
    // 清理 Pinia 中的 store 实例，避免 HMR 后状态混乱
    const pinia = usePinia()
    pinia._s.forEach(store => store.$reset?.())
  })
}
```

---

## 十、钩子执行顺序控制

### enforce — 控制插件执行顺序

```ts
{
  name: 'my-plugin',
  enforce: 'pre',   // 'pre' | 'post' | 不设置
  transform(code, id) { ... }
}
```

执行顺序：
1. `enforce: 'pre'` 的插件
2. 没有 `enforce` 的普通插件
3. Vite 内置插件（`vite:xxx`）
4. `enforce: 'post'` 的插件

### apply — 限制执行环境

```ts
// 写法 1：字符串
{
  apply: 'build'   // 只在 vite build 时生效
  // apply: 'serve'  // 只在 vite dev 时生效
}

// 写法 2：函数（更精细的控制）
{
  apply(config, { command }) {
    // 只在生产构建、非 SSR 时生效
    return command === 'build' && !config.build?.ssr
  }
}
```

### 常见组合

```ts
// 只在生产构建中、在所有其他插件之后执行的插件
{
  name: 'vite-plugin-post-build',
  apply: 'build',
  enforce: 'post',
  generateBundle(options, bundle) { ... }
}

// 只在开发模式中、在所有插件之前执行的插件（如自定义文件解析器）
{
  name: 'vite-plugin-pre-resolve',
  apply: 'serve',
  enforce: 'pre',
  resolveId(id) { ... }
}
```

---

## 十一、完整插件模板

以下是一个包含所有常用钩子的完整 Vite 插件模板，可以作为编写插件的起点：

```ts
// vite-plugin-template.ts

import type {
  Plugin,
  ResolvedConfig,
  ViteDevServer,
  HmrContext
} from 'vite'

interface PluginOptions {
  // 插件配置项
  include?: string[]
  exclude?: string[]
  verbose?: boolean
}

export default function myPlugin(options: PluginOptions = {}): Plugin {
  // 插件内部状态（钩子间共享）
  let config: ResolvedConfig
  let server: ViteDevServer
  let isBuild = false

  return {
    // ── 基础属性 ────────────────────────────────
    name: 'vite-plugin-template',
    enforce: 'pre',    // 'pre' | 'post'
    apply: 'build',    // 'serve' | 'build' | 函数

    // ── 通用钩子（Dev + Build）────────────────────
    config(userConfig, { command, mode }) {
      // 修改 Vite 配置
      if (command === 'serve') {
        return { server: { /* ... */ } }
      }
      return { build: { /* ... */ } }
    },

    configResolved(resolvedConfig) {
      // 保存最终配置
      config = resolvedConfig
      isBuild = config.command === 'build'
    },

    buildStart(inputOptions) {
      // 构建开始：初始化缓存、临时目录等
      console.log('📦 构建开始')
    },

    resolveId(id, importer, opts) {
      // 自定义模块路径解析
      if (id === 'virtual:my-module') {
        return '\0virtual:my-module'
      }
    },

    load(id) {
      // 自定义模块内容加载
      if (id === '\0virtual:my-module') {
        return `export const hello = 'world'`
      }
    },

    transform(code, id) {
      // 转换模块源码
      if (!id.endsWith('.ts')) return
      return { code: code, map: null }
    },

    buildEnd(error) {
      // 构建结束（成功或失败都会调用）
      if (error) {
        console.error('❌ 构建失败:', error.message)
      }
    },

    // ── Build 专属钩子 ──────────────────────────
    renderChunk(code, chunk, outputOptions) {
      // 处理打包后的 chunk（合并后的 JS）
      return { code: `/* banner */\n${code}`, map: null }
    },

    generateBundle(outputOptions, bundle) {
      // 生成产物前：增删改文件
      this.emitFile({
        type: 'asset',
        fileName: 'version.json',
        source: JSON.stringify({ version: '1.0.0' })
      })
    },

    writeBundle(outputOptions, bundle) {
      // 文件写入磁盘后：上传 CDN、触发部署等
      console.log('✅ 构建产物已写入磁盘')
    },

    closeBundle() {
      // 整个构建流程的最后一个钩子
      console.log('🎉 构建完成')
    },

    // ── Dev 专属钩子 ────────────────────────────
    configureServer(devServer) {
      server = devServer

      // 添加中间件
      devServer.middlewares.use('/api', (req, res, next) => {
        // mock API 处理
        next()
      })

      // 返回函数 = 后置中间件
      return () => {
        devServer.middlewares.use((req, res, next) => {
          next()
        })
      }
    },

    configurePreviewServer(previewServer) {
      // vite preview 时的中间件（与 configureServer 用法相同）
    },

    transformIndexHtml: {
      order: 'pre',  // 'pre' | 'post'
      handler(html, ctx) {
        // 转换 index.html
        return {
          html,
          tags: [
            {
              tag: 'meta',
              attrs: { name: 'version', content: '1.0.0' },
              injectTo: 'head'
            }
          ]
        }
      }
    },

    handleHotUpdate(ctx: HmrContext) {
      // 自定义 HMR 行为
      if (ctx.file.endsWith('.json')) {
        ctx.server.ws.send({ type: 'full-reload' })
        return []  // 阻止默认 HMR
      }
      // 不 return → 走默认流程
    }
  }
}
```

---

## 附录：钩子参数速查

| 钩子 | 关键参数 | 返回值 |
|---|---|---|
| `config` | `(config, { command, mode })` | `Partial<UserConfig>` |
| `configResolved` | `(resolvedConfig)` | `void` |
| `buildStart` | `(inputOptions)` | `void` |
| `resolveId` | `(id, importer, opts)` | `string \| false \| { id, external }` |
| `load` | `(id)` | `string \| { code, map }` |
| `transform` | `(code, id)` | `string \| { code, map }` |
| `buildEnd` | `(error?)` | `void` |
| `renderChunk` | `(code, chunk, outputOptions)` | `{ code, map }` |
| `generateBundle` | `(outputOptions, bundle)` | `void`（通过 `this.emitFile` 新增文件） |
| `writeBundle` | `(outputOptions, bundle)` | `void` |
| `closeBundle` | `()` | `void` |
| `configureServer` | `(server)` | `(() => void)` 或 `void` |
| `transformIndexHtml` | `(html, ctx)` | `string \| { html, tags }` |
| `handleHotUpdate` | `({ file, server, modules, timestamp, read })` | `ModuleNode[] \| void` |

---

*文档版本：Vite 5.x / 基于 Rollup 4.x 插件 API*