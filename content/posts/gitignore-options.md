---
title: "gitignore 配置详解"
date: 2025-12-05
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 什么是 .gitignore

`.gitignore` 是一个文本文件，用于告诉 Git 哪些文件或目录不需要被版本控制。它可以帮助你：

- 🚫 **排除文件**：阻止特定文件被提交到仓库
- 🧹 **保持整洁**：避免不必要的文件污染仓库
- 🔒 **保护隐私**：防止敏感信息（如密钥、密码）被提交
- ⚡ **提升性能**：减少 Git 需要跟踪的文件数量
- 👥 **团队协作**：统一忽略规则，避免冲突

```bash
# 创建 .gitignore 文件
touch .gitignore

# 查看当前被忽略的文件
git status --ignored
```

:::tip 工作原理
`.gitignore` 文件使用模式匹配来决定哪些文件应该被忽略。Git 会按照从上到下的顺序读取规则，后面的规则可以覆盖前面的规则。
:::

## 文件位置和优先级

### 1. 配置文件类型

Git 支持多种方式配置忽略规则：

```bash
# 1. 仓库级别 .gitignore（推荐）
.gitignore                    # 项目根目录
src/.gitignore               # 子目录也可以有

# 2. 全局 .gitignore
~/.gitignore_global          # 用户主目录

# 3. Git 仓库内部
.git/info/exclude            # 本地仓库专用，不会被提交
```

### 2. 优先级顺序

优先级从高到低：

| 优先级 | 位置                   | 作用范围       | 是否提交 |
| ------ | ---------------------- | -------------- | -------- |
| 1      | 命令行参数             | 当前命令       | ❌       |
| 2      | `.gitignore`（子目录） | 该目录及子目录 | ✅       |
| 3      | `.gitignore`（根目录） | 整个项目       | ✅       |
| 4      | `.git/info/exclude`    | 整个项目       | ❌       |
| 5      | `~/.gitignore_global`  | 所有项目       | ❌       |

### 3. 配置全局 .gitignore

```bash
# 创建全局 .gitignore
touch ~/.gitignore_global

# 配置 Git 使用全局文件
git config --global core.excludesfile ~/.gitignore_global
```

**全局 .gitignore 适用场景**：

- 操作系统生成的文件（`.DS_Store`、`Thumbs.db`）
- 编辑器配置文件（`.vscode`、`.idea`）
- 个人工具配置（不影响团队）

## 一、匹配模式语法

### 1.1 基本规则

```bash
# 1. 注释
# 这是一行注释

# 2. 空行
# 空行会被忽略，可用于分隔不同类型的规则

# 3. 忽略文件
file.txt                    # 忽略所有 file.txt

# 4. 忽略目录
node_modules/               # 忽略 node_modules 目录
build/                      # 忽略 build 目录

# 5. 否定模式（重新包含）
*.log                       # 忽略所有 .log 文件
!important.log              # 但不忽略 important.log

# 6. 转义特殊字符
\#file.txt                  # 忽略名为 #file.txt 的文件
\!important.txt             # 忽略名为 !important.txt 的文件
```

### 1.2 通配符

| 通配符   | 说明                       | 示例             | 匹配                                    | 不匹配           |
| -------- | -------------------------- | ---------------- | --------------------------------------- | ---------------- |
| `*`      | 匹配任意字符（不包括 `/`） | `*.log`          | `error.log`<br>`app.log`                | `logs/error.log` |
| `**`     | 匹配任意层级目录           | `**/logs`        | `logs/`<br>`build/logs/`<br>`src/logs/` | -                |
| `?`      | 匹配单个字符               | `file?.txt`      | `file1.txt`<br>`fileA.txt`              | `file10.txt`     |
| `[abc]`  | 匹配方括号中的任意字符     | `file[0-9].txt`  | `file0.txt`<br>`file5.txt`              | `fileA.txt`      |
| `[!abc]` | 匹配不在方括号中的字符     | `file[!0-9].txt` | `fileA.txt`<br>`fileB.txt`              | `file0.txt`      |

### 1.3 目录规则

```bash
# 1. 忽略所有同名文件或目录
logs                        # 忽略所有名为 logs 的文件和目录

# 2. 只忽略目录（末尾加 /）
logs/                       # 只忽略 logs 目录，不忽略 logs 文件

# 3. 只忽略根目录的文件或目录（开头加 /）
/config.js                  # 只忽略根目录的 config.js
/logs/                      # 只忽略根目录的 logs 目录

# 4. 忽略所有层级的目录
**/node_modules/            # 忽略所有 node_modules 目录
```

### 1.4 否定模式

```bash
# 忽略所有 .log 文件，但保留 important.log
*.log
!important.log

# 忽略 build 目录，但保留 build/README.md
build/
!build/README.md

# ⚠️ 注意：无法重新包含已被父目录规则忽略的文件
logs/                       # 忽略 logs 目录
!logs/important.log         # ❌ 无效：logs 目录已被忽略

# ✅ 正确做法：
logs/*                      # 忽略 logs 目录下的所有文件
!logs/important.log         # ✅ 有效：保留 important.log
```

### 1.5 高级模式

```bash
# 1. 忽略特定深度的文件
/*.log                      # 只忽略根目录的 .log 文件
/**/*.log                   # 忽略所有 .log 文件

# 2. 忽略特定扩展名的文件
*.{log,tmp,cache}           # 忽略 .log、.tmp、.cache 文件

# 3. 忽略除了特定文件外的所有文件
/*                          # 忽略根目录所有文件
!.gitignore                 # 保留 .gitignore
!README.md                  # 保留 README.md
!src/                       # 保留 src 目录

# 4. 使用范围
file[0-9].txt               # 匹配 file0.txt ~ file9.txt
file[a-z].txt               # 匹配 filea.txt ~ filez.txt
file[!a-z].txt              # 匹配不包含小写字母的文件
```

## 二、模式匹配示例

### 2.1 文件匹配

```bash
# 示例项目结构
project/
├── error.log
├── debug.log
├── src/
│   ├── app.log
│   └── utils.log
└── logs/
    └── server.log

# 匹配规则对比
*.log                       # ✅ 匹配：error.log, debug.log, app.log, utils.log, server.log

/*.log                      # ✅ 匹配：error.log, debug.log
                           # ❌ 不匹配：app.log, utils.log, server.log

logs/*.log                  # ✅ 匹配：server.log
                           # ❌ 不匹配：error.log, debug.log, app.log, utils.log

**/logs/*.log               # ✅ 匹配：server.log
```

### 2.2 目录匹配

```bash
# 示例项目结构
project/
├── dist/
├── build/
├── src/
│   └── dist/
└── test/
    └── build/

# 匹配规则对比
dist                        # ✅ 匹配：dist/, src/dist/
dist/                       # ✅ 匹配：dist/, src/dist/
/dist/                      # ✅ 匹配：dist/
                           # ❌ 不匹配：src/dist/

**/dist/                    # ✅ 匹配：dist/, src/dist/
```

### 2.3 否定模式示例

```bash
# 场景1：忽略所有 .log，但保留 important.log
*.log
!important.log

# 场景2：忽略 build 目录，但保留 README.md
build/*
!build/README.md

# 场景3：忽略所有 .js，但保留 config 目录下的
*.js
!config/
!config/*.js

# 场景4：只保留特定文件
/*                          # 忽略所有
!.gitignore                 # 保留 .gitignore
!README.md                  # 保留 README.md
!src/                       # 保留 src 目录
```

### 2.4 常见错误

```bash
# ❌ 错误1：想忽略目录，但忘记加 /
node_modules                # 会忽略文件和目录
node_modules/               # ✅ 只忽略目录

# ❌ 错误2：无法重新包含已被忽略的目录下的文件
logs/                       # 忽略整个 logs 目录
!logs/important.log         # ❌ 无效

# ✅ 正确做法
logs/*                      # 忽略 logs 目录下的所有内容
!logs/important.log         # ✅ 保留 important.log

# ❌ 错误3：路径分隔符错误（Windows）
src\components\*.vue        # ❌ 错误

# ✅ 正确做法
src/components/*.vue        # ✅ 始终使用 /

# ❌ 错误4：多余的空格
*.log                       # ✅ 正确
*.log                       # ❌ 包含空格，不会匹配
```

## 三、常用项目模板

### 3.1 Node.js 项目

```bash
# 依赖
node_modules/
jspm_packages/

# 构建产物
dist/
build/
out/
.next/
.nuxt/
.cache/

# 日志
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# 测试覆盖率
coverage/
*.lcov
.nyc_output/

# 环境变量
.env
.env.local
.env.*.local
.env.production

# 编辑器
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
Thumbs.db
Desktop.ini

# 临时文件
*.tmp
*.temp
*.bak
*.old
```

### 3.2 Vue 项目

```bash
# 基础 Node.js 忽略（参考 3.1）
node_modules/
dist/
*.log

# Vue 特定
.vite/
.nuxt/
.output/
.cache/

# Auto-generated files
auto-imports.d.ts
components.d.ts
typed-router.d.ts

# Vite
vite.config.js.timestamp-*
vite.config.ts.timestamp-*

# 环境变量
.env
.env.local
.env.*.local

# IDE
.vscode/*
!.vscode/extensions.json
.idea/

# 测试
coverage/
test-results/

# 构建产物
dist-ssr/
*.local
```

### 3.3 React 项目

```bash
# 依赖
node_modules/

# 构建产物
build/
dist/
.next/
out/

# 测试
coverage/
.nyc_output/

# 环境变量
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# 日志
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Create React App
/build
/.pnp
.pnp.js

# Next.js
.next/
out/
next-env.d.ts

# Gatsby
.cache/
public/

# IDE
.vscode/
.idea/

# 操作系统
.DS_Store
Thumbs.db
```

### 3.4 TypeScript 项目

```bash
# 依赖
node_modules/

# 构建产物
dist/
lib/
build/
out/

# TypeScript
*.tsbuildinfo
tsconfig.tsbuildinfo

# 临时文件
*.tmp
*.temp

# 日志
*.log

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/

# 测试
coverage/
```

### 3.5 Python 项目

```bash
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local
```

### 3.6 Java 项目

```bash
# Compiled class files
*.class

# Log files
*.log

# Package Files
*.jar
*.war
*.ear
*.zip
*.tar.gz
*.rar

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties

# Gradle
.gradle/
build/

# IntelliJ IDEA
.idea/
*.iws
*.iml
*.ipr
out/

# Eclipse
.classpath
.project
.settings/

# NetBeans
/nbproject/private/
/nbbuild/
/dist/
/nbdist/
```

## 四、特殊场景配置

### 4.1 Monorepo 项目

```bash
# 根目录 .gitignore
node_modules/
dist/
build/
.cache/
.turbo/
*.log

# 包管理器
pnpm-lock.yaml
yarn.lock
package-lock.json

# 环境变量
.env
.env.local

# 子包构建产物
packages/*/dist/
packages/*/build/
packages/*/lib/

# IDE
.vscode/
.idea/
```

### 4.2 前后端分离项目

```bash
# 前端
frontend/node_modules/
frontend/dist/
frontend/build/
frontend/.vite/

# 后端
backend/node_modules/
backend/dist/
backend/logs/
backend/.env

# 共享
.DS_Store
*.log
.vscode/
.idea/
```

### 4.3 开源项目

```bash
# 依赖
node_modules/

# 构建产物
dist/
build/
lib/

# 日志
*.log

# 环境变量（示例文件保留）
.env
!.env.example

# 编辑器配置（保留推荐配置）
.vscode/*
!.vscode/extensions.json
!.vscode/settings.json

.idea/

# 测试
coverage/

# 操作系统
.DS_Store
Thumbs.db

# 临时文件
*.tmp
*.bak
```

### 4.4 私有项目

```bash
# 所有依赖
node_modules/

# 所有构建产物
dist/
build/
out/

# 所有日志
logs/
*.log

# 所有环境变量
.env*
!.env.example

# 所有 IDE 配置
.vscode/
.idea/
*.swp

# 敏感文件
secrets/
credentials/
*.key
*.pem
*.cert

# 测试和覆盖率
coverage/
test-results/

# 操作系统
.DS_Store
Thumbs.db
```

## 五、最佳实践

### 5.1 应该忽略的文件

```bash
# ✅ 应该忽略

# 1. 依赖目录
node_modules/
vendor/
packages/

# 2. 构建产物
dist/
build/
out/
*.min.js
*.min.css

# 3. 日志文件
*.log
logs/

# 4. 临时文件
*.tmp
*.temp
*.cache
*.swp

# 5. 环境变量和密钥
.env
.env.local
*.key
*.pem
credentials.json

# 6. 系统文件
.DS_Store
Thumbs.db
desktop.ini

# 7. IDE 配置（个人配置）
.vscode/settings.json
.idea/workspace.xml

# 8. 测试覆盖率
coverage/
.nyc_output/
```

### 5.2 不应该忽略的文件

```bash
# ❌ 不应该忽略

# 1. 源代码
src/
*.js
*.ts
*.vue
*.jsx
*.tsx

# 2. 配置文件
package.json
tsconfig.json
vite.config.js
.eslintrc.js

# 3. 文档
README.md
CHANGELOG.md
LICENSE

# 4. 示例文件
.env.example
config.example.js

# 5. 公共资源
public/
assets/
static/

# 6. 测试文件
*.test.js
*.spec.js
__tests__/

# 7. Git 配置
.gitignore
.gitattributes

# 8. CI/CD 配置
.github/
.gitlab-ci.yml
.travis.yml
```

### 5.3 组织规则的建议

```bash
# 使用注释分组，提高可读性

# ============================================
# 依赖
# ============================================
node_modules/
vendor/

# ============================================
# 构建产物
# ============================================
dist/
build/
out/
*.min.js

# ============================================
# 环境变量
# ============================================
.env
.env.local
.env.*.local
!.env.example

# ============================================
# 日志
# ============================================
logs/
*.log
npm-debug.log*

# ============================================
# 编辑器和 IDE
# ============================================
.vscode/
.idea/
*.swp

# ============================================
# 操作系统
# ============================================
.DS_Store
Thumbs.db

# ============================================
# 测试
# ============================================
coverage/
.nyc_output/
```

### 5.4 性能优化

```bash
# 1. 使用更具体的路径
# ❌ 慢
**/node_modules/

# ✅ 快
node_modules/

# 2. 避免过多的否定模式
# ❌ 慢
dist/*
!dist/index.html
!dist/assets/
!dist/assets/*.js

# ✅ 快：考虑调整目录结构，或使用其他方式

# 3. 将常用规则放在前面
node_modules/              # 最常匹配
dist/
*.log
```

## 六、常见问题

### 6.1 已被 Git 跟踪的文件

**问题**：添加 `.gitignore` 后，已经被 Git 跟踪的文件仍然显示修改。

```bash
# 查看被跟踪的文件
git ls-files

# 从 Git 跟踪中移除文件（保留本地文件）
git rm --cached <file>
git rm --cached -r <directory>

# 示例：移除 node_modules
git rm --cached -r node_modules/

# 提交更改
git add .gitignore
git commit -m "chore: update .gitignore and remove tracked files"
```

### 6.2 查看忽略规则

```bash
# 查看哪个规则导致文件被忽略
git check-ignore -v <file>

# 示例
git check-ignore -v node_modules/express/package.json
# 输出：.gitignore:1:node_modules/    node_modules/express/package.json

# 查看所有被忽略的文件
git status --ignored

# 列出所有被忽略的文件（包括子目录）
git ls-files --others --ignored --exclude-standard
```

### 6.3 临时包含被忽略的文件

```bash
# 强制添加被忽略的文件
git add -f <file>

# 示例：添加特定的配置文件
git add -f config/production.env
```

### 6.4 清理未跟踪的文件

```bash
# 预览将被删除的文件（不包括被忽略的）
git clean -n

# 预览将被删除的文件（包括被忽略的）
git clean -n -x

# 删除未跟踪的文件
git clean -f

# 删除未跟踪的文件和目录
git clean -fd

# 删除包括被忽略的文件
git clean -fx

# 交互式删除
git clean -i
```

### 6.5 调试 .gitignore

```bash
# 1. 检查文件是否被忽略
git check-ignore <file>

# 2. 查看详细的忽略规则
git check-ignore -v <file>

# 3. 检查多个文件
git check-ignore file1.txt file2.js dir/

# 4. 使用通配符
git check-ignore *.log

# 5. 测试模式（不实际修改）
# 在 .gitignore 中添加规则后
git status                  # 查看效果
git check-ignore -v <file> # 确认规则
```

### 6.6 全局 vs 项目级别

| 场景         | 使用 | 示例                       |
| ------------ | ---- | -------------------------- |
| 操作系统文件 | 全局 | `.DS_Store`, `Thumbs.db`   |
| 编辑器配置   | 全局 | `.vscode/`, `.idea/`       |
| 项目依赖     | 项目 | `node_modules/`, `vendor/` |
| 构建产物     | 项目 | `dist/`, `build/`          |
| 环境变量     | 项目 | `.env`, `.env.local`       |

```bash
# 全局 .gitignore（~/.gitignore_global）
.DS_Store
.Spotlight-V100
.Trashes
Thumbs.db
.vscode/
.idea/
*.swp

# 项目 .gitignore
node_modules/
dist/
.env
*.log
```

### 6.7 Gitignore 模板

使用 GitHub 官方模板：

```bash
# 访问 GitHub gitignore 模板仓库
# https://github.com/github/gitignore

# 常用模板
- Node.gitignore
- Python.gitignore
- Java.gitignore
- Go.gitignore
- Ruby.gitignore
```

**在线生成工具**：

- [gitignore.io](https://www.toptal.com/developers/gitignore)
- 输入技术栈，自动生成 `.gitignore`

```bash
# 使用 gitignore.io API
curl -L https://www.toptal.com/developers/gitignore/api/node,vue,vscode > .gitignore
```

## 七、高级技巧

### 7.1 条件忽略

```bash
# 忽略所有 .env 文件，但保留 .env.example
.env*
!.env.example

# 忽略 config 目录，但保留 config.example.js
config/*
!config/.gitkeep
!config/config.example.js

# 忽略所有 .js，但保留特定目录
*.js
!src/
!src/**/*.js
```

### 7.2 使用 .gitkeep

```bash
# 场景：需要提交空目录
# Git 不跟踪空目录，使用 .gitkeep 占位

logs/
!logs/.gitkeep

# 创建 .gitkeep
mkdir logs
touch logs/.gitkeep
git add logs/.gitkeep
```

### 7.3 子目录配置

```bash
# 项目根目录 .gitignore
node_modules/
dist/

# src/.gitignore（更具体的规则）
*.log
!important.log

# 优先级：子目录规则 > 根目录规则
```

### 7.4 忽略除了特定文件外的所有内容

```bash
# 场景：只提交特定文件到仓库

# 忽略所有
/*

# 保留特定文件
!.gitignore
!README.md
!LICENSE

# 保留特定目录
!src/
# 注意：需要递归排除目录内的忽略规则
!src/**
```

### 7.5 使用 .git/info/exclude

**使用场景**：个人本地忽略规则，不想提交到仓库。

```bash
# 编辑 .git/info/exclude
vim .git/info/exclude

# 添加规则（语法与 .gitignore 相同）
# 个人临时文件
*.local.js
temp/
notes.txt

# 这些规则只在本地生效，不会被提交
```

## 八、与其他工具集成

### 8.1 VS Code 集成

**.vscode/settings.json**：

```json
{
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/dist": true,
    "**/build": true,
    "**/coverage": true
  }
}
```

### 8.2 .gitattributes 配合

```bash
# .gitignore
*.pdf

# .gitattributes（设置已跟踪的 PDF 文件的处理方式）
*.pdf binary
docs/*.pdf -diff
```

### 8.3 .dockerignore

`.dockerignore` 与 `.gitignore` 类似，但用于 Docker 构建：

```bash
# .dockerignore
node_modules/
npm-debug.log
.git
.gitignore
README.md
.env
.env.*
dist/
coverage/
```

### 8.4 .npmignore

控制 npm 包发布时包含的文件：

```bash
# .npmignore
# 如果没有 .npmignore，npm 会使用 .gitignore

# 测试文件
test/
*.test.js
*.spec.js

# 开发配置
.eslintrc.js
.prettierrc
tsconfig.json

# CI 配置
.github/
.gitlab-ci.yml

# 文档
docs/
*.md
!README.md
```

## 九、安全注意事项

### 9.1 敏感信息保护

```bash
# ✅ 必须忽略的敏感文件
.env
.env.local
.env.*.local

# API 密钥
*.key
*.pem
*.cert
*.crt
**/secrets/
credentials.json
service-account.json

# 数据库
*.sql
*.db
*.sqlite

# 配置文件（包含密码）
config.production.js
.aws/
.ssh/
```

### 9.2 防止意外提交

```bash
# 1. 使用 .env.example
.env                        # 忽略实际配置
!.env.example               # 保留示例文件

# 2. 使用前缀命名
.env.*                      # 忽略所有环境变量文件
!.env.example               # 保留示例

# 3. 敏感目录完全忽略
secrets/
credentials/
.aws/
.ssh/
```

### 9.3 已提交的敏感信息

**如果已经提交了敏感信息**：

```bash
# 1. 从历史记录中完全移除（谨慎使用）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. 使用 BFG Repo-Cleaner（推荐）
# 下载 BFG：https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 3. 强制推送
git push origin --force --all

# ⚠️ 重要：即使删除了文件，也要：
# - 撤销所有暴露的密钥和密码
# - 生成新的凭证
# - 通知团队成员
```

## 十、常见项目完整示例

### 10.1 完整的 Vue 3 项目

```bash
# ============================================
# 依赖
# ============================================
node_modules/
.pnp
.pnp.js

# ============================================
# 构建产物
# ============================================
dist/
dist-ssr/
*.local

# Vite
.vite/

# Nuxt
.nuxt/
.output/
.cache/

# ============================================
# 环境变量
# ============================================
.env
.env.local
.env.*.local
!.env.example

# ============================================
# 日志
# ============================================
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# ============================================
# 编辑器和 IDE
# ============================================
.vscode/*
!.vscode/extensions.json
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# ============================================
# 操作系统
# ============================================
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
Desktop.ini

# ============================================
# 测试
# ============================================
coverage/
.nyc_output/
test-results/
playwright-report/

# ============================================
# 自动生成的文件
# ============================================
auto-imports.d.ts
components.d.ts
typed-router.d.ts

# ============================================
# 临时文件
# ============================================
*.tmp
*.temp
*.bak
*.swp
*~
```

### 10.2 完整的 React + TypeScript 项目

```bash
# ============================================
# 依赖
# ============================================
node_modules/
.pnp/
.pnp.js

# ============================================
# 构建产物
# ============================================
build/
dist/
.next/
out/

# ============================================
# TypeScript
# ============================================
*.tsbuildinfo
next-env.d.ts

# ============================================
# 环境变量
# ============================================
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
!.env.example

# ============================================
# 日志
# ============================================
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# ============================================
# 测试
# ============================================
coverage/
.nyc_output/
jest-results/

# ============================================
# 编辑器和 IDE
# ============================================
.vscode/*
!.vscode/extensions.json
!.vscode/launch.json
.idea/
*.swp
*.swo
*~

# ============================================
# 操作系统
# ============================================
.DS_Store
Thumbs.db

# ============================================
# 调试
# ============================================
.vercel
.turbo
```

## 十一、工具和资源

### 11.1 在线工具

| 工具             | 链接                                        | 说明                       |
| ---------------- | ------------------------------------------- | -------------------------- |
| gitignore.io     | https://www.toptal.com/developers/gitignore | 根据技术栈生成 .gitignore  |
| GitHub 模板      | https://github.com/github/gitignore         | 官方 .gitignore 模板仓库   |
| Git Check-ignore | -                                           | 使用 `git check-ignore -v` |

### 11.2 VS Code 扩展

```json
{
  "recommendations": [
    "codezombiech.gitignore" // .gitignore 语法高亮和自动补全
  ]
}
```

### 11.3 命令行工具

```bash
# 生成 .gitignore（使用 gitignore.io API）
gi() { curl -sL https://www.toptal.com/developers/gitignore/api/$@ ;}

# 使用示例
gi node,vue,vscode > .gitignore

# 查看可用模板
gi list
```

### 11.4 Git 钩子

创建提交前检查：

```bash
# .husky/pre-commit
#!/bin/sh

# 检查是否包含敏感文件
if git diff --cached --name-only | grep -E "\.env$|\.key$|\.pem$|secrets/"; then
  echo "❌ Error: 检测到敏感文件，请检查 .gitignore"
  exit 1
fi
```

## 十二、总结

### 12.1 最佳实践清单

- ✅ 在项目初始化时立即创建 `.gitignore`
- ✅ 使用模板（gitignore.io 或 GitHub 模板）作为起点
- ✅ 将规则按类型分组并添加注释
- ✅ 忽略所有构建产物和依赖
- ✅ 忽略所有敏感信息（.env、密钥等）
- ✅ 使用 `.env.example` 提供环境变量示例
- ✅ 定期检查和更新 `.gitignore`
- ✅ 使用 `git check-ignore` 调试规则
- ✅ 配置全局 `.gitignore` 处理操作系统和编辑器文件
- ✅ 在 README 中说明特殊的忽略规则

### 12.2 常用命令速查

```bash
# 创建 .gitignore
touch .gitignore

# 查看被忽略的文件
git status --ignored

# 检查文件是否被忽略
git check-ignore -v <file>

# 移除已跟踪的文件
git rm --cached <file>
git rm --cached -r <directory>

# 清理未跟踪的文件
git clean -fd

# 配置全局 .gitignore
git config --global core.excludesfile ~/.gitignore_global

# 生成 .gitignore（使用 API）
curl -L https://www.toptal.com/developers/gitignore/api/node,vue > .gitignore
```

### 12.3 学习建议

1. **从模板开始**：使用 gitignore.io 或 GitHub 模板
2. **理解语法**：掌握通配符和路径规则
3. **分类管理**：按类型组织规则，添加清晰的注释
4. **定期更新**：随着项目发展调整规则
5. **团队协作**：统一团队的忽略规则
6. **安全第一**：永远不要提交敏感信息

## 参考资源

- [Git 官方文档 - gitignore](https://git-scm.com/docs/gitignore)
- [GitHub gitignore 模板](https://github.com/github/gitignore)
- [gitignore.io](https://www.toptal.com/developers/gitignore)
- [Git Book - 忽略文件](https://git-scm.com/book/zh/v2/Git-基础-记录每次更新到仓库#忽略文件)
- [Atlassian Git Ignore 教程](https://www.atlassian.com/git/tutorials/saving-changes/gitignore)
