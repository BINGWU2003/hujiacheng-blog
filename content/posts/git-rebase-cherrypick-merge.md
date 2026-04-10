---
title: "Git 分支整合：rebase、cherry-pick、merge 详解"
date: 2026-04-10
draft: false
description: ""
tags: ["Git", "分支", "rebase", "cherry-pick", "merge"]
categories: ["博客"]
---

## 目录

- [核心区别一览](#核心区别一览)
- [git merge](#git-merge)
  - [原理](#merge-原理)
  - [Fast-forward 合并](#fast-forward-合并)
  - [三方合并](#三方合并)
  - [常用命令](#merge-常用命令)
  - [冲突处理](#merge-冲突处理)
  - [使用场景](#merge-使用场景)
- [git rebase](#git-rebase)
  - [原理](#rebase-原理)
  - [常用命令](#rebase-常用命令)
  - [交互式 rebase](#交互式-rebase)
  - [冲突处理](#rebase-冲突处理)
  - [使用场景](#rebase-使用场景)
  - [注意事项](#rebase-注意事项)
- [git cherry-pick](#git-cherry-pick)
  - [原理](#cherry-pick-原理)
  - [常用命令](#cherry-pick-常用命令)
  - [冲突处理](#cherry-pick-冲突处理)
  - [使用场景](#cherry-pick-使用场景)
- [对比总结](#对比总结)
- [选择指南](#选择指南)

---

## 核心区别一览

| 对比项 | `git merge` | `git rebase` | `git cherry-pick` |
|--------|------------|--------------|-------------------|
| 操作粒度 | 整个分支 | 整个分支 | 单个或多个指定提交 |
| 历史记录 | 保留分叉，有 merge commit | 线性，无分叉 | 线性，复制指定提交 |
| 原始 commit hash | 不变 | **会改变** | **会改变** |
| 冲突处理 | 一次性处理 | 逐个提交处理 | 逐个提交处理 |
| 适用场景 | 功能合并到主分支 | 同步主分支最新代码 | 精准摘取某个提交 |

---

## git merge

### merge 原理

merge 把两个分支的历史**汇合**在一起，根据两个分支的关系不同，分为两种情况。

---

### Fast-forward 合并

当目标分支是当前分支的**直接祖先**时（即没有分叉），Git 直接把指针往前移，**不会产生新的 commit**。

```
merge 前：
main:    A → B
                ↘
feature:          C → D（HEAD on feature）

git checkout main
git merge feature

merge 后（fast-forward）：
main:    A → B → C → D（HEAD on main）
```

此时历史完全线性，看不出曾经有 feature 分支的痕迹。

如果想强制保留分支痕迹，可以禁用 fast-forward：

```bash
git merge feature --no-ff
```

```
merge 后（--no-ff）：
main:    A → B ──────────────→ M（merge commit）
                ↘            ↗
feature:          C → D
```

---

### 三方合并

当两个分支**都有各自新的提交**时，Git 找到公共祖先，进行三方合并，并生成一个新的 **merge commit**。

```
merge 前：
main:    A → B → C → D
                  ↑
                  公共祖先
feature: A → B → C → E → F

git checkout main
git merge feature

merge 后：
main:    A → B → C → D ──────→ M（merge commit，有两个父节点：D 和 F）
                  ↘           ↗
feature:            E → F
```

merge commit `M` 有两个父节点，记录了完整的分支历史。

---

### merge 常用命令

```bash
# 把 feature 合并到当前分支
git merge feature

# 禁用 fast-forward，强制生成 merge commit
git merge feature --no-ff

# 合并但不自动提交（改动放到暂存区，手动 commit）
git merge feature --no-commit

# 把 feature 所有提交压缩成一个提交合并（不保留 feature 的历史）
git merge feature --squash

# 放弃当前合并
git merge --abort
```

#### `--squash` 的效果

```
merge --squash 前：
main:    A → B → C
feature: A → B → D → E → F

git merge feature --squash

merge --squash 后：
main:    A → B → C → S（squash commit，包含 D/E/F 的所有改动，需手动 commit）
feature 历史不会出现在 main 中
```

---

### merge 冲突处理

```bash
git merge feature
# 提示：CONFLICT (content): Merge conflict in file.js

# 冲突文件中会出现如下标记：
# <<<<<<< HEAD
# 当前分支的内容
# =======
# 合并进来的内容
# >>>>>>> feature

# 1. 手动编辑冲突文件，保留正确内容，删除标记符
# 2. 标记已解决
git add file.js

# 3. 完成合并
git commit

# 或直接放弃
git merge --abort
```

---

### merge 使用场景

**场景 1：feature 分支开发完成，合并到 main**
```bash
git checkout main
git merge feature --no-ff -m "feat: 合并用户登录功能"
```

**场景 2：合并但保持 main 历史整洁（squash）**
```bash
git checkout main
git merge feature --squash
git commit -m "feat: 用户登录功能（合并自 feature/login）"
```

**场景 3：同步远程 main 的最新代码到本地**
```bash
git fetch origin
git merge origin/main
```

---

## git rebase

### rebase 原理

rebase 的核心是：**找到两个分支的公共祖先，把当前分支独有的提交逐个"重新应用"到目标分支的顶端**。

原始提交不会被修改，而是生成内容相同但 **hash 全新**的提交副本。

```
rebase 前：
main:    A → B → C → D
                  ↑
                  公共祖先（base）
feature: A → B → C → E → F → G

# 在 feature 分支上执行
git rebase main
```

**rebase 内部执行步骤：**

```
第一步：找到公共祖先 C
第二步：把 feature 独有的提交 E、F、G 暂存（记录 patch）
第三步：把 feature 的 HEAD 移到 main 的顶端 D
第四步：逐个重新应用 E → F → G，生成 E'、F'、G'
```

```
rebase 后：
main:    A → B → C → D
                       ↘
feature:                 E' → F' → G'（新的 hash）
```

此时 feature 变成了 D 的直接后代，再合并到 main 就会触发 fast-forward，历史完全线性：

```
git checkout main
git merge feature

最终结果：
main:    A → B → C → D → E' → F' → G'
```

---

### rebase 常用命令

```bash
# 把当前分支 rebase 到 main 的顶端
git rebase main

# 把当前分支 rebase 到指定 commit
git rebase abc1234

# 变基远程分支（同步同事的最新提交）
git fetch origin
git rebase origin/main

# 放弃 rebase，恢复到执行前状态
git rebase --abort

# 解决冲突后继续
git rebase --continue

# 跳过当前冲突的提交（谨慎使用）
git rebase --skip
```

---

### 交互式 rebase

交互式 rebase 是 rebase 最强大的功能，可以对提交历史进行**自由整理**。

```bash
# 对最近 3 个提交进行交互式操作
git rebase -i HEAD~3
```

执行后会打开编辑器，列出最近 3 个提交：

```
pick abc1111 feat: 添加登录页面
pick abc2222 fix: 修复按钮样式
pick abc3333 feat: 添加登录接口

# 把 pick 改成以下命令来操作：
# pick   = 保留该提交（默认）
# reword = 保留提交，但修改 commit message
# edit   = 保留提交，但暂停以便修改内容
# squash = 合并到上一个提交，保留 commit message
# fixup  = 合并到上一个提交，丢弃自己的 commit message
# drop   = 删除该提交
```

#### 常见整理操作

**合并零碎提交（squash）**

```
修改前：
pick abc1111 feat: 添加登录页面
pick abc2222 fix: 修复登录页面样式
pick abc3333 fix: 再次修复登录页面

修改后：
pick abc1111 feat: 添加登录页面
squash abc2222 fix: 修复登录页面样式
squash abc3333 fix: 再次修复登录页面

结果：三个提交合并为一个
```

**修改提交信息（reword）**

```
pick   abc1111 feat: 添加登录页面
reword abc2222 fix typo          ← 保存后会弹出编辑框让你重写 message
pick   abc3333 feat: 添加登录接口
```

**删除某个提交（drop）**

```
pick abc1111 feat: 添加登录页面
drop abc2222 调试代码，不该提交   ← 该提交会被删除
pick abc3333 feat: 添加登录接口
```

**调整提交顺序**

```
# 直接调整行的顺序即可
pick abc3333 feat: 添加登录接口
pick abc1111 feat: 添加登录页面
pick abc2222 fix: 修复登录页面样式
```

---

### rebase 冲突处理

rebase 是**逐个提交**重新应用，每个提交都可能触发冲突，需要逐个解决。

```bash
git rebase main
# 提示：CONFLICT (content): Merge conflict in file.js
# 当前暂停在第 2 个提交（共 3 个）

# 1. 解决冲突
# 编辑 file.js...

# 2. 标记已解决
git add file.js

# 3. 继续处理下一个提交
git rebase --continue

# 如果下一个提交又有冲突，重复上面步骤
# 直到所有提交都处理完毕

# 任何时候想放弃
git rebase --abort
```

---

### rebase 使用场景

**场景 1：同步主分支，保持线性历史**
```bash
# 同事往 main 推了新代码，把自己的 feature 分支同步过来
git checkout feature
git fetch origin
git rebase origin/main
```

**场景 2：提交前整理本地提交记录**
```bash
# 开发过程中产生了很多零碎提交，push 前整理干净
git rebase -i HEAD~5
# 把相关的 fix 提交 squash 到对应的 feat 提交里
```

**场景 3：合并到主分支，保持历史整洁**
```bash
git checkout feature
git rebase main          # 先把 feature rebase 到 main 最新状态
git checkout main
git merge feature        # 此时触发 fast-forward，历史线性
```

---

### rebase 注意事项

> ⚠️ **黄金法则：不要对已经 push 到公共分支的提交进行 rebase**

rebase 会改变提交的 hash，如果别人已经基于你的提交进行了开发，rebase 之后他们的历史就乱了。

```
错误示范：
1. 你把 feature push 到远程
2. 同事基于你的 feature 拉取并开发
3. 你对 feature 做了 rebase，强制推送（force push）
4. 同事的本地历史和远程产生冲突 → 一团糟

正确做法：
- 只对本地未 push 的提交进行 rebase
- 已 push 的提交需要用 merge 或 revert
```

---

## git cherry-pick

### cherry-pick 原理

cherry-pick 是**精准摘取**：把另一个分支上的某个（或某几个）提交，单独拿过来应用到当前分支。

和 rebase 类似，也是重新应用提交内容，生成新的 hash。

```
cherry-pick 前：
main:    A → B → C（HEAD）
feature: A → D → E → F → G

# 只想把 E 带到 main，不想合并整个 feature
git checkout main
git cherry-pick E的hash

cherry-pick 后：
main:    A → B → C → E'（新 hash，内容与 E 相同）
feature: A → D → E → F → G（不受影响）
```

---

### cherry-pick 常用命令

```bash
# 摘取单个提交
git cherry-pick abc1234

# 摘取多个不连续的提交（按顺序应用）
git cherry-pick abc1234 def5678 ghi9012

# 摘取连续范围（不含左端，含右端）
git cherry-pick E..G
# 等价于摘取 F、G

# 摘取连续范围（含两端，使用 ^ 符号）
git cherry-pick E^..G
# 等价于摘取 E、F、G

# 摘取但不自动提交，改动放到暂存区
git cherry-pick abc1234 -n

# 放弃当前 cherry-pick
git cherry-pick --abort

# 解决冲突后继续
git cherry-pick --continue
```

---

### cherry-pick 冲突处理

```bash
git cherry-pick abc1234
# 提示：CONFLICT (content): Merge conflict in file.js

# 1. 解决冲突文件
# 2. 标记已解决
git add file.js

# 3. 继续完成
git cherry-pick --continue

# 或放弃
git cherry-pick --abort
```

---

### cherry-pick 使用场景

**场景 1：热修复同步到多个版本分支**

```bash
# 在 fix 分支上修了一个 bug（commit: abc1234）
# 需要同步到 main、v1.0、v2.0 三个分支

git checkout main
git cherry-pick abc1234

git checkout v1.0
git cherry-pick abc1234

git checkout v2.0
git cherry-pick abc1234
```

**场景 2：提交到了错误的分支**

```bash
# 不小心把提交做在了 main 上，应该在 feature 上
git checkout feature
git cherry-pick abc1234    # 把提交复制到 feature

git checkout main
git reset --hard HEAD~1    # 把 main 上的错误提交删掉
```

**场景 3：只想要 feature 分支的部分功能**

```bash
# feature 分支开发了 10 个提交，只想要其中 2 个
git checkout main
git cherry-pick abc1234 def5678
```

---

## 对比总结

### 历史记录形态对比

```
初始状态：
main:    A → B → C → D
feature: A → B → E → F → G
                ↑
               公共祖先 B

─────────────────────────────────────────────

git merge feature（三方合并）：

main:    A → B → C → D ────────→ M
                      ↗  (merge commit)
feature:    E → F → G

特点：保留分叉历史，有 merge commit

─────────────────────────────────────────────

git merge feature --no-ff：

main:    A → B → C → D ────────→ M
                  ↘             ↗
feature:            E → F → G

特点：即使能 fast-forward 也强制保留分支痕迹

─────────────────────────────────────────────

git rebase main（在 feature 上）后再 merge：

main:    A → B → C → D → E' → F' → G'

特点：完全线性，看不出分支历史，hash 已变

─────────────────────────────────────────────

git cherry-pick E（只摘取 E）：

main:    A → B → C → D → E'

feature: A → B → E → F → G（不变）

特点：点对点精准复制，粒度最细
```

---

### 三者核心差异

| | merge | rebase | cherry-pick |
|---|---|---|---|
| **历史** | 有分叉 | 线性 | 线性 |
| **hash 变化** | 不变 | 变 | 变 |
| **操作对象** | 整个分支 | 整个分支 | 指定提交 |
| **冲突次数** | 一次 | 多次（每个提交） | 多次（每个提交） |
| **是否保留来源信息** | ✅ merge commit 记录了来源 | ❌ 看不出来自哪个分支 | ❌ 看不出原始来源 |
| **公共分支安全性** | ✅ 安全 | ⚠️ 不能对已 push 使用 | ✅ 安全 |

---

## 选择指南

```
需要把 feature 合并到主分支？
  ├─ 想保留完整分支历史？              → git merge --no-ff
  ├─ 想要线性历史、整洁的 log？         → git rebase + git merge（fast-forward）
  └─ 想把 feature 所有提交压成一个？    → git merge --squash

需要同步主分支的最新代码到 feature？
  ├─ 想线性历史（推荐）？               → git rebase main
  └─ 想保留时间线？                     → git merge main

只需要某个分支的一个或几个提交？
  └─                                   → git cherry-pick

误操作，提交到了错误分支？
  └─ cherry-pick 到正确分支 + reset 原分支

同一个 bug fix 需要同步到多个版本分支？
  └─                                   → git cherry-pick
```

---

> **一句话记忆：**
> - `merge` 是**汇合**，历史有分叉，适合最终合并
> - `rebase` 是**嫁接**，历史变线性，适合日常同步
> - `cherry-pick` 是**摘樱桃**，精准复制，适合跨分支搬运提交
