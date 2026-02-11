---
title: "Markdown 写作技巧与最佳实践"
date: 2026-02-09
draft: false
author: "hujiacheng"
description: "提升 Markdown 写作效率的实用技巧，包括常用语法、扩展功能、排版建议，帮助你写出结构清晰的技术文章。"
tags: ["Markdown", "写作", "效率"]
categories: ["写作"]
showToc: true
TocOpen: false
---

## 为什么用 Markdown？

Markdown 是技术写作的事实标准：

- **简洁** — 专注内容而非格式
- **通用** — GitHub、博客、文档都支持
- **可移植** — 纯文本格式，任何编辑器都能打开
- **版本控制友好** — 与 Git 完美配合

## 常用语法速查

### 标题

```markdown
# 一级标题

## 二级标题

### 三级标题
```

> **建议**：文章中只用一个 `#` 作为标题，正文从 `##` 开始。

### 文本样式

```markdown
**粗体文本**
_斜体文本_
~~删除线~~
`行内代码`
```

### 列表

```markdown
- 无序列表项 1
- 无序列表项 2
  - 嵌套项

1. 有序列表项 1
2. 有序列表项 2
```

### 代码块

使用三个反引号包裹，并指定语言：

````markdown
```javascript
function hello() {
  console.log("Hello, World!");
}
```
````

### 表格

```markdown
| 列 1 | 列 2 | 列 3 |
| ---- | ---- | ---- |
| 内容 | 内容 | 内容 |
```

### 链接与图片

```markdown
[链接文字](https://example.com)
![图片描述](/images/example.png)
```

## 写作排版建议

### 1. 中英文之间加空格

```
[O] 使用 Hugo 搭建博客
[X] 使用Hugo搭建博客
```

### 2. 善用引用块

> 引用块适合用来放重要提示、注意事项、引用他人的话。

### 3. 合理使用标题层级

文章结构应该像一棵树：

```
## 一级主题
### 二级细节
### 二级细节
## 一级主题
### 二级细节
```

### 4. 代码块指定语言

始终为代码块指定语言，这样才有语法高亮：

```python
# 指定了 python，有语法高亮
def greet(name):
    return f"Hello, {name}!"
```

### 5. 使用任务列表

```markdown
- [x] 已完成的任务
- [ ] 待完成的任务
```

## 进阶技巧

### Hugo Shortcodes

Hugo 提供了 shortcodes 来扩展 Markdown 能力：

```markdown
{{</* figure src="/images/photo.png" caption="图片说明" */>}}
```

### 数学公式

如果启用了 KaTeX，可以写数学公式：

行内公式：`$E = mc^2$`

块级公式：

```
$$
\sum_{i=1}^{n} x_i = x_1 + x_2 + \cdots + x_n
$$
```

## 推荐工具

| 工具         | 用途                     |
| ------------ | ------------------------ |
| VS Code      | Markdown 编辑 + 实时预览 |
| Typora       | 所见即所得编辑器         |
| Markdownlint | Markdown 格式检查        |
| draw.io      | 画流程图 / 架构图        |

---

> 好的排版让读者更愿意阅读你的文章。花几分钟优化格式，值得！
