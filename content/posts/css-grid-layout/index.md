---
title: "CSS Grid 布局完全指南"
date: 2026-01-28
draft: false
description: "从零开始学习 CSS Grid 布局，掌握现代网页布局的核心技术。"
tags: ["CSS", "布局", "前端"]
categories: ["前端开发"]
---

## 什么是 CSS Grid？

CSS Grid 是二维布局系统，可以同时处理行和列，是现代网页布局的首选方案。

## 基础概念

```css
.container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto;
  gap: 1rem;
}
```

## 常用布局模式

### 经典两栏布局

```css
.layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  min-height: 100vh;
}
```

### 响应式卡片网格

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}
```

### Holy Grail 布局

```css
.holy-grail {
  display: grid;
  grid-template:
    "header  header  header" auto
    "sidebar content aside" 1fr
    "footer  footer  footer" auto
    / 200px 1fr 200px;
  min-height: 100vh;
}

.header {
  grid-area: header;
}
.sidebar {
  grid-area: sidebar;
}
.content {
  grid-area: content;
}
.aside {
  grid-area: aside;
}
.footer {
  grid-area: footer;
}
```

## Grid vs Flexbox

| 特性     | Grid         | Flexbox      |
| -------- | ------------ | ------------ |
| 维度     | 二维         | 一维         |
| 适用场景 | 页面整体布局 | 组件内部排列 |
| 对齐     | 行列同时控制 | 主轴+交叉轴  |

实际项目中，Grid 和 Flexbox 经常配合使用，各取所长。
