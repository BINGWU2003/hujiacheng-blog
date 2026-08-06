---
title: "Docker 编排篇：Docker Compose、健康检查与服务生命周期"
date: 2026-08-06
draft: false
description: "使用 Compose 声明和管理多个容器，理解项目名、服务、健康检查、启动依赖和重建行为。"
tags: ["Docker", "Docker Compose", "健康检查", "容器编排"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 3
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 为什么需要 Docker Compose

只运行一个容器时，`docker run` 足够简单：

```sh
docker run -d --name docker-demo-web -p 3000:3000 docker-demo-web:v1
```

当项目有多个服务时，需要分别记住：

- 每个容器使用什么镜像；
- 每个镜像如何构建；
- 端口如何映射；
- 服务需要加入哪些网络；
- 服务之间有什么启动依赖；
- 健康检查和重启策略是什么。

Compose 把这些参数写进一个声明式配置文件。执行 `docker compose up` 时，Compose 负责把当前状态调整到配置描述的目标状态。

## 从两条 `docker run` 到 `compose.yaml`

本项目最终配置的核心结构：

```yaml
name: docker-demo

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    image: docker-demo-web:v1
    restart: unless-stopped
    networks:
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:3000"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s

  docs:
    build:
      context: .
      dockerfile: Dockerfile.docs
    image: docker-demo-docs:v1
    ports:
      - "3001:3001"
    restart: unless-stopped
    depends_on:
      web:
        condition: service_healthy
    networks:
      - public
      - backend
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:3001"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s

networks:
  public:
  backend:
    internal: true
```

## 配置中的核心对象

### 项目 Project

```yaml
name: docker-demo
```

项目是 Compose 管理资源的边界。容器、网络和标签都会记录所属项目。

### 服务 Service

```yaml
services:
  web:
  docs:
```

服务描述一种容器角色，例如前端、后端、数据库或缓存。

### 构建 Build

```yaml
build:
  context: .
  dockerfile: Dockerfile.docs
```

`context` 指定构建上下文，`dockerfile` 指定要使用的 Dockerfile。

### 镜像 Image

```yaml
image: docker-demo-docs:v1
```

指定构建结果或运行时使用的镜像名称。

### 端口 Ports

```yaml
ports:
  - "3001:3001"
```

格式仍然是：

```text
宿主机端口:容器端口
```

### 重启策略 Restart

```yaml
restart: unless-stopped
```

容器异常退出或 Docker 重启后自动恢复，但主动停止的容器不会立刻被重新拉起。

## Compose 如何知道管理哪个项目

在项目目录中执行：

```sh
docker compose ps
```

Compose 会读取当前目录中的 `compose.yaml`，从中得到项目名和服务定义，再通过容器标签查找资源。

容器上会有类似标签：

```text
com.docker.compose.project=docker-demo
com.docker.compose.service=web
```

容器名称通常是：

```text
项目名-服务名-序号
```

本项目中是：

```text
docker-demo-web-1
docker-demo-docs-1
```

查看本机所有 Compose 项目：

```sh
docker compose ls
```

明确指定配置文件：

```sh
docker compose -f D:\files\hjc-code\docker-demo\compose.yaml ps
```

明确指定项目名：

```sh
docker compose -p docker-demo ps
```

如果两个目录使用相同的顶层 `name`，Compose 可能把它们视为同一个逻辑项目。即使项目名不同，如果都发布宿主机的同一个端口，仍会产生端口冲突。

## Compose 生命周期

首次构建并后台启动：

```sh
docker compose up -d --build
```

查看状态：

```sh
docker compose ps
```

查看日志：

```sh
docker compose logs --tail 50
docker compose logs --follow web
```

停止全部服务，但保留容器：

```sh
docker compose stop
```

恢复已存在的容器：

```sh
docker compose start
```

删除本项目容器和 Compose 网络：

```sh
docker compose down
```

`down` 默认保留镜像。之后再次执行：

```sh
docker compose up -d
```

Compose 可以使用保留的镜像重新创建容器。

## `docker ps` 与 `docker compose ps`

```sh
docker ps
```

查看 Docker Engine 中所有正在运行的容器，不区分项目。

```sh
docker compose ps
```

查看当前 Compose 项目的服务容器。

查看当前项目的镜像使用情况：

```sh
docker compose images
```

因此 `docker compose ps` 主要显示容器，不是镜像列表。

## 运行中不等于健康

容器进程存在时，状态可以是 `Up`，但应用可能仍然：

- 没有完成初始化；
- 没有监听预期端口；
- 无法连接数据库；
- 只剩一个没有业务能力的主进程。

健康检查用于验证应用是否真的能够响应：

```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:3000"]
  interval: 10s
  timeout: 3s
  retries: 3
  start_period: 10s
```

字段含义：

| 字段           | 含义                             |
| -------------- | -------------------------------- |
| `test`         | 容器内部执行的检查命令           |
| `interval`     | 两次检查之间的间隔               |
| `timeout`      | 单次检查超时                     |
| `retries`      | 连续失败多少次后标记为 unhealthy |
| `start_period` | 启动宽限期                       |

状态变化通常是：

```text
starting → healthy
starting → unhealthy
```

## 健康检查的真实踩坑

最初我使用：

```yaml
test: ["CMD", "wget", "--quiet", "--spider", "http://localhost:3000"]
```

页面从宿主机可以正常访问，但两个容器都显示 `unhealthy`。

读取健康检查日志后发现：

```text
wget: can't connect to remote host: Connection refused
```

容器内的 `localhost` 优先解析到了 IPv6 `::1`，应用只监听 IPv4 的 `0.0.0.0`。改成明确的 IPv4 地址后恢复：

```yaml
test: ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:3000"]
```

这个问题说明：

```text
浏览器能访问 ≠ 容器内部健康检查一定成功
健康检查失败时应读取它自己的退出码和输出
```

查看详细健康记录：

```sh
docker inspect docker-demo-web-1
```

或者提取容器 ID：

```sh
docker inspect $(docker compose ps -q web)
```

后一种写法适用于支持命令替换的 Shell；在 CMD 中建议先执行 `docker compose ps -q web` 再复制 ID。

## 等后端健康后再启动前端

```yaml
depends_on:
  web:
    condition: service_healthy
```

这表示 `docs` 等待 `web` 通过健康检查后再启动。

需要注意：

- 它解决的是容器启动顺序；
- 它不能保证后端永远健康；
- 运行期间后端暂时失败时，前端或调用方仍应有超时、重试和错误处理。

## 修改配置或镜像后如何应用

只构建某个服务：

```sh
docker compose build web
```

强制重新创建容器：

```sh
docker compose up -d --force-recreate web
```

合并执行：

```sh
docker compose up -d --build --force-recreate web
```

本次实践中曾出现“镜像已经变了，但正在运行的容器仍引用旧镜像 ID”。因此页面内容异常陈旧时，应同时确认：

1. 源码是否真的保存；
2. 新镜像是否构建成功；
3. 容器是否重新创建；
4. 浏览器是否需要强制刷新。

## 本篇速记

```text
Compose 用声明式 YAML 管理多服务
Project 是 Compose 资源边界
Service 是一种容器角色
up 创建或调整服务
stop/start 暂停和恢复容器
down 删除项目容器和网络
ps 查看当前项目容器
images 查看当前项目镜像
Up 不等于 healthy
depends_on 可以等待依赖服务健康
```

## 自测问题

1. `docker compose stop` 与 `docker compose down` 有什么区别？
2. `docker compose ps` 如何确定当前项目？
3. 为什么两个不同 Compose 项目仍可能产生端口冲突？
4. 容器显示 `Up` 时，应用是否一定可用？
5. `depends_on: condition: service_healthy` 能否代替应用自身的重试逻辑？
