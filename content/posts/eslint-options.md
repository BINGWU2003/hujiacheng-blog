---
title: "eslint 配置选项"
date: 2025-11-06
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 ESLint

[ESLint](https://eslint.org/) 是一个开源的 JavaScript 代码检查工具，用于识别和报告代码中的模式问题，帮助开发者：

- 🔍 **发现问题**：找出潜在的错误和 bug
- 📏 **统一风格**：强制执行一致的代码风格
- ⚡ **自动修复**：自动修复可修复的问题
- 🔧 **高度可配置**：支持自定义规则和插件
- 🚀 **现代化**：支持 ES6+、TypeScript、JSX 等

```bash
# 安装 ESLint
npm install --save-dev eslint

# 初始化配置文件（ESLint 8.x）
npx eslint --init
```

:::tip 版本说明
本文档基于 **ESLint 8.x** 编写，该版本已于 **2024-10-05 停止维护**。建议新项目使用 [ESLint 9.x](https://eslint.org/docs/latest/) 及其扁平化配置（Flat Config）。

**ESLint 8.x vs 9.x 主要区别**：

- ✅ **ESLint 9.x**（推荐新项目）：
  - 使用 `eslint.config.js` 扁平化配置格式
  - 移除 `env` 选项，使用 `globals` 包代替
  - 配置格式更简洁，采用数组形式
  - `ecmaVersion` 默认为 `"latest"`，`sourceType` 默认为 `"module"`
- ⚠️ **ESLint 8.x**（本文档）：
  - 使用 `.eslintrc.js` / `.eslintrc.json` 配置格式
  - 支持 `env`、`extends` 等传统配置选项
  - 仍然广泛使用于现有项目中

**ESLint 10.x 重大变更**：

- ❌ 完全移除对旧配置格式（`.eslintrc.*`）的支持
- ❌ 移除 `ESLINT_USE_FLAT_CONFIG` 环境变量
- ✅ 只支持扁平化配置格式（`eslint.config.js`）
  :::

:::warning 注意事项

- 本文档适用于使用 ESLint 8.x 及传统配置格式的项目
- 如果你正在启动新项目，建议直接使用 ESLint 9.x+ 和扁平化配置
- 现有项目可以使用 `@eslint/migrate-config` 工具迁移到新格式
- 配置迁移指南：https://eslint.org/docs/latest/use/configure/migration-guide
  :::

## 配置文件

ESLint 8.x 支持多种配置文件格式：

```bash
# JavaScript 格式（推荐）
.eslintrc.js
.eslintrc.cjs

# JSON 格式
.eslintrc.json
.eslintrc

# YAML 格式
.eslintrc.yaml
.eslintrc.yml

# package.json 中配置
{
  "eslintConfig": {
    // 配置项
  }
}
```

**推荐使用** `.eslintrc.js` 或 `.eslintrc.cjs`，本文以 JavaScript 格式为例。

### 配置文件后缀说明

#### .eslintrc.js vs .eslintrc.cjs

根据项目的模块系统选择：

**1. .eslintrc.js**

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
  },
  rules: {
    "no-console": "warn",
  },
};
```

**使用模块系统**：

- `package.json` 中 `"type": "commonjs"` 或未指定 → CommonJS
- `package.json` 中 `"type": "module"` → ES Module（需要 `export default`）

**2. .eslintrc.cjs（ES Module 项目推荐）**

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
  },
};
```

**适用场景**：

- 项目 `package.json` 中有 `"type": "module"`
- 明确使用 CommonJS 语法
- 避免模块系统混淆

## 一、核心配置选项

### 1.1 root

**作用**：限制 ESLint 向上查找配置文件。

```javascript
{
  "root": true
}
```

**默认值**：`false`

**影响对比**：

```javascript
// root: false（默认）
// ESLint 会向上查找父目录的配置文件，直到找到 root: true 或到达文件系统根目录
project/
├── .eslintrc.js (root: false)
├── src/
│   └── index.js
└── parent/
    └── .eslintrc.js  // 也会被应用

// root: true
// ESLint 只使用当前项目的配置，不再向上查找
project/
├── .eslintrc.js (root: true)  // 只使用这个
├── src/
│   └── index.js
```

**使用建议**：

- 项目根目录：`true`（推荐）
- 子目录覆盖配置：`false`

### 1.2 env

**作用**：指定代码运行环境，自动添加对应的全局变量。

```javascript
{
  "env": {
    "browser": true,    // 浏览器全局变量
    "node": true,       // Node.js 全局变量
    "es2021": true      // ES2021 全局变量
  }
}
```

**常用环境**：

```javascript
{
  "env": {
    // 运行环境
    "browser": true,      // 浏览器全局变量（window, document, localStorage 等）
    "node": true,         // Node.js 全局变量（process, __dirname, require 等）
    "worker": true,       // Web Worker 全局变量
    "serviceworker": true,// Service Worker 全局变量
    "commonjs": true,     // CommonJS 全局变量（module, exports）
    "shared-node-browser": true,  // Node.js 和浏览器共享的全局变量
    "amd": true,          // AMD 规范的 require() 和 define()

    // ECMAScript 版本（同时设置 parserOptions.ecmaVersion）
    "es6": true,          // ES6 全局变量（Promise, Set, Map），ecmaVersion 设为 6
    "es2016": true,       // ES2016 全局变量，ecmaVersion 设为 7
    "es2017": true,       // ES2017 全局变量，ecmaVersion 设为 8
    "es2018": true,       // ES2018 全局变量，ecmaVersion 设为 9
    "es2019": true,       // ES2019 全局变量，ecmaVersion 设为 10
    "es2020": true,       // ES2020 全局变量（BigInt, globalThis），ecmaVersion 设为 11
    "es2021": true,       // ES2021 全局变量，ecmaVersion 设为 12
    "es2022": true,       // ES2022 全局变量，ecmaVersion 设为 13
    "es2023": true,       // ES2023 全局变量，ecmaVersion 设为 14
    "es2024": true,       // ES2024 全局变量，ecmaVersion 设为 15

    // 测试框架
    "jest": true,         // Jest 全局变量（describe, test, expect）
    "mocha": true,        // Mocha 全局变量（describe, it, before）
    "jasmine": true,      // Jasmine 全局变量
    "qunit": true,        // QUnit 全局变量

    // 其他
    "jquery": true,       // jQuery 全局变量（$, jQuery）
    "mongo": true,        // MongoDB 全局变量
    "greasemonkey": true, // GreaseMonkey 全局变量
    "webextensions": true // WebExtensions 全局变量
  }
}
```

**影响对比**：

```javascript
// ❌ 未配置 env.browser
console.log(window.location); // ❌ 错误：'window' is not defined
document.querySelector(".btn"); // ❌ 错误：'document' is not defined

// ✅ 配置 env.browser: true
console.log(window.location); // ✅ 正确
document.querySelector(".btn"); // ✅ 正确

// ❌ 未配置 env.node
console.log(process.env.NODE_ENV); // ❌ 错误：'process' is not defined
const path = require("path"); // ❌ 错误：'require' is not defined

// ✅ 配置 env.node: true
console.log(process.env.NODE_ENV); // ✅ 正确
const path = require("path"); // ✅ 正确
```

### 1.3 globals

**作用**：定义自定义全局变量。

```javascript
{
  "globals": {
    "$": "readonly",      // jQuery（只读）
    "myGlobal": "writable",  // 可写全局变量
    "MY_CONST": "readonly"   // 只读常量
  }
}
```

**可选值**：

- `"readonly"`：只读，不可修改
- `"writable"`：可读写
- `"off"`：禁用该全局变量（即使环境中定义了也不可用）

**影响对比**：

```javascript
// ❌ 未声明全局变量
console.log(myAPI);  // ❌ 错误：'myAPI' is not defined

// ✅ 配置 globals
{
  "globals": {
    "myAPI": "readonly"
  }
}
console.log(myAPI);  // ✅ 正确

// readonly vs writable
{
  "globals": {
    "config": "readonly"
  }
}
config = {};  // ❌ 错误：'config' is read-only

{
  "globals": {
    "config": "writable"
  }
}
config = {};  // ✅ 正确
```

### 1.4 extends

**作用**：继承共享配置。

```javascript
{
  "extends": [
    "eslint:recommended",           // ESLint 推荐规则
    "plugin:vue/vue3-recommended",  // Vue 3 推荐规则
    "plugin:@typescript-eslint/recommended"  // TypeScript 推荐规则
  ]
}
```

**常用配置**：

```javascript
{
  "extends": [
    // ESLint 官方
    "eslint:recommended",    // 核心推荐规则
    "eslint:all",           // 所有规则（不推荐）

    // Vue
    "plugin:vue/vue3-essential",     // Vue 3 必要规则
    "plugin:vue/vue3-strongly-recommended",  // Vue 3 强烈推荐
    "plugin:vue/vue3-recommended",   // Vue 3 推荐规则（最严格）

    // React
    "plugin:react/recommended",      // React 推荐规则
    "plugin:react-hooks/recommended", // React Hooks 规则

    // TypeScript
    "plugin:@typescript-eslint/recommended",  // TS 推荐规则
    "plugin:@typescript-eslint/recommended-requiring-type-checking",  // 需要类型检查

    // Prettier（必须放在最后）
    "plugin:prettier/recommended"
  ]
}
```

**配置顺序**：后面的配置会覆盖前面的。

```javascript
{
  "extends": [
    "eslint:recommended",  // 基础规则
    "plugin:vue/vue3-recommended",  // Vue 规则（可能覆盖基础规则）
    "plugin:prettier/recommended"   // Prettier 规则（必须最后，禁用冲突规则）
  ]
}
```

### 1.5 plugins

**作用**：加载第三方插件。

```javascript
{
  "plugins": [
    "vue",              // eslint-plugin-vue
    "@typescript-eslint",  // @typescript-eslint/eslint-plugin
    "import",           // eslint-plugin-import
    "prettier"          // eslint-plugin-prettier
  ]
}
```

**插件命名规则**：

- `eslint-plugin-` 前缀可以省略
- `@scope/eslint-plugin-name` → `@scope/name`
- `@scope/eslint-plugin` → `@scope`

**影响对比**：

```javascript
// ❌ 未安装/配置插件
{
  "rules": {
    "vue/no-unused-vars": "error"  // ❌ 错误：找不到 vue 插件
  }
}

// ✅ 配置插件
{
  "plugins": ["vue"],
  "rules": {
    "vue/no-unused-vars": "error"  // ✅ 正确
  }
}
```

**常用插件**：

```bash
# Vue
npm install --save-dev eslint-plugin-vue

# TypeScript
npm install --save-dev @typescript-eslint/eslint-plugin @typescript-eslint/parser

# React
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks

# Import
npm install --save-dev eslint-plugin-import

# Prettier
npm install --save-dev eslint-plugin-prettier eslint-config-prettier
```

### 1.6 parser

**作用**：指定解析器，支持不同的语法。

```javascript
{
  "parser": "@typescript-eslint/parser"
}
```

**常用解析器**：

```javascript
// 默认：espree（ESLint 内置）
// 支持标准 JavaScript

// TypeScript
{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  }
}

// Vue
{
  "parser": "vue-eslint-parser",
  "parserOptions": {
    "parser": "@typescript-eslint/parser"  // 解析 <script> 标签内容
  }
}

// Babel
{
  "parser": "@babel/eslint-parser",
  "parserOptions": {
    "requireConfigFile": false
  }
}
```

**影响对比**：

```typescript
// ❌ 默认解析器无法解析 TypeScript
interface User {
  name: string;
}  // ❌ 语法错误

// ✅ 使用 TypeScript 解析器
{
  "parser": "@typescript-eslint/parser"
}
interface User {
  name: string;
}  // ✅ 正确解析
```

### 1.7 parserOptions

**作用**：配置解析器选项。

```javascript
{
  "parserOptions": {
    "ecmaVersion": 2021,           // ECMAScript 版本
    "sourceType": "module",        // 模块类型
    "ecmaFeatures": {
      "jsx": true,                 // 启用 JSX
      "globalReturn": false,       // 允许全局 return
      "impliedStrict": true        // 启用严格模式
    }
  }
}
```

**详细说明**：

```javascript
{
  "parserOptions": {
    // ECMAScript 版本
    // 可选值: 3, 5(默认), 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
    //        或 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
    //        或 "latest"（自动使用最新支持的版本）
    "ecmaVersion": "latest",

    // 模块类型
    "sourceType": "module",  // "script"(默认) 或 "module"

    // ECMAScript 特性
    "ecmaFeatures": {
      "jsx": true,              // 启用 JSX 解析
      "globalReturn": false,    // 允许全局作用域使用 return
      "impliedStrict": false    // 启用全局严格模式（ecmaVersion >= 5）
    },

    // TypeScript 特定（需要 @typescript-eslint/parser）
    "project": "./tsconfig.json",  // TypeScript 配置文件
    "tsconfigRootDir": __dirname   // tsconfig.json 所在目录
  }
}
```

**影响对比**：

```javascript
// sourceType: "script"（默认）
import { foo } from "./foo"; // ❌ 错误：不支持 import

// sourceType: "module"
import { foo } from "./foo"; // ✅ 正确

// ecmaFeatures.jsx: false
const element = <div>Hello</div>; // ❌ 语法错误

// ecmaFeatures.jsx: true
const element = <div>Hello</div>; // ✅ 正确解析
```

### 1.8 rules

**作用**：配置具体的检查规则。

```javascript
{
  "rules": {
    "semi": ["error", "always"],           // 要求分号
    "quotes": ["error", "single"],         // 使用单引号
    "no-console": "warn",                  // 警告 console
    "no-unused-vars": "error",             // 错误：未使用的变量
    "prefer-const": "error",               // 优先使用 const
    "@typescript-eslint/no-explicit-any": "off"  // 关闭规则
  }
}
```

**规则级别**：

```javascript
{
  "rules": {
    // 字符串形式
    "semi": "off",    // 关闭规则
    "semi": "warn",   // 警告
    "semi": "error",  // 错误

    // 数字形式（不推荐）
    "semi": 0,        // 关闭
    "semi": 1,        // 警告
    "semi": 2,        // 错误

    // 数组形式（带配置）
    "semi": ["error", "always"],  // 错误级别 + 配置
    "quotes": ["error", "single", { "avoidEscape": true }]
  }
}
```

**影响对比**：

```javascript
// semi: "off"
const name = "John"; // ✅ 不报错

// semi: "warn"
const name = "John"; // ⚠️ 警告：Missing semicolon

// semi: "error"
const name = "John"; // ❌ 错误：Missing semicolon

// semi: ["error", "always"]
const name = "John"; // ❌ 错误
const name = "John"; // ✅ 正确

// semi: ["error", "never"]
const name = "John"; // ❌ 错误
const name = "John"; // ✅ 正确
```

### 1.9 overrides

**作用**：为特定文件应用不同的配置。

```javascript
{
  "rules": {
    "no-console": "error"
  },
  "overrides": [
    {
      "files": ["*.test.js", "*.spec.js"],
      "env": {
        "jest": true
      },
      "rules": {
        "no-console": "off"  // 测试文件允许 console
      }
    },
    {
      "files": ["*.ts", "*.tsx"],
      "parser": "@typescript-eslint/parser",
      "rules": {
        "@typescript-eslint/no-unused-vars": "error"
      }
    }
  ]
}
```

**使用场景**：

```javascript
{
  "overrides": [
    // Vue 文件
    {
      "files": ["*.vue"],
      "parser": "vue-eslint-parser"
    },

    // 配置文件
    {
      "files": ["*.config.js", ".*rc.js"],
      "env": {
        "node": true
      },
      "rules": {
        "no-console": "off"
      }
    },

    // TypeScript 文件
    {
      "files": ["*.ts", "*.tsx"],
      "extends": ["plugin:@typescript-eslint/recommended"],
      "rules": {
        "no-undef": "off"  // TS 已经检查
      }
    }
  ]
}
```

## 二、常用规则详解

### 2.1 代码质量规则

#### no-unused-vars

**作用**：禁止未使用的变量。

```javascript
{
  "rules": {
    "no-unused-vars": ["error", {
      "vars": "all",              // 检查所有变量（包括全局）
      "args": "after-used",       // 只检查最后一个使用参数之后的参数
      "ignoreRestSiblings": true, // 忽略解构中的剩余兄弟属性
      "argsIgnorePattern": "^_",  // 忽略以 _ 开头的参数
      "varsIgnorePattern": "^_"   // 忽略以 _ 开头的变量
    }]
  }
}
```

**配置选项说明**：

| 选项                        | 可选值                              | 说明                                                                            |
| --------------------------- | ----------------------------------- | ------------------------------------------------------------------------------- |
| `vars`                      | `"all"` / `"local"`                 | `all`：检查所有变量；`local`：只检查局部变量                                    |
| `args`                      | `"after-used"` / `"all"` / `"none"` | `after-used`：只检查最后使用参数之后的；`all`：检查所有参数；`none`：不检查参数 |
| `ignoreRestSiblings`        | `true` / `false`                    | 是否忽略解构中剩余兄弟属性                                                      |
| `argsIgnorePattern`         | 正则表达式                          | 忽略匹配的参数名                                                                |
| `varsIgnorePattern`         | 正则表达式                          | 忽略匹配的变量名                                                                |
| `caughtErrors`              | `"all"` / `"none"`                  | 是否检查 catch 块中的错误参数                                                   |
| `caughtErrorsIgnorePattern` | 正则表达式                          | 忽略匹配的 catch 错误参数名                                                     |

**影响对比**：

```javascript
// ❌ 错误
const unused = 10; // ❌ 'unused' is assigned a value but never used

// args: "after-used" 时
function calculate(a, b, c, d) {
  // ❌ 'c' 和 'd' 在最后使用的 'b' 之后，会报错
  return a + b;
}

// ✅ 正确
const used = 10;
console.log(used);

function calculate(a, b) {
  // 只声明使用的参数
  return a + b;
}

// 使用下划线前缀表示故意不使用（配合 argsIgnorePattern: "^_"）
function calculate(a, b, _c) {
  // ✅ 正确
  return a + b;
}

// 解构中的剩余兄弟属性（配合 ignoreRestSiblings: true）
const { used, ...rest } = obj; // ✅ rest 即使未使用也不报错
console.log(used);
```

#### no-undef

**作用**：禁止使用未声明的变量。

```javascript
{
  "rules": {
    "no-undef": "error"
  }
}
```

**影响对比**：

```javascript
// ❌ 错误
console.log(undeclaredVar);  // ❌ 'undeclaredVar' is not defined

// ✅ 正确
const declaredVar = 10;
console.log(declaredVar);

// 或在 globals 中声明
{
  "globals": {
    "myGlobal": "readonly"
  }
}
console.log(myGlobal);  // ✅ 正确
```

#### no-const-assign

**作用**：禁止修改 const 声明的变量。

```javascript
{
  "rules": {
    "no-const-assign": "error"
  }
}
```

**影响对比**：

```javascript
// ❌ 错误
const PI = 3.14;
PI = 3.14159; // ❌ 'PI' is constant

// ✅ 正确
let value = 10;
value = 20; // ✅ 可以修改 let
```

### 2.2 最佳实践规则

#### prefer-const

**作用**：优先使用 const。

```javascript
{
  "rules": {
    "prefer-const": ["error", {
      "destructuring": "all",        // 解构赋值全用 const
      "ignoreReadBeforeAssign": false
    }]
  }
}
```

**影响对比**：

```javascript
// ❌ 错误
let name = "John"; // ❌ 'name' is never reassigned
console.log(name);

// ✅ 正确
const name = "John"; // ✅ 使用 const
console.log(name);

let count = 0; // ✅ 需要修改，使用 let
count++;
```

#### eqeqeq

**作用**：要求使用 === 和 !==。

```javascript
{
  "rules": {
    "eqeqeq": ["error", "always"]
  }
}
```

**影响对比**：

```javascript
// ❌ 错误
if (x == 10) {}      // ❌ Expected '===' and instead saw '=='
if (x != null) {}    // ❌ Expected '!==' and instead saw '!='

// ✅ 正确
if (x === 10) {}     // ✅
if (x !== null) {}   // ✅

// 特殊情况：允许与 null 比较
{
  "rules": {
    "eqeqeq": ["error", "always", { "null": "ignore" }]
  }
}
if (x == null) {}    // ✅ 允许 x == null 检查 null 和 undefined
```

#### no-var

**作用**：禁止使用 var。

```javascript
{
  "rules": {
    "no-var": "error"
  }
}
```

**影响对比**：

```javascript
// ❌ 错误
var name = "John"; // ❌ Unexpected var, use let or const instead

// ✅ 正确
const name = "John"; // ✅
let count = 0; // ✅
```

### 2.3 代码风格规则

#### semi

**作用**：要求或禁止分号。

```javascript
{
  "rules": {
    "semi": ["error", "always"]  // 或 "never"
  }
}
```

**影响对比**：

```javascript
// semi: ["error", "always"]
const name = "John"; // ❌ Missing semicolon
const name = "John"; // ✅

// semi: ["error", "never"]
const name = "John"; // ❌ Extra semicolon
const name = "John"; // ✅
```

#### quotes

**作用**：强制使用一致的引号。

```javascript
{
  "rules": {
    "quotes": ["error", "single", {
      "avoidEscape": true,        // 避免转义
      "allowTemplateLiterals": true  // 允许模板字符串
    }]
  }
}
```

**影响对比**：

```javascript
// quotes: ["error", "single"]
const name = "John"; // ❌ Strings must use singlequote
const name = "John"; // ✅

// avoidEscape: true
const text = "It's ok"; // ❌ 需要转义
const text = "It's ok"; // ✅ 避免转义，允许双引号
const text = `It's ok`; // ✅ 模板字符串

// allowTemplateLiterals: true
const name = `John`; // ✅ 允许模板字符串
const greeting = `Hello ${name}`; // ✅
```

#### indent

**作用**：强制使用一致的缩进。

```javascript
{
  "rules": {
    "indent": ["error", 2, {
      "SwitchCase": 1,           // switch case 缩进
      "VariableDeclarator": 1    // 变量声明缩进
    }]
  }
}
```

**影响对比**：

```javascript
// indent: ["error", 2]
function greet() {
  console.log("Hello"); // ❌ Expected indentation of 2 spaces but found 4
}

function greet() {
  console.log("Hello"); // ✅
}

// SwitchCase: 1
switch (x) {
  case 1: // ❌ Expected indentation of 2 spaces
    break;
}

switch (x) {
  case 1: // ✅
    break;
}
```

### 2.4 Vue 特定规则

#### vue/multi-word-component-names

**作用**：要求组件名为多个单词。

```javascript
{
  "rules": {
    "vue/multi-word-component-names": ["error", {
      "ignores": ["index", "App"]
    }]
  }
}
```

**影响对比**：

```vue
<!-- ❌ 错误 -->
<script>
export default {
  name: "Button", // ❌ Component name should be multi-word
};
</script>

<!-- ✅ 正确 -->
<script>
export default {
  name: "BaseButton", // ✅ 多个单词
};
</script>

<!-- 特殊情况 -->
<script>
export default {
  name: "App", // ✅ 在 ignores 中
};
</script>
```

#### vue/html-indent

**作用**：Vue 模板缩进。

```javascript
{
  "rules": {
    "vue/html-indent": ["error", 2, {
      "attribute": 1,
      "baseIndent": 1
    }]
  }
}
```

### 2.5 TypeScript 特定规则

#### @typescript-eslint/no-explicit-any

**作用**：禁止使用 any 类型。

```javascript
{
  "rules": {
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

**影响对比**：

```typescript
// ❌ 错误
function process(data: any) {
  // ❌ Unexpected any
  return data;
}

// ✅ 正确
function process(data: unknown) {
  // ✅ 使用 unknown
  return data;
}

function process<T>(data: T): T {
  // ✅ 使用泛型
  return data;
}
```

#### @typescript-eslint/no-unused-vars

**作用**：TypeScript 版本的未使用变量检查。

```javascript
{
  "rules": {
    "no-unused-vars": "off",  // 关闭基础规则，避免与 TS 规则冲突
    "@typescript-eslint/no-unused-vars": ["error", {
      "args": "all",                       // 检查所有参数
      "argsIgnorePattern": "^_",           // 忽略 _ 开头的参数
      "varsIgnorePattern": "^_",           // 忽略 _ 开头的变量
      "caughtErrors": "all",               // 检查 catch 中的错误参数
      "caughtErrorsIgnorePattern": "^_",   // 忽略 _ 开头的错误参数
      "destructuredArrayIgnorePattern": "^_",  // 忽略解构数组中 _ 开头的元素
      "ignoreRestSiblings": true           // 忽略剩余兄弟属性
    }]
  }
}
```

## 三、完整推荐配置

### 3.1 纯 JavaScript 项目

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: ["eslint:recommended"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  rules: {
    // 代码质量
    "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",

    // 最佳实践
    "prefer-const": "error",
    "no-var": "error",
    eqeqeq: ["error", "always", { null: "ignore" }],

    // 代码风格
    semi: ["error", "always"],
    quotes: ["error", "single", { avoidEscape: true }],
    indent: ["error", 2, { SwitchCase: 1 }],
    "comma-dangle": ["error", "never"],
  },
};
```

### 3.2 Vue 3 + TypeScript 项目

```javascript
// .eslintrc.cjs
module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:vue/vue3-recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended", // 必须放在最后
  ],
  parser: "vue-eslint-parser",
  parserOptions: {
    ecmaVersion: "latest",
    parser: "@typescript-eslint/parser",
    sourceType: "module",
    project: "./tsconfig.json",
    extraFileExtensions: [".vue"],
  },
  plugins: ["vue", "@typescript-eslint"],
  rules: {
    // Vue 规则
    "vue/multi-word-component-names": [
      "error",
      {
        ignores: ["index", "App", "[id]"],
      },
    ],
    "vue/component-name-in-template-casing": ["error", "PascalCase"],
    "vue/component-definition-name-casing": ["error", "PascalCase"],
    "vue/html-self-closing": [
      "error",
      {
        html: {
          void: "always",
          normal: "never",
          component: "always",
        },
      },
    ],

    // TypeScript 规则
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-module-boundary-types": "off",

    // 通用规则
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off",
  },
  overrides: [
    // 配置文件
    {
      files: ["*.config.js", "*.config.ts"],
      rules: {
        "no-console": "off",
      },
    },
  ],
};
```

### 3.3 React + TypeScript 项目

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended",
  ],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
    project: "./tsconfig.json",
  },
  plugins: ["react", "react-hooks", "@typescript-eslint"],
  settings: {
    react: {
      version: "detect", // 自动检测 React 版本
    },
  },
  rules: {
    // React 规则
    "react/react-in-jsx-scope": "off", // React 17+ 不需要
    "react/prop-types": "off", // 使用 TypeScript
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",

    // TypeScript 规则
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
      },
    ],
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "@typescript-eslint/no-explicit-any": "warn",

    // 通用规则
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
  },
};
```

### 3.4 Node.js 项目

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
  },
  extends: ["eslint:recommended"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  rules: {
    // Node.js 特定
    "no-console": "off", // Node.js 允许 console
    "no-process-exit": "error",

    // 代码质量
    "no-unused-vars": [
      "error",
      {
        argsIgnorePattern: "^_",
      },
    ],
    "prefer-const": "error",
    "no-var": "error",
  },
};
```

## 四、与 Prettier 集成

### 4.1 安装依赖

```bash
npm install --save-dev eslint prettier eslint-config-prettier eslint-plugin-prettier
```

### 4.2 配置 ESLint

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended", // 必须放在最后
  ],
};
```

### 4.3 配置 Prettier

```json
// .prettierrc.json
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "es5",
  "arrowParens": "always"
}
```

### 4.4 package.json 脚本

```json
{
  "scripts": {
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx,.vue",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx,.vue --fix",
    "format": "prettier --write ."
  }
}
```

## 五、忽略文件

### 5.1 .eslintignore

```bash
# 依赖
node_modules
pnpm-lock.yaml
package-lock.json

# 构建产物
dist
build
.next
.nuxt
out
coverage

# 缓存
.cache
*.log

# 自动生成的文件
*.min.js
auto-imports.d.ts
components.d.ts

# 配置文件
.env
.env.*
```

### 5.2 在配置文件中忽略

```javascript
module.exports = {
  ignorePatterns: ["dist", "node_modules", "*.min.js"],
};
```

## 六、常见问题和最佳实践

### 6.1 ESLint vs Prettier

**区别**：

| 工具     | 职责                | 示例                           |
| -------- | ------------------- | ------------------------------ |
| ESLint   | 代码质量 + 部分风格 | 未使用变量、潜在 bug、部分格式 |
| Prettier | 代码格式化          | 缩进、引号、分号、换行         |

**推荐做法**：

1. 使用 ESLint 检查代码质量
2. 使用 Prettier 格式化代码
3. 使用 `eslint-config-prettier` 禁用 ESLint 中与 Prettier 冲突的规则

```javascript
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended", // 禁用冲突规则并启用 Prettier 规则
  ],
};
```

### 6.2 性能优化

**1. 使用缓存**：

```json
{
  "scripts": {
    "lint": "eslint . --cache --cache-location node_modules/.cache/eslint"
  }
}
```

**2. 限制检查文件**：

```json
{
  "scripts": {
    "lint": "eslint src --ext .js,.jsx,.ts,.tsx"
  }
}
```

**3. 使用 ignorePatterns**：

```javascript
module.exports = {
  ignorePatterns: ["dist", "node_modules", "*.min.js"],
};
```

### 6.3 VS Code 集成

**.vscode/settings.json**：

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact",
    "vue"
  ],
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### 6.4 Git Hooks 集成

**使用 husky + lint-staged**：

```bash
npm install --save-dev husky lint-staged
npx husky init
```

**package.json**：

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx,vue}": ["eslint --fix", "prettier --write"]
  }
}
```

**.husky/pre-commit**：

```bash
#!/usr/bin/env sh
npx lint-staged
```

### 6.5 CI 中运行

**.github/workflows/lint.yml**：

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "18"
      - run: npm ci
      - run: npm run lint
```

### 6.6 迁移现有项目

**步骤**：

```bash
# 1. 安装 ESLint
npm install --save-dev eslint

# 2. 初始化配置
npx eslint --init

# 3. 检查问题
npm run lint

# 4. 自动修复
npm run lint:fix

# 5. 手动修复剩余问题

# 6. 提交更改
git add .
git commit -m "chore: 添加 ESLint 配置"
```

### 6.7 禁用规则的正确方式

**文件级别**：

```javascript
/* eslint-disable */
// 整个文件禁用

/* eslint-enable */
// 重新启用
```

**行级别**：

```javascript
// eslint-disable-next-line
const unused = 10;

const unused = 10; // eslint-disable-line

// 禁用特定规则
// eslint-disable-next-line no-console
console.log("Debug");
```

**块级别**：

```javascript
/* eslint-disable no-console */
console.log("Debug 1");
console.log("Debug 2");
/* eslint-enable no-console */
```

### 6.8 常见错误解决

**1. Parsing error: Cannot find module '@typescript-eslint/parser'**

```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**2. 'module' is not defined**

```javascript
// .eslintrc.js
module.exports = {
  env: {
    node: true, // 添加 node 环境
  },
};
```

**3. ESLint 和 Prettier 冲突**

```bash
npm install --save-dev eslint-config-prettier
```

```javascript
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended", // 必须放在最后
  ],
};
```

## 七、总结

### 必须配置的选项

1. **root**: `true` - 限制配置查找
2. **env** - 声明运行环境
3. **extends** - 继承推荐配置
4. **parser** - TypeScript/Vue 项目必需
5. **rules** - 根据团队规范自定义

### 推荐工作流

1. 使用 `eslint:recommended` 作为基础
2. 根据框架添加对应插件（Vue/React/TypeScript）
3. 集成 Prettier 处理代码格式
4. 配置 Git Hooks 自动检查
5. 在 CI 中运行 lint

### 常用命令

```bash
# 检查代码
npx eslint .

# 自动修复
npx eslint . --fix

# 检查特定文件
npx eslint src/index.js

# 使用缓存
npx eslint . --cache

# 输出 JSON 格式
npx eslint . --format json

# 检查并报告未使用的禁用指令
npx eslint . --report-unused-disable-directives
```

### 学习建议

1. 从 `eslint:recommended` 开始
2. 逐步添加规则，不要一次性开启所有
3. 理解每个规则的作用，而不是盲目配置
4. 使用 `--fix` 自动修复可修复的问题
5. 定期更新 ESLint 和插件版本

## 八、ESLint 9.x 新特性预览

ESLint 9.x 引入了全新的**扁平化配置（Flat Config）**系统，使用 `eslint.config.js` 替代 `.eslintrc.*` 文件。

### 8.1 主要变化

| 特性         | ESLint 8.x                        | ESLint 9.x                  |
| ------------ | --------------------------------- | --------------------------- |
| 配置文件     | `.eslintrc.js` / `.eslintrc.json` | `eslint.config.js`          |
| 配置格式     | 对象形式                          | 数组形式                    |
| env 选项     | 支持                              | 移除，使用 `globals` 包代替 |
| plugins 格式 | 字符串数组                        | 对象形式                    |
| extends      | 支持                              | 移除，直接使用配置数组      |

### 8.2 扁平化配置示例

```javascript
// eslint.config.js
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";

export default [
  // 推荐配置
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs["flat/recommended"],

  // 自定义配置
  {
    files: ["**/*.{js,ts,vue}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      "no-console": "warn",
      "no-unused-vars": "error",
    },
  },

  // 忽略文件
  {
    ignores: ["dist/**", "node_modules/**"],
  },
];
```

### 8.3 迁移建议

如果你正在使用 ESLint 8.x，可以通过以下命令检查配置迁移：

```bash
# 安装迁移工具
npx @eslint/migrate-config .eslintrc.js

# 或手动迁移
# 参考官方迁移指南：https://eslint.org/docs/latest/use/configure/migration-guide
```

## 参考资源

- [ESLint 官方文档](https://eslint.org/docs/latest/)
- [ESLint 8.x 文档](https://eslint.org/docs/v8.x/)
- [ESLint 规则列表](https://eslint.org/docs/latest/rules/)
- [ESLint 配置迁移指南](https://eslint.org/docs/latest/use/configure/migration-guide)
- [Vue ESLint Plugin](https://eslint.vuejs.org/)
- [TypeScript ESLint](https://typescript-eslint.io/)
- [React ESLint Plugin](https://github.com/jsx-eslint/eslint-plugin-react)
- [ESLint Playground](https://eslint.org/play/)
