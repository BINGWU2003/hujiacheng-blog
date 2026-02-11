---
title: "commitizen 配置选项"
date: 2025-11-17
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 Commitizen

[Commitizen](https://github.com/commitizen/cz-cli) 是一个命令行工具,用于规范化 Git 提交信息(commit message),帮助团队:

- 📝 **规范提交**:通过交互式命令行引导编写符合约定的提交信息
- 🔍 **易于查找**:结构化的提交信息便于查找和过滤
- 📦 **自动生成日志**:配合工具自动生成 CHANGELOG
- 🚀 **语义化版本**:支持自动化的语义化版本管理
- 🤝 **团队协作**:统一团队提交规范,提高代码审查效率

```bash
# 安装 Commitizen
npm install --save-dev commitizen

# 初始化适配器(以 cz-conventional-changelog 为例)
npx commitizen init cz-conventional-changelog --save-dev --save-exact

# 使用 Commitizen 提交代码
npx cz
# 或者使用 git cz(需要全局安装或配置脚本)
```

:::tip 版本说明
本文档基于 **Commitizen 4.x** (cz-cli) 编写，适用于 JavaScript/TypeScript 项目。

**当前版本**：

- **Commitizen (cz-cli)**: v4.3.1 (2024-09-27 发布)
- **cz-conventional-changelog**: v3.3.0 (2019 发布，5年未更新)

**注意区分两个同名项目**：

- ✅ **commitizen/cz-cli** (本文档)：Node.js 生态，用于 JavaScript/TypeScript 项目
- ⚠️ **commitizen-tools/commitizen**：Python 生态，用于 Python 项目

**主要版本历史**：

- **v4.3.1** (2024-09-27)：修复重试提交后的进程关闭问题
- **v4.3.0** (2024-01-19)：最新功能版本
- **v4.2.x** (2020-2021)：稳定版本系列
  :::

:::warning 注意事项

- `cz-conventional-changelog` 适配器已 5 年未更新（v3.3.0），但仍然可用且稳定
- 如果需要更现代的适配器，建议使用 `cz-customizable`、`@commitlint/cz-commitlint` 或 `cz-git`
- 确保 Node.js 版本 >= 14.x（Commitizen 4.x 要求）
- 本文档的配置选项主要适用于各类适配器，具体选项可能因适配器而异
  :::

**提交效果对比**:

```bash
# ❌ 传统提交(不规范)
git commit -m "fix bug"
git commit -m "update code"
git commit -m "修改了一些东西"

# ✅ 使用 Commitizen(规范化)
git cz
# 交互式选择:
# ? Select the type of change: feat
# ? What is the scope: user-auth
# ? Write a short description: add login functionality
#
# 生成提交信息:
# feat(user-auth): add login functionality
```

## 配置方式

Commitizen 支持多种配置方式:

### 1. package.json 配置(推荐)

```json
{
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

### 2. .czrc 文件

```json
{
  "path": "cz-conventional-changelog"
}
```

### 3. .czrc 配置文件（更多选项）

```json
{
  "path": "cz-conventional-changelog",
  "maxHeaderWidth": 100,
  "maxLineWidth": 100,
  "defaultType": "",
  "defaultScope": "",
  "defaultSubject": "",
  "defaultBody": "",
  "defaultIssues": "",
  "types": {
    "feat": {
      "description": "A new feature",
      "title": "Features"
    },
    "fix": {
      "description": "A bug fix",
      "title": "Bug Fixes"
    }
  }
}
```

### 4. commitizen.config.js 或 .commitizenrc.js

```javascript
module.exports = {
  path: "cz-conventional-changelog",
  maxHeaderWidth: 100,
  maxLineWidth: 100,
  defaultType: "",
  defaultScope: "",
  defaultSubject: "",
  defaultBody: "",
  defaultIssues: "",
};
```

**推荐使用** `package.json` 或 `.cz.json`,本文以 JSON 格式为例。

## 一、核心配置选项

### 1.1 path

**作用**:指定使用的适配器(adapter)。

```json
{
  "path": "cz-conventional-changelog"
}
```

**常用适配器**:

```json
{
  // 官方推荐:符合 Conventional Commits 规范
  "path": "cz-conventional-changelog"
}

{
  // 自定义适配器:支持中英文、Emoji 等
  "path": "cz-customizable"
}

{
  // Git Emoji 风格
  "path": "cz-emoji"
}

{
  // 简化版
  "path": "cz-conventional-changelog-zh"
}
```

**影响对比**:

```bash
# cz-conventional-changelog(英文)
? Select the type of change that you're committing: (Use arrow keys)
❯ feat:     A new feature
  fix:      A bug fix
  docs:     Documentation only changes

# cz-customizable(可自定义中文)
? 选择提交类型: (Use arrow keys)
❯ ✨ feat:     新功能
  🐛 fix:      修复 Bug
  📝 docs:     文档变更

# cz-emoji(Emoji 风格)
? Select the type of change you are committing: (Use arrow keys)
❯ ✨ feat:     Introducing new features
  🐛 fix:      Fixing a bug
  📝 docs:     Writing docs
```

### 1.2 maxHeaderWidth

**作用**:限制提交信息标题(header)的最大长度。

```json
{
  "maxHeaderWidth": 100
}
```

**默认值**:`100`

**影响对比**:

```bash
# maxHeaderWidth: 50
feat(user): add user authentication and authorization system
# ❌ 错误:标题超过 50 字符

feat(user): add user authentication
# ✅ 正确:标题在 50 字符以内

# maxHeaderWidth: 100
feat(user): add user authentication and authorization system with JWT
# ✅ 正确:标题在 100 字符以内
```

**推荐值**:

- 严格项目:`72`(符合 Git 推荐)
- 一般项目:`100`(默认值)
- 宽松项目:`120`

### 1.3 maxLineWidth

**作用**:限制提交信息正文(body)每行的最大长度。

```json
{
  "maxLineWidth": 100
}
```

**默认值**:`100`

**影响对比**:

```bash
# maxLineWidth: 80
This is a very long line that exceeds the maximum line width limit and should be wrapped to multiple lines.
# ❌ 错误:单行超过 80 字符

This is a very long line that exceeds the maximum line width limit
and should be wrapped to multiple lines.
# ✅ 正确:每行不超过 80 字符

# maxLineWidth: 100
This is a very long line that exceeds the maximum line width limit and should be wrapped.
# ✅ 正确:单行不超过 100 字符
```

### 1.4 defaultType

**作用**:设置默认的提交类型。

```json
{
  "defaultType": "feat"
}
```

**默认值**:`""`(空字符串)

**影响对比**:

```bash
# defaultType: ""(默认)
? Select the type of change: (Use arrow keys)
❯ feat
  fix
  docs
# 需要手动选择

# defaultType: "feat"
? Select the type of change: (Use arrow keys)
❯ feat  # 默认选中
  fix
  docs
# 直接按回车即可使用 feat
```

**使用场景**:

- 功能开发分支:设置为 `"feat"`
- 修复分支:设置为 `"fix"`
- 文档项目:设置为 `"docs"`

### 1.5 defaultScope

**作用**:设置默认的影响范围(scope)。

```json
{
  "defaultScope": "core"
}
```

**默认值**:`""`(空字符串)

**影响对比**:

```bash
# defaultScope: ""
? What is the scope of this change (e.g. component or file name):
# 需要手动输入

# defaultScope: "core"
? What is the scope of this change (e.g. component or file name): (core)
# 默认填充 "core",可直接回车或修改
```

### 1.6 defaultSubject

**作用**:设置默认的简短描述。

```json
{
  "defaultSubject": ""
}
```

**默认值**:`""`(空字符串)

**影响**:一般不设置,保持为空。

### 1.7 defaultBody

**作用**:设置默认的详细描述。

```json
{
  "defaultBody": ""
}
```

**默认值**:`""`(空字符串)

**影响**:一般不设置,保持为空。

### 1.8 defaultIssues

**作用**:设置默认关联的 Issue。

```json
{
  "defaultIssues": ""
}
```

**默认值**:`""`(空字符串)

**影响对比**:

```bash
# defaultIssues: ""
? Add issue references (e.g. "fix #123", "re #123".):
# 需要手动输入

# defaultIssues: "#123"
? Add issue references (e.g. "fix #123", "re #123".): (#123)
# 默认填充 "#123"
```

## 二、常用适配器详解

### 2.1 cz-conventional-changelog(官方推荐)

**安装**:

```bash
npm install --save-dev cz-conventional-changelog
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

**提交类型**:

| 类型       | 说明                         | 示例                                      |
| ---------- | ---------------------------- | ----------------------------------------- |
| `feat`     | 新功能                       | `feat(auth): add login functionality`     |
| `fix`      | 修复 Bug                     | `fix(api): handle null pointer exception` |
| `docs`     | 文档变更                     | `docs(readme): update installation guide` |
| `style`    | 代码格式(不影响代码运行)     | `style(format): fix indentation`          |
| `refactor` | 重构(既不是新功能也不是修复) | `refactor(user): extract user service`    |
| `perf`     | 性能优化                     | `perf(query): optimize database query`    |
| `test`     | 测试相关                     | `test(auth): add login unit tests`        |
| `build`    | 构建系统或外部依赖           | `build(deps): upgrade vue to 3.4.0`       |
| `ci`       | CI 配置文件和脚本            | `ci(github): add lint workflow`           |
| `chore`    | 其他不修改 src 或测试文件    | `chore(release): bump version to 1.0.0`   |
| `revert`   | 回退之前的提交               | `revert: revert commit abc123`            |

**使用示例**:

```bash
$ git cz

? Select the type of change that you're committing: feat
? What is the scope of this change (e.g. component or file name): user-auth
? Write a short, imperative tense description of the change: add login functionality
? Provide a longer description of the change: (press enter to skip)
 Add JWT-based authentication with email and password
? Are there any breaking changes? No
? Does this change affect any open issues? Yes
? Add issue references (e.g. "fix #123", "re #123".): close #45

# 生成的提交信息:
feat(user-auth): add login functionality

Add JWT-based authentication with email and password

Close #45
```

### 2.2 cz-customizable(高度可定制)

**安装**:

```bash
npm install --save-dev cz-customizable
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "cz-customizable"
    },
    "cz-customizable": {
      "config": ".cz-config.js"
    }
  }
}
```

**自定义配置文件** `.cz-config.js`:

```javascript
module.exports = {
  // 提交类型
  types: [
    { value: "feat", name: "feat:     ✨ 新功能" },
    { value: "fix", name: "fix:      🐛 修复 Bug" },
    { value: "docs", name: "docs:     📝 文档变更" },
    { value: "style", name: "style:    💄 代码格式(不影响功能)" },
    { value: "refactor", name: "refactor: ♻️  代码重构" },
    { value: "perf", name: "perf:     ⚡️ 性能优化" },
    { value: "test", name: "test:     ✅ 测试相关" },
    { value: "build", name: "build:    📦️ 构建系统或依赖" },
    { value: "ci", name: "ci:       🎡 CI 配置" },
    { value: "chore", name: "chore:    🔨 其他修改" },
    { value: "revert", name: "revert:   ⏪️ 回退" },
  ],

  // 影响范围
  scopes: [
    { name: "core" },
    { name: "ui" },
    { name: "api" },
    { name: "auth" },
    { name: "utils" },
    { name: "docs" },
    { name: "config" },
  ],

  // 允许自定义 scope
  allowCustomScopes: true,

  // 允许 Breaking Changes 的类型
  allowBreakingChanges: ["feat", "fix"],

  // 跳过问题
  skipQuestions: ["body", "footer"],

  // 标题最大长度
  subjectLimit: 100,

  // 自定义提示信息
  messages: {
    type: "选择提交类型:",
    scope: "选择影响范围(可选):",
    customScope: "请输入自定义的 scope:",
    subject: "简短描述:",
    body: '详细描述(可选,使用 "|" 换行):',
    breaking: "列出 BREAKING CHANGES(可选):",
    footer: "关联的 Issue(可选,例如: #31, #34):",
    confirmCommit: "确认提交?",
  },
};
```

**使用示例**:

```bash
$ git cz

? 选择提交类型: (Use arrow keys)
❯ feat:     ✨ 新功能
  fix:      🐛 修复 Bug
  docs:     📝 文档变更

? 选择影响范围(可选): api
? 简短描述: 添加用户登录接口
? 确认提交? Yes

# 生成:feat(api): 添加用户登录接口
```

### 2.3 cz-emoji(Emoji 风格)

**安装**:

```bash
npm install --save-dev cz-emoji
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "cz-emoji"
    }
  }
}
```

**提交类型**(带 Emoji):

| Emoji | 类型       | 说明     |
| ----- | ---------- | -------- |
| ✨    | `feat`     | 新功能   |
| 🐛    | `fix`      | 修复 Bug |
| 📝    | `docs`     | 文档     |
| 💄    | `style`    | 格式     |
| ♻️    | `refactor` | 重构     |
| ⚡️    | `perf`     | 性能     |
| ✅    | `test`     | 测试     |
| 📦    | `build`    | 构建     |
| 🎡    | `ci`       | CI       |
| 🔨    | `chore`    | 其他     |

**生成效果**:

```bash
✨ feat(api): add user authentication
🐛 fix(ui): correct button alignment
📝 docs(readme): update installation steps
```

### 2.4 cz-git(现代化推荐)

**安装**:

```bash
npm install --save-dev cz-git
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "node_modules/cz-git"
    }
  }
}
```

**特点**:

- 🤖 **轻量级**：基于 Commitizen,零依赖,更快的安装速度
- ⚡ **高性能**：优化的交互体验
- 🎨 **高度可定制**：支持 Emoji、作用域、自定义问题
- 🌍 **国际化**：内置中英文支持
- 📝 **智能提示**：更好的 TypeScript 支持

**配置文件** `.commitlintrc.js`:

```javascript
module.exports = {
  extends: ["@commitlint/config-conventional"],
  prompt: {
    messages: {
      type: "选择你要提交的类型 :",
      scope: "选择一个提交范围（可选）:",
      customScope: "请输入自定义的提交范围 :",
      subject: "填写简短精炼的变更描述 :\n",
      body: '填写更加详细的变更描述（可选）。使用 "|" 换行 :\n',
      breaking: '列举非兼容性重大的变更（可选）。使用 "|" 换行 :\n',
      footerPrefixesSelect: "选择关联issue前缀（可选）:",
      customFooterPrefix: "输入自定义issue前缀 :",
      footer: "列举关联issue (可选) 例如: #31, #I3244 :\n",
      confirmCommit: "是否提交或修改commit ?",
    },
    types: [
      { value: "feat", name: "feat:     ✨  新增功能", emoji: ":sparkles:" },
      { value: "fix", name: "fix:      🐛  修复缺陷", emoji: ":bug:" },
      { value: "docs", name: "docs:     📝  文档更新", emoji: ":memo:" },
      { value: "style", name: "style:    💄  代码格式", emoji: ":lipstick:" },
      {
        value: "refactor",
        name: "refactor: ♻️   代码重构",
        emoji: ":recycle:",
      },
      { value: "perf", name: "perf:     ⚡️  性能提升", emoji: ":zap:" },
      {
        value: "test",
        name: "test:     ✅  测试相关",
        emoji: ":white_check_mark:",
      },
      { value: "build", name: "build:    📦️  构建相关", emoji: ":package:" },
      { value: "ci", name: "ci:       🎡  持续集成", emoji: ":ferris_wheel:" },
      { value: "chore", name: "chore:    🔨  其他修改", emoji: ":hammer:" },
      { value: "revert", name: "revert:   ⏪️  回退代码", emoji: ":rewind:" },
    ],
    useEmoji: true,
    emojiAlign: "center",
    themeColorCode: "",
    scopes: [],
    allowCustomScopes: true,
    allowEmptyScopes: true,
    customScopesAlign: "bottom",
    customScopesAlias: "custom",
    emptyScopesAlias: "empty",
    upperCaseSubject: false,
    markBreakingChangeMode: false,
    allowBreakingChanges: ["feat", "fix"],
    breaklineNumber: 100,
    breaklineChar: "|",
    skipQuestions: [],
    issuePrefixes: [
      { value: "closed", name: "closed:   ISSUES has been processed" },
    ],
    customIssuePrefixAlign: "top",
    emptyIssuePrefixAlias: "skip",
    customIssuePrefixAlias: "custom",
    allowCustomIssuePrefix: true,
    allowEmptyIssuePrefix: true,
    confirmColorize: true,
    maxHeaderLength: Infinity,
    maxSubjectLength: Infinity,
    minSubjectLength: 0,
    scopeOverrides: undefined,
    defaultBody: "",
    defaultIssues: "",
    defaultScope: "",
    defaultSubject: "",
  },
};
```

### 2.5 @commitlint/cz-commitlint(官方 Commitlint 适配器)

**安装**:

```bash
npm install --save-dev @commitlint/cz-commitlint commitizen inquirer@9
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "@commitlint/cz-commitlint"
    }
  }
}
```

**特点**:

- 🔗 **与 Commitlint 深度集成**：配置一次,两个工具共享
- 📏 **规则同步**：Commitlint 的规则自动应用到 Commitizen
- ⚙️ **零额外配置**：使用现有的 `commitlint.config.js`

### 2.6 cz-conventional-changelog-zh(中文简化版)

**安装**:

```bash
npm install --save-dev cz-conventional-changelog-zh
```

**配置**:

```json
{
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog-zh"
    }
  }
}
```

**特点**:

- 中文提示
- 简化流程
- 符合 Conventional Commits

## 三、完整推荐配置

### 3.1 基础配置(cz-conventional-changelog)

**package.json**:

```json
{
  "name": "my-project",
  "version": "1.0.0",
  "scripts": {
    "commit": "git-cz"
  },
  "devDependencies": {
    "commitizen": "^4.3.0",
    "cz-conventional-changelog": "^3.3.0"
  },
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

**使用**:

```bash
npm run commit
# 或
npx cz
```

### 3.2 高级配置(cz-customizable)

**package.json**:

```json
{
  "scripts": {
    "commit": "git-cz"
  },
  "devDependencies": {
    "commitizen": "^4.3.0",
    "cz-customizable": "^7.0.0"
  },
  "config": {
    "commitizen": {
      "path": "cz-customizable"
    },
    "cz-customizable": {
      "config": ".cz-config.js"
    }
  }
}
```

**.cz-config.js**(完整配置):

```javascript
module.exports = {
  types: [
    { value: "feat", name: "feat:     ✨ 新功能" },
    { value: "fix", name: "fix:      🐛 修复 Bug" },
    { value: "docs", name: "docs:     📝 文档变更" },
    { value: "style", name: "style:    💄 代码格式(不影响功能)" },
    { value: "refactor", name: "refactor: ♻️  代码重构" },
    { value: "perf", name: "perf:     ⚡️ 性能优化" },
    { value: "test", name: "test:     ✅ 添加测试" },
    { value: "build", name: "build:    📦️ 构建系统或依赖变更" },
    { value: "ci", name: "ci:       🎡 CI 配置" },
    { value: "chore", name: "chore:    🔨 其他修改(不修改 src 或测试文件)" },
    { value: "revert", name: "revert:   ⏪️ 回退提交" },
  ],

  scopes: [
    { name: "components" },
    { name: "utils" },
    { name: "api" },
    { name: "styles" },
    { name: "deps" },
    { name: "config" },
    { name: "other" },
  ],

  allowCustomScopes: true,
  allowBreakingChanges: ["feat", "fix"],
  skipQuestions: ["body"],
  subjectLimit: 100,

  messages: {
    type: "选择提交类型:",
    scope: "选择影响范围(可选):",
    customScope: "请输入自定义的 scope:",
    subject: "简短描述:\n",
    body: '详细描述,使用 "|" 换行(可选):\n',
    breaking: "列出 BREAKING CHANGES(可选):\n",
    footer: "关联的 Issue,例如: #31, #34(可选):\n",
    confirmCommit: "确认提交?",
  },
};
```

### 3.3 配合 Commitlint 使用

**安装依赖**:

```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
```

**commitlint.config.js**:

```javascript
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
      ],
    ],
    "subject-max-length": [2, "always", 100],
    "subject-case": [0],
  },
};
```

### 3.4 配合 Husky 使用

**安装**:

```bash
npm install --save-dev husky
npx husky init
```

**.husky/commit-msg**:

```bash
#!/usr/bin/env sh
npx --no -- commitlint --edit $1
```

**package.json**:

```json
{
  "scripts": {
    "commit": "git-cz",
    "prepare": "husky"
  }
}
```

## 四、与其他工具集成

### 4.1 与 Standard Version 集成

**安装**:

```bash
npm install --save-dev standard-version
```

**package.json**:

```json
{
  "scripts": {
    "commit": "git-cz",
    "release": "standard-version",
    "release:minor": "standard-version --release-as minor",
    "release:major": "standard-version --release-as major"
  }
}
```

**工作流**:

```bash
# 1. 提交代码
npm run commit

# 2. 发布版本
npm run release  # 自动根据提交类型决定版本号
# 或
npm run release:minor  # 手动指定版本
```

### 4.2 与 Conventional Changelog 集成

**安装**:

```bash
npm install --save-dev conventional-changelog-cli
```

**package.json**:

```json
{
  "scripts": {
    "changelog": "conventional-changelog -p angular -i CHANGELOG.md -s",
    "changelog:all": "conventional-changelog -p angular -i CHANGELOG.md -s -r 0"
  }
}
```

**生成 CHANGELOG**:

```bash
npm run changelog  # 生成本次版本的变更日志
npm run changelog:all  # 生成所有版本的变更日志
```

### 4.3 VS Code 集成

**安装插件**:

- [Visual Studio Code Commitizen Support](https://marketplace.visualstudio.com/items?itemName=KnisterPeter.vscode-commitizen)

**使用**:

1. 在 VS Code 中按 `Ctrl+Shift+P`(Mac: `Cmd+Shift+P`)
2. 输入 `Conventional Commit`
3. 按照提示填写提交信息

**.vscode/settings.json**:

```json
{
  "commitizen.autoSync": false,
  "commitizen.showOutputChannel": "off"
}
```

## 五、最佳实践

### 5.1 提交信息格式规范

**标准格式**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**示例**:

```
feat(auth): add JWT authentication

- Implement JWT token generation
- Add refresh token mechanism
- Update user model with token fields

Close #123
```

**说明**:

- **type**: 必填,提交类型
- **scope**: 可选,影响范围
- **subject**: 必填,简短描述(动词开头,不超过 50 字符)
- **body**: 可选,详细描述
- **footer**: 可选,关联 Issue 或 Breaking Changes

### 5.2 提交类型使用建议

| 类型       | 何时使用         | 示例                                        |
| ---------- | ---------------- | ------------------------------------------- |
| `feat`     | 添加新功能       | `feat(api): add user registration endpoint` |
| `fix`      | 修复 Bug         | `fix(ui): correct button click handler`     |
| `docs`     | 仅修改文档       | `docs(readme): update API documentation`    |
| `style`    | 代码格式、缩进等 | `style: format code with prettier`          |
| `refactor` | 代码重构         | `refactor(auth): extract validation logic`  |
| `perf`     | 性能优化         | `perf(db): optimize query performance`      |
| `test`     | 添加或修改测试   | `test(auth): add login integration tests`   |
| `build`    | 构建工具、依赖   | `build(deps): upgrade vue to 3.4.0`         |
| `ci`       | CI 配置          | `ci: add automated testing workflow`        |
| `chore`    | 杂项(不修改 src) | `chore: update .gitignore`                  |

### 5.3 Scope 命名建议

**按模块划分**:

```
feat(auth): add login
feat(user): add profile page
feat(admin): add user management
```

**按功能划分**:

```
feat(api): add REST endpoints
feat(ui): update dashboard layout
feat(db): add user migration
```

**按文件/组件**:

```
feat(UserList): add pagination
fix(LoginForm): validate email format
```

### 5.4 Subject 编写建议

**✅ 好的示例**:

```
feat(auth): add JWT authentication
fix(api): handle null response
docs(readme): update installation steps
```

**❌ 不好的示例**:

```
feat(auth): Added JWT authentication.  // 使用过去式,带句号
fix: bug fix  // 描述不清晰
update code  // 缺少类型和 scope
```

**原则**:

1. 使用祈使句,现在时态(`add` 而不是 `added`)
2. 首字母小写
3. 结尾不加句号
4. 不超过 50-72 字符
5. 描述做了什么,而不是为什么

### 5.5 Breaking Changes

**格式**:

```
feat(api): change user endpoint response format

BREAKING CHANGE: The user endpoint now returns data in a different structure.
Old format: { user: {...} }
New format: { data: {...} }

Migration guide: Update client code to access user.data instead of user.user
```

**触发条件**:

- API 接口变更
- 配置格式变更
- 移除已废弃的功能
- 重大重构

### 5.6 关联 Issue

**格式**:

```
fix(auth): correct password validation logic

Fix password validation to properly handle special characters.

Close #123
Ref #456
```

**关键词**:

- `Close #123` / `Closes #123` / `Closed #123`: 关闭 Issue
- `Fix #123` / `Fixes #123` / `Fixed #123`: 修复 Issue
- `Resolve #123` / `Resolves #123` / `Resolved #123`: 解决 Issue
- `Ref #123` / `Refs #123`: 引用 Issue

## 六、常见问题

### 6.1 提交失败

**问题**: 运行 `git cz` 或 `npm run commit` 失败

**解决方案**:

```bash
# 1. 检查是否安装了 commitizen
npm list commitizen

# 2. 检查配置是否正确
cat package.json | grep -A 5 commitizen

# 3. 重新安装
npm install --save-dev commitizen cz-conventional-changelog

# 4. 重新初始化
npx commitizen init cz-conventional-changelog --save-dev --save-exact --force
```

### 6.2 自定义配置不生效

**问题**: 使用 `cz-customizable` 但自定义配置不生效

**解决方案**:

```json
// package.json
{
  "config": {
    "commitizen": {
      "path": "cz-customizable"
    },
    "cz-customizable": {
      "config": ".cz-config.js" // 确保路径正确
    }
  }
}
```

```bash
# 检查配置文件是否存在
ls -la .cz-config.js

# 检查配置文件语法
node -c .cz-config.js
```

### 6.3 与 Commitlint 冲突

**问题**: Commitizen 生成的提交信息被 Commitlint 拒绝

**解决方案**:

```javascript
// commitlint.config.js
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // 确保规则与 Commitizen 配置一致
    "type-enum": [
      2,
      "always",
      [
        "feat",
        "fix",
        "docs",
        "style",
        "refactor",
        "perf",
        "test",
        "build",
        "ci",
        "chore",
        "revert",
      ],
    ],
    "subject-max-length": [2, "always", 100],
    "subject-case": [0], // 关闭大小写检查
  },
};
```

### 6.4 全局安装 vs 本地安装

**问题**: 应该全局安装还是本地安装?

**推荐**: 本地安装

```bash
# ✅ 推荐:本地安装
npm install --save-dev commitizen cz-conventional-changelog

# package.json
{
  "scripts": {
    "commit": "git-cz"
  }
}

# 使用
npm run commit
```

**优点**:

- 版本锁定,团队一致
- 不污染全局环境
- 便于 CI/CD 集成

### 6.5 跳过某些步骤

**问题**: 想跳过详细描述(body)等步骤

**解决方案**:

```javascript
// .cz-config.js
module.exports = {
  skipQuestions: ["body", "footer"], // 跳过这些问题
  // ...
};
```

或使用 `.cz.json`:

```json
{
  "skipQuestions": ["body", "footer"]
}
```

### 6.6 Emoji 不显示

**问题**: 使用 `cz-emoji` 但 Emoji 不显示

**解决方案**:

```bash
# 1. 确保终端支持 Unicode
# 2. Windows 用户安装 Windows Terminal
# 3. 配置 Git
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
```

## 七、完整工作流示例

### 7.1 初始化项目

```bash
# 1. 初始化项目
mkdir my-project
cd my-project
npm init -y
git init

# 2. 安装 Commitizen
npm install --save-dev commitizen cz-conventional-changelog

# 3. 初始化 Commitizen
npx commitizen init cz-conventional-changelog --save-dev --save-exact

# 4. 安装 Commitlint
npm install --save-dev @commitlint/cli @commitlint/config-conventional

# 5. 创建 Commitlint 配置
echo "module.exports = {extends: ['@commitlint/config-conventional']};" > commitlint.config.js

# 6. 安装 Husky
npm install --save-dev husky
npx husky init

# 7. 添加 commit-msg hook
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg

# 8. 添加 npm 脚本
npm pkg set scripts.commit="git-cz"
```

### 7.2 日常使用

```bash
# 1. 修改代码
# ... 编写代码 ...

# 2. 暂存文件
git add .

# 3. 使用 Commitizen 提交
npm run commit

# 或直接使用
npx cz

# 4. 推送代码
git push
```

### 7.3 发布流程

```bash
# 1. 安装 Standard Version
npm install --save-dev standard-version

# 2. 添加脚本
npm pkg set scripts.release="standard-version"

# 3. 发布
npm run release  # 自动生成 CHANGELOG 并打 tag

# 4. 推送
git push --follow-tags origin main
```

## 八、总结

### 核心要点

1. **选择合适的适配器**:
   - 🌟 **现代化项目**: `cz-git` (推荐,轻量级、高性能、中文支持)
   - 🔗 **Commitlint 集成**: `@commitlint/cz-commitlint` (配置共享)
   - 📦 **传统标准项目**: `cz-conventional-changelog` (稳定但陈旧)
   - 🎨 **高度定制**: `cz-customizable` (完全自定义)
   - ✨ **Emoji 风格**: `cz-emoji` (视觉化提交类型)

2. **配置关键选项**:
   - `path`: 指定适配器 (必选)
   - `maxHeaderWidth`: 标题长度限制 (推荐 100)
   - `skipQuestions`: 跳过不需要的问题
   - `defaultType`/`defaultScope`: 设置默认值

3. **集成相关工具**:
   - **Commitlint**: 验证提交信息格式
   - **Husky**: Git hooks 自动化
   - **Standard Version**: 自动化版本管理和 CHANGELOG
   - **Conventional Changelog**: 生成变更日志

### 推荐配置组合

**方案一：现代化配置（推荐 2024+）**

```json
{
  "scripts": {
    "commit": "git-cz",
    "release": "standard-version"
  },
  "devDependencies": {
    "commitizen": "^4.3.1",
    "cz-git": "^1.9.0",
    "@commitlint/cli": "^19.0.0",
    "@commitlint/config-conventional": "^19.0.0",
    "husky": "^9.0.0",
    "standard-version": "^9.5.0"
  },
  "config": {
    "commitizen": {
      "path": "node_modules/cz-git"
    }
  }
}
```

**方案二：官方集成配置**

```json
{
  "scripts": {
    "commit": "git-cz"
  },
  "devDependencies": {
    "commitizen": "^4.3.1",
    "@commitlint/cli": "^19.0.0",
    "@commitlint/config-conventional": "^19.0.0",
    "@commitlint/cz-commitlint": "^19.0.0",
    "inquirer": "^9.0.0",
    "husky": "^9.0.0"
  },
  "config": {
    "commitizen": {
      "path": "@commitlint/cz-commitlint"
    }
  }
}
```

**方案三：传统稳定配置**

```json
{
  "scripts": {
    "commit": "git-cz",
    "release": "standard-version"
  },
  "devDependencies": {
    "commitizen": "^4.3.1",
    "cz-conventional-changelog": "^3.3.0",
    "@commitlint/cli": "^18.0.0",
    "@commitlint/config-conventional": "^18.0.0",
    "husky": "^9.0.0",
    "standard-version": "^9.5.0"
  },
  "config": {
    "commitizen": {
      "path": "cz-conventional-changelog"
    }
  }
}
```

### 学习建议

1. **新项目**：直接使用 `cz-git` 或 `@commitlint/cz-commitlint`（更现代化）
2. **现有项目**：先使用 `cz-conventional-changelog`，再逐步迁移
3. **理解规范**：深入学习 [Conventional Commits](https://www.conventionalcommits.org/) 规范
4. **集成工具**：逐步集成 Commitlint 和 Husky，形成完整工作流
5. **团队定制**：根据团队需求使用 `cz-customizable` 自定义配置
6. **自动化**：配合 Standard Version 实现自动化版本管理

### 适配器对比

| 适配器                        | 维护状态     | 学习曲线 | 自定义程度 | 推荐场景             |
| ----------------------------- | ------------ | -------- | ---------- | -------------------- |
| **cz-git**                    | ✅ 活跃      | 低       | 高         | 🌟 新项目首选        |
| **@commitlint/cz-commitlint** | ✅ 活跃      | 低       | 中         | 已有 Commitlint 配置 |
| **cz-conventional-changelog** | ⚠️ 5年未更新 | 低       | 低         | 传统项目             |
| **cz-customizable**           | ✅ 活跃      | 中       | 极高       | 需要完全自定义       |
| **cz-emoji**                  | ⚠️ 不活跃    | 低       | 低         | 喜欢 Emoji 风格      |

## 参考资源

### 官方文档

- [Commitizen 官方文档](https://github.com/commitizen/cz-cli) - cz-cli 主项目
- [Conventional Commits 规范](https://www.conventionalcommits.org/) - 提交信息规范标准
- [Commitlint 文档](https://commitlint.js.org/) - 提交信息校验工具
- [Standard Version](https://github.com/conventional-changelog/standard-version) - 自动化版本管理

### 现代化适配器

- [cz-git](https://cz-git.qbb.sh/) - 🌟 推荐的现代化适配器
- [@commitlint/cz-commitlint](https://github.com/conventional-changelog/commitlint/tree/master/@commitlint/cz-commitlint) - 官方 Commitlint 适配器
- [cz-customizable](https://github.com/leoforfree/cz-customizable) - 高度可定制适配器
- [cz-emoji](https://github.com/ngryman/cz-emoji) - Emoji 风格适配器

### 相关工具

- [Husky](https://typicode.github.io/husky/) - Git hooks 工具
- [lint-staged](https://github.com/okonet/lint-staged) - 暂存区文件校验
- [Conventional Changelog](https://github.com/conventional-changelog/conventional-changelog) - 变更日志生成器

### 学习资源

- [Angular Git Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit) - Angular 提交规范
- [语义化版本 (Semver)](https://semver.org/lang/zh-CN/) - 版本号规范
- [如何写好 Git Commit Message](https://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html) - 阮一峰博客

---

🎉 掌握 Commitizen，让你的 Git 提交更规范！
