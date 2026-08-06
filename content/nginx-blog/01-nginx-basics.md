---
title: "Nginx 基础篇：Nginx 是什么，请求如何到达应用"
date: 2026-08-06
draft: false
description: "从域名、端口和 HTTP 请求开始，理解 Nginx 的静态文件服务器与反向代理角色。"
tags: ["Nginx", "HTTP", "静态文件", "反向代理"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 1
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 我为什么会遇到 Nginx

在服务器部署前端项目时，经常会得到这样的访问地址：

```text
https://example.com/my-app/
```

这很容易让人误以为 `/my-app` 天然对应服务器上的某个项目目录。实际上：

```text
/my-app 只是 HTTP 请求中的 URL 路径
```

是 Nginx 的配置决定了这段路径最终对应：

- 某个磁盘目录中的静态文件；
- 某个本机端口；
- 某个 Docker 容器；
- 或另一台服务器上的服务。

## 请求到达项目之前发生了什么

访问：

```text
https://example.com/my-app/
```

可以拆成下面几个阶段：

```text
域名 example.com
  │ DNS 解析
  ▼
服务器 IP
  │ TCP 连接到 443 端口
  ▼
Nginx
  │ 根据域名和路径选择规则
  ▼
静态文件或后端服务
```

每一部分的职责不同：

| 部分                | 负责什么                  |
| ------------------- | ------------------------- |
| DNS                 | 把域名解析到服务器 IP     |
| `listen`            | 指定 Nginx 接收请求的端口 |
| `server_name`       | 根据域名选择网站          |
| `location`          | 根据 URL 路径选择处理规则 |
| `root`、`try_files` | 查找并返回静态文件        |
| `proxy_pass`        | 把请求转发给后端服务      |

Nginx 不负责购买域名，也不会自动完成 DNS 解析。域名必须先在 DNS 服务商处指向服务器 IP，之后 Nginx 才能处理已经到达服务器的请求。

## Nginx 的第一个角色：静态文件服务器

Vite 项目执行：

```sh
pnpm --filter docs build
```

会产生类似下面的文件：

```text
dist/
├─ index.html
├─ favicon.ico
└─ assets/
   ├─ index-xxxx.js
   └─ index-xxxx.css
```

部署时可以把这些文件放进 Nginx 的目录：

```text
/usr/share/nginx/html/my-app/
```

浏览器请求 `/my-app/assets/index-xxxx.js` 时，Nginx 从文件系统找到对应文件并返回。

这个过程中没有“启动 React”：

```text
Vite 负责构建
Nginx 负责传输文件
浏览器负责执行 JavaScript 和渲染 React
```

因此普通 Vite/React 前端正式部署后，不需要一直运行 `pnpm dev` 或 `vite preview`。

## Nginx 的第二个角色：反向代理

浏览器请求：

```text
/my-app/api/message
```

这不是一个 JavaScript 或 CSS 文件，而是需要后端动态处理的 API。前端容器 Nginx 可以把它转发到：

```text
http://web:3000/api/message
```

请求链路变成：

```text
浏览器
  → 前端 Nginx
  → Next.js 后端
  → 前端 Nginx
  → 浏览器
```

浏览器始终只访问公开域名，不需要知道：

- 后端容器叫 `web`；
- 后端监听 3000 端口；
- 后端当前容器 IP；
- Docker 内部网络如何组织。

## 为什么叫“反向代理”

普通正向代理代表客户端访问外部资源：

```text
客户端 → 代理 → 外部网站
```

反向代理代表服务器端的一组服务接收外部请求：

```text
浏览器 → Nginx → 内部服务
```

浏览器知道 Nginx 的公开地址，却不需要知道后面的具体服务，所以 Nginx 是内部服务的统一入口。

## 为什么不直接暴露后端端口

如果让浏览器直接请求：

```text
http://服务器IP:3000/api/message
```

会带来额外问题：

- 用户必须知道后端端口；
- 前后端可能变成不同源，需要处理 CORS；
- HTTPS 页面不能随意请求 HTTP API；
- 后端服务直接暴露在公网；
- 后续修改端口或拆分服务会影响前端地址。

通过 Nginx 后，浏览器只需要使用同一套域名：

```text
页面：https://example.com/my-app/
接口：https://example.com/my-app/api/message
```

## 当前 Demo 为什么使用两层 Nginx

第一层是服务器 Nginx：

```text
example.com/my-app/*
  → http://127.0.0.1:3001/my-app/*
```

它负责服务器级别的事情：

- 域名；
- HTTPS；
- 多个项目的入口；
- 把 `/my-app` 交给正确的容器。

第二层是前端容器 Nginx：

```text
/my-app/*      → 静态文件
/my-app/api/*  → web:3000
```

它负责应用内部的事情：

- 返回 React 构建产物；
- SPA 路由回退；
- 把 API 请求转发到后端容器。

这样服务器 Nginx 不需要理解项目内部有哪些后端服务，只需要找到前端入口。

## 返回响应时发生什么

API 的请求和响应路径如下：

```text
请求：浏览器 → 服务器 Nginx → 前端 Nginx → web
响应：浏览器 ← 服务器 Nginx ← 前端 Nginx ← web
```

两个 Nginx 通常不会修改后端返回的 JSON 内容，只负责传递状态码、响应头和响应体。静态请求则由前端 Nginx 自己产生响应，不会进入 `web`。

## 本篇速记

```text
Nginx 的核心工作：接收、匹配、处理

静态请求：
请求 → Nginx → 磁盘文件 → 浏览器

动态请求：
请求 → Nginx → 后端服务 → Nginx → 浏览器

DNS           决定域名去哪个服务器
server_name   决定请求交给哪个网站
location      决定路径使用哪条规则
try_files     决定返回哪个静态文件
proxy_pass    决定转发给哪个服务
```

## 自测问题

1. `/my-app` 是否天然对应服务器上的真实目录？
2. 普通 Vite/React 项目上线后，Nginx 会不会启动 React？
3. 静态文件请求和 API 请求的处理方式有什么区别？
4. 为什么浏览器不需要知道 `web:3000`？
5. DNS 和 `server_name` 分别负责什么？
