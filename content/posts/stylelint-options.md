---
title: "stylelint 配置选项"
date: 2025-11-06
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 Stylelint

[Stylelint](https://stylelint.io/) 是一个强大的 CSS 代码检查工具，帮助你：

- 🎯 **避免错误**：检测无效的 CSS 语法、拼写错误的属性名等
- 📐 **强制规范**：统一代码风格，如缩进、引号、命名规范等
- 🔧 **自动修复**：自动修复大部分格式问题
- 🔌 **高度可扩展**：支持 100+ 内置规则和自定义插件
- 💪 **支持预处理器**：SCSS、Sass、Less、SugarSS 等
- 🌐 **支持现代 CSS**：CSS Grid、Custom Properties、Modern Color Functions

```bash
# 安装 Stylelint
npm install --save-dev stylelint stylelint-config-standard

# 创建配置文件
echo '{"extends": ["stylelint-config-standard"]}' > .stylelintrc.json

# 运行检查
npx stylelint "**/*.css"
```

## 为什么需要 Stylelint

### 传统问题

没有代码检查工具时，CSS 代码容易出现各种问题：

```css
/* ❌ 问题代码 */
.selector {
  colro: #fff; /* 拼写错误 */
  background: #ffffff; /* 大小写不统一 */
  margin: 0.5px; /* 缺少前导 0 */
  color: rgb(255, 255, 255); /* 空格不统一 */
}

.selector {
  /* 重复的选择器 */
  color: red;
}

#id-selector {
} /* 过多的 ID 选择器 */
#another-id {
}
```

**结果**：

- ❌ 拼写错误导致样式不生效
- ❌ 代码风格不统一，难以维护
- ❌ 潜在的性能问题
- ❌ 难以发现重复或冗余代码

### 使用 Stylelint 后

```css
/* ✅ 规范的代码 */
.selector {
  color: #fff;
  background-color: #ffffff;
  margin: 0.5px;
  color: rgb(255, 255, 255);
}

/* Stylelint 会提示：
   - 拼写错误
   - 重复的选择器
   - ID 选择器过多
   - 格式问题（自动修复）
*/
```

**结果**：

- ✅ 自动检测拼写错误
- ✅ 代码风格自动统一
- ✅ 提前发现潜在问题
- ✅ 提高代码质量

## 安装

### 基础安装

```bash
# 使用 npm
npm install --save-dev stylelint stylelint-config-standard

# 使用 yarn
yarn add -D stylelint stylelint-config-standard

# 使用 pnpm
pnpm add -D stylelint stylelint-config-standard
```

### SCSS/Sass 项目

```bash
npm install --save-dev stylelint stylelint-config-standard-scss
```

### Vue 项目

```bash
npm install --save-dev stylelint stylelint-config-standard-vue
```

### 完整安装（推荐）

```bash
# Stylelint 核心 + 标准配置 + SCSS 支持 + 属性排序
npm install --save-dev \
  stylelint \
  stylelint-config-standard-scss \
  stylelint-config-recommended-vue \
  stylelint-order \
  postcss postcss-html
```

## 配置文件

### 支持的配置文件格式

Stylelint 支持多种配置文件格式：

```bash
# JavaScript（推荐）
.stylelintrc.js
.stylelintrc.cjs
.stylelintrc.mjs
stylelint.config.js
stylelint.config.cjs
stylelint.config.mjs

# JSON
.stylelintrc
.stylelintrc.json

# YAML
.stylelintrc.yaml
.stylelintrc.yml

# package.json 中配置
{
  "stylelint": {
    // 配置项
  }
}
```

**推荐使用** `.stylelintrc.js` 或 `stylelint.config.js`。

### 配置文件后缀说明

#### .stylelintrc.js vs .stylelintrc.cjs vs .stylelintrc.mjs

根据项目的模块系统选择：

**1. .stylelintrc.js 或 stylelint.config.js**

```javascript
// .stylelintrc.js
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "color-hex-case": "lower",
  },
};
```

**使用模块系统**：

- `package.json` 中 `"type": "commonjs"` 或未指定 → CommonJS
- `package.json` 中 `"type": "module"` → ES Module（需要 `export default`）

**2. .stylelintrc.cjs（CommonJS 明确标识）**

```javascript
// .stylelintrc.cjs
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "color-hex-case": "lower",
  },
};
```

**适用场景**：

- 项目是 ES Module（`"type": "module"`），但配置文件需要使用 CommonJS

**3. .stylelintrc.mjs（ES Module 明确标识）**

```javascript
// .stylelintrc.mjs
export default {
  extends: ["stylelint-config-standard"],
  rules: {
    "color-hex-case": "lower",
  },
};
```

**适用场景**：

- 项目是 CommonJS 或未指定，但配置文件想使用 ES Module
- Node.js 18+ 推荐使用

## 一、核心配置选项

### 1.1 extends

**作用**：继承共享配置。

```javascript
module.exports = {
  extends: ["stylelint-config-standard"],
};
```

**常用共享配置**：

```javascript
module.exports = {
  extends: [
    "stylelint-config-standard", // 标准配置（推荐）
    "stylelint-config-standard-scss", // SCSS 标准配置
    "stylelint-config-recommended-vue", // Vue 推荐配置
    "stylelint-config-prettier", // 禁用与 Prettier 冲突的规则
  ],
};
```

**配置包说明**：

| 配置包                             | 说明                           | 适用场景             |
| ---------------------------------- | ------------------------------ | -------------------- |
| `stylelint-config-standard`        | CSS 标准配置，包含所有推荐规则 | 纯 CSS 项目          |
| `stylelint-config-standard-scss`   | SCSS 标准配置，扩展 CSS 配置   | SCSS/Sass 项目       |
| `stylelint-config-recommended-vue` | Vue 推荐配置，支持 `.vue` 文件 | Vue 项目             |
| `stylelint-config-prettier`        | 禁用与 Prettier 冲突的规则     | 使用 Prettier 的项目 |

**影响对比**：

```css
/* 不使用 extends（无规则） */
.selector {
  colro: #fff; /* ✅ 不会报错（但有拼写错误）*/
}

/* 使用 stylelint-config-standard */
.selector {
  colro: #fff; /* ❌ 错误：Unknown property "colro" */
  color: #fff; /* ⚠️ 警告：Expected "#FFF" to be "#fff" (color-hex-case) */
}
```

### 1.2 plugins

**作用**：加载第三方插件，扩展 Stylelint 功能。

```javascript
module.exports = {
  plugins: ["stylelint-order", "stylelint-scss"],
  rules: {
    "order/properties-alphabetical-order": true,
    "scss/at-rule-no-unknown": true,
  },
};
```

**常用插件**：

```javascript
module.exports = {
  plugins: [
    "stylelint-order", // 属性排序
    "stylelint-scss", // SCSS 规则
    "stylelint-declaration-block-no-ignored-properties", // 检测冲突属性
    "stylelint-high-performance-animation", // 性能优化
  ],
};
```

**影响对比**：

```css
/* 不使用 stylelint-order 插件 */
.selector {
  color: red;
  margin: 10px;
  background: blue;
  padding: 5px;
}
/* ✅ 通过（但属性顺序混乱）*/

/* 使用 stylelint-order 插件 */
.selector {
  color: red;
  margin: 10px;
  background: blue;
  padding: 5px;
}
/* ❌ 错误：属性顺序不正确 */

/* 正确的顺序（可自动修复）*/
.selector {
  background: blue;
  color: red;
  margin: 10px;
  padding: 5px;
}
/* ✅ 通过 */
```

### 1.3 rules

**作用**：配置具体的检查规则。

```javascript
module.exports = {
  rules: {
    "color-hex-case": "lower",
    "color-hex-length": "short",
    indentation: 2,
    "max-nesting-depth": 3,
  },
};
```

**规则格式**：

```javascript
module.exports = {
  rules: {
    // 格式 1：只有值
    "rule-name": "value",

    // 格式 2：值 + 选项
    "rule-name": ["value", { option: true }],

    // 格式 3：null（禁用规则）
    "rule-name": null,
  },
};
```

**规则严重级别**：

```javascript
module.exports = {
  rules: {
    // "error" 或 2：错误（会阻止构建）
    "color-hex-case": ["error", "lower"],

    // "warning" 或 1：警告（不会阻止构建）
    "color-hex-length": ["warning", "short"],

    // null：禁用规则
    indentation: null,
  },
};
```

**影响对比**：

```css
/* color-hex-case: 'lower' */
.selector {
  color: #fff; /* ❌ 错误：Expected "#FFF" to be "#fff" */
  color: #fff; /* ✅ 通过 */
}

/* color-hex-case: 'upper' */
.selector {
  color: #fff; /* ❌ 错误：Expected "#fff" to be "#FFF" */
  color: #fff; /* ✅ 通过 */
}

/* color-hex-case: null（禁用） */
.selector {
  color: #fff; /* ✅ 通过 */
  color: #fff; /* ✅ 通过 */
}
```

### 1.4 ignoreFiles

**作用**：忽略特定文件或目录。

```javascript
module.exports = {
  ignoreFiles: ["node_modules/**", "dist/**", "build/**", "**/*.min.css"],
};
```

**支持 glob 模式**：

```javascript
module.exports = {
  ignoreFiles: [
    "**/*.min.css", // 忽略所有压缩文件
    "vendor/**", // 忽略 vendor 目录
    "**/node_modules/**", // 忽略所有 node_modules
    "src/styles/reset.css", // 忽略特定文件
    "!src/styles/custom.css", // 不忽略（取消忽略）
  ],
};
```

### 1.5 customSyntax

**作用**：指定自定义语法解析器。

```javascript
module.exports = {
  // Vue 单文件组件
  customSyntax: "postcss-html",

  // 或者针对不同文件使用不同语法
  overrides: [
    {
      files: ["*.vue", "**/*.vue"],
      customSyntax: "postcss-html",
    },
    {
      files: ["*.scss", "**/*.scss"],
      customSyntax: "postcss-scss",
    },
  ],
};
```

**常用语法解析器**：

| 解析器         | 说明                      | 安装                    |
| -------------- | ------------------------- | ----------------------- |
| `postcss-html` | 解析 HTML、Vue、Svelte 等 | `npm i -D postcss-html` |
| `postcss-scss` | 解析 SCSS                 | `npm i -D postcss-scss` |
| `postcss-less` | 解析 Less                 | `npm i -D postcss-less` |
| `postcss-sass` | 解析 Sass                 | `npm i -D postcss-sass` |
| `sugarss`      | 解析 SugarSS              | `npm i -D sugarss`      |

### 1.6 overrides

**作用**：针对特定文件覆盖配置。

```javascript
module.exports = {
  extends: ["stylelint-config-standard"],

  overrides: [
    // Vue 文件
    {
      files: ["*.vue", "**/*.vue"],
      customSyntax: "postcss-html",
      rules: {
        "selector-class-pattern": null, // 禁用类名检查
      },
    },

    // SCSS 文件
    {
      files: ["*.scss", "**/*.scss"],
      customSyntax: "postcss-scss",
      extends: ["stylelint-config-standard-scss"],
    },

    // 第三方库样式
    {
      files: ["vendor/**/*.css"],
      rules: null, // 禁用所有规则
    },
  ],
};
```

### 1.7 defaultSeverity

**作用**：设置默认严重级别。

```javascript
module.exports = {
  defaultSeverity: "warning", // 'error' 或 'warning'
  rules: {
    "color-hex-case": "lower", // 使用默认的 warning 级别
  },
};
```

## 二、常用规则详解

### 2.1 颜色相关规则

#### color-hex-case

**作用**：指定十六进制颜色的大小写。

```javascript
module.exports = {
  rules: {
    "color-hex-case": "lower", // 'lower' 或 'upper'
  },
};
```

**影响对比**：

```css
/* color-hex-case: 'lower' */
.selector {
  color: #fff; /* ❌ 错误 */
  color: #fff; /* ✅ 通过 */
}

/* color-hex-case: 'upper' */
.selector {
  color: #fff; /* ❌ 错误 */
  color: #fff; /* ✅ 通过 */
}
```

#### color-hex-length

**作用**：指定十六进制颜色的长度。

```javascript
module.exports = {
  rules: {
    "color-hex-length": "short", // 'short' 或 'long'
  },
};
```

**影响对比**：

```css
/* color-hex-length: 'short' */
.selector {
  color: #ffffff; /* ❌ 错误：应该是 #fff */
  color: #fff; /* ✅ 通过 */
}

/* color-hex-length: 'long' */
.selector {
  color: #fff; /* ❌ 错误：应该是 #ffffff */
  color: #ffffff; /* ✅ 通过 */
}
```

#### color-no-invalid-hex

**作用**：禁止无效的十六进制颜色。

```javascript
module.exports = {
  rules: {
    "color-no-invalid-hex": true,
  },
};
```

**影响对比**：

```css
.selector {
  color: #00; /* ❌ 错误：无效的十六进制颜色 */
  color: #0000; /* ❌ 错误：无效的十六进制颜色 */
  color: #gggggg; /* ❌ 错误：包含非十六进制字符 */
  color: #000; /* ✅ 通过 */
  color: #000000; /* ✅ 通过 */
}
```

### 2.2 字体相关规则

#### font-family-no-duplicate-names

**作用**：禁止重复的字体名称。

```javascript
module.exports = {
  rules: {
    "font-family-no-duplicate-names": true,
  },
};
```

**影响对比**：

```css
.selector {
  font-family: Arial, Arial, sans-serif; /* ❌ 错误：重复的 Arial */
  font-family: Arial, Helvetica, sans-serif; /* ✅ 通过 */
}
```

#### font-family-name-quotes

**作用**：指定字体名称是否需要引号。

```javascript
module.exports = {
  rules: {
    "font-family-name-quotes": "always-where-required",
    // 'always-where-recommended' | 'always-where-required' | 'always-unless-keyword'
  },
};
```

**影响对比**：

```css
/* font-family-name-quotes: 'always-where-required' */
.selector {
  font-family: Times New Roman; /* ❌ 错误：包含空格需要引号 */
  font-family: "Times New Roman"; /* ✅ 通过 */
  font-family: Arial; /* ✅ 通过（单词不需要引号）*/
}
```

### 2.3 选择器相关规则

#### selector-class-pattern

**作用**：指定类选择器的命名模式。

```javascript
module.exports = {
  rules: {
    // BEM 命名规范
    "selector-class-pattern":
      "^[a-z][a-z0-9]*(-[a-z0-9]+)*(__[a-z0-9]+(-[a-z0-9]+)*)?(--[a-z0-9]+(-[a-z0-9]+)*)?$",

    // 或者简单的 kebab-case
    "selector-class-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$",
  },
};
```

**影响对比**：

```css
/* BEM 命名规范 */
.block {
} /* ✅ 通过 */
.block__element {
} /* ✅ 通过 */
.block--modifier {
} /* ✅ 通过 */
.block__element--modifier {
} /* ✅ 通过 */
.Block {
} /* ❌ 错误：不能以大写开头 */
.block_element {
} /* ❌ 错误：应该使用双下划线 */
```

#### selector-max-id

**作用**：限制选择器中 ID 选择器的数量。

```javascript
module.exports = {
  rules: {
    "selector-max-id": 0, // 不允许使用 ID 选择器
  },
};
```

**影响对比**：

```css
/* selector-max-id: 0 */
#id {
} /* ❌ 错误：不允许 ID 选择器 */
.class {
} /* ✅ 通过 */

/* selector-max-id: 1 */
#id {
} /* ✅ 通过 */
#id1 #id2 {
} /* ❌ 错误：超过 1 个 ID 选择器 */
```

#### selector-no-qualifying-type

**作用**：禁止使用类型选择器限定其他选择器。

```javascript
module.exports = {
  rules: {
    "selector-no-qualifying-type": true,
  },
};
```

**影响对比**：

```css
.selector {
  div.class {
  } /* ❌ 错误：不应该用 div 限定 .class */
  .class {
  } /* ✅ 通过 */

  div#id {
  } /* ❌ 错误：不应该用 div 限定 #id */
  #id {
  } /* ✅ 通过 */
}
```

### 2.4 属性相关规则

#### property-no-unknown

**作用**：禁止未知的属性。

```javascript
module.exports = {
  rules: {
    "property-no-unknown": true,
  },
};
```

**影响对比**：

```css
.selector {
  colro: red; /* ❌ 错误：未知的属性（拼写错误）*/
  color: red; /* ✅ 通过 */

  border-raidus: 5px; /* ❌ 错误：未知的属性（拼写错误）*/
  border-radius: 5px; /* ✅ 通过 */
}
```

#### property-case

**作用**：指定属性名的大小写。

```javascript
module.exports = {
  rules: {
    "property-case": "lower", // 'lower' 或 'upper'
  },
};
```

**影响对比**：

```css
/* property-case: 'lower' */
.selector {
  color: red; /* ❌ 错误：属性名应该小写 */
  color: red; /* ✅ 通过 */
}
```

### 2.5 数值相关规则

#### number-leading-zero

**作用**：指定数字的前导零。

```javascript
module.exports = {
  rules: {
    "number-leading-zero": "always", // 'always' 或 'never'
  },
};
```

**影响对比**：

```css
/* number-leading-zero: 'always' */
.selector {
  opacity: 0.5; /* ❌ 错误：应该是 0.5 */
  opacity: 0.5; /* ✅ 通过 */
}

/* number-leading-zero: 'never' */
.selector {
  opacity: 0.5; /* ❌ 错误：应该是 .5 */
  opacity: 0.5; /* ✅ 通过 */
}
```

#### number-no-trailing-zeros

**作用**：禁止数字的尾随零。

```javascript
module.exports = {
  rules: {
    "number-no-trailing-zeros": true,
  },
};
```

**影响对比**：

```css
.selector {
  opacity: 0.5; /* ❌ 错误：应该是 0.5 */
  opacity: 0.5; /* ✅ 通过 */

  margin: 1px; /* ❌ 错误：应该是 1px */
  margin: 1px; /* ✅ 通过 */
}
```

### 2.6 缩进和空格规则

#### indentation

**作用**：指定缩进。

```javascript
module.exports = {
  rules: {
    indentation: 2, // 2 或 4 或 'tab'

    // 或者带选项
    indentation: [
      2,
      {
        baseIndentLevel: 1,
        indentInsideParens: "once-at-root-twice-in-block",
      },
    ],
  },
};
```

**影响对比**：

```css
/* indentation: 2 */
.selector {
  ··property: value; /* ✅ 通过（2 个空格）*/
  ····property: value; /* ❌ 错误：应该是 2 个空格 */
}

/* indentation: 4 */
.selector {
  ····property: value; /* ✅ 通过（4 个空格）*/
  ··property: value; /* ❌ 错误：应该是 4 个空格 */
}
```

#### string-quotes

**作用**：指定字符串引号。

```javascript
module.exports = {
  rules: {
    "string-quotes": "single", // 'single' 或 'double'
  },
};
```

**影响对比**：

```css
/* string-quotes: 'single' */
.selector {
  content: "hello"; /* ❌ 错误：应该使用单引号 */
  content: "hello"; /* ✅ 通过 */
}

/* string-quotes: 'double' */
.selector {
  content: "hello"; /* ❌ 错误：应该使用双引号 */
  content: "hello"; /* ✅ 通过 */
}
```

### 2.7 其他重要规则

#### no-descending-specificity

**作用**：禁止低优先级的选择器出现在高优先级之后。

```javascript
module.exports = {
  rules: {
    "no-descending-specificity": true,
  },
};
```

**影响对比**：

```css
/* ❌ 错误：.class 比 #id .class 优先级低，但出现在后面 */
#id .class {
  color: red;
}
.class {
  color: blue; /* 这个规则永远不会生效 */
}

/* ✅ 通过：优先级从低到高排列 */
.class {
  color: blue;
}
#id .class {
  color: red;
}
```

#### declaration-block-no-duplicate-properties

**作用**：禁止重复的属性。

```javascript
module.exports = {
  rules: {
    "declaration-block-no-duplicate-properties": true,
  },
};
```

**影响对比**：

```css
.selector {
  color: red;
  color: blue; /* ❌ 错误：重复的 color 属性 */
}

/* ✅ 通过 */
.selector {
  color: red;
}
```

## 三、完整推荐配置

### 3.1 纯 CSS 项目

```javascript
// .stylelintrc.js
module.exports = {
  extends: ["stylelint-config-standard"],

  rules: {
    // 颜色
    "color-hex-case": "lower",
    "color-hex-length": "short",

    // 字体
    "font-family-name-quotes": "always-where-required",

    // 数值
    "number-leading-zero": "always",
    "number-no-trailing-zeros": true,

    // 字符串
    "string-quotes": "single",

    // 缩进
    indentation: 2,

    // 选择器
    "selector-class-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$",
    "selector-max-id": 0,

    // 其他
    "max-nesting-depth": 3,
    "no-descending-specificity": null, // 关闭，因为有时需要覆盖
  },
};
```

### 3.2 SCSS 项目

```javascript
// .stylelintrc.js
module.exports = {
  extends: [
    "stylelint-config-standard-scss",
    "stylelint-config-prettier", // 与 Prettier 集成
  ],

  plugins: ["stylelint-order"],

  rules: {
    // CSS 规则
    "color-hex-case": "lower",
    "color-hex-length": "short",
    indentation: 2,
    "string-quotes": "single",
    "selector-class-pattern":
      "^[a-z][a-z0-9]*(-[a-z0-9]+)*(__[a-z0-9]+(-[a-z0-9]+)*)?(--[a-z0-9]+(-[a-z0-9]+)*)?$",

    // SCSS 规则
    "scss/at-rule-no-unknown": true,
    "scss/dollar-variable-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$",
    "scss/at-extend-no-missing-placeholder": true,
    "scss/selector-no-redundant-nesting-selector": true,

    // 属性排序
    "order/properties-alphabetical-order": true,
  },
};
```

### 3.3 Vue 3 项目

```javascript
// .stylelintrc.js
module.exports = {
  extends: [
    "stylelint-config-standard-scss",
    "stylelint-config-recommended-vue",
    "stylelint-config-prettier",
  ],

  plugins: ["stylelint-order"],

  overrides: [
    {
      files: ["*.vue", "**/*.vue"],
      customSyntax: "postcss-html",
    },
    {
      files: ["*.scss", "**/*.scss"],
      customSyntax: "postcss-scss",
    },
  ],

  rules: {
    // 颜色
    "color-hex-case": "lower",
    "color-hex-length": "short",

    // 字体
    "font-family-name-quotes": "always-where-required",

    // 字符串
    "string-quotes": "single",

    // 缩进
    indentation: 2,

    // 选择器
    "selector-class-pattern": null, // Vue 中组件名称可能不符合规范
    "selector-pseudo-class-no-unknown": [
      true,
      {
        ignorePseudoClasses: ["deep", "global"], // Vue 特殊选择器
      },
    ],
    "selector-pseudo-element-no-unknown": [
      true,
      {
        ignorePseudoElements: ["v-deep"], // Vue 2 特殊选择器
      },
    ],

    // SCSS 规则
    "scss/at-rule-no-unknown": true,
    "scss/dollar-variable-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*$",

    // 属性排序
    "order/properties-order": [
      // 定位
      "position",
      "top",
      "right",
      "bottom",
      "left",
      "z-index",

      // 盒模型
      "display",
      "flex",
      "flex-direction",
      "flex-wrap",
      "justify-content",
      "align-items",
      "width",
      "height",
      "margin",
      "padding",
      "border",

      // 字体
      "font-family",
      "font-size",
      "font-weight",
      "line-height",
      "color",

      // 背景
      "background",
      "background-color",
      "background-image",

      // 其他
      "opacity",
      "cursor",
      "transition",
      "transform",
    ],
  },
};
```

### 3.4 React 项目（CSS Modules）

```javascript
// .stylelintrc.js
module.exports = {
  extends: ["stylelint-config-standard", "stylelint-config-prettier"],

  plugins: ["stylelint-order"],

  rules: {
    // 颜色
    "color-hex-case": "lower",
    "color-hex-length": "short",

    // 字符串
    "string-quotes": "single",

    // 缩进
    indentation: 2,

    // 选择器（CSS Modules 使用 camelCase）
    "selector-class-pattern": "^[a-z][a-zA-Z0-9]+$",

    // 属性排序
    "order/properties-alphabetical-order": true,

    // CSS Modules 特定
    "selector-pseudo-class-no-unknown": [
      true,
      {
        ignorePseudoClasses: ["global", "local"], // CSS Modules 伪类
      },
    ],
  },
};
```

### 3.5 包含属性排序的完整配置

```javascript
// .stylelintrc.js
module.exports = {
  extends: ["stylelint-config-standard-scss", "stylelint-config-prettier"],

  plugins: ["stylelint-order"],

  rules: {
    // 基础规则
    "color-hex-case": "lower",
    "color-hex-length": "short",
    "string-quotes": "single",
    indentation: 2,

    // 属性排序（按类型分组）
    "order/properties-order": [
      {
        groupName: "special",
        emptyLineBefore: "never",
        properties: ["composes", "@import", "@extend", "@mixin"],
      },
      {
        groupName: "positioning",
        emptyLineBefore: "never",
        properties: ["position", "top", "right", "bottom", "left", "z-index"],
      },
      {
        groupName: "boxModel",
        emptyLineBefore: "never",
        properties: [
          "display",
          "flex",
          "flex-direction",
          "flex-wrap",
          "justify-content",
          "align-items",
          "width",
          "min-width",
          "max-width",
          "height",
          "min-height",
          "max-height",
          "margin",
          "margin-top",
          "margin-right",
          "margin-bottom",
          "margin-left",
          "padding",
          "padding-top",
          "padding-right",
          "padding-bottom",
          "padding-left",
          "overflow",
          "overflow-x",
          "overflow-y",
        ],
      },
      {
        groupName: "typography",
        emptyLineBefore: "never",
        properties: [
          "font",
          "font-family",
          "font-size",
          "font-weight",
          "font-style",
          "line-height",
          "letter-spacing",
          "text-align",
          "text-decoration",
          "text-transform",
          "white-space",
          "word-break",
          "word-wrap",
          "color",
        ],
      },
      {
        groupName: "visual",
        emptyLineBefore: "never",
        properties: [
          "background",
          "background-color",
          "background-image",
          "background-repeat",
          "background-position",
          "background-size",
          "border",
          "border-radius",
          "box-shadow",
          "opacity",
        ],
      },
      {
        groupName: "animation",
        emptyLineBefore: "never",
        properties: [
          "transition",
          "transition-property",
          "transition-duration",
          "transition-timing-function",
          "animation",
          "transform",
        ],
      },
      {
        groupName: "misc",
        emptyLineBefore: "never",
        properties: ["cursor", "pointer-events", "user-select"],
      },
    ],
  },
};
```

## 四、忽略文件

### 4.1 .stylelintignore

创建 `.stylelintignore` 文件：

```
# 依赖
node_modules/

# 构建产物
dist/
build/
public/

# 压缩文件
**/*.min.css

# 第三方库
vendor/
lib/

# 自动生成的文件
**/*.generated.css
```

### 4.2 配置文件中忽略

```javascript
// .stylelintrc.js
module.exports = {
  ignoreFiles: [
    "node_modules/**",
    "dist/**",
    "build/**",
    "**/*.min.css",
    "vendor/**",
  ],
};
```

### 4.3 在文件中忽略特定代码

```css
/* stylelint-disable */
.selector {
  colro: red; /* 不会报错 */
}
/* stylelint-enable */

/* 忽略下一行 */
/* stylelint-disable-next-line */
.selector {
  colro: red;
}

/* 忽略特定规则 */
/* stylelint-disable color-hex-case */
.selector {
  color: #fff;
}
/* stylelint-enable color-hex-case */

/* 忽略整个文件 */
/* stylelint-disable */
```

## 五、与其他工具集成

### 5.1 与 Prettier 集成

**安装**：

```bash
npm install --save-dev stylelint-config-prettier
```

**配置**：

```javascript
// .stylelintrc.js
module.exports = {
  extends: [
    "stylelint-config-standard",
    "stylelint-config-prettier", // 必须放在最后
  ],
};
```

**Prettier 配置**：

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "endOfLine": "lf"
}
```

### 5.2 与 Git Hooks 集成（Husky + lint-staged）

**安装**：

```bash
npm install --save-dev husky lint-staged
npx husky init
```

**配置**：

```json
// package.json
{
  "scripts": {
    "prepare": "husky",
    "lint:css": "stylelint \"**/*.{css,scss,vue}\"",
    "lint:css:fix": "stylelint \"**/*.{css,scss,vue}\" --fix"
  },
  "lint-staged": {
    "*.{css,scss}": ["stylelint --fix", "prettier --write"],
    "*.vue": ["stylelint --fix", "eslint --fix", "prettier --write"]
  }
}
```

**.husky/pre-commit**：

```bash
#!/usr/bin/env sh
npx lint-staged
```

### 5.3 与 VSCode 集成

**安装扩展**：

1. 在 VSCode 中搜索并安装 `Stylelint` 扩展

**配置**：

```json
// .vscode/settings.json
{
  // 启用 Stylelint
  "stylelint.enable": true,

  // 验证的文件类型
  "stylelint.validate": ["css", "scss", "sass", "less", "vue"],

  // 保存时自动修复
  "editor.codeActionsOnSave": {
    "source.fixAll.stylelint": "explicit"
  },

  // 禁用 VSCode 内置的 CSS 验证（避免冲突）
  "css.validate": false,
  "scss.validate": false,
  "less.validate": false
}
```

### 5.4 与 CI/CD 集成

**GitHub Actions**：

```yaml
# .github/workflows/lint-css.yml
name: Lint CSS

on: [push, pull_request]

jobs:
  stylelint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - run: npm ci

      - name: Run Stylelint
        run: npm run lint:css
```

**GitLab CI**：

```yaml
# .gitlab-ci.yml
lint-css:
  stage: test
  image: node:18
  before_script:
    - npm ci
  script:
    - npm run lint:css
```

## 六、常见问题和最佳实践

### 6.1 Stylelint vs Prettier vs ESLint

**三者的区别**：

```
Stylelint：
- CSS/SCSS 代码检查工具
- 检查 CSS 语法错误、代码质量和风格
- 可以自动修复部分问题
- 专注于样式文件

Prettier：
- 代码格式化工具
- 统一代码格式（缩进、换行、引号等）
- 支持多种语言（JS、CSS、HTML 等）
- 只关注格式，不关注代码质量

ESLint：
- JavaScript 代码检查工具
- 检查 JS 语法错误、代码质量和风格
- 可以自动修复部分问题
- 专注于 JavaScript 文件
```

**推荐配合使用**：

```javascript
// .stylelintrc.js（CSS 代码质量）
module.exports = {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-prettier'  // 禁用与 Prettier 冲突的规则
  ]
};

// .prettierrc（代码格式）
{
  "singleQuote": true,
  "semi": true
}

// .eslintrc.js（JS 代码质量）
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:prettier/recommended'
  ]
};
```

### 6.2 配置不生效的排查

**问题 1：找不到配置文件**

```bash
# 确保配置文件在项目根目录
ls -la | grep stylelint

# 应该看到以下文件之一：
# .stylelintrc
# .stylelintrc.json
# .stylelintrc.js
# stylelint.config.js
```

**问题 2：配置文件语法错误**

```javascript
// ❌ 错误：拼写错误
module.exports = {
  extend: ["stylelint-config-standard"], // 应该是 extends
};

// ✅ 正确
module.exports = {
  extends: ["stylelint-config-standard"],
};
```

**问题 3：缺少依赖**

```bash
# 检查是否安装了共享配置
npm ls stylelint-config-standard

# 如果没有，安装它
npm install --save-dev stylelint-config-standard
```

**问题 4：VSCode 扩展问题**

```json
// settings.json
{
  // 确保启用了 Stylelint
  "stylelint.enable": true,

  // 确保包含了正确的文件类型
  "stylelint.validate": ["css", "scss", "vue"],

  // 禁用内置的 CSS 验证
  "css.validate": false
}
```

**问题 5：缓存问题**

```bash
# 清除 Stylelint 缓存
npx stylelint --清除缓存

# 或者手动删除缓存目录
rm -rf node_modules/.cache/stylelint
```

### 6.3 常见错误和解决方案

**1. Unknown rule**

```bash
# 错误信息
Unknown rule "color-hex-case"

# 原因：规则名称拼写错误或规则不存在
# 解决：检查规则名称是否正确
```

**2. Cannot find module 'stylelint-config-standard'**

```bash
# 原因：缺少共享配置包
# 解决：安装对应的包
npm install --save-dev stylelint-config-standard
```

**3. Unexpected unknown pseudo-class selector ":deep"**

```javascript
// 原因：Vue 3 的 :deep 伪类选择器不被识别
// 解决：在配置中忽略
module.exports = {
  rules: {
    "selector-pseudo-class-no-unknown": [
      true,
      {
        ignorePseudoClasses: ["deep", "global"],
      },
    ],
  },
};
```

**4. Expected indentation of 2 spaces**

```css
/* 原因：缩进不正确 */
.selector {
  ····color: red; /* 使用了 4 个空格 */
}

/* 解决：使用 --fix 自动修复 */
```

```bash
npx stylelint "**/*.css" --fix
```

### 6.4 最佳实践

**1. 从宽松开始，逐步严格**

```javascript
// 第一步：使用标准配置
module.exports = {
  extends: ["stylelint-config-standard"],
};

// 第二步：添加常用规则
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "color-hex-case": "lower",
    indentation: 2,
  },
};

// 第三步：添加更严格的规则
module.exports = {
  extends: ["stylelint-config-standard"],
  rules: {
    "color-hex-case": "lower",
    indentation: 2,
    "selector-max-id": 0,
    "max-nesting-depth": 3,
  },
};
```

**2. 提交到版本控制**

```bash
git add .stylelintrc.js .stylelintignore
git commit -m "chore: 添加 Stylelint 配置"
```

**3. 在 README 中说明**

````markdown
## 开发规范

### CSS/SCSS 代码检查

本项目使用 Stylelint 进行 CSS 代码检查。

```bash
# 检查所有样式文件
npm run lint:css

# 自动修复问题
npm run lint:css:fix
```
````

VSCode 用户请安装 Stylelint 扩展，保存时自动修复。

````

**4. 配置 package.json 脚本**

```json
{
  "scripts": {
    "lint:css": "stylelint \"**/*.{css,scss,vue}\"",
    "lint:css:fix": "stylelint \"**/*.{css,scss,vue}\" --fix",
    "lint:css:cache": "stylelint \"**/*.{css,scss,vue}\" --cache"
  }
}
````

**5. 团队协作**

```
1. 所有成员安装 VSCode Stylelint 扩展
2. 统一使用项目的 Stylelint 配置
3. 提交前自动检查（Git hooks）
4. CI/CD 中强制检查
5. 定期 review 和更新规则
```

## 七、常用命令

### 检查文件

```bash
# 检查单个文件
npx stylelint "src/style.css"

# 检查多个文件
npx stylelint "src/**/*.css"

# 检查多种文件类型
npx stylelint "**/*.{css,scss,vue}"
```

### 自动修复

```bash
# 自动修复问题
npx stylelint "**/*.css" --fix

# 修复并显示修复了什么
npx stylelint "**/*.css" --fix --formatter verbose
```

### 使用缓存

```bash
# 使用缓存（加快后续检查速度）
npx stylelint "**/*.css" --cache

# 指定缓存位置
npx stylelint "**/*.css" --cache --cache-location "node_modules/.cache/stylelint"
```

### 指定配置文件

```bash
# 使用特定的配置文件
npx stylelint "**/*.css" --config .stylelintrc.prod.js

# 不使用配置文件
npx stylelint "**/*.css" --config-basedir false
```

### 输出格式

```bash
# 默认格式
npx stylelint "**/*.css"

# JSON 格式
npx stylelint "**/*.css" --formatter json

# Verbose 格式（详细）
npx stylelint "**/*.css" --formatter verbose

# 输出到文件
npx stylelint "**/*.css" --output-file report.txt
```

### 其他有用命令

```bash
# 打印有效配置
npx stylelint --print-config src/style.css

# 忽略特定模式
npx stylelint "**/*.css" --ignore-pattern "dist/**"

# 只报告错误（忽略警告）
npx stylelint "**/*.css" --quiet

# 设置最大警告数
npx stylelint "**/*.css" --max-warnings 0
```

## 八、总结

### 必须配置的选项

```javascript
module.exports = {
  // 1. 继承标准配置
  extends: ["stylelint-config-standard"],

  // 2. 常用规则
  rules: {
    "color-hex-case": "lower",
    "color-hex-length": "short",
    indentation: 2,
    "string-quotes": "single",
  },
};
```

### 推荐工作流

1. 安装 Stylelint 和配置
2. 配置 VSCode 扩展
3. 配置 Git hooks（自动检查）
4. 配置 CI/CD（强制检查）
5. 团队培训和规范

### 学习建议

1. 从 `stylelint-config-standard` 开始
2. 理解每个规则的作用
3. 根据团队需求调整规则
4. 使用 `--fix` 自动修复
5. 配合 Prettier 使用

## 参考资源

- [Stylelint 官方文档](https://stylelint.io/)
- [Stylelint 规则列表](https://stylelint.io/user-guide/rules/list)
- [stylelint-config-standard](https://github.com/stylelint/stylelint-config-standard)
- [stylelint-config-standard-scss](https://github.com/stylelint-scss/stylelint-config-standard-scss)
- [Awesome Stylelint](https://github.com/stylelint/awesome-stylelint)
