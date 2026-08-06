---
title: "Docker 网络篇：服务发现、内部网络与前后端反向代理"
date: 2026-08-06
draft: false
description: "理解容器网络、Compose 服务名、localhost、host.docker.internal，以及 docs 到 web 的内部代理链路。"
tags: ["Docker", "Docker 网络", "反向代理", "Vite", "服务发现"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 4
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 容器为什么需要网络

实际项目通常不止一个进程：

```text
浏览器 → 前端 → 后端 API → 数据库 → 缓存
```

如果每个组件都运行在不同容器中，它们需要：

- 能够互相找到；
- 不依赖容易变化的容器 IP；
- 只暴露真正需要对外开放的端口；
- 根据职责进行网络隔离。

Docker 网络解决这些问题。

## 三个经常混淆的地址

### 容器中的 `localhost`

在 `docs` 容器里访问：

```text
http://localhost:3001
```

指向 `docs` 容器自己。

在 `docs` 容器里访问：

```text
http://localhost:3000
```

仍然指向 `docs` 自己，不会自动找到 `web`。

### Compose 服务名

两个服务加入同一 Compose 网络后，Docker DNS 会解析服务名：

```text
http://web:3000
```

这表示访问名为 `web` 的服务容器。

### `host.docker.internal`

如果服务运行在 Windows 或 macOS 宿主机而不是容器中，容器通常可以使用：

```text
http://host.docker.internal:8080
```

三者的选择规则：

```text
访问当前容器自己       → 127.0.0.1 或 localhost
访问另一个 Compose 服务 → 服务名，例如 web:3000
访问 Docker 宿主机      → host.docker.internal
```

## Compose 默认网络与服务发现

Compose 默认会为项目创建一张网络。服务加入同一网络后可以使用服务名互相访问。

查看网络：

```sh
docker network ls
```

查看网络详情：

```sh
docker network inspect docker-demo_default
```

测试服务名解析：

```sh
docker compose exec web ping -c 3 docs
```

本次得到：

```text
PING docs (172.18.0.3)
3 packets transmitted, 3 packets received, 0% packet loss
```

这里的 `172.18.0.3` 是当时的容器 IP。它可能在重建后变化，因此配置中应该使用 `docs`，而不是写死这个 IP。

## `wget --spider` 是什么

测试容器内 HTTP 连通性：

```sh
docker compose exec web wget --spider http://docs:3001
```

`wget --spider` 主要检查目标资源是否可访问，不需要下载完整正文。

它是一次性诊断命令：

```text
执行命令
  → web 容器发起一次请求
  → 检查 docs 是否响应
  → 命令结束
```

它不会持续监听端口，也不会替浏览器转发后续请求。

## `wget` 与反向代理的区别

一次性测试：

```text
终端 → web 容器 → wget → docs
```

持续反向代理：

```text
浏览器 → docs 容器 → proxy → web 容器
```

| 项目           | `wget --spider` | 反向代理           |
| -------------- | --------------- | ------------------ |
| 作用           | 检查能否访问    | 转发真实业务请求   |
| 生命周期       | 命令执行期间    | 服务持续运行期间   |
| 外部入口       | 不提供          | 提供               |
| 请求正文和响应 | 通常不下载正文  | 转发完整请求与响应 |
| 常见用途       | 排障、健康检查  | API 入口、同源代理 |

可以先使用 `wget` 验证网络通路，再检查代理配置：

```text
wget 失败 → 优先排查网络、服务名、端口和监听地址
wget 成功但代理失败 → 优先排查代理规则、路径重写和 Host 校验
```

## 本项目的代理目标

我把 `docs` 作为对外前端，把 `web` 作为内部后端：

```text
外部浏览器
  │ localhost:3001
  ▼
docs
  │ /api/message
  │ proxy 到 http://web:3000/api/message
  ▼
web
```

浏览器只知道：

```text
http://localhost:3001/api/message
```

浏览器不需要知道：

- `web` 的容器 IP；
- `web` 的内部服务名；
- `web` 是否发布宿主机端口。

## 后端 API

`web` 使用 Next.js Route Handler：

```ts
export async function GET() {
  return Response.json({
    message: "请求已由 docs 容器代理到 web 容器",
    service: "web",
    timestamp: new Date().toISOString(),
  });
}
```

容器内部地址：

```text
http://web:3000/api/message
```

## Vite 代理

`docs` 的 Vite 配置：

```ts
const apiProxy = {
  "/api": {
    target: "http://web:3000",
    changeOrigin: true,
  },
};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: apiProxy,
  },
  preview: {
    allowedHosts: ["docs"],
    proxy: apiProxy,
  },
});
```

前端只请求相对路径：

```ts
const result = await fetch("/api/message");
```

这样浏览器请求仍然发送给 `docs`，由 `docs` 的 Preview Server 在容器内部把请求转给 `web`。

这种模式可以减少浏览器直接访问不同域名或端口造成的跨域配置问题。

## `403 Forbidden` 的真实踩坑

网络测试时：

```sh
docker compose exec web wget --spider http://docs:3001
```

服务名成功解析，Ping 也成功，但 HTTP 返回：

```text
HTTP/1.1 403 Forbidden
```

直接请求容器 IP 却返回 200。这说明：

- Docker 网络正常；
- 端口监听正常；
- 失败发生在 HTTP 应用层；
- Vite 拒绝了 Host 为 `docs` 的请求。

修复方式：

```ts
preview: {
  allowedHosts: ["docs"],
}
```

修复后：

```text
Connecting to docs:3001 (...)
remote file exists
```

排障时应区分不同层：

```text
DNS 能否解析
  ↓
TCP 端口能否连接
  ↓
HTTP 是否返回成功状态
  ↓
业务响应是否正确
```

## `internal: true` 是什么

最终使用两张网络：

```yaml
services:
  web:
    networks:
      - backend

  docs:
    ports:
      - "3001:3001"
    networks:
      - public
      - backend

networks:
  public:
  backend:
    internal: true
```

拓扑：

```text
宿主机
  │ 发布端口 3001
  ▼
docs
  ├─ public
  └─ backend (internal)
          │
          ▼
         web
         └─ backend (internal)
```

`web` 没有 `ports` 配置，因此宿主机不能直接访问 3000：

```text
http://localhost:3000 → 无法访问，符合预期
```

但 `docs` 与 `web` 在同一内部网络中：

```text
docs → http://web:3000 → 成功
```

需要注意：

- `internal: true` 负责网络隔离，不负责请求转发；
- 真正转发 `/api` 的是 Vite proxy；
- 内部网络不是完整安全边界，应用仍需要鉴权和密钥管理。

## 如果使用 Nginx

生产前端常使用 Nginx 提供静态文件和反向代理：

```nginx
server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }

    location /api/ {
        proxy_pass http://web:3000/;
    }
}
```

这里仍然使用 Docker 服务名 `web`。区别只是代理服务器从 Vite Preview Server 换成 Nginx。

## 本篇速记

```text
容器里的 localhost 只指向当前容器
Compose 服务名用于访问另一个服务
host.docker.internal 用于访问宿主机
容器 IP 会变化，不应写死
wget --spider 是一次性连通性测试
proxy 是持续运行的请求转发
ports 决定宿主机入口
internal: true 用于内部网络隔离
网络成功不代表 HTTP Host 校验一定成功
```

## 自测问题

1. 在 `docs` 容器里访问 `localhost:3000` 为什么找不到 `web`？
2. `wget --spider` 与反向代理的主要区别是什么？
3. 为什么配置中应使用 `web:3000` 而不是 `172.18.0.3:3000`？
4. `internal: true` 是否会自动完成 `/api` 转发？
5. Ping 成功但 HTTP 返回 403，应该优先排查哪一层？
