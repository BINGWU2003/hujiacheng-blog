---
title: "Git 代码回退：revert 与 reset 详解"
date: 2026-04-10
draft: false
description: ""
tags: ["Git", "revert", "reset"]
categories: ["博客"]
---

## 目录

- [核心区别一览](#核心区别一览)
- [git reset](#git-reset)
  - [原理](#reset-原理)
  - [三种模式](#三种模式)
  - [常用命令](#reset-常用命令)
  - [使用场景](#reset-使用场景)
  - [注意事项](#reset-注意事项)
- [git revert](#git-revert)
  - [原理](#revert-原理)
  - [常用命令](#revert-常用命令)
  - [重要参数](#重要参数)
  - [撤销 merge commit](#撤销-merge-commit)
  - [遇到冲突](#遇到冲突)
  - [使用场景](#revert-使用场景)
- [对比总结](#对比总结)
- [操作流程图](#操作流程图)

---

## 核心区别一览

| 对比项 | `git reset` | `git revert` |
|--------|------------|--------------|
| 历史记录 | **删除**目标提交之后的历史 | **保留**所有历史，新增一个反向提交 |
| 操作方式 | 移动 HEAD 指针 | 生成新的 commit |
| 适用场景 | 本地未 push 的提交 | 已 push 到远程、多人协作 |
| 是否影响他人 | 会（强推会覆盖远程历史） | 不会 |
| 可恢复性 | `--hard` 模式下改动直接丢弃 | 随时可以 revert 那个 revert commit |

---

## git reset

### reset 原理

`git reset` 通过**移动 HEAD 指针**来实现回退，目标提交之后的记录会从历史中消失。

```
执行前：
A → B → C → D（HEAD）

git reset B

执行后：
A → B（HEAD）

C、D 从分支历史中消失（但短期内可通过 git reflog 找回）
```

---

### 三种模式

`git reset` 有三种模式，区别在于对**暂存区**和**工作区**的处理方式不同。

```
提交历史   暂存区（Index）   工作区（Working Directory）
  回退         保留                   保留             ← --soft
  回退         清空                   保留             ← --mixed（默认）
  回退         清空                   丢弃             ← --hard
```

#### `--soft`

```bash
git reset --soft HEAD~1
```

- 提交历史回退一个
- 改动**保留在暂存区**，相当于撤销了 `git commit`，但 `git add` 的结果还在
- 适合：提交信息写错了，想重新提交

```
执行后状态：
$ git status
Changes to be committed:
  modified: file.js   ← 改动还在暂存区
```

#### `--mixed`（默认）

```bash
git reset --mixed HEAD~1
# 等同于
git reset HEAD~1
```

- 提交历史回退一个
- 改动**保留在工作区**，相当于撤销了 `git commit` 和 `git add`
- 适合：提交了不该提交的内容，想重新整理再提交

```
执行后状态：
$ git status
Changes not staged for commit:
  modified: file.js   ← 改动在工作区，需要重新 add
```

#### `--hard`

```bash
git reset --hard HEAD~1
```

- 提交历史回退一个
- 改动**完全丢弃**，工作区恢复到目标提交时的状态
- 适合：彻底放弃某些提交，不想保留任何改动
- ⚠️ **危险操作**，丢失的改动无法通过常规方式找回

```
执行后状态：
$ git status
nothing to commit, working tree clean
```

---

### reset 常用命令

```bash
# 回退到上一个提交
git reset HEAD~1
git reset HEAD^        # 等同写法

# 回退多个提交
git reset HEAD~3       # 回退3个提交

# 回退到指定 commit hash
git reset abc1234
git reset --hard abc1234

# 只撤销暂存区（unstage），不影响提交历史和工作区
git reset HEAD <file>
# 或更新写法
git restore --staged <file>

# 查看 reflog，找回 reset 丢失的提交
git reflog
git reset --hard abc1234   # 通过 reflog 中的 hash 找回
```

---

### reset 使用场景

**场景 1：提交信息写错了**
```bash
git reset --soft HEAD~1
git commit -m "正确的提交信息"
```

**场景 2：提交了不该提交的文件**
```bash
git reset HEAD~1          # 改动回到工作区
# 重新整理，只 add 需要的文件
git add src/
git commit -m "只提交 src 目录的改动"
```

**场景 3：彻底放弃最近几次提交**
```bash
git reset --hard HEAD~3
```

**场景 4：撤销暂存区（已 add 但未 commit）**
```bash
git restore --staged file.js
```

---

### reset 注意事项

> ⚠️ **已经 push 到远程的分支，不要用 reset**

如果已经 push，执行 reset 后本地历史落后于远程，需要强制推送：

```bash
git push --force   # 危险！会覆盖远程历史，影响其他协作者
```

**唯一安全的例外**：完全个人使用的分支（没有其他人在用），此时可以谨慎使用。

---

## git revert

### revert 原理

`git revert` **不修改历史**，而是分析目标提交做了哪些改动，生成一个**完全相反的新提交**来抵消它。

```
执行前：
A → B → C → D（HEAD）

git revert C

执行后：
A → B → C → D → C'（HEAD）
                  ↑
                  C 的反向操作：
                  C 加了什么 → C' 删掉什么
                  C 删了什么 → C' 加回什么
```

C 依然存在于历史中，只是其效果被 C' 抵消了。

#### 具体例子

假设提交 C 做了以下操作：
- 删除了函数 `add()`
- 新增了文件 `ab.vue` 并写了一些代码

执行 `git revert C` 后，C' 会：
- 把 `add()` 函数**加回来**
- 把 `ab.vue` **整个删掉**

最终代码状态回到 C 之前，但历史里 C 和 C' 都完整保留。

---

### revert 常用命令

```bash
# 撤销最新提交
git revert HEAD

# 撤销倒数第 2 个提交
git revert HEAD~1

# 撤销指定 hash 的提交
git revert abc1234

# 撤销多个不连续的提交（每个都会生成一个 revert commit）
git revert abc1234 def5678

# 撤销一个连续范围（不含左端，含右端）
git revert HEAD~3..HEAD~1
```

---

### 重要参数

#### `--no-edit`

不弹出 commit 信息编辑器，直接使用默认信息提交：

```bash
git revert HEAD --no-edit
# 默认 commit message 格式：Revert "原始提交信息"
```

#### `-n` / `--no-commit`

只应用反向改动，不自动生成提交，改动停留在暂存区：

```bash
# 适合撤销多个提交但合并成一个 revert commit
git revert HEAD -n
git revert HEAD~1 -n
git revert HEAD~2 -n
git commit -m "revert: 撤销最近三次提交"
```

---

### 撤销 merge commit

merge commit 有**两个父节点**，revert 时必须用 `-m` 指定以哪个父节点为基准：

```bash
git revert <merge-commit-hash> -m 1
```

`-m 1` 表示保留第一个父节点（通常是 main 分支）的视角，撤销合并进来的内容。

```
合并前：
main:    A → B
                ↘
feature:  X → Y → merge commit（父节点1: B，父节点2: Y）

git revert merge_commit -m 1
# 以 B（main 侧）为基准，撤销 X、Y 带来的所有改动
```

> ⚠️ 撤销 merge commit 后，如果之后想重新合并该 feature 分支，需要先 revert 那个 revert commit，否则 Git 会认为这些改动已经存在过。

---

### 遇到冲突

revert 也可能产生冲突，处理流程如下：

```bash
git revert abc1234
# 提示：CONFLICT (content): Merge conflict in file.js

# 第一步：手动打开冲突文件，解决冲突
# 第二步：标记已解决
git add file.js

# 第三步：继续完成 revert
git revert --continue

# 或者放弃这次 revert，回到执行前状态
git revert --abort
```

---

### revert 使用场景

**场景 1：撤销已经 push 的错误提交**
```bash
git revert abc1234
git push   # 正常推送，不影响他人
```

**场景 2：撤销多个提交，合并成一个记录**
```bash
git revert HEAD~2..HEAD -n
git commit -m "revert: 回退功能 X 相关的三次提交"
```

**场景 3：撤销某个历史中间的提交**
```bash
# 不影响该提交之后的其他提交
git revert abc1234
```

---

## 对比总结

### 执行结果对比

```
初始状态：A → B → C → D（HEAD）

git reset B：
  A → B（HEAD）             历史被截断，C/D 消失

git revert C：
  A → B → C → D → C'（HEAD）  历史完整，C 被抵消
```

### 选择指南

```
代码还没有 push？
  └─ 想彻底丢弃改动     → git reset --hard
  └─ 想保留改动重新整理  → git reset --mixed / --soft

代码已经 push，多人协作？
  └─ 只能用              → git revert

只是想撤销暂存区（未 commit）？
  └─                     → git restore --staged <file>

只是想丢弃工作区改动（未 add）？
  └─                     → git restore <file>
  └─ 或                  → git checkout -- <file>
```

### 安全性对比

| 操作 | 能否找回 | 对他人影响 |
|------|---------|-----------|
| `reset --soft` | ✅ 改动还在 | ❌ push 后影响他人 |
| `reset --mixed` | ✅ 改动还在 | ❌ push 后影响他人 |
| `reset --hard` | ⚠️ reflog 可短期找回 | ❌ push 后影响他人 |
| `revert` | ✅ 历史完整保留 | ✅ 安全，不影响他人 |

---

## 操作流程图

```
发现问题，需要回退代码
        │
        ▼
  代码已经 push 了吗？
   │              │
  Yes             No
   │              │
   ▼              ▼
git revert    想保留改动吗？
              │         │
             Yes         No
              │          │
              ▼          ▼
        reset --soft  reset --hard
        reset --mixed  （慎用！）
```

---

> **黄金法则：已经推送到公共分支的提交，只用 `git revert`，永远不要对公共分支使用 `git reset`。**
