---
title: "package.json 配置选项"
date: 2025-11-27
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 package.json

`package.json` 是 Node.js 项目的核心配置文件，位于项目根目录，包含项目的元数据和依赖信息。

### 主要作用

- 📦 **项目信息**：记录项目名称、版本、描述等基本信息
- 📚 **依赖管理**：管理项目依赖的第三方包
- 🚀 **脚本命令**：定义可执行的脚本命令
- 🔧 **配置选项**：配置各种工具和构建选项
- 📄 **发布信息**：发布到 npm 仓库的相关配置

### 创建 package.json

```bash
# 交互式创建
npm init

# 使用默认值快速创建
npm init -y

# 使用 ES Module 创建
npm init -y --type=module
```

:::tip 版本说明
本文档基于 **npm 10.x** 和 **Node.js 18+** 编写，涵盖最新的 package.json 规范。

**规范版本**：

- **npm CLI**: v10.9.2 (2024 年 12 月发布)
- **package.json 规范**: 遵循 [npm package.json 规范](https://docs.npmjs.com/cli/v10/configuring-npm/package-json)
- **Node.js 包规范**: 遵循 [Node.js Packages 规范](https://nodejs.org/api/packages.html)

**关键特性支持时间线**：

- ✅ **type** 字段：Node.js 12.0.0+ (2019-04)，指定模块系统（CommonJS/ESM）
- ✅ **exports** 字段：Node.js 12.7.0+ (2019-07)，现代包入口标准
- ✅ **imports** 字段：Node.js 14.6.0+ (2020-07)，内部导入映射
- ✅ **workspaces** 字段：npm 7.0.0+ (2020-10)，Monorepo 工作区支持
- ✅ **overrides** 字段：npm 8.3.0+ (2021-12)，强制覆盖传递依赖版本

**现代化特性（2024-2025）**：

- 📦 **条件导出**：根据环境（import/require）和条件（node/browser/types）选择不同入口
- 🎯 **子路径导出**：精确控制包的公开 API，隐藏内部实现细节
- 🔧 **TypeScript 集成**：通过 exports 字段的 types 条件原生支持
- 🚀 **ESM 优先**：现代项目推荐使用 ES Modules（`"type": "module"`）
- 🔒 **包导出封装**：使用 exports 替代 main 实现更好的封装
  :::

:::warning 注意事项

- **exports 优先级**：当存在 exports 字段时，main 字段会被忽略
- **TypeScript 兼容**：使用 exports 需要 TypeScript 4.7+ 和 moduleResolution: "node16" 或 "nodenext"
- **向后兼容**：使用 exports 时建议保留 main 字段以兼容旧版本 Node.js
- **工作区限制**：workspaces 仅在包管理器的根 package.json 中有效
  :::

## 基础字段

### 1. name（必需）

**作用**：定义项目名称。

```json
{
  "name": "my-project"
}
```

**命名规则**：

- 必须小写
- 不能包含空格
- 可以使用 `-` 和 `_`
- 不能以 `.` 或 `_` 开头
- 不能包含非 URL 安全字符
- 长度限制：1-214 个字符

**作用域包（Scoped Package）**：

```json
{
  "name": "@username/project-name",
  "name": "@organization/project-name"
}
```

**影响对比**：

```bash
# ❌ 不配置 name
# 无法发布到 npm
# npm install 会报错
# 无法被其他项目引用

# ✅ 配置 name
# 可以发布到 npm
# 可以被其他项目通过名称安装
npm install my-project
```

**命名示例**：

```json
// ✅ 正确的命名
{
  "name": "my-project",
  "name": "my-awesome-package",
  "name": "@myorg/my-package"
}

// ❌ 错误的命名
{
  "name": "My Project",        // 包含空格和大写
  "name": ".myproject",         // 以点开头
  "name": "_myproject",         // 以下划线开头
  "name": "my project",         // 包含空格
}
```

### 2. version（必需）

**作用**：定义项目版本号，遵循 [语义化版本](https://semver.org/)（Semantic Versioning）。

```json
{
  "version": "1.0.0"
}
```

**版本格式**：`主版本号.次版本号.修订号`（MAJOR.MINOR.PATCH）

- **主版本号**（MAJOR）：不兼容的 API 修改
- **次版本号**（MINOR）：向下兼容的功能新增
- **修订号**（PATCH）：向下兼容的 bug 修复

**影响对比**：

```bash
# ❌ 不配置 version
# 无法发布到 npm
# 无法进行版本管理

# ✅ 配置 version
# 可以发布到 npm
# 用户可以安装特定版本
npm install my-project@1.0.0
npm install my-project@^1.0.0
npm install my-project@~1.0.0
```

**版本更新**：

```bash
# 修订号 +1：1.0.0 → 1.0.1
npm version patch

# 次版本号 +1：1.0.0 → 1.1.0
npm version minor

# 主版本号 +1：1.0.0 → 2.0.0
npm version major
```

**版本示例**：

```json
{
  "version": "1.0.0", // 稳定版本
  "version": "0.1.0", // 初始开发版本
  "version": "1.0.0-beta.1", // 预发布版本
  "version": "1.0.0-alpha.1" // Alpha 版本
}
```

### 3. description

**作用**：项目的简短描述，显示在 npm 搜索结果中。

```json
{
  "description": "一个用于处理用户认证的工具库"
}
```

**影响对比**：

```bash
# ❌ 不配置 description
# npm search 结果中没有描述
# 用户难以了解项目用途

# ✅ 配置 description
# npm search 结果中显示描述
# 提高项目的可发现性
```

**示例**：

```json
{
  "name": "my-logger",
  "description": "一个轻量级的 JavaScript 日志工具，支持多种输出格式和日志级别"
}
```

### 4. keywords

**作用**：关键词数组，帮助用户搜索到你的包。

```json
{
  "keywords": ["logger", "log", "console", "debug"]
}
```

**影响对比**：

```bash
# ❌ 不配置 keywords
# 搜索相关关键词时不易被发现

# ✅ 配置 keywords
# 提高搜索可发现性
# 用户更容易找到你的包
```

**示例**：

```json
{
  "name": "vue-toast",
  "keywords": ["vue", "vue3", "toast", "notification", "message", "alert"]
}
```

### 5. homepage

**作用**：项目主页的 URL。

```json
{
  "homepage": "https://github.com/username/project#readme"
}
```

**影响对比**：

```bash
# ❌ 不配置 homepage
# npm 页面没有主页链接

# ✅ 配置 homepage
# npm 页面显示主页链接
# 用户可以快速访问文档
```

### 6. bugs

**作用**：问题反馈的 URL 或邮箱。

```json
{
  "bugs": {
    "url": "https://github.com/username/project/issues",
    "email": "project@hostname.com"
  }
}
```

**简写形式**：

```json
{
  "bugs": "https://github.com/username/project/issues"
}
```

### 7. license

**作用**：指定项目的许可证。

```json
{
  "license": "MIT"
}
```

**常用许可证**：

```json
{
  "license": "MIT", // MIT 许可证（最宽松）
  "license": "ISC", // ISC 许可证
  "license": "Apache-2.0", // Apache 2.0 许可证
  "license": "GPL-3.0", // GPL 3.0 许可证
  "license": "BSD-3-Clause", // BSD 许可证
  "license": "UNLICENSED" // 私有项目，不开源
}
```

**影响对比**：

```bash
# ❌ 不配置 license
# npm 会发出警告
# 用户不清楚使用条款

# ✅ 配置 license
# 明确使用条款
# 用户可以放心使用
```

### 8. author

**作用**：项目作者信息。

```json
{
  "author": "Your Name <your.email@example.com> (https://yourwebsite.com)"
}
```

**对象格式**：

```json
{
  "author": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "url": "https://yourwebsite.com"
  }
}
```

### 9. contributors

**作用**：项目贡献者列表。

```json
{
  "contributors": ["Alice <alice@example.com>", "Bob <bob@example.com>"]
}
```

**对象格式**：

```json
{
  "contributors": [
    {
      "name": "Alice",
      "email": "alice@example.com",
      "url": "https://alice.com"
    },
    {
      "name": "Bob",
      "email": "bob@example.com"
    }
  ]
}
```

### 10. repository

**作用**：代码仓库的位置。

```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/username/project.git"
  }
}
```

**简写形式**：

```json
{
  "repository": "github:username/project",
  "repository": "gitlab:username/project",
  "repository": "bitbucket:username/project"
}
```

**Monorepo 子包**：

```json
{
  "repository": {
    "type": "git",
    "url": "https://github.com/username/monorepo.git",
    "directory": "packages/my-package"
  }
}
```

## 依赖管理

### 1. dependencies

**作用**：生产环境依赖，项目运行时必需的包。

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  }
}
```

**影响对比**：

```bash
# ❌ 不配置 dependencies
# 项目无法运行
# 用户需要手动安装依赖

# ✅ 配置 dependencies
# npm install 自动安装
# 确保项目正常运行
```

**版本号说明**：

```json
{
  "dependencies": {
    "package-1": "1.0.0", // 精确版本
    "package-2": "^1.0.0", // 兼容版本（推荐）
    "package-3": "~1.0.0", // 补丁版本
    "package-4": ">=1.0.0", // 大于等于
    "package-5": "1.0.0 - 2.0.0", // 范围
    "package-6": "*", // 任意版本（不推荐）
    "package-7": "latest" // 最新版本（不推荐）
  }
}
```

**版本符号详解**：

| 符号 | 说明             | 示例      | 允许的版本       |
| ---- | ---------------- | --------- | ---------------- |
| `^`  | 兼容版本（推荐） | `^1.2.3`  | `>=1.2.3 <2.0.0` |
| `~`  | 补丁版本         | `~1.2.3`  | `>=1.2.3 <1.3.0` |
| 无   | 精确版本         | `1.2.3`   | `1.2.3`          |
| `>`  | 大于             | `>1.2.3`  | `>1.2.3`         |
| `>=` | 大于等于         | `>=1.2.3` | `>=1.2.3`        |
| `<`  | 小于             | `<1.2.3`  | `<1.2.3`         |
| `<=` | 小于等于         | `<=1.2.3` | `<=1.2.3`        |

**示例**：

```json
{
  "dependencies": {
    "vue": "^3.4.0", // 生产依赖
    "vue-router": "^4.2.0", // 路由
    "pinia": "^2.1.0", // 状态管理
    "axios": "^1.6.0" // HTTP 客户端
  }
}
```

### 2. devDependencies

**作用**：开发环境依赖，仅在开发时需要的包。

```json
{
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "eslint": "^8.56.0",
    "prettier": "^3.1.0"
  }
}
```

**影响对比**：

```bash
# dependencies vs devDependencies

# 安装所有依赖（开发环境）
npm install

# 只安装生产依赖（生产环境）
npm install --production
npm ci --omit=dev

# devDependencies 不会被安装到生产环境
# 减少部署体积
```

**何时使用**：

```json
{
  "dependencies": {
    // 运行时需要的包
    "vue": "^3.4.0",
    "express": "^4.18.0"
  },
  "devDependencies": {
    // 开发时需要的包
    "vite": "^5.0.0", // 构建工具
    "typescript": "^5.3.0", // TypeScript
    "eslint": "^8.56.0", // 代码检查
    "prettier": "^3.1.0", // 代码格式化
    "@types/node": "^20.10.0", // 类型定义
    "vitest": "^1.0.0" // 测试框架
  }
}
```

### 3. peerDependencies

**作用**：对等依赖，指定当前包需要宿主项目安装的依赖。

```json
{
  "name": "vue-plugin",
  "peerDependencies": {
    "vue": "^3.0.0"
  }
}
```

**使用场景**：插件、工具库

```json
// Vue 插件
{
  "name": "my-vue-plugin",
  "peerDependencies": {
    "vue": "^3.0.0"
  }
}

// React 组件库
{
  "name": "my-react-component",
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}

// ESLint 插件
{
  "name": "eslint-plugin-custom",
  "peerDependencies": {
    "eslint": "^8.0.0"
  }
}
```

**影响对比**：

```bash
# ❌ 不配置 peerDependencies
# 可能安装多个版本的相同包
# 增加包体积

# ✅ 配置 peerDependencies
# 确保只有一个版本
# 减少包体积
# npm 会提示用户安装对等依赖
```

**npm 7+ 重要变更**：

:::warning npm 7+ 行为变化

- **npm 3-6**：peerDependencies 仅显示警告，不会自动安装
- **npm 7+**：peerDependencies 会自动安装，版本冲突时报错
- **解决冲突**：如遇版本冲突，可临时使用 `--legacy-peer-deps` 标志恢复旧行为
  :::

```bash
# npm 7+ 自动安装 peer dependencies
npm install my-vue-plugin
# 会自动安装 vue@^3.0.0（如果项目中没有）

# 如遇冲突，使用 legacy 模式
npm install --legacy-peer-deps

# 或在 .npmrc 中配置
legacy-peer-deps=true
```

### 4. peerDependenciesMeta

**作用**：标记对等依赖为可选。

```json
{
  "peerDependencies": {
    "vue": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "peerDependenciesMeta": {
    "typescript": {
      "optional": true
    }
  }
}
```

**说明**：`typescript` 是可选的对等依赖，不安装也不会报错。

### 5. optionalDependencies

**作用**：可选依赖，安装失败不会影响整体安装过程。

```json
{
  "optionalDependencies": {
    "fsevents": "^2.3.0" // macOS 特定依赖
  }
}
```

**使用场景**：

- 平台特定的依赖
- 可选的性能优化包
- 可选的功能增强包

**代码处理**：

```javascript
// 需要在代码中处理依赖不存在的情况
try {
  const fsevents = require("fsevents");
  // 使用 fsevents
} catch (err) {
  // 使用备用方案
  console.log("fsevents not available, using fallback");
}
```

### 6. bundleDependencies

**作用**：打包依赖，发布时将指定的依赖一起打包。

```json
{
  "bundleDependencies": ["package1", "package2"]
}
```

**使用场景**：

- 需要保证依赖版本完全一致
- 离线安装
- 避免依赖被修改或删除

### 7. overrides

**作用**：强制覆盖依赖树中的包版本（npm 8.3.0+）。

```json
{
  "overrides": {
    "foo": "1.0.0"
  }
}
```

**使用场景**：

- 修复依赖包的安全漏洞
- 统一依赖版本
- 使用 fork 版本替代原包
- 解决版本冲突

**简单覆盖**：

```json
{
  "overrides": {
    "foo": "1.0.0",
    "bar": "2.0.0"
  }
}
```

**嵌套覆盖**（只覆盖特定依赖下的包）：

```json
{
  "overrides": {
    "bar": {
      "foo": "1.0.0"
    }
  }
}
```

这表示只覆盖 `bar` 包依赖的 `foo`，其他包依赖的 `foo` 不受影响。

**深层嵌套覆盖**：

```json
{
  "overrides": {
    "baz": {
      "bar": {
        "foo": "1.0.0"
      }
    }
  }
}
```

只覆盖 `baz → bar → foo` 这条依赖链中的 `foo`。

**版本特定覆盖**：

```json
{
  "overrides": {
    "bar@2.0.0": {
      "foo": "1.0.0"
    }
  }
}
```

只有当 `bar` 的版本是 `2.0.0` 时，才覆盖其依赖的 `foo`。

**引用当前包的版本**：

```json
{
  "dependencies": {
    "foo": "^1.0.0"
  },
  "overrides": {
    "foo": "$foo",
    "bar": "$foo"
  }
}
```

使用 `$foo` 引用当前包定义的 `foo` 版本，确保 `bar` 也使用相同版本。

**完整示例**（安全漏洞修复）：

```json
{
  "name": "my-app",
  "dependencies": {
    "express": "^4.18.0"
  },
  "overrides": {
    "express": {
      "qs": "6.11.0"
    }
  }
}
```

这会强制 `express` 及其所有依赖使用 `qs@6.11.0`，即使 `express` 本身依赖的是旧版本。

**注意事项**：

- ⚠️ **谨慎使用**：强制覆盖可能导致依赖不兼容
- ⚠️ **优先级最高**：overrides 会覆盖所有其他版本声明
- ⚠️ **npm 专用**：pnpm 使用 `overrides`，yarn 使用 `resolutions`
- ✅ **安全更新**：主要用于修复安全漏洞，确保测试充分

**与其他包管理器的对比**：

```json
// npm / pnpm
{
  "overrides": {
    "foo": "1.0.0"
  }
}

// yarn (classic / berry)
{
  "resolutions": {
    "foo": "1.0.0"
  }
}
```

## 脚本配置

### scripts

**作用**：定义可执行的脚本命令。

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier --write ."
  }
}
```

**执行方式**：

```bash
# 运行脚本
npm run dev
npm run build

# 内置脚本可以省略 run
npm start   # = npm run start
npm test    # = npm run test
npm stop    # = npm run stop
npm restart # = npm run restart
```

**生命周期钩子**：

```json
{
  "scripts": {
    // 安装前后
    "preinstall": "echo 'Installing...'",
    "install": "node-gyp rebuild",
    "postinstall": "echo 'Installed!'",

    // 脚本前后
    "prebuild": "echo 'Building...'",
    "build": "vite build",
    "postbuild": "echo 'Built!'",

    // 发布前后
    "prepublishOnly": "npm run build",
    "postpublish": "echo 'Published!'"
  }
}
```

**常用脚本示例**：

```json
{
  "scripts": {
    // 开发
    "dev": "vite",
    "serve": "vite --host",

    // 构建
    "build": "vite build",
    "build:prod": "vite build --mode production",
    "build:staging": "vite build --mode staging",

    // 预览
    "preview": "vite preview",

    // 代码检查
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx,.vue",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx,.vue --fix",
    "lint:css": "stylelint \"**/*.{css,scss,vue}\"",

    // 代码格式化
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,vue,json,css,scss,md}\"",
    "format:check": "prettier --check \"**/*.{js,jsx,ts,tsx,vue,json,css,scss,md}\"",

    // 测试
    "test": "vitest",
    "test:unit": "vitest run",
    "test:e2e": "cypress run",
    "test:coverage": "vitest run --coverage",

    // 类型检查
    "type-check": "vue-tsc --noEmit",

    // Git hooks
    "prepare": "husky",

    // 清理
    "clean": "rm -rf node_modules dist",

    // 发布前
    "prepublishOnly": "npm run lint && npm run test && npm run build"
  }
}
```

**脚本中使用环境变量**：

```json
{
  "scripts": {
    "dev": "NODE_ENV=development vite",
    "build": "NODE_ENV=production vite build"
  }
}
```

**跨平台环境变量**：

```bash
# 安装 cross-env
npm install --save-dev cross-env
```

```json
{
  "scripts": {
    "dev": "cross-env NODE_ENV=development vite",
    "build": "cross-env NODE_ENV=production vite build"
  }
}
```

**串行和并行执行**：

```json
{
  "scripts": {
    // 串行执行（依次执行）
    "build": "npm run clean && npm run compile && npm run bundle",

    // 并行执行（同时执行）
    "lint:all": "npm run lint:js & npm run lint:css & npm run lint:html"
  }
}
```

**使用 npm-run-all**：

```bash
npm install --save-dev npm-run-all
```

```json
{
  "scripts": {
    // 串行执行
    "build": "npm-run-all clean compile bundle",

    // 并行执行
    "lint:all": "npm-run-all --parallel lint:*",

    "clean": "rm -rf dist",
    "compile": "tsc",
    "bundle": "webpack",
    "lint:js": "eslint .",
    "lint:css": "stylelint \"**/*.css\"",
    "lint:html": "htmlhint \"**/*.html\""
  }
}
```

## 文件配置

### 1. main

**作用**：指定包的入口文件（CommonJS）。

```json
{
  "main": "index.js"
}
```

**影响对比**：

```bash
# ❌ 不配置 main
# 默认使用 index.js
# 如果没有 index.js 会报错

# ✅ 配置 main
# 指定具体的入口文件
# require('my-package') 会加载指定文件
```

**示例**：

```json
{
  "main": "./dist/index.js"
}
```

```javascript
// 使用时
const myPackage = require("my-package");
// 实际加载的是 ./dist/index.js
```

### 2. module

**作用**：指定 ES Module 的入口文件。

```json
{
  "main": "./dist/index.cjs", // CommonJS 入口
  "module": "./dist/index.mjs" // ES Module 入口
}
```

**说明**：构建工具（如 Webpack、Rollup）会优先使用 `module` 字段。

### 3. exports

**作用**：定义包的导出（Node.js 12+），更精确的控制导出。

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.cjs"
    }
  }
}
```

**使用示例**：

```javascript
// 导入主入口
import pkg from "my-package"; // 使用 ./dist/index.mjs
const pkg = require("my-package"); // 使用 ./dist/index.cjs

// 导入子路径
import utils from "my-package/utils"; // 使用 ./dist/utils.mjs
const utils = require("my-package/utils"); // 使用 ./dist/utils.cjs
```

**条件导出**：

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts", // TypeScript 类型
      "import": "./dist/index.mjs", // ES Module
      "require": "./dist/index.cjs", // CommonJS
      "default": "./dist/index.js" // 默认
    }
  }
}
```

**完整示例**：

```json
{
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./package.json": "./package.json",
    "./style.css": "./dist/style.css",
    "./utils/*": {
      "import": "./dist/utils/*.mjs",
      "require": "./dist/utils/*.cjs"
    }
  }
}
```

### 4. imports

**作用**：定义包内部的私有路径映射（Node.js 14.6.0+），用于简化内部导入。

```json
{
  "imports": {
    "#utils/*": "./src/utils/*",
    "#lib/*": "./src/lib/*"
  }
}
```

**使用场景**：

- 简化包内部的导入路径
- 避免使用相对路径（`../../utils`）
- 仅对包内部有效，外部无法访问
- TypeScript 5.4+ 原生支持

**基本示例**：

```json
{
  "name": "my-package",
  "imports": {
    "#utils": "./src/utils/index.js",
    "#config": "./src/config.js"
  }
}
```

**在代码中使用**：

```javascript
// ❌ 传统方式：使用相对路径
import { helper } from "../../utils/helper.js";
import config from "../../config.js";

// ✅ 使用 imports：简洁清晰
import { helper } from "#utils/helper.js";
import config from "#config";
```

**通配符模式**：

```json
{
  "imports": {
    "#utils/*": "./src/utils/*",
    "#components/*": "./src/components/*"
  }
}
```

```javascript
// 使用通配符映射
import { formatDate } from "#utils/date.js";
import Button from "#components/Button.js";

// 实际加载的是：
// ./src/utils/date.js
// ./src/components/Button.js
```

**条件导入**（根据环境选择不同实现）：

```json
{
  "imports": {
    "#db": {
      "node": "./src/db-node.js",
      "default": "./src/db-browser.js"
    }
  }
}
```

**TypeScript 集成**（TypeScript 5.4+）：

从 TypeScript 5.4 开始，无需在 `tsconfig.json` 中重复配置路径映射，TypeScript 会自动识别 `package.json` 中的 `imports` 字段。

```json
// package.json
{
  "imports": {
    "#utils/*": "./src/utils/*"
  }
}

// TypeScript 5.4+ 自动识别，无需额外配置
// TypeScript 5.3 及以下需要在 tsconfig.json 中配置 paths
```

**完整示例**：

```json
{
  "name": "my-app",
  "type": "module",
  "imports": {
    "#utils/*": "./src/utils/*",
    "#components/*": "./src/components/*",
    "#types": "./src/types/index.ts",
    "#config": {
      "development": "./src/config/dev.js",
      "production": "./src/config/prod.js",
      "default": "./src/config/default.js"
    }
  }
}
```

**注意事项**：

- ✅ **必须以 # 开头**：区别于外部包（如 `@scope/package`）
- ✅ **仅包内部可用**：外部无法通过 `#` 导入访问
- ✅ **Node.js 14.6.0+**：需要 Node.js 14.6.0 或更高版本
- ✅ **TypeScript 5.4+**：完整支持，无需额外配置
- ⚠️ **与 exports 的区别**：
  - `exports`：定义包对外的公开 API
  - `imports`：定义包内部的私有路径映射

**imports vs TypeScript paths 对比**：

```json
// imports（推荐，2024+ 标准）
{
  "imports": {
    "#utils/*": "./src/utils/*"
  }
}

// TypeScript paths（传统方式）
{
  "compilerOptions": {
    "paths": {
      "@utils/*": ["./src/utils/*"]
    }
  }
}
```

**优势**：

- 📦 **原生支持**：Node.js 和现代打包工具原生支持
- 🔧 **无需构建配置**：不依赖打包工具的别名配置
- ✅ **TypeScript 5.4+**：自动识别，无需重复配置
- 🚀 **未来标准**：推荐用于新项目

### 5. types / typings

**作用**：指定 TypeScript 类型定义文件。

```json
{
  "types": "./dist/index.d.ts"
}
```

**示例**：

```json
{
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  }
}
```

### 6. bin

**作用**：指定可执行文件，创建命令行工具。

```json
{
  "name": "my-cli",
  "bin": {
    "my-cli": "./bin/cli.js"
  }
}
```

**或简写**：

```json
{
  "name": "my-cli",
  "bin": "./bin/cli.js"
}
```

**可执行文件示例**：

```javascript
#!/usr/bin/env node

// bin/cli.js
console.log("Hello from my-cli!");
```

**安装后使用**：

```bash
# 全局安装
npm install -g my-cli
my-cli  # 直接运行

# 局部安装
npm install --save-dev my-cli
npx my-cli  # 通过 npx 运行
```

**影响对比**：

```bash
# ❌ 不配置 bin
# 无法作为命令行工具使用

# ✅ 配置 bin
# 可以创建命令行工具
# npm 会创建符号链接
```

### 7. files

**作用**：指定发布到 npm 时包含的文件。

```json
{
  "files": ["dist", "lib", "src", "README.md", "LICENSE"]
}
```

**默认包含的文件**：

- `package.json`
- `README.md`
- `LICENSE`
- `main` 字段指定的文件

**默认排除的文件**：

- `node_modules`
- `.git`
- `.DS_Store`
- `npm-debug.log`

**影响对比**：

```bash
# ❌ 不配置 files
# 发布时包含所有文件（除了默认排除的）
# 包体积可能很大

# ✅ 配置 files
# 只发布必要的文件
# 减小包体积
# 提高安装速度
```

**示例**：

```json
{
  "files": [
    "dist", // 构建产物
    "src", // 源代码（可选）
    "README.md", // 说明文档
    "LICENSE", // 许可证
    "*.d.ts" // TypeScript 类型定义
  ]
}
```

## 项目配置

### 1. type

**作用**：指定模块系统类型。

```json
{
  "type": "module" // ES Module
}
```

**或**：

```json
{
  "type": "commonjs" // CommonJS（默认）
}
```

**影响对比**：

```javascript
// type: "module"
// .js 文件被视为 ES Module
import fs from 'fs';
export default function() {}

// 使用 CommonJS 需要 .cjs 扩展名
// file.cjs
const fs = require('fs');
module.exports = function() {}

// type: "commonjs" 或不配置
// .js 文件被视为 CommonJS
const fs = require('fs');
module.exports = function() {}

// 使用 ES Module 需要 .mjs 扩展名
// file.mjs
import fs from 'fs';
export default function() {}
```

### 2. engines

**作用**：指定项目运行所需的 Node.js 和 npm 版本。

```json
{
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

**影响对比**：

```bash
# ❌ 不配置 engines
# 用户可能使用不兼容的版本
# 可能出现运行时错误

# ✅ 配置 engines
# npm 会发出版本警告
# 帮助用户使用正确的版本
```

**版本范围示例**：

```json
{
  "engines": {
    "node": ">=18.0.0 <21.0.0", // 18.x - 20.x
    "node": "^18.0.0 || ^20.0.0", // 18.x 或 20.x
    "npm": ">=9.0.0", // npm 9.0.0 及以上
    "pnpm": ">=8.0.0", // pnpm 8.0.0 及以上
    "yarn": ">=1.22.0" // yarn 1.22.0 及以上
  }
}
```

**注意事项**：

- ⚠️ **仅警告**：不符合 `engines` 要求时，npm 默认只显示警告，不会阻止安装
- ✅ **强制检查**：使用 `npm install --engine-strict` 或配置 `.npmrc` 中 `engine-strict=true` 可强制执行
- 📦 **包管理器**：除了 Node.js 和 npm，还可以指定 pnpm、yarn 版本

### 3. devEngines

**作用**：指定开发环境所需的工具版本（npm 11.0.0+）。

```json
{
  "devEngines": {
    "runtime": {
      "name": "node",
      "version": ">=20.0.0",
      "onFail": "error"
    },
    "packageManager": {
      "name": "npm",
      "version": ">=10.0.0",
      "onFail": "warn"
    }
  }
}
```

**字段说明**：

- **runtime**：运行时环境（node、deno、bun）
- **packageManager**：包管理器（npm、pnpm、yarn）
- **onFail**：版本不匹配时的行为
  - `error`：报错并阻止安装
  - `warn`：仅显示警告（默认）
  - `ignore`：忽略版本检查

**完整示例**：

```json
{
  "engines": {
    "node": ">=18.0.0"
  },
  "devEngines": {
    "runtime": {
      "name": "node",
      "version": ">=20.0.0",
      "onFail": "error"
    },
    "packageManager": {
      "name": "npm",
      "version": ">=10.0.0",
      "onFail": "error"
    },
    "cpu": ["x64", "arm64"],
    "os": ["darwin", "linux", "win32"]
  }
}
```

**使用场景**：

- 团队协作时统一开发环境
- 确保所有开发者使用相同版本的 Node.js 和包管理器
- 避免因版本差异导致的问题

**engines vs devEngines 对比**：

| 字段           | 作用范围           | 默认行为                    | 强制执行           |
| -------------- | ------------------ | --------------------------- | ------------------ |
| **engines**    | 生产环境和开发环境 | 警告                        | `--engine-strict`  |
| **devEngines** | 仅开发环境         | 可配置（warn/error/ignore） | 通过 `onFail` 控制 |

**最佳实践**：

```json
{
  "name": "my-project",
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "devEngines": {
    "runtime": {
      "name": "node",
      "version": "20.18.1",
      "onFail": "error"
    },
    "packageManager": {
      "name": "npm",
      "version": "10.9.2",
      "onFail": "error"
    }
  }
}
```

### 4. os

**作用**：指定支持的操作系统。

```json
{
  "os": ["darwin", "linux"]
}
```

**或排除某些系统**：

```json
{
  "os": ["!win32"]
}
```

**支持的值**：

- `darwin` - macOS
- `linux` - Linux
- `win32` - Windows
- `freebsd` - FreeBSD
- `openbsd` - OpenBSD

### 5. cpu

**作用**：指定支持的 CPU 架构。

```json
{
  "cpu": ["x64", "arm64"]
}
```

**或排除某些架构**：

```json
{
  "cpu": ["!arm", "!mips"]
}
```

### 6. private

**作用**：标记为私有包，防止意外发布。

```json
{
  "private": true
}
```

**影响对比**：

```bash
# private: true
# npm publish 会失败
# 防止私有包被发布到公共仓库

# 不配置或 private: false
# 可以正常发布到 npm
```

**使用场景**：

- 公司内部项目
- 个人项目（不想发布）
- Monorepo 的根包

## 发布配置

### 1. publishConfig

**作用**：发布时的配置。

```json
{
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/",
    "tag": "latest"
  }
}
```

**access 选项**：

```json
{
  "name": "@myorg/my-package",
  "publishConfig": {
    "access": "public" // 公开发布（作用域包默认私有）
  }
}
```

**自定义 registry**：

```json
{
  "publishConfig": {
    "registry": "https://npm.pkg.github.com/" // GitHub Packages
  }
}
```

### 2. config

**作用**：配置脚本中使用的参数。

```json
{
  "config": {
    "port": "8080",
    "api_url": "https://api.example.com"
  },
  "scripts": {
    "start": "node server.js"
  }
}
```

**在脚本中使用**：

```javascript
// server.js
const port = process.env.npm_package_config_port;
const apiUrl = process.env.npm_package_config_api_url;

console.log(`Server running on port ${port}`);
console.log(`API URL: ${apiUrl}`);
```

**覆盖配置**：

```bash
npm config set my-package:port 3000
npm start
```

## Workspace 配置

### workspaces

**作用**：定义 Monorepo 工作区。

```json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["packages/*"]
}
```

**完整示例**：

```
my-monorepo/
├── package.json
├── packages/
│   ├── package-a/
│   │   └── package.json
│   ├── package-b/
│   │   └── package.json
│   └── package-c/
│       └── package.json
```

```json
// 根目录 package.json
{
  "name": "my-monorepo",
  "private": true,
  "workspaces": ["packages/*", "apps/*"],
  "scripts": {
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces"
  }
}
```

**使用 workspace**：

```bash
# 安装所有 workspace 的依赖
npm install

# 在特定 workspace 中运行命令
npm run build --workspace=package-a

# 在所有 workspace 中运行命令
npm run build --workspaces

# 添加依赖到特定 workspace
npm install lodash --workspace=package-a
```

## 其他字段

### 1. browserslist

**作用**：指定项目支持的浏览器版本。

```json
{
  "browserslist": ["> 1%", "last 2 versions", "not dead"]
}
```

**或使用独立文件**：

```
# .browserslistrc
> 1%
last 2 versions
not dead
not ie 11
```

**常用配置**：

```json
{
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### 2. sideEffects

**作用**：标记模块是否有副作用，用于 Tree Shaking。

```json
{
  "sideEffects": false
}
```

**指定有副作用的文件**：

```json
{
  "sideEffects": ["*.css", "*.scss", "./src/polyfills.js"]
}
```

**影响对比**：

```bash
# sideEffects: false
# 所有未使用的模块都会被删除
# 包体积更小

# 不配置 sideEffects
# 打包工具可能无法安全地删除未使用的代码
# 包体积更大
```

## 完整示例

### Vue 3 项目完整配置

```json
{
  "name": "my-vue-app",
  "version": "1.0.0",
  "description": "A Vue 3 application with TypeScript",
  "type": "module",
  "private": true,
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "keywords": ["vue", "typescript", "vite"],
  "homepage": "https://github.com/username/my-vue-app#readme",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/my-vue-app.git"
  },
  "bugs": {
    "url": "https://github.com/username/my-vue-app/issues"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx,.vue",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx,.vue --fix",
    "format": "prettier --write \"**/*.{js,jsx,ts,tsx,vue,json,css,scss,md}\"",
    "type-check": "vue-tsc --noEmit",
    "test": "vitest",
    "test:coverage": "vitest run --coverage"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@typescript-eslint/eslint-plugin": "^6.15.0",
    "@typescript-eslint/parser": "^6.15.0",
    "eslint": "^8.56.0",
    "eslint-plugin-vue": "^9.19.0",
    "prettier": "^3.1.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8",
    "vitest": "^1.0.4",
    "vue-tsc": "^1.8.25"
  },
  "browserslist": ["> 1%", "last 2 versions", "not dead"]
}
```

### npm 包完整配置

```json
{
  "name": "@myorg/my-library",
  "version": "1.0.0",
  "description": "A reusable JavaScript library",
  "type": "module",
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "keywords": ["library", "utility", "typescript"],
  "homepage": "https://github.com/myorg/my-library#readme",
  "repository": {
    "type": "git",
    "url": "https://github.com/myorg/my-library.git"
  },
  "bugs": {
    "url": "https://github.com/myorg/my-library/issues"
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./package.json": "./package.json"
  },
  "files": ["dist", "README.md", "LICENSE"],
  "engines": {
    "node": ">=18.0.0"
  },
  "scripts": {
    "build": "tsup src/index.ts --format cjs,esm --dts",
    "dev": "tsup src/index.ts --format cjs,esm --dts --watch",
    "lint": "eslint . --ext .ts",
    "test": "vitest",
    "prepublishOnly": "npm run lint && npm run test && npm run build"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "eslint": "^8.56.0",
    "tsup": "^8.0.0",
    "typescript": "^5.3.3",
    "vitest": "^1.0.4"
  },
  "publishConfig": {
    "access": "public",
    "registry": "https://registry.npmjs.org/"
  },
  "sideEffects": false
}
```

### Monorepo 根包配置

```json
{
  "name": "my-monorepo",
  "version": "1.0.0",
  "description": "A monorepo workspace",
  "private": true,
  "author": "Your Name",
  "license": "MIT",
  "workspaces": ["packages/*", "apps/*"],
  "scripts": {
    "dev": "npm run dev --workspaces",
    "build": "npm run build --workspaces",
    "lint": "npm run lint --workspaces",
    "test": "npm run test --workspaces",
    "clean": "rm -rf node_modules packages/*/node_modules apps/*/node_modules"
  },
  "devDependencies": {
    "eslint": "^8.56.0",
    "prettier": "^3.1.1",
    "typescript": "^5.3.3"
  }
}
```

## 常见问题

### 1. dependencies vs devDependencies

**如何区分**：

```json
{
  "dependencies": {
    // 运行时必需的包
    // - 框架（Vue、React、Express）
    // - 工具库（axios、lodash）
    // - UI 组件库（element-plus、ant-design）
    "vue": "^3.4.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    // 开发时需要的包
    // - 构建工具（Vite、Webpack）
    // - 代码检查（ESLint、Prettier）
    // - 测试框架（Vitest、Jest）
    // - 类型定义（@types/*）
    "vite": "^5.0.0",
    "eslint": "^8.56.0",
    "@types/node": "^20.10.0"
  }
}
```

### 2. 版本号选择

**推荐使用 `^` 符号**：

```json
{
  "dependencies": {
    "vue": "^3.4.0" // ✅ 推荐：允许小版本更新
  }
}
```

**不推荐**：

```json
{
  "dependencies": {
    "vue": "*", // ❌ 不推荐：可能安装不兼容版本
    "vue": "latest", // ❌ 不推荐：不稳定
    "vue": "3.4.0" // ⚠️  可以但不推荐：无法获取 bug 修复
  }
}
```

### 3. package-lock.json 的作用

```bash
# package-lock.json 的作用：
# 1. 锁定依赖版本
# 2. 确保团队成员安装相同版本
# 3. 加快安装速度（缓存依赖树）

# 应该提交到版本控制
git add package-lock.json package.json
git commit -m "chore: 更新依赖"
```

### 4. 清理和重装依赖

```bash
# 清理缓存
npm cache clean --force

# 删除依赖
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 或使用 npm ci（CI 环境推荐）
npm ci
```

## 最佳实践

### 1. 语义化版本

遵循 [Semantic Versioning](https://semver.org/)：

```json
{
  "version": "1.2.3"
  // 主版本号.次版本号.修订号
  // MAJOR.MINOR.PATCH
}
```

**更新规则**：

- **MAJOR**：不兼容的 API 修改
- **MINOR**：向下兼容的功能新增
- **PATCH**：向下兼容的 bug 修复

### 2. 脚本组织

```json
{
  "scripts": {
    // 开发相关
    "dev": "vite",
    "serve": "vite --host",

    // 构建相关
    "build": "vite build",
    "build:prod": "vite build --mode production",

    // 代码质量
    "lint": "npm-run-all --parallel lint:*",
    "lint:js": "eslint .",
    "lint:css": "stylelint \"**/*.css\"",

    // 测试相关
    "test": "vitest",
    "test:unit": "vitest run",
    "test:e2e": "cypress run",

    // 其他
    "clean": "rm -rf dist",
    "type-check": "tsc --noEmit"
  }
}
```

### 3. 依赖版本管理

```json
{
  "dependencies": {
    // 使用 ^ 允许小版本更新
    "vue": "^3.4.0",

    // 使用 ~ 只允许补丁更新
    "lodash": "~4.17.21",

    // 使用精确版本（特殊情况）
    "some-buggy-package": "1.2.3"
  }
}
```

### 4. 发布前检查

```json
{
  "scripts": {
    "prepublishOnly": "npm run lint && npm run test && npm run build"
  }
}
```

## 参考资源

- [npm package.json 官方文档](https://docs.npmjs.com/cli/v10/configuring-npm/package-json)
- [Semantic Versioning 规范](https://semver.org/)
- [npm scripts 文档](https://docs.npmjs.com/cli/v10/using-npm/scripts)
- [npm workspaces 文档](https://docs.npmjs.com/cli/v10/using-npm/workspaces)

---

🎉 现在你已经掌握了 package.json 的所有常用配置！
