---
title: "Changesets 配置选项"
date: 2025-11-27
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 Changesets

[Changesets](https://github.com/changesets/changesets) 是一个用于管理版本和 changelog 的工具，专注于解决 Monorepo 多包管理问题。它让贡献者在提交代码时声明如何发布变更，然后自动更新版本号、生成 changelog 并发布包。

```bash
# 安装 Changesets
npm install -D @changesets/cli

# 初始化
npx changeset init

# 添加 changeset
npx changeset

# 版本更新
npx changeset version

# 发布
npx changeset publish
```

> [!TIP] 版本说明
> 本文档基于 **@changesets/cli 2.x** 编写，适用于 Monorepo 项目的版本管理和 changelog 生成。
>
> **当前版本**：
>
> - **@changesets/cli**: v2.29.7 (2024 年发布)
>
> **主要更新** (2024):
>
> - ✅ 更新 is-ci 依赖，改进 CI 环境检测
> - ✅ npm 7+ 兼容性改进，正确处理 stderr 输出
> - ✅ 改进 2FA 检查时的错误信息显示
> - ✅ pnpm workspaces exclude 规则支持
> - ✅ 修复 pre 模式下的版本号生成问题
>
> **核心工作流程**：
>
> 1. 📝 开发时：使用 `npx changeset` 记录变更
> 2. 🔢 发布前：使用 `npx changeset version` 更新版本号和 changelog
> 3. 🚀 发布时：使用 `npx changeset publish` 发布到 npm

> [!WARNING] 注意事项
>
> - 本工具专为 **Monorepo** 设计，单包项目可使用 npm version 或 semantic-release
> - 需要配合 Git 使用，依赖 commit 信息生成 changelog
> - 推荐与 Commitlint 配合使用，确保提交信息规范
> - CI/CD 集成需要配置 NPM_TOKEN 等环境变量

### 核心特性

- 📝 **变更记录**：在开发时记录变更，而不是发布时
- 🔢 **版本管理**：自动处理版本号更新（semver）
- 📋 **Changelog 生成**：自动生成格式化的 changelog
- 🎯 **Monorepo 支持**：处理多包之间的依赖关系
- 🤖 **CI/CD 集成**：自动化版本发布流程
- 👥 **团队协作**：多人协作时的版本管理

## 为什么需要 Changesets

### 传统版本管理的问题

没有 Changesets 之前，Monorepo 版本管理面临诸多问题：

```bash
# ❌ 传统方式：手动管理版本
# 1. 修改代码
# 2. 手动更新 package.json 版本号
# 3. 手动写 CHANGELOG.md
# 4. 手动检查依赖包的版本
# 5. 手动发布每个包

# 问题：
# - 容易忘记更新版本
# - 忘记记录 changelog
# - 依赖包版本不一致
# - 发布流程繁琐
# - 多人协作冲突

# 项目结构
packages/
├── shared/  (v1.0.0)
├── ui/      (v1.2.0) → 依赖 shared@1.0.0
└── web/     (v2.1.0) → 依赖 ui@1.2.0, shared@1.0.0

# 如果更新了 shared：
# ❌ 需要手动更新：
# 1. shared 的版本号
# 2. ui 的依赖版本
# 3. web 的依赖版本
# 4. 三个包的 CHANGELOG.md
```

### 使用 Changesets 后

```bash
# ✅ 使用 Changesets：自动化流程

# 1. 添加 changeset（开发时）
npx changeset
# ? Which packages would you like to include?
# ✓ shared
# ? What kind of change is this for shared?
# ✓ minor (增加新功能)
# ? Please enter a summary: 添加新的工具函数

# 2. 版本更新（发布前）
npx changeset version
# ✓ 自动更新 shared 版本：1.0.0 → 1.1.0
# ✓ 自动更新 ui 依赖：shared@1.0.0 → shared@1.1.0
# ✓ 自动更新 web 依赖：shared@1.0.0 → shared@1.1.0
# ✓ 自动生成 CHANGELOG.md

# 3. 发布（一键发布）
npx changeset publish
# ✓ 发布 shared@1.1.0
# ✓ 发布 ui@1.2.1（依赖更新）
# ✓ 发布 web@2.1.1（依赖更新）
# ✓ 推送 git tags
```

**效果**：

- ✅ 自动管理版本号
- ✅ 自动生成 changelog
- ✅ 自动处理依赖关系
- ✅ 避免版本冲突
- ✅ 简化发布流程

## 安装

### 基础安装

```bash
# 使用 npm
npm install -D @changesets/cli

# 使用 yarn
yarn add -D @changesets/cli

# 使用 pnpm（推荐）
pnpm add -D @changesets/cli
```

### 初始化

```bash
# 初始化 Changesets
npx changeset init

# 生成的文件
.changeset/
├── config.json    # 配置文件
└── README.md      # 使用说明
```

## 基础工作流

### 1. 添加 Changeset

```bash
# 开发完成后，添加 changeset
npx changeset

# 交互式问答
? Which packages would you like to include? ›
  ◉ @my-monorepo/shared
  ◯ @my-monorepo/ui
  ◯ @my-monorepo/web

? What kind of change is this for @my-monorepo/shared? ›
  ◯ major (破坏性更新)
  ◉ minor (新功能)
  ◯ patch (bug 修复)

? Please enter a summary for this change:
  添加新的日期格式化函数

# 生成文件：.changeset/random-name.md
---
"@my-monorepo/shared": minor
---

添加新的日期格式化函数
```

### 2. 版本更新

```bash
# 更新版本号
npx changeset version

# 自动执行：
# 1. 读取所有 changeset 文件
# 2. 计算新版本号
# 3. 更新 package.json
# 4. 生成 CHANGELOG.md
# 5. 删除已处理的 changeset 文件
```

### 3. 发布

```bash
# 发布到 npm
npx changeset publish

# 自动执行：
# 1. 发布所有更新的包
# 2. 推送 git tags
```

## 配置文件

### config.json 结构

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

## 一、核心配置选项

### 1.1 changelog（Changelog 生成器）

**作用**：指定 changelog 生成方式。

```json
{
  "changelog": "@changesets/cli/changelog"
}
```

**可选值**：

```json
// 默认生成器
{
  "changelog": "@changesets/cli/changelog"
}

// 使用 GitHub（推荐开源项目）
{
  "changelog": [
    "@changesets/changelog-github",
    { "repo": "owner/repo" }
  ]
}

// 自定义生成器
{
  "changelog": "./my-changelog-config.js"
}

// 带选项的自定义生成器
{
  "changelog": ["./my-changelog-config.js", { "repo": "myorg/myrepo" }]
}

// 不生成 changelog
{
  "changelog": false
}
```

**影响对比**：

```markdown
<!-- @changesets/cli/changelog -->

## 1.1.0

### Minor Changes

- abc123: 添加新功能

<!-- @changesets/changelog-github -->

## 1.1.0

### Minor Changes

- [#123](https://github.com/owner/repo/pull/123) 添加新功能 ([@username](https://github.com/username))

<!-- false -->

（不生成 CHANGELOG.md）
```

**自定义 Changelog 生成器**：

```javascript
// my-changelog-config.js
const { getInfo } = require("@changesets/get-github-info");

async function getReleaseLine(changeset, type, options) {
  const [firstLine, ...futureLines] = changeset.summary
    .split("\n")
    .map((l) => l.trimEnd());

  let returnVal = `- ${
    changeset.commit
      ? `[\`${changeset.commit}\`](${options.repo}/commit/${changeset.commit})`
      : ""
  } ${firstLine}`;

  if (futureLines.length > 0) {
    returnVal += `\n${futureLines.map((l) => `  ${l}`).join("\n")}`;
  }

  return returnVal;
}

async function getDependencyReleaseLine(
  changesets,
  dependenciesUpdated,
  options,
) {
  if (dependenciesUpdated.length === 0) return "";

  const changesetLinks = changesets.map(
    (changeset) => `- Updated dependencies [${changeset.commit?.slice(0, 7)}]`,
  );

  const updatedDependenciesList = dependenciesUpdated.map(
    (dependency) => `  - ${dependency.name}@${dependency.newVersion}`,
  );

  return [...changesetLinks, ...updatedDependenciesList].join("\n");
}

module.exports = {
  getReleaseLine,
  getDependencyReleaseLine,
};
```

**使用自定义生成器**：

```json
{
  "changelog": ["./my-changelog-config.js", { "repo": "myorg/myrepo" }]
}
```

### 1.2 commit（自动提交）

**作用**：版本更新后是否自动提交。

```json
{
  "commit": false  // 默认值，不自动提交
}

// 启用自动提交（使用默认提交信息生成器）
{
  "commit": true
}

// 等价于
{
  "commit": ["@changesets/cli/commit", { "skipCI": "version" }]
}

// 自定义提交信息生成器
{
  "commit": "../scripts/commit.js"
}

// 带选项的自定义生成器
{
  "commit": ["../scripts/commit.js", { "customOption": true }]
}
```

**影响对比**：

```bash
# commit: false（默认）
npx changeset version
# ✓ 版本更新完成
# ✗ 不自动提交（需要手动 git commit）

git add .
git commit -m "chore: version packages"

# commit: true
npx changeset version
# ✓ 版本更新完成
# ✓ 自动提交（默认信息：Version Packages）
# ✓ 提交信息包含 [skip ci]（skipCI: "version"）

# commit: ["@changesets/cli/commit", { "skipCI": false }]
npx changeset version
# ✓ 版本更新完成
# ✓ 自动提交，不跳过 CI
```

**自定义提交信息生成器**：

```javascript
// scripts/commit.js
async function getAddMessage(changeset, options) {
  // changeset 添加时的提交信息
  return `docs: add changeset for ${changeset.summary}`;
}

async function getVersionMessage(releasePlan, options) {
  // version 更新时的提交信息
  const releases = releasePlan.releases
    .map((r) => `${r.name}@${r.newVersion}`)
    .join(", ");

  return `chore: release ${releases}`;
}

module.exports = {
  getAddMessage,
  getVersionMessage,
};
```

**使用自定义生成器**：

```json
{
  "commit": ["../scripts/commit.js", { "skipCI": true }]
}
```

### 1.3 access（发布权限）

**作用**：指定包的发布权限。

```json
{
  "access": "restricted"  // 私有包（默认）
}

// 公开包
{
  "access": "public"
}
```

**影响对比**：

```bash
# access: "restricted"
npx changeset publish
# → npm publish --access restricted
# （只有授权用户可以安装）

# access: "public"
npx changeset publish
# → npm publish --access public
# （所有人都可以安装）
```

**使用场景**：

```json
// 私有 Monorepo
{
  "access": "restricted"
}

// 开源项目
{
  "access": "public"
}

// 混合（在 package.json 中单独配置）
{
  "access": "public",  // 默认公开
  "packages": {
    "@my-org/internal": {
      "access": "restricted"  // 特定包私有
    }
  }
}
```

### 1.4 baseBranch（基础分支）

**作用**：指定版本管理的基础分支。

```json
{
  "baseBranch": "main"  // 默认
}

// 使用其他分支
{
  "baseBranch": "master"
}

{
  "baseBranch": "develop"
}
```

**影响对比**：

```bash
# baseBranch: "main"
git checkout feature-branch
npx changeset

# Changesets 会检查：
# - 当前分支相对于 main 的变更
# - 确保在 main 分支上发布

# baseBranch: "develop"
# - 基于 develop 分支管理版本
# - 发布前需要合并到 develop
```

### 1.5 updateInternalDependencies（内部依赖更新）

**作用**：当包更新时，如何更新依赖它的包。

```json
{
  "updateInternalDependencies": "patch" // 默认
}
```

**可选值**：

| 值        | 说明              | 示例                     |
| --------- | ----------------- | ------------------------ |
| `"patch"` | 更新为 patch 版本 | 依赖从 `1.0.0` → `1.0.1` |
| `"minor"` | 更新为 minor 版本 | 依赖从 `1.0.0` → `1.1.0` |

**影响对比**：

```json
// 项目结构
{
  "packages": {
    "shared": "1.0.0",
    "ui": "1.0.0" // 依赖 shared@1.0.0
  }
}

// shared 添加了 minor 变更
// updateInternalDependencies: "patch"
{
  "shared": "1.1.0",
  "ui": "1.0.1"  // 自动 patch 更新
}

// updateInternalDependencies: "minor"
{
  "shared": "1.1.0",
  "ui": "1.1.0"  // 自动 minor 更新
}
```

### 1.6 fixed（固定版本）

**作用**：将多个包的版本固定在一起（统一版本）。

```json
{
  "fixed": [["@my-monorepo/ui", "@my-monorepo/theme"]]
}
```

**影响对比**：

```bash
# 不使用 fixed
# ui: 1.0.0 → 1.1.0
# theme: 1.5.0 → 1.5.0（不变）

# 使用 fixed
{
  "fixed": [["@my-monorepo/ui", "@my-monorepo/theme"]]
}

# 更新 ui
npx changeset version
# ui: 1.0.0 → 1.1.0
# theme: 1.5.0 → 1.1.0（同步更新）
```

**使用场景**：

```json
// Vue 生态（vue, vue-router, vuex 统一版本）
{
  "fixed": [
    ["vue", "vue-router", "vuex"]
  ]
}

// UI 组件库（核心和主题统一版本）
{
  "fixed": [
    ["@myui/core", "@myui/theme", "@myui/icons"]
  ]
}
```

### 1.7 linked（关联版本）

**作用**：链接多个包，但保持独立版本号。

```json
{
  "linked": [["@my-monorepo/ui", "@my-monorepo/components"]]
}
```

**fixed vs linked**：

```bash
# fixed：统一版本号
{
  "fixed": [["ui", "theme"]]
}
# ui: 1.0.0 → 1.1.0
# theme: 2.0.0 → 1.1.0（版本号相同）

# linked：同时更新，但保持相对关系
{
  "linked": [["ui", "theme"]]
}
# ui: 1.0.0 → 1.1.0
# theme: 2.0.0 → 2.1.0（同时 minor 更新，但版本号不同）
```

### 1.8 ignore（忽略包）

**作用**：排除不需要版本管理的包。

```json
{
  "ignore": ["@my-monorepo/docs", "@my-monorepo/examples"]
}
```

**影响对比**：

```bash
# 不使用 ignore
npx changeset
# 显示所有包：
# ◯ @my-monorepo/shared
# ◯ @my-monorepo/ui
# ◯ @my-monorepo/docs      ← 文档包也显示
# ◯ @my-monorepo/examples  ← 示例包也显示

# 使用 ignore
{
  "ignore": ["@my-monorepo/docs", "@my-monorepo/examples"]
}

npx changeset
# 只显示需要管理的包：
# ◯ @my-monorepo/shared
# ◯ @my-monorepo/ui
```

### 1.9 privatePackages（私有包）

**作用**：配置私有包的行为。

```json
{
  "privatePackages": {
    "version": true, // 是否更新版本
    "tag": false // 是否打 git tag
  }
}
```

**影响对比**：

```json
// package.json
{
  "private": true,
  "name": "@my-monorepo/internal"
}

// privatePackages.version: true
npx changeset version
# ✓ 更新 internal 的版本号
# ✓ 更新依赖它的包

// privatePackages.version: false
npx changeset version
# ✗ 跳过 internal 的版本更新
```

## 二、完整推荐配置

### 2.1 开源项目配置

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "username/repo" }],
  "commit": false,
  "fixed": [],
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["@my-monorepo/docs", "@my-monorepo/examples"]
}
```

### 2.2 私有项目配置

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": true,
  "fixed": [],
  "linked": [],
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": []
}
```

### 2.3 统一版本配置

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "fixed": [["@myui/core", "@myui/theme", "@myui/icons"]],
  "linked": [],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "minor",
  "ignore": []
}
```

### 2.4 混合模式配置

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "username/repo" }],
  "commit": false,
  "fixed": [["@my-monorepo/ui", "@my-monorepo/theme"]],
  "linked": [["@my-monorepo/core", "@my-monorepo/utils"]],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": [
    "@my-monorepo/docs",
    "@my-monorepo/examples",
    "@my-monorepo/internal"
  ]
}
```

## 三、常用命令

### 3.1 基础命令

```bash
# 初始化
npx changeset init

# 添加 changeset
npx changeset
npx changeset add  # 同上

# 添加空 changeset（不包含任何包变更）
npx changeset --empty

# 添加 changeset 并在编辑器中打开
npx changeset --open

# 查看状态
npx changeset status
npx changeset status --verbose  # 详细信息
npx changeset status --since main  # 自指定分支以来的变更
npx changeset status --output status.json  # 输出为 JSON 文件
```

### 3.2 版本管理

```bash
# 更新版本
npx changeset version

# 忽略特定包（跳过不发布）
npx changeset version --ignore package-name
npx changeset version --ignore @my-org/package-a --ignore @my-org/package-b

# Snapshot 模式（测试版本更新，不修改 semver 范围）
npx changeset version --snapshot
npx changeset version --snapshot canary  # 生成 1.0.0-canary-20240101120000

# 预发布版本
npx changeset pre enter alpha
npx changeset version
npx changeset pre exit
```

### 3.3 发布

```bash
# 发布到 npm
npx changeset publish

# 使用一次性密码（OTP）发布（如果启用了 2FA）
npx changeset publish --otp=123456

# 发布到指定 tag（默认是 latest）
npx changeset publish --tag next
npx changeset publish --tag beta
npx changeset publish --tag canary

# 只打 git tag，不发布到 npm
npx changeset tag
```

### 3.4 预发布（Pre-release）

```bash
# 1. 进入预发布模式
npx changeset pre enter alpha   # 或 beta、rc 等

# 2. 添加 changeset
npx changeset

# 3. 更新版本
npx changeset version
# 1.0.0 → 1.1.0-alpha.0

# 4. 发布
npx changeset publish --tag alpha

# 5. 退出预发布模式
npx changeset pre exit

# 完整示例
npx changeset pre enter beta
npx changeset
npx changeset version  # 生成 1.1.0-beta.0
npx changeset publish --tag beta
npx changeset pre exit
```

### 3.5 Snapshot 版本（测试版本）

**作用**：生成临时测试版本，不影响正式版本号。

```bash
# 生成 snapshot 版本
npx changeset version --snapshot

# 带标签的 snapshot
npx changeset version --snapshot canary
# 生成版本号：1.0.0-canary-20240101120000

# 发布 snapshot 版本
npx changeset publish --tag canary

# 使用场景
# 1. PR 预览构建
# 2. 快速测试
# 3. CI/CD 临时版本
```

**Snapshot vs Pre-release**：

| 特性         | Snapshot                | Pre-release     |
| ------------ | ----------------------- | --------------- |
| **版本号**   | `1.0.0-canary-20240101` | `1.0.0-alpha.0` |
| **时间戳**   | ✅ 包含时间戳           | ❌ 无时间戳     |
| **状态持久** | ❌ 一次性               | ✅ 持续状态     |
| **使用场景** | 临时测试                | 正式预发布      |
| **依赖更新** | ⚠️ 不更新 semver        | ✅ 正常更新     |

````

### 3.6 配置 package.json

```json
{
  "scripts": {
    "changeset": "changeset",
    "version": "changeset version",
    "release": "changeset publish",
    "status": "changeset status"
  }
}
````

## 四、CI/CD 集成

### 4.1 GitHub Actions（推荐）

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches:
      - main

concurrency: ${{ github.workflow }}-${{ github.ref }}

jobs:
  release:
    name: Release
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Install dependencies
        run: pnpm install

      - name: Create Release Pull Request or Publish
        uses: changesets/action@v1
        with:
          version: pnpm version
          publish: pnpm release
          commit: "chore: version packages"
          title: "chore: version packages"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**工作流程**：

```
1. 开发者提交代码 + changeset
   ↓
2. GitHub Actions 检测到 changesets
   ↓
3. 创建版本更新 PR
   - 自动更新版本号
   - 自动生成 CHANGELOG
   ↓
4. Review 并合并 PR
   ↓
5. 自动发布到 npm
```

### 4.2 检查 Changeset

```yaml
# .github/workflows/check-changeset.yml
name: Check Changeset

on:
  pull_request:
    branches:
      - main

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - run: pnpm install

      - name: Check for changesets
        run: |
          if [ "$(ls -A .changeset/*.md 2>/dev/null | grep -v README)" ]; then
            echo "✓ Changeset found"
          else
            echo "✗ No changeset found"
            exit 1
          fi
```

### 4.3 Changeset Bot

安装 [Changeset Bot](https://github.com/apps/changeset-bot)：

```
自动在 PR 中提示：
- ✓ Has changeset（包含 changeset）
- ✗ Missing changeset（缺少 changeset）
- 📝 Click here to add a changeset（点击添加）
```

## 五、常见问题和最佳实践

### 5.1 什么时候添加 Changeset

**时机**：

```bash
# ✅ 正确时机
1. Feature 完成后
2. Bug 修复后
3. 破坏性更新后
4. PR 提交前

# ❌ 错误时机
1. 重构代码（用户不可见）
2. 更新依赖（不影响功能）
3. 修改文档
4. 调整配置
```

**判断标准**：

```
需要添加 changeset：
- 用户可见的变更
- API 变更
- 新功能
- Bug 修复
- 性能优化

不需要添加 changeset：
- 内部重构
- 依赖更新
- 文档更新
- 配置调整
- CI/CD 配置
```

### 5.2 如何选择版本类型

**Semver 规则**：

```bash
# major（破坏性更新）1.0.0 → 2.0.0
- 删除 API
- 修改 API 签名
- 改变默认行为
- 不兼容的更新

示例：
- 删除 formatDate 函数
- 修改 add(a, b) → add({ a, b })
- 改变返回值类型

# minor（新功能）
1.0.0 → 1.1.0
- 添加新 API
- 新增功能
- 向后兼容的更新

示例：
- 添加 formatDateTime 函数
- 添加可选参数 add(a, b, options?)
- 添加新的工具函数

# patch（Bug 修复）
1.0.0 → 1.0.1
- Bug 修复
- 性能优化
- 文档更新（用户可见）

示例：
- 修复 formatDate 的 bug
- 优化性能
- 修正类型定义
```

### 5.3 依赖包版本不一致

**问题**：更新了 shared 包，但 ui 和 web 的依赖没有更新。

**解决方案**：

```json
// .changeset/config.json
{
  "updateInternalDependencies": "patch"
}

// 执行版本更新
npx changeset version

// 结果：
// shared: 1.0.0 → 1.1.0
// ui: 1.5.0 → 1.5.1（依赖自动更新为 shared@1.1.0）
// web: 2.0.0 → 2.0.1（依赖自动更新为 shared@1.1.0, ui@1.5.1）
```

### 5.4 多个 Changeset 如何合并

**场景**：一个 PR 包含多个变更。

**方案一：一个 changeset 包含所有变更**

```bash
npx changeset

? Which packages would you like to include?
  ◉ @my-monorepo/shared
  ◉ @my-monorepo/ui

? What kind of change is this for shared?
  ◉ minor

? What kind of change is this for ui?
  ◉ patch

? Please enter a summary:
  添加新功能并修复 UI bug
```

**方案二：多个独立的 changeset**

```bash
# 第一个 changeset
npx changeset
# shared: minor - 添加新功能

# 第二个 changeset
npx changeset
# ui: patch - 修复 bug

# 版本更新时会自动合并
npx changeset version
```

### 5.5 私有包的处理

**问题**：私有包不需要发布到 npm。

**解决方案**：

```json
// package.json
{
  "name": "@my-monorepo/internal",
  "private": true  // 标记为私有
}

// .changeset/config.json
{
  "privatePackages": {
    "version": true,   // 仍然更新版本号
    "tag": false       // 不打 git tag
  },
  "ignore": [
    "@my-monorepo/internal"  // 或者完全忽略
  ]
}
```

### 5.6 Monorepo 发布策略

**策略一：独立版本（推荐）**

```json
{
  "fixed": [],
  "linked": []
}

// 结果：
// shared: 1.0.0 → 1.1.0
// ui: 2.5.0 → 2.5.1
// web: 3.2.0 → 3.2.1
```

**策略二：固定版本**

```json
{
  "fixed": [["@my-monorepo/shared", "@my-monorepo/ui", "@my-monorepo/web"]]
}

// 结果（统一版本）：
// shared: 1.0.0 → 2.0.0
// ui: 1.0.0 → 2.0.0
// web: 1.0.0 → 2.0.0
```

**策略三：混合模式**

```json
{
  "fixed": [
    ["@my-monorepo/ui", "@my-monorepo/theme"] // UI 相关统一
  ],
  "linked": [],
  "ignore": ["@my-monorepo/docs"] // 文档包忽略
}

// 结果：
// shared: 1.0.0 → 1.1.0（独立）
// ui: 2.0.0 → 2.1.0（和 theme 统一）
// theme: 2.0.0 → 2.1.0（和 ui 统一）
// web: 3.0.0 → 3.0.1（独立，依赖更新）
```

### 5.7 最佳实践

#### 1. 在 PR 中添加 Changeset

```bash
# 开发流程
1. git checkout -b feature/new-function
2. 开发功能
3. npx changeset  # 添加 changeset
4. git add .
5. git commit -m "feat: add new function"
6. 提交 PR
```

#### 2. 使用 Changeset Bot

```
安装 Changeset Bot 到 GitHub 仓库
→ 自动检查 PR 是否包含 changeset
→ 提供快速添加 changeset 的链接
```

#### 3. 配置 package.json scripts

```json
{
  "scripts": {
    "changeset": "changeset",
    "changeset:status": "changeset status",
    "version": "changeset version && pnpm install --lockfile-only",
    "release": "pnpm build && changeset publish"
  }
}
```

#### 4. 提交信息规范

```bash
# changeset 文件名规范
.changeset/
├── kind-tigers-smile.md     # 随机名称（默认）
├── add-new-feature.md       # 或自定义名称
└── fix-button-bug.md

# changeset 内容规范
---
"@my-monorepo/ui": minor
---

添加新的 Button 组件

- 支持多种尺寸
- 支持主题定制
- 完善的 TypeScript 类型
```

#### 5. 发布前检查

```bash
# 1. 检查 changeset 状态
npx changeset status

# 2. 预览版本更新
npx changeset version --dry-run

# 3. 构建所有包
pnpm build

# 4. 运行测试
pnpm test

# 5. 发布
npx changeset publish
```

## 六、实际案例

### 案例 1：开源组件库

```json
// .changeset/config.json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": ["@changesets/changelog-github", { "repo": "myorg/ui-library" }],
  "commit": false,
  "fixed": [["@myui/core", "@myui/theme"]],
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch",
  "ignore": ["@myui/docs", "@myui/examples"]
}
```

**工作流**：

```bash
# 1. 开发新组件
# 2. 添加 changeset
npx changeset
# ? @myui/core: minor
# ? 添加 Select 组件

# 3. 提交 PR
git commit -m "feat: add Select component"

# 4. 合并后，CI 创建版本 PR
# 5. Review 版本 PR
# 6. 合并版本 PR，自动发布
```

### 案例 2：私有工具库

```json
// .changeset/config.json
{
  "changelog": "@changesets/cli/changelog",
  "commit": true,
  "access": "restricted",
  "baseBranch": "main",
  "updateInternalDependencies": "minor",
  "privatePackages": {
    "version": true,
    "tag": false
  }
}
```

```json
// package.json
{
  "scripts": {
    "changeset": "changeset",
    "version": "changeset version",
    "release": "pnpm build && changeset publish"
  }
}
```

### 案例 3：大型 Monorepo

```json
// .changeset/config.json
{
  "changelog": ["@changesets/changelog-github", { "repo": "company/monorepo" }],
  "commit": false,
  "fixed": [
    ["@company/ui-core", "@company/ui-theme"],
    ["@company/shared-utils", "@company/shared-types"]
  ],
  "linked": [["@company/app-web", "@company/app-mobile"]],
  "access": "restricted",
  "baseBranch": "develop",
  "updateInternalDependencies": "patch",
  "ignore": ["@company/docs", "@company/internal-tools", "@company/examples"]
}
```

## 七、与其他工具对比

### Changesets vs Lerna

| 特性          | Changesets              | Lerna           |
| ------------- | ----------------------- | --------------- |
| **版本管理**  | ✅ 灵活（独立/固定）    | ✅ 支持         |
| **Changelog** | ✅ 自动生成             | ⚠️ 需要插件     |
| **工作流**    | ⭐⭐⭐ 简单             | ⭐⭐ 中等       |
| **CI/CD**     | ✅ 优秀的 GitHub Action | ⚠️ 需要自己配置 |
| **学习曲线**  | ⭐⭐ 低                 | ⭐⭐⭐ 高       |
| **社区**      | ⭐⭐⭐ 活跃             | ⭐⭐ 一般       |

### Changesets vs semantic-release

| 特性         | Changesets        | semantic-release |
| ------------ | ----------------- | ---------------- |
| **手动控制** | ✅ 开发者决定版本 | ❌ 自动判断      |
| **Monorepo** | ✅ 原生支持       | ⚠️ 需要配置      |
| **灵活性**   | ⭐⭐⭐ 高         | ⭐⭐ 中          |
| **学习曲线** | ⭐⭐ 低           | ⭐⭐⭐ 高        |

**推荐选择**：

```
Monorepo + 手动控制版本 → Changesets ⭐⭐⭐⭐⭐
- 多包管理
- 灵活的版本策略
- 优秀的 CI/CD 集成

自动化语义化版本 → semantic-release ⭐⭐⭐⭐
- 基于 commit 自动判断版本
- 适合单一仓库

传统 Monorepo 工具 → Lerna ⭐⭐⭐
- 成熟稳定
- 功能全面
- 但 Changesets 更现代
```

## 八、总结

### 核心优势

1. **开发时记录变更**：不用在发布时回忆改了什么
2. **自动版本管理**：自动处理版本号和依赖关系
3. **自动 Changelog**：自动生成格式化的更新日志
4. **Monorepo 友好**：专为多包仓库设计
5. **CI/CD 集成**：优秀的 GitHub Actions 支持

### 最小配置

```json
{
  "$schema": "https://unpkg.com/@changesets/config@3.0.0/schema.json",
  "changelog": "@changesets/cli/changelog",
  "commit": false,
  "access": "public",
  "baseBranch": "main",
  "updateInternalDependencies": "patch"
}
```

### 推荐工作流

```
1. 开发功能
   ↓
2. npx changeset（添加变更记录）
   ↓
3. 提交 PR（包含 changeset 文件）
   ↓
4. 合并 PR
   ↓
5. CI 自动创建版本更新 PR
   ↓
6. Review 版本 PR
   ↓
7. 合并版本 PR
   ↓
8. CI 自动发布到 npm
```

### 关键要点

1. **及时添加 changeset**：开发完成后立即添加
2. **正确选择版本类型**：major/minor/patch
3. **写好变更说明**：清晰描述改了什么
4. **配置 CI/CD**：自动化发布流程
5. **使用 Changeset Bot**：PR 检查
6. **合理配置 ignore**：排除不需要版本管理的包

### 学习路径

1. **基础**：理解 semver 和 changeset 概念
2. **实践**：在项目中添加 changeset
3. **进阶**：配置 fixed/linked 策略
4. **自动化**：集成 CI/CD
5. **优化**：根据团队调整工作流

## 参考资源

- [Changesets GitHub](https://github.com/changesets/changesets)
- [Changesets 文档](https://github.com/changesets/changesets/tree/main/docs)
- [Semver 规范](https://semver.org/)
- [Changesets Action](https://github.com/changesets/action)
- [Changeset Bot](https://github.com/apps/changeset-bot)

---

🎉 使用 Changesets，让 Monorepo 版本管理变得简单优雅！
