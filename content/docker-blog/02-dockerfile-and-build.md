---
title: "Docker 构建篇：Dockerfile、分层缓存与多阶段构建"
date: 2026-08-06
draft: false
description: "记录 Dockerfile 常用指令、构建上下文、缓存失效规则，以及将 Next.js 镜像从 1.19 GB 优化到 313 MB 的过程。"
tags: ["Docker", "Dockerfile", "构建缓存", "多阶段构建", "Next.js"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 2
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## Dockerfile 解决什么问题

Dockerfile 用代码描述如何构建镜像。相比在容器中手动安装软件，它具有几个重要特点：

- 构建过程可以重复；
- 配置可以进入版本控制；
- 团队和 CI 可以得到一致镜像；
- 每一步构建结果可以形成可复用的缓存层。

最初的单阶段 Dockerfile：

```dockerfile
FROM node:22-alpine

RUN corepack enable

WORKDIR /app

COPY . .

RUN pnpm install --frozen-lockfile
RUN pnpm --filter web build

EXPOSE 3000

CMD ["pnpm", "--filter", "web", "start", "--hostname", "0.0.0.0"]
```

它能够工作，但还没有考虑缓存效率和最终镜像体积。

## 常用 Dockerfile 指令

### `FROM`

```dockerfile
FROM node:22-alpine
```

指定基础镜像。这里使用带 Node.js 22 的 Alpine Linux。

### `WORKDIR`

```dockerfile
WORKDIR /app
```

设置后续指令的默认工作目录。目录不存在时 Docker 会创建它。

### `COPY`

```dockerfile
COPY . .
```

把构建上下文中的文件复制到镜像。

### `RUN`

```dockerfile
RUN pnpm install --frozen-lockfile
```

在构建镜像时执行命令，结果会进入镜像层。

### `ENV`

```dockerfile
ENV NODE_ENV=production
```

设置镜像和容器中的环境变量。

### `EXPOSE`

```dockerfile
EXPOSE 3000
```

声明应用预期监听的端口。它主要是镜像元数据，不等于把端口发布到宿主机。真正的端口发布由 `docker run -p` 或 Compose 的 `ports` 完成。

### `CMD`

```dockerfile
CMD ["node", "apps/web/server.js"]
```

指定容器默认启动命令。`RUN` 在构建时执行，`CMD` 在容器启动时执行。

### `USER`

```dockerfile
USER nextjs
```

指定运行应用的用户。生产运行阶段尽量不要使用 root 用户。

## 构建上下文与 `.dockerignore`

```sh
docker build -t docker-demo-web:v1 .
```

最后的 `.` 表示当前目录是构建上下文。Dockerfile 中的 `COPY` 只能读取构建上下文中的文件。

不需要参与构建的文件应写进 `.dockerignore`：

```text
node_modules
**/node_modules
.next
**/.next
dist
**/dist
.git
```

好处包括：

- 减少传给 Docker Builder 的文件；
- 避免把宿主机依赖复制进 Linux 镜像；
- 避免本地构建产物污染镜像；
- 减少无关文件导致缓存失效。

## Docker 为什么能使用缓存

Dockerfile 中的每条构建指令都会形成一个逻辑层。再次构建时，如果某一步的指令和输入没有变化，Docker 可以复用旧结果。

例如：

```dockerfile
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm --filter web build
```

只要修改任意源码，`COPY . .` 的输入就发生变化。它之后的依赖安装和应用构建都会重新执行。

这解释了为什么我只修改了一行页面文案，`pnpm install` 仍然重新运行。

## 优化依赖安装缓存

依赖只由 `package.json`、锁文件和 workspace 清单决定，因此应先复制这些稳定文件：

```dockerfile
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY apps/docs/package.json ./apps/docs/package.json
COPY packages/ui/package.json ./packages/ui/package.json
COPY packages/eslint-config/package.json ./packages/eslint-config/package.json
COPY packages/typescript-config/package.json ./packages/typescript-config/package.json

RUN pnpm install --frozen-lockfile

COPY . .
RUN pnpm --filter web build
```

新的顺序是：

```text
复制依赖清单
  ↓
安装依赖
  ↓
复制经常变化的源码
  ↓
构建应用
```

现在只修改源码时，输出中会出现：

```text
RUN pnpm install --frozen-lockfile
CACHED
```

只有修改依赖清单或锁文件，依赖安装层才会失效。

> 缓存优化的核心不是让所有步骤永远缓存，而是让变化频率不同的文件分层复制。

## 为什么单阶段镜像很大

单阶段构建把所有工作都放在同一个镜像中：

```text
完整源码
开发依赖
TypeScript 和构建工具
构建缓存
生产运行依赖
最终构建产物
```

构建完成后，编译工具和源码通常不再是运行应用的必要条件，但它们仍留在最终镜像中。

本次单阶段 Next.js 镜像结果：

```text
DISK USAGE  1.19 GB
CONTENT SIZE 284 MB
```

## 多阶段构建

多阶段 Dockerfile 包含多个 `FROM`：

```dockerfile
FROM node:22-alpine AS deps
# 安装依赖

FROM node:22-alpine AS builder
# 构建应用

FROM node:22-alpine AS runner
# 只运行最终产物
```

阶段之间通过 `COPY --from` 传递需要的文件：

```dockerfile
COPY --from=builder /app/apps/web/.next/standalone ./
```

本项目的职责划分：

```text
deps
  └─ 安装 pnpm workspace 依赖

builder
  ├─ 复制依赖和源码
  └─ 执行 next build

runner
  ├─ 复制 standalone 产物
  ├─ 复制 public 和 .next/static
  └─ 使用非 root 用户运行 server.js
```

多阶段构建不会同时启动三个容器。默认最终镜像只使用最后一个目标阶段，前面的阶段用于生成产物和构建缓存。

## Next.js standalone 输出

Next.js 配置：

```js
const nextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.join(currentDir, "../.."),
};
```

`standalone` 会收集运行服务器所需的最小依赖。运行阶段还需要单独复制：

```text
public/
.next/static/
.next/standalone/
```

最终启动命令：

```dockerfile
CMD ["node", "apps/web/server.js"]
```

## 非 root 用户运行

运行阶段创建专用用户：

```dockerfile
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs ...

USER nextjs
```

这样应用进程不以 root 权限运行。即使应用出现漏洞，攻击者在容器中默认获得的权限也更受限制。

## 优化结果

优化前先为旧镜像保留标签：

```sh
docker tag docker-demo-web:v1 docker-demo-web:single-stage
```

重新构建后比较：

```sh
docker image ls --filter "reference=docker-demo-web:*"
```

实测结果：

| 镜像   | Disk Usage | Content Size |
| ------ | ---------: | -----------: |
| 单阶段 |    1.19 GB |       284 MB |
| 多阶段 |     313 MB |      78.2 MB |

磁盘占用减少约 74%。

这里的两个大小可以粗略理解为：

- `DISK USAGE`：本地解包和存储后占用；
- `CONTENT SIZE`：镜像内容层的压缩体积。

## 镜像不可变与容器替换

修改代码并重新构建镜像，不会让正在运行的旧容器自动变成新容器。

本次曾出现：

```text
源码已修改
新镜像已构建
页面仍显示旧内容
```

检查后发现镜像标签已经指向新镜像，但容器仍引用旧镜像 ID。

强制重新创建：

```sh
docker compose up -d --force-recreate web
```

构建与替换可以合并：

```sh
docker compose up -d --build --force-recreate web
```

需要牢记：

```text
构建新镜像 ≠ 修改已有容器
新镜像需要通过新容器运行
```

## 本篇速记

```text
RUN 在构建时执行
CMD 在容器启动时执行
EXPOSE 不等于发布端口
.dockerignore 控制构建上下文
稳定文件先 COPY，易变源码后 COPY
多阶段构建让构建环境与运行环境分离
COPY --from 用于跨阶段复制产物
新镜像不会自动替换旧容器
```

## 自测问题

1. 为什么 `COPY . .` 放在 `pnpm install` 前面会降低缓存命中率？
2. `RUN` 和 `CMD` 分别在什么时候执行？
3. Dockerfile 写了 `EXPOSE 3000`，为什么宿主机仍可能无法访问？
4. 多阶段构建是否会产生三个运行中的容器？
5. 构建新镜像后，为什么可能仍看到旧页面？
