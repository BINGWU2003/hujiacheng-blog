---
title: "Hugo + PaperMod 博客搭建指南"
date: 2026-02-11
draft: false
author: "hujiacheng"
description: "从零开始搭建一个基于 Hugo 和 PaperMod 主题的个人技术博客，包含配置优化、内容组织和部署上线的完整流程。"
tags: ["Hugo", "博客", "PaperMod", "静态网站"]
categories: ["建站"]
showToc: true
TocOpen: true
weight: 1
---

## 前言

搭建个人技术博客是每个开发者的必经之路。相比动态博客（如 WordPress），静态博客有以下优势：

- **速度快** — 纯静态 HTML，无需数据库查询
- **安全性高** — 没有后端服务，攻击面极小
- **成本低** — 可免费托管在 GitHub Pages / Vercel / Netlify
- **专注写作** — 使用 Markdown 书写，版本控制友好

本文记录我使用 Hugo + PaperMod 搭建博客的完整过程。

## 环境准备

### 安装 Hugo

```bash
# macOS
brew install hugo

# Windows (Scoop)
scoop install hugo-extended

# 验证安装
hugo version
```

### 创建新站点

```bash
hugo new site my-blog
cd my-blog
git init
```

### 安装 PaperMod 主题

```bash
git submodule add https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
```

## 核心配置

在 `hugo.toml` 中添加基础配置：

```toml
baseURL = "https://yourdomain.com/"
languageCode = "zh-cn"
title = "我的技术博客"
theme = "PaperMod"
paginate = 10

[params]
  ShowReadingTime = true
  ShowCodeCopyButtons = true
  ShowToc = true
```

### 几个关键配置说明

| 配置项                | 作用                  |
| --------------------- | --------------------- |
| `ShowReadingTime`     | 显示预计阅读时间      |
| `ShowCodeCopyButtons` | 代码块显示复制按钮    |
| `ShowToc`             | 显示文章目录          |
| `defaultTheme: auto`  | 跟随系统深色/浅色模式 |

## 写第一篇文章

```bash
hugo new posts/my-first-post.md
```

编辑生成的文件，将 `draft: true` 改为 `draft: false`，然后添加你的内容。

## 本地预览

```bash
hugo server -D
```

访问 `http://localhost:1313` 即可预览。

## 部署

推荐使用 GitHub Actions 自动部署到 GitHub Pages：

1. 将代码推送到 GitHub 仓库
2. 在 Settings → Pages 中选择 GitHub Actions 作为部署源
3. 添加 `.github/workflows/hugo.yml` 工作流文件

每次 push 代码后会自动构建并部署。

## 总结

Hugo + PaperMod 是一个高效、美观的博客方案。后续我会继续分享：

- 自定义主题配置的进阶技巧
- SEO 优化实践
- 评论系统集成

---

> 如果你也在搭建博客，欢迎交流！
