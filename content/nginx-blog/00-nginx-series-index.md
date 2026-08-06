---
title: "Nginx 学习笔记：从静态文件到两层反向代理"
date: 2026-08-06
draft: false
description: "基于 Docker Demo 整理的 Nginx 入门系列，覆盖静态文件托管、server、location、反向代理、子路径部署与两层 Nginx 架构。"
tags: ["Nginx", "反向代理", "静态部署", "学习笔记"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 0
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 这套笔记记录什么

这套笔记接着 Docker Demo 的实践继续学习 Nginx。项目包含两个服务：

- `docs`：Vite + React 前端，构建后由容器内的 Nginx 提供静态文件；
- `web`：Next.js 服务，只在 Docker 内部网络中提供 API；
- 服务器上还有一层 Nginx，根据域名和 `/my-app/` 路径把请求交给前端容器。

最终希望得到下面的请求链路：

```text
浏览器
  → https://example.com/my-app/
  → 服务器 Nginx
  → 127.0.0.1:3001
  → 前端容器 Nginx
      ├─ 静态请求 → React 构建产物
      └─ API 请求 → http://web:3000/api/*
```

这套笔记重点回答我刚接触 Nginx 时最关心的问题：

- Nginx 到底是干什么的；
- 为什么服务器域名加上 `/my-app` 就能访问前端项目；
- `listen`、`server_name` 和 `location` 分别控制什么；
- Nginx 如何返回 HTML、JavaScript 和 CSS；
- Nginx 如何把 API 请求转发给后端；
- `proxy_pass` 结尾的 `/` 为什么会影响请求路径；
- 为什么当前架构需要服务器 Nginx 和前端容器 Nginx 两层配置。

## 系列目录

| 顺序 | 文章                                                                                                 | 主要内容                                     |
| ---- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 1    | [基础篇：Nginx 是什么，请求如何到达应用]({{< ref "01-nginx-basics" >}})                              | 建立域名、端口、静态文件和反向代理的心智模型 |
| 2    | [配置篇：listen、server_name 与 location]({{< ref "02-server-location-and-server-name" >}})          | 理解 Nginx 如何选择网站和处理规则            |
| 3    | [静态部署篇：Vite 构建产物、子路径与 SPA 回退]({{< ref "03-static-files-and-spa" >}})                | 把 React 前端部署到 `/my-app/`               |
| 4    | [反向代理篇：proxy_pass、路径替换与 Docker DNS]({{< ref "04-reverse-proxy-and-path-rewrite" >}})     | 分清路径保留、路径替换和 API 转发            |
| 5    | [部署与排障篇：两层 Nginx 的完整请求链路]({{< ref "05-two-layer-deployment-and-troubleshooting" >}}) | 组合服务器入口、前端容器和后端容器           |

## 最重要的心智模型

Nginx 可以先理解为服务器上的“HTTP 请求入口和分流器”：

```text
请求到达 Nginx
  ├─ 需要静态文件 → 从文件系统读取并返回
  └─ 需要后端处理 → 转发给另一个服务并返回响应
```

Nginx 不会“启动 React”。对于普通 Vite/React 单页应用：

1. Vite 在构建阶段生成 HTML、JavaScript、CSS 和图片；
2. Nginx 在运行阶段把这些文件返回给浏览器；
3. 浏览器执行 JavaScript，最终渲染 React 页面。

## Demo 的目标架构

```text
互联网
  │
  │ example.com:80/443
  ▼
服务器 Nginx
  │ 只处理域名、HTTPS 和 /my-app 入口
  │ 保留 /my-app 路径
  ▼
127.0.0.1:3001
  │
  ▼
docs 容器中的 Nginx
  ├─ /my-app/*      → 静态文件
  └─ /my-app/api/*  → web:3000/api/*
                            │
                            ▼
                         web 容器
```

关键约束：

- 服务器 Nginx 只需要知道前端容器发布的 `127.0.0.1:3001`；
- `docs` 容器的 80 端口不直接绑定所有公网网卡；
- `web` 不发布宿主机端口；
- `docs` 通过 Docker 服务名 `web` 访问后端；
- `/my-app` 会原样经过服务器 Nginx；
- 前端容器在转发 API 时才去掉 `/my-app` 前缀。

## 当前实践状态

项目已经完成以下改造：

- `Dockerfile.docs` 使用 Node 构建、Nginx 运行的多阶段构建；
- Vite 构建基础路径设置为 `/my-app/`；
- 前端容器配置了静态文件、SPA 回退和 API 代理；
- Compose 只将前端容器发布到 `127.0.0.1:3001`；
- 项目包含服务器 Nginx 示例配置；
- TypeScript、ESLint 和生产构建已经通过。

当前电脑尚未安装 Docker，因此镜像构建、`nginx -t` 和完整 HTTP 链路还需要在 Docker 环境中继续验证。笔记会明确区分“已完成的代码检查”和“待完成的运行验证”。

## 推荐阅读方式

第一次阅读时按 1 → 5 的顺序进行。

以后复习可以直接定位：

- 不清楚 Nginx 的作用：看基础篇；
- 不理解 `server_name`：看配置篇；
- 页面能打开但 JS、CSS 404：看静态部署篇；
- API 路径莫名少了一段：看反向代理篇；
- 遇到 404、502 或重定向循环：看部署与排障篇。

## 暂不展开的内容

本系列只总结当前 Demo 实际涉及的知识。以下内容只作为后续方向，不在本轮展开：

- 自动申请和续期 TLS 证书；
- 缓存策略和 CDN；
- 多实例负载均衡；
- 限流、鉴权和 Web Application Firewall；
- 灰度发布和高可用 Nginx。

## 参考文件

- [`../nginx/frontend.conf`](../nginx/frontend.conf)
- [`../nginx/host.example.conf`](../nginx/host.example.conf)
- [`../Dockerfile.docs`](../Dockerfile.docs)
- [`../compose.yaml`](../compose.yaml)

## 源代码

https://github.com/BINGWU2003/docker-demo
