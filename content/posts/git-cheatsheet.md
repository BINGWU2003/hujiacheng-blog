---
title: "Git 常用命令速查手册"
date: 2026-02-10
draft: false
author: "hujiacheng"
description: "整理日常开发中最常用的 Git 命令，涵盖基础操作、分支管理、撤销回退、远程协作等场景，方便随时查阅。"
tags: ["Git", "工具", "效率"]
categories: ["工具"]
showToc: true
TocOpen: false
---

## 基础操作

```bash
# 初始化仓库
git init

# 查看状态
git status

# 添加文件到暂存区
git add .                  # 添加所有文件
git add <file>             # 添加指定文件

# 提交
git commit -m "feat: 提交说明"

# 查看提交日志
git log --oneline --graph
```

## 分支管理

```bash
# 查看分支
git branch          # 本地分支
git branch -a       # 所有分支（含远程）

# 创建并切换分支
git checkout -b feature/new-feature
# 或使用新语法
git switch -c feature/new-feature

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

## 撤销与回退

这是最容易搞混的部分，按场景整理：

### 场景 1：修改了文件，还没 add

```bash
git checkout -- <file>
# 或
git restore <file>
```

### 场景 2：已经 add，还没 commit

```bash
git reset HEAD <file>
# 或
git restore --staged <file>
```

### 场景 3：已经 commit，想撤回

```bash
# 保留修改，撤回 commit
git reset --soft HEAD~1

# 撤回 commit 和 add，保留修改
git reset --mixed HEAD~1

# 彻底回退，丢弃修改（慎用！）
git reset --hard HEAD~1
```

## 远程操作

```bash
# 添加远程仓库
git remote add origin <url>

# 推送
git push -u origin main

# 拉取
git pull origin main

# 查看远程信息
git remote -v
```

## 实用技巧

### Stash 暂存

开发到一半需要切分支？用 stash：

```bash
git stash                    # 暂存当前修改
git stash list               # 查看暂存列表
git stash pop                # 恢复最近的暂存
git stash drop stash@{0}     # 删除指定暂存
```

### Cherry-pick

从其他分支摘取某个 commit：

```bash
git cherry-pick <commit-hash>
```

### 修改最近的 commit 信息

```bash
git commit --amend -m "新的提交信息"
```

## Commit 规范

推荐使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

| 类型       | 说明                   |
| ---------- | ---------------------- |
| `feat`     | 新功能                 |
| `fix`      | 修复 Bug               |
| `docs`     | 文档更新               |
| `style`    | 代码格式（不影响逻辑） |
| `refactor` | 重构                   |
| `test`     | 测试相关               |
| `chore`    | 构建/工具变动          |

---

> 熟练掌握 Git 是高效协作的基础，建议收藏备用。
