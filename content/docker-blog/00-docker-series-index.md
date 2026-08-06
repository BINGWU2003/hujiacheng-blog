---
title: "Docker 学习笔记：从容器基础到内部网络代理"
date: 2026-08-06
draft: false
description: "基于一个 Turborepo Demo 整理的 Docker 系列学习笔记索引，覆盖镜像、容器、Dockerfile、Compose、网络、代理与排障。"
tags: ["Docker", "Docker Compose", "容器", "学习笔记"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 0
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 这套笔记记录什么

这套笔记来自一次完整的 Docker 上手过程。我从完全不了解镜像和容器开始，把一个包含两个应用的 Turborepo 项目部署到了 Docker Desktop：

- `docs`：Vite + React 前端，对宿主机发布 3001 端口。
- `web`：Next.js 服务，只在 Docker 内部网络中提供 API。
- 浏览器访问 `docs`，由 `docs` 将 `/api/*` 请求代理到 `web:3000`。

最终请求链路如下：

```text
浏览器
  → http://localhost:3001/api/message
  → docs 容器
  → Vite proxy
  → http://web:3000/api/message
  → web 容器
  → JSON 响应返回浏览器
```

这些文章不是 Docker 官方文档的替代品，而是我的个人复习材料，重点记录：

- 一个概念解决了什么问题；
- 我实际执行过哪些命令；
- 命令成功时发生了什么；
- 出错时应该如何定位；
- 这次实践中遇到过哪些真实问题。

## 系列目录

| 顺序 | 文章                                                                                   | 主要内容                             |
| ---- | -------------------------------------------------------------------------------------- | ------------------------------------ |
| 1    | [基础篇：镜像、容器、端口与生命周期]({{< ref "01-docker-basics" >}})                   | Docker 的核心对象和第一组常用命令    |
| 2    | [构建篇：Dockerfile、缓存与多阶段构建]({{< ref "02-dockerfile-and-build" >}})          | 如何把源码构建成更小、更安全的镜像   |
| 3    | [编排篇：Docker Compose 与健康检查]({{< ref "03-docker-compose" >}})                   | 用声明式配置管理多个服务             |
| 4    | [网络篇：服务发现、内部网络与反向代理]({{< ref "04-docker-network-and-proxy" >}})      | 容器如何互通，以及如何只暴露前端入口 |
| 5    | [排障与速查篇：错误复盘和常用命令]({{< ref "05-docker-troubleshooting-cheatsheet" >}}) | 本次踩坑、诊断路径和命令清单         |

## Demo 的最终状态

```text
Windows 宿主机
  │
  │ localhost:3001
  ▼
docs 容器
  ├─ public 网络
  └─ backend 内部网络
          │
          │ http://web:3000
          ▼
       web 容器
       └─ backend 内部网络
```

关键约束：

- 宿主机可以访问 `localhost:3001`。
- 宿主机不能直接访问 `localhost:3000`。
- `docs` 可以通过服务名 `web` 访问 `web:3000`。
- `backend` 网络设置了 `internal: true`。
- 两个容器都配置了健康检查。
- `docs` 只有在 `web` 健康后才启动。

## 推荐复习顺序

第一次阅读时按 1 → 5 的顺序进行。

以后查阅时可以直接跳转：

- 忘记镜像和容器的区别：看基础篇。
- 修改源码后不确定为什么需要重建：看构建篇。
- 忘记 `up`、`stop`、`down` 的区别：看编排篇。
- 不清楚 `localhost`、服务名和宿主机地址：看网络篇。
- 遇到 `unhealthy`、`403` 或旧镜像问题：看排障篇。

## 环境说明

本次实践环境：

```text
系统：Windows + WSL 2
容器运行时：Docker Desktop（Linux containers）
项目：Turborepo + pnpm workspace
前端：Vite + React
后端：Next.js App Router
```

示例主要使用单行命令，CMD 和 PowerShell 都可以执行。涉及多行命令时，需要注意不同 Shell 的续行符不同：

```text
CMD        → ^
PowerShell → `
```

不确定当前使用什么 Shell 时，优先使用单行命令。

## 重要提醒

这套 Demo 用于本地学习，不是生产模板：

- `docs` 使用 Vite Preview Server，而不是 Nginx；
- 没有 TLS、鉴权、数据库和持久化卷；
- 没有镜像仓库、版本发布和 CI/CD；
- 内部网络可以减少暴露面，但不能代替应用权限控制和密钥管理。

## 参考资料

- [Docker Get Started](https://docs.docker.com/get-started/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Blowfish Front Matter](https://blowfish.page/docs/front-matter/)

## 源代码

https://github.com/BINGWU2003/docker-demo
