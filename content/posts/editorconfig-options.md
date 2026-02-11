---
title: "editorconfig 配置选项"
date: 2025-11-27
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 EditorConfig

[EditorConfig](https://editorconfig.org/) 是一个帮助开发者在不同编辑器和 IDE 之间保持一致代码风格的工具。它包含：

- 📝 **统一代码风格**：定义缩进、换行符、字符编码等基础格式
- 🔧 **跨编辑器支持**：VSCode、WebStorm、Vim、Sublime Text 等都支持
- 👥 **团队协作**：确保团队成员使用相同的编辑器配置
- 🎯 **简单配置**：使用 `.editorconfig` 文件，易读易维护
- 🔄 **版本控制友好**：配置文件可以提交到版本控制系统

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

:::tip 版本说明
本文档基于 **EditorConfig 规范 v0.17.2** 编写，适用于所有支持 EditorConfig 的编辑器和 IDE。

**当前规范版本**：

- **EditorConfig 规范**: v0.17.2 (Copyright 2019-2024 by EditorConfig Team)
- **官方网站**: [editorconfig.org](https://editorconfig.org/)
- **规范文档**: [spec.editorconfig.org](https://spec.editorconfig.org/)

**规范更新历史**：

- **v0.17.2** (当前版本)：更新文件格式定义
- **v0.15.0**：重要变更 - 分号 (;) 和井号 (#) 只能在行首作为注释标记
  - 修复了值中包含这些字符时的解析混淆问题
- **v0.14.0 及更早**：早期规范版本

**主流编辑器支持**：

- ✅ **Visual Studio Code** - 原生支持（需要扩展）
- ✅ **JetBrains IDEs** (WebStorm, IntelliJ IDEA 等) - 原生支持
- ✅ **Sublime Text** - 通过插件支持
- ✅ **Vim** - 通过插件支持
- ✅ **Atom** - 通过插件支持
- ✅ **Emacs** - 通过插件支持
  :::

:::warning 注意事项

- **注释规则变更**：v0.15.0+ 中，`;` 和 `#` 只能在行首作为注释，不能在行中间
- **大小写敏感**：配置文件名必须是小写的 `.editorconfig`
- **作用范围**：配置从当前目录向上查找，直到找到 `root = true` 或到达文件系统根目录
- **插件版本**：编辑器插件版本号独立于规范版本号
- **属性优先级**：较近的 `.editorconfig` 文件的配置会覆盖较远的配置
  :::

## 为什么需要 EditorConfig

### 传统问题

不同编辑器默认配置不同，导致代码风格混乱：

```
团队成员 A（使用 VSCode）：
- 使用 2 个空格缩进
- 使用 LF 换行符
- UTF-8 编码

团队成员 B（使用 WebStorm）：
- 使用 4 个空格缩进
- 使用 CRLF 换行符
- UTF-8 编码

团队成员 C（使用 Sublime Text）：
- 使用 Tab 缩进
- 使用 LF 换行符
- 保留尾随空格
```

**结果**：

- ❌ Git diff 显示大量无意义的空格/换行符变更
- ❌ 代码审查时难以分辨实质性修改
- ❌ 代码风格不统一，影响可读性
- ❌ 合并冲突增多

### 使用 EditorConfig 后

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

**结果**：

- ✅ 所有编辑器自动使用相同配置
- ✅ Git diff 只显示实质性修改
- ✅ 代码风格统一
- ✅ 减少不必要的冲突

## 配置文件

### 文件名和位置

**文件名**：`.editorconfig`（全小写）

**查找规则**：

1. 从当前文件所在目录开始查找 `.editorconfig`
2. 向上递归查找父目录
3. 遇到 `root = true` 或到达根目录时停止

**示例目录结构**：

```
project/
├── .editorconfig          # root = true
├── src/
│   ├── .editorconfig      # 特定配置（可选）
│   └── index.js
└── docs/
    └── README.md
```

**配置优先级**：

- 距离文件最近的配置优先级最高
- 同一文件中，后面的规则覆盖前面的规则

### Windows 用户注意

在 Windows 资源管理器中创建 `.editorconfig`：

1. 创建名为 `.editorconfig.` 的文件（注意末尾的点）
2. Windows 会自动重命名为 `.editorconfig`

或者使用命令行：

```bash
# PowerShell
New-Item .editorconfig -Type File

# CMD
type nul > .editorconfig
```

## 文件格式

EditorConfig 使用类似 INI 的格式：

```ini
# 注释使用 # 或 ;
; 这也是注释

# 顶级配置
root = true

# 所有文件
[*]
property = value

# 匹配特定文件
[*.js]
property = value

# 使用大括号匹配多个扩展名
[*.{js,ts,jsx,tsx}]
property = value

# 匹配特定路径
[lib/**.js]
property = value

# 匹配确切的文件
[{package.json,.travis.yml}]
property = value
```

### 通配符模式

| 模式           | 说明                                 | 示例                                                    |
| -------------- | ------------------------------------ | ------------------------------------------------------- |
| `*`            | 匹配任意字符串（不含路径分隔符 `/`） | `*.js` 匹配 `file.js`，不匹配 `path/file.js`            |
| `**`           | 匹配任意字符串（含路径分隔符）       | `lib/**.js` 匹配 `lib/file.js` 和 `lib/path/file.js`    |
| `?`            | 匹配任意单个字符                     | `file?.js` 匹配 `file1.js`，不匹配 `file10.js`          |
| `[name]`       | 匹配 name 中的任意单个字符           | `file[01].js` 匹配 `file0.js` 和 `file1.js`             |
| `[!name]`      | 匹配不在 name 中的任意单个字符       | `file[!01].js` 匹配 `file2.js`，不匹配 `file0.js`       |
| `{s1,s2,s3}`   | 匹配任意给定的字符串                 | `{*.js,*.ts}` 匹配 `.js` 和 `.ts` 文件                  |
| `{num1..num2}` | 匹配 num1 到 num2 之间的整数         | `file{1..3}.js` 匹配 `file1.js`、`file2.js`、`file3.js` |

**示例**：

```ini
# 匹配所有 .js 文件
[*.js]
indent_size = 2

# 匹配所有目录下的 .js 文件
[**.js]
indent_size = 2

# 匹配 lib 目录下所有 .js 文件
[lib/**.js]
indent_size = 2

# 匹配多种文件类型
[*.{js,jsx,ts,tsx,vue}]
indent_size = 2

# 匹配特定文件
[{package.json,.travis.yml,tsconfig.json}]
indent_size = 2

# 匹配 Makefile 和 makefile
[{Makefile,makefile}]
indent_style = tab
```

## 核心配置属性

### 1. indent_style

**作用**：设置缩进风格。

**可选值**：

- `space`：使用空格
- `tab`：使用制表符 Tab

```ini
[*]
indent_style = space
```

**影响对比**：

```javascript
// indent_style = space
function hello() {
··return 'world';  // 2 个空格
}

// indent_style = tab
function hello() {
→	return 'world';  // 1 个 Tab
}
```

**适用场景**：

- `space`：大多数现代项目（JavaScript、TypeScript、Python、HTML、CSS）
- `tab`：Makefile（必须）、Go（推荐）、某些 C/C++ 项目

### 2. indent_size

**作用**：设置缩进大小（列数）。

**可选值**：整数（通常是 2 或 4）

```ini
[*]
indent_size = 2

[*.py]
indent_size = 4
```

**影响对比**：

```javascript
// indent_size = 2
function hello() {
··return {
····name: 'world'
··};
}

// indent_size = 4
function hello() {
····return {
········name: 'world'
····};
}
```

**推荐值**：

- JavaScript/TypeScript/Vue/React：`2`
- Python：`4`（PEP 8 标准）
- Java：`4`
- HTML/CSS：`2`

**特殊值**：`tab`

```ini
[*]
indent_style = space
indent_size = tab  # 使用 tab_width 的值
```

### 3. tab_width

**作用**：设置 Tab 字符的显示宽度。

**默认值**：`indent_size` 的值

```ini
[*]
tab_width = 4
```

**影响对比**：

```javascript
// tab_width = 2
function hello() {
→	return 'world';  // Tab 显示为 2 个空格宽度
}

// tab_width = 4
function hello() {
→		return 'world';  // Tab 显示为 4 个空格宽度
}
```

**使用场景**：

- 当 `indent_style = tab` 时，设置 Tab 的显示宽度
- 通常不需要设置，除非与 `indent_size` 不同

```ini
# 使用 Tab 缩进，但显示为 4 个空格宽度
[Makefile]
indent_style = tab
tab_width = 4
```

### 4. end_of_line

**作用**：设置换行符格式。

**可选值**：

- `lf`：Unix/Linux/macOS 换行符（`\n`）
- `crlf`：Windows 换行符（`\r\n`）
- `cr`：旧版 Mac 换行符（`\r`，很少使用）

```ini
[*]
end_of_line = lf
```

**影响对比**：

```
# end_of_line = lf（推荐）
function hello() {\n
··return 'world';\n
}\n

# end_of_line = crlf（Windows 默认）
function hello() {\r\n
··return 'world';\r\n
}\r\n
```

**推荐配置**：

```ini
# 推荐：统一使用 lf
[*]
end_of_line = lf

# Git 配置（配合使用）
# .gitattributes
* text=auto eol=lf
```

**为什么推荐 lf**：

- ✅ Unix/Linux/macOS 原生支持
- ✅ Git 默认推荐
- ✅ 避免跨平台协作时的换行符冲突
- ✅ 大多数现代工具支持

**特殊情况**：

```ini
# Windows 批处理脚本必须使用 crlf
[*.{bat,cmd}]
end_of_line = crlf

# Shell 脚本使用 lf
[*.{sh,bash}]
end_of_line = lf
```

### 5. charset

**作用**：设置文件字符编码。

**可选值**：

- `utf-8`：UTF-8 编码（推荐）
- `utf-8-bom`：带 BOM 的 UTF-8
- `utf-16be`：UTF-16 大端序
- `utf-16le`：UTF-16 小端序
- `latin1`：ISO-8859-1

```ini
[*]
charset = utf-8
```

**影响对比**：

```
# charset = utf-8（推荐）
- 支持所有语言字符
- 无 BOM（字节顺序标记）
- 兼容 ASCII
- 文件更小

# charset = utf-8-bom
- 文件开头有 BOM（EF BB BF）
- 某些旧工具需要
- 可能导致问题（如 PHP）

# charset = latin1
- 只支持西欧字符
- 不支持中文、日文等
- 不推荐使用
```

**推荐配置**：

```ini
# 现代项目：统一使用 utf-8
[*]
charset = utf-8

# 特殊情况：某些 Windows 工具需要 BOM
[*.txt]
charset = utf-8-bom
```

### 6. trim_trailing_whitespace

**作用**：删除行尾的空白字符。

**可选值**：

- `true`：删除行尾空白
- `false`：保留行尾空白

```ini
[*]
trim_trailing_whitespace = true
```

**影响对比**：

```javascript
// trim_trailing_whitespace = true
function hello() {
··return 'world';
}
// 行尾没有多余空格

// trim_trailing_whitespace = false
function hello() {····
··return 'world';····
}····
// 行尾有多余空格（用 · 表示）
```

**为什么推荐 true**：

- ✅ 避免无意义的 Git diff
- ✅ 减少文件大小
- ✅ 符合代码规范
- ✅ 避免某些编辑器的警告

**特殊情况**：

```ini
# Markdown 文件：行尾两个空格表示换行
[*.md]
trim_trailing_whitespace = false

# 其他文件：删除行尾空格
[*]
trim_trailing_whitespace = true
```

### 7. insert_final_newline

**作用**：确保文件末尾有换行符。

**可选值**：

- `true`：文件末尾添加换行符
- `false`：文件末尾不添加换行符

```ini
[*]
insert_final_newline = true
```

**影响对比**：

```javascript
// insert_final_newline = true
function hello() {
··return 'world';
}
␊  // 文件末尾有换行符

// insert_final_newline = false
function hello() {
··return 'world';
}  // 文件末尾没有换行符（可能显示警告）
```

**为什么推荐 true**：

- ✅ POSIX 标准要求文本文件末尾有换行符
- ✅ 避免某些工具的警告
- ✅ 更好的 Git diff 显示
- ✅ 符合 Unix 传统

**示例**：

```bash
# 没有末尾换行符的文件
$ cat file.js
function hello() { return 'world'; }%  # % 表示没有换行符

# 有末尾换行符的文件
$ cat file.js
function hello() { return 'world'; }
$  # 正常的命令提示符位置
```

### 8. root

**作用**：标识这是根配置文件，停止向上查找。

**可选值**：

- `true`：这是根配置
- `false` 或不设置：继续向上查找

```ini
# 顶级 .editorconfig
root = true

[*]
indent_size = 2
```

**影响对比**：

```
# 没有 root = true
project/
├── .editorconfig       # 会继续向上查找
├── src/
│   └── index.js
父目录/
└── .editorconfig       # 也会被应用

# 有 root = true
project/
├── .editorconfig       # root = true，停止向上查找
└── src/
    └── index.js
父目录/
└── .editorconfig       # 不会被应用
```

**推荐配置**：

```ini
# 项目根目录的 .editorconfig
root = true  # 总是在项目根目录设置

[*]
# 其他配置...
```

### 9. max_line_length

**作用**：设置单行最大长度（部分编辑器支持）。

**可选值**：整数或 `off`

```ini
[*]
max_line_length = 100

[*.md]
max_line_length = off
```

**注意**：

- ⚠️ 不是所有编辑器都支持
- ⚠️ 不会自动换行，只是提示
- ⚠️ 建议配合 Prettier/ESLint 使用

## 高级属性（非标准/特定编辑器）

以下属性不是 EditorConfig 官方规范的一部分，但被某些编辑器支持：

### 1. quote_type（JetBrains IDEs）

**作用**：设置引号类型（JetBrains 系列 IDE 专用）。

**可选值**：

- `single`：单引号
- `double`：双引号

```ini
[*.{js,ts}]
quote_type = single
```

### 2. spaces_around_operators（JetBrains IDEs）

**作用**：操作符周围是否添加空格。

**可选值**：`true` / `false`

```ini
[*.{js,ts}]
spaces_around_operators = true
```

### 3. spaces_around_brackets（JetBrains IDEs）

**作用**：括号周围是否添加空格。

**可选值**：`none` / `inside` / `outside` / `both`

```ini
[*.{js,ts}]
spaces_around_brackets = none
```

**注意**：

- ⚠️ 这些属性仅被特定编辑器支持
- ⚠️ 不建议在通用项目中使用
- ⚠️ 推荐使用 Prettier/ESLint 处理这类格式化

## 完整推荐配置

### 1. 通用项目配置（推荐）

```ini
# .editorconfig
root = true

# 所有文件的默认配置
[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# Markdown 文件：保留行尾空格（用于换行）
[*.md]
trim_trailing_whitespace = false

# Makefile：必须使用 Tab
[Makefile]
indent_style = tab

# Python 文件：使用 4 个空格
[*.py]
indent_size = 4

# Go 文件：使用 Tab
[*.go]
indent_style = tab

# 配置文件：使用 2 个空格
[*.{json,yml,yaml,toml}]
indent_size = 2

# Windows 批处理：使用 CRLF
[*.{bat,cmd,ps1}]
end_of_line = crlf
```

### 2. 前端项目配置（JavaScript/TypeScript）

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# JavaScript/TypeScript 文件
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_size = 2

# Vue 文件
[*.vue]
indent_size = 2

# HTML 文件
[*.{html,htm}]
indent_size = 2

# CSS/SCSS/Less 文件
[*.{css,scss,sass,less,styl}]
indent_size = 2

# JSON 文件
[*.json]
indent_size = 2
insert_final_newline = false  # JSON 文件通常不需要末尾换行

# YAML 文件
[*.{yml,yaml}]
indent_size = 2

# Markdown 文件
[*.md]
trim_trailing_whitespace = false
max_line_length = off

# 配置文件
[{package.json,.prettierrc,.eslintrc,.babelrc}]
indent_size = 2

# Makefile
[Makefile]
indent_style = tab
```

### 3. Vue 3 项目配置

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 100

# Vue 单文件组件
[*.vue]
indent_size = 2

# JavaScript/TypeScript
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_size = 2

# CSS 预处理器
[*.{css,scss,sass,less,postcss}]
indent_size = 2

# HTML 模板
[*.html]
indent_size = 2

# 配置文件
[*.{json,jsonc,json5}]
indent_size = 2

[*.{yml,yaml}]
indent_size = 2

# Vite 配置
[vite.config.{js,ts}]
indent_size = 2

# 环境变量文件
[.env*]
insert_final_newline = false

# Markdown 文档
[*.md]
trim_trailing_whitespace = false
max_line_length = off
```

### 4. React 项目配置

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# React 组件
[*.{js,jsx,ts,tsx}]
indent_size = 2

# CSS Modules
[*.module.{css,scss,sass}]
indent_size = 2

# 样式文件
[*.{css,scss,sass,less}]
indent_size = 2

# JSON 配置
[*.{json,jsonc}]
indent_size = 2

# YAML 配置
[*.{yml,yaml}]
indent_size = 2

# TypeScript 配置
[tsconfig*.json]
indent_size = 2

# package.json
[package.json]
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false
max_line_length = off
```

### 5. Node.js 后端项目配置

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# JavaScript/TypeScript
[*.{js,mjs,cjs,ts}]
indent_size = 2

# JSON 配置
[*.json]
indent_size = 2

# YAML 配置（Docker、CI/CD）
[*.{yml,yaml}]
indent_size = 2

# 环境变量
[.env*]
insert_final_newline = false
trim_trailing_whitespace = false

# Shell 脚本
[*.{sh,bash}]
indent_size = 2
end_of_line = lf

# Dockerfile
[Dockerfile*]
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false

# SQL 文件
[*.sql]
indent_size = 2
```

### 6. Python 项目配置

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 88  # Black 格式化器的默认值

# Python 文件（PEP 8）
[*.py]
indent_size = 4
max_line_length = 88

# Python 配置文件
[*.{cfg,ini}]
indent_size = 4

# YAML（如 .gitlab-ci.yml）
[*.{yml,yaml}]
indent_size = 2

# TOML（如 pyproject.toml）
[*.toml]
indent_size = 4

# JSON
[*.json]
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false
max_line_length = off

# Makefile
[Makefile]
indent_style = tab

# Shell 脚本
[*.sh]
indent_size = 4
end_of_line = lf
```

### 7. Monorepo 项目配置

```ini
# .editorconfig（根目录）
root = true

# 全局默认配置
[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# JavaScript/TypeScript（所有包）
[*.{js,jsx,ts,tsx,mjs,cjs}]
indent_size = 2

# Vue 组件
[*.vue]
indent_size = 2

# 样式文件
[*.{css,scss,sass,less}]
indent_size = 2

# 配置文件
[*.{json,jsonc,json5}]
indent_size = 2

[*.{yml,yaml}]
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false

# Lerna/pnpm workspace 配置
[{lerna.json,pnpm-workspace.yaml}]
indent_size = 2

# 各个包可以有自己的 .editorconfig（可选）
# packages/*/
#   └── .editorconfig
```

### 8. 全栈项目配置（前后端）

```ini
# .editorconfig
root = true

# 全局默认
[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

# 前端文件
[{client,frontend,web}/**.{js,jsx,ts,tsx,vue}]
indent_size = 2

[{client,frontend,web}/**.{css,scss,sass,less}]
indent_size = 2

# 后端文件
[{server,backend,api}/**.{js,ts}]
indent_size = 2

# Python 后端
[{server,backend,api}/**.py]
indent_size = 4

# 配置文件
[*.{json,jsonc,json5}]
indent_size = 2

[*.{yml,yaml}]
indent_size = 2

# Docker
[{Dockerfile,docker-compose.yml}]
indent_size = 2

# 脚本
[*.{sh,bash}]
indent_size = 2

# Markdown
[*.md]
trim_trailing_whitespace = false
max_line_length = off
```

## 编辑器支持

### 原生支持（无需插件）

以下编辑器原生支持 EditorConfig：

- **VSCode**（Visual Studio Code）
- **WebStorm** / **PhpStorm** / **PyCharm** / **IntelliJ IDEA**
- **Vim** 8.1+
- **Neovim**
- **Sublime Text** 4
- **GitHub**（在线编辑器）
- **GitLab**（在线编辑器）
- **Xcode**
- **Visual Studio** 2017+

### 需要插件支持

- **Sublime Text 3**：安装 `EditorConfig` 插件
- **Atom**：安装 `editorconfig` 插件
- **Brackets**：安装 `brackets-editorconfig` 插件
- **Notepad++**：安装 `EditorConfigPlugin`
- **Emacs**：安装 `editorconfig-emacs` 插件

### VSCode 配置

VSCode 原生支持 EditorConfig，无需额外配置。

**验证是否生效**：

1. 打开文件
2. 查看状态栏右下角（显示缩进设置）
3. 应该显示 `.editorconfig` 配置的值

**手动触发**：

```
Ctrl+Shift+P（或 Cmd+Shift+P）
输入：Format Document
```

**与其他格式化工具配合**：

```json
// settings.json
{
  // EditorConfig 优先级高于 VSCode 设置
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",

  // 禁用自动检测缩进（使用 .editorconfig）
  "editor.detectIndentation": false
}
```

### WebStorm/IntelliJ 配置

WebStorm 原生支持，会自动读取 `.editorconfig`。

**检查是否启用**：

```
File → Settings → Editor → Code Style
☑ Enable EditorConfig support
```

**优先级**：

1. `.editorconfig`
2. IDE 代码样式设置
3. 语言默认设置

## 常见问题和最佳实践

### 1. EditorConfig vs Prettier vs ESLint

**区别**：

```
EditorConfig：
- 编辑器层面的配置
- 控制基础格式（缩进、换行符、编码等）
- 跨编辑器统一
- 实时生效（边写边应用）

Prettier：
- 代码格式化工具
- 控制代码风格（引号、分号、括号等）
- 保存时格式化
- 更强大的格式化能力

ESLint：
- 代码质量工具
- 检查代码错误和风格
- 可以自动修复部分问题
- 更注重代码质量
```

**推荐配合使用**：

```ini
# .editorconfig（基础格式）
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

```javascript
// .prettierrc（代码格式化）
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,  // 与 .editorconfig 保持一致
  "endOfLine": "lf"  // 与 .editorconfig 保持一致
}
```

```javascript
// .eslintrc.js（代码质量）
module.exports = {
  extends: [
    "eslint:recommended",
    "plugin:prettier/recommended", // 集成 Prettier
  ],
  rules: {
    indent: ["error", 2], // 与 .editorconfig 保持一致
    "linebreak-style": ["error", "unix"], // 与 .editorconfig 保持一致
  },
};
```

### 2. 配置不生效的排查

**问题 1：编辑器不支持**

```bash
# 检查编辑器是否支持 EditorConfig
# VSCode：查看扩展中是否已安装/启用

# 查看状态栏是否显示 EditorConfig 配置
```

**问题 2：文件名错误**

```bash
# ✅ 正确
.editorconfig

# ❌ 错误
editorconfig
.editorConfig
editorconfig.ini
```

**问题 3：语法错误**

```ini
# ❌ 错误：属性名拼写错误
[*]
indet_size = 2  # 应该是 indent_size

# ❌ 错误：值不合法
[*]
indent_style = spaces  # 应该是 space

# ✅ 正确
[*]
indent_size = 2
indent_style = space
```

**问题 4：匹配模式错误**

```ini
# ❌ 错误：使用反斜杠
[src\*.js]

# ✅ 正确：使用正斜杠
[src/*.js]

# ✅ 正确：匹配所有子目录
[src/**.js]
```

**问题 5：VSCode 设置冲突**

```json
// settings.json
{
  // ❌ 这会覆盖 .editorconfig
  "editor.detectIndentation": true,

  // ✅ 让 .editorconfig 优先
  "editor.detectIndentation": false
}
```

**调试方法**：

```bash
# 1. 检查文件内容
cat .editorconfig

# 2. 手动测试
# 创建新文件，查看是否应用了配置

# 3. 检查编辑器设置
# VSCode: Ctrl+Shift+P → Preferences: Open Settings (JSON)
```

### 3. 跨平台换行符问题

**问题**：Windows 使用 CRLF，Unix/Mac 使用 LF

**解决方案**：

**1. EditorConfig 统一换行符**

```ini
# .editorconfig
[*]
end_of_line = lf
```

**2. Git 配置**

```ini
# .gitattributes
* text=auto eol=lf
*.sh text eol=lf
*.bat text eol=crlf
```

**3. Git 全局配置**

```bash
# Windows 用户：签出时转换为 CRLF，提交时转换为 LF
git config --global core.autocrlf true

# Mac/Linux 用户：签出时不转换，提交时转换为 LF
git config --global core.autocrlf input

# 推荐：所有平台都使用 LF
git config --global core.autocrlf false
git config --global core.eol lf
```

**4. 修复已有文件的换行符**

```bash
# 保存所有文件
# 然后执行

# 删除 Git 缓存
git rm --cached -r .

# 重新添加所有文件（会应用 .gitattributes）
git add .

# 提交
git commit -m "chore: 统一换行符为 LF"
```

### 4. Markdown 文件特殊处理

**问题**：Markdown 中行尾两个空格表示换行

```markdown
这是第一行··
这是第二行（与上一行分开）

这是第三行
这是第四行（与上一行连在一起）
```

**解决方案**：

```ini
# .editorconfig
[*]
trim_trailing_whitespace = true

# Markdown 文件：不删除行尾空格
[*.md]
trim_trailing_whitespace = false
max_line_length = off  # 也不限制行长度
```

### 5. 最佳实践

**1. 在项目根目录添加 .editorconfig**

```ini
# .editorconfig
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 2
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

**2. 提交到版本控制**

```bash
git add .editorconfig
git commit -m "chore: 添加 EditorConfig 配置"
```

**3. 在 README 中说明**

```markdown
# 项目名称

## 开发环境设置

本项目使用 EditorConfig 统一代码风格。

### 编辑器配置

- VSCode：已内置支持
- WebStorm：已内置支持
- Sublime Text：需要安装 EditorConfig 插件
- 其他编辑器：请查看 https://editorconfig.org/

### 手动设置（如果编辑器不支持）

- 缩进：2 个空格
- 换行符：LF（Unix）
- 字符编码：UTF-8
- 文件末尾：添加换行符
- 行尾空格：删除
```

**4. 与 Git 配合**

```ini
# .gitattributes
* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
```

**5. 团队规范**

```
1. 所有成员使用支持 EditorConfig 的编辑器
2. 新加入成员先配置编辑器
3. 代码审查时检查格式是否符合规范
4. CI/CD 中检查代码格式
```

**6. 逐步迁移**

```ini
# 第一步：只配置最基础的
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true

# 第二步：添加缩进配置
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2

# 第三步：添加更多细节配置
[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true
```

## 测试配置是否生效

### 方法 1：创建测试文件

```javascript
// test.js
function hello() {
  return "world";
}
```

**保存后应该自动格式化为**：

```javascript
// test.js
function hello() {
··return 'world';
}
␊
```

### 方法 2：查看编辑器状态栏

**VSCode**：

- 右下角显示：`Spaces: 2`（表示使用 2 个空格缩进）
- 右下角显示：`LF`（表示使用 LF 换行符）
- 右下角显示：`UTF-8`（表示使用 UTF-8 编码）

**WebStorm**：

- 右下角显示：`LF`
- 右下角显示：`UTF-8`
- 右下角显示：`Spaces: 2`

### 方法 3：使用 editorconfig-checker

```bash
# 安装 editorconfig-checker
npm install -g editorconfig-checker

# 检查所有文件
editorconfig-checker

# 检查特定文件
editorconfig-checker src/index.js

# 在 package.json 中添加脚本
{
  "scripts": {
    "lint:editorconfig": "editorconfig-checker"
  }
}
```

## 总结

### EditorConfig 核心规范属性

根据 [EditorConfig 规范 v0.17.2](https://spec.editorconfig.org/)，以下是官方标准支持的属性：

**通用属性（所有编辑器应支持）**：

- `indent_style` - 缩进风格（space / tab）
- `indent_size` - 缩进大小（整数 / tab）
- `tab_width` - Tab 显示宽度（整数）
- `end_of_line` - 换行符（lf / crlf / cr）
- `charset` - 字符编码（utf-8 / utf-8-bom / latin1 / utf-16be / utf-16le）
- `trim_trailing_whitespace` - 删除行尾空格（true / false）
- `insert_final_newline` - 文件末尾换行（true / false）
- `root` - 标记根配置（true / false）

**扩展属性（部分编辑器支持）**：

- `max_line_length` - 最大行长度（整数 / off）

### 必须配置的属性

```ini
root = true

[*]
charset = utf-8            # 字符编码
indent_style = space       # 缩进风格
indent_size = 2            # 缩进大小
end_of_line = lf           # 换行符
insert_final_newline = true           # 文件末尾换行
trim_trailing_whitespace = true       # 删除行尾空格
```

### 常用特殊配置

```ini
# Markdown：保留行尾空格
[*.md]
trim_trailing_whitespace = false

# Makefile：必须使用 Tab
[Makefile]
indent_style = tab

# Python：使用 4 个空格
[*.py]
indent_size = 4

# Windows 脚本：使用 CRLF
[*.{bat,cmd}]
end_of_line = crlf
```

### 最佳实践

1. ✅ 在项目根目录创建 `.editorconfig`
2. ✅ 设置 `root = true`
3. ✅ 提交到版本控制
4. ✅ 配合 Prettier/ESLint 使用
5. ✅ 配合 `.gitattributes` 使用
6. ✅ 在团队中推广
7. ✅ 在 README 中说明

### 学习建议

1. 从简单配置开始
2. 理解每个属性的作用
3. 根据项目类型选择合适的配置
4. 确保团队成员编辑器支持
5. 配合其他工具一起使用

## 参考资源

### 官方文档

- [EditorConfig 官方网站](https://editorconfig.org/) - 主页和简介
- [EditorConfig 规范 v0.17.2](https://spec.editorconfig.org/) - 完整规范文档
- [EditorConfig GitHub](https://github.com/editorconfig/editorconfig) - 官方仓库
- [EditorConfig Wiki](https://github.com/editorconfig/editorconfig/wiki) - 社区文档
- [EditorConfig 属性列表](https://github.com/editorconfig/editorconfig/wiki/EditorConfig-Properties) - 所有支持的属性

### 编辑器插件

- [VSCode EditorConfig](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig) - Visual Studio Code 扩展
- [Sublime Text EditorConfig](https://packagecontrol.io/packages/EditorConfig) - Sublime Text 插件
- [Atom EditorConfig](https://atom.io/packages/editorconfig) - Atom 插件
- [Vim EditorConfig](https://github.com/editorconfig/editorconfig-vim) - Vim 插件
- [Emacs EditorConfig](https://github.com/editorconfig/editorconfig-emacs) - Emacs 插件

### 工具和验证

- [EditorConfig Checker](https://github.com/editorconfig-checker/editorconfig-checker) - 配置验证工具
- [EditorConfig Core](https://github.com/editorconfig/editorconfig-core-js) - JavaScript 核心库
- [EditorConfig Python](https://github.com/editorconfig/editorconfig-core-py) - Python 核心库

### 相关资源

- [Prettier 文档](https://prettier.io/) - 代码格式化工具
- [ESLint 文档](https://eslint.org/) - JavaScript 代码检查工具
- [Git 属性文档](https://git-scm.com/docs/gitattributes) - .gitattributes 配置
