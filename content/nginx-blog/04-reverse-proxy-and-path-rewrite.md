---
title: "Nginx 反向代理篇：proxy_pass、路径替换与 Docker DNS"
date: 2026-08-06
draft: false
description: "通过两层 Nginx 配置理解 proxy_pass 的路径规则、转发请求头和 Docker 服务发现。"
tags: ["Nginx", "proxy_pass", "Docker DNS", "路径重写"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 4
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 当前架构中有两次反向代理

API 请求：

```text
https://example.com/my-app/api/message
```

会经过两次 `proxy_pass`：

```text
浏览器
  → 服务器 Nginx
  → 前端容器 Nginx
  → web:3000
```

两次代理的目标不同：

| 层级           | 上游地址         | 路径处理                             |
| -------------- | ---------------- | ------------------------------------ |
| 服务器 Nginx   | `127.0.0.1:3001` | 保留 `/my-app/...`                   |
| 前端容器 Nginx | `web:3000`       | 将 `/my-app/api/...` 改成 `/api/...` |

理解这两处路径变化，是本次 Nginx 学习最关键的部分。

## 服务器 Nginx：保留原路径

```nginx
location /my-app/ {
    proxy_pass http://127.0.0.1:3001;
}
```

`proxy_pass` 地址后面没有 URI 部分，也没有结尾 `/`。请求路径会原样传递：

```text
浏览器请求                        前端容器收到
/my-app/                         /my-app/
/my-app/assets/app.js            /my-app/assets/app.js
/my-app/api/message              /my-app/api/message
```

服务器 Nginx 只负责找到前端项目，不参与应用内部的静态/API 分流。

## 如果服务器 `proxy_pass` 带结尾 `/`

改成：

```nginx
location /my-app/ {
    proxy_pass http://127.0.0.1:3001/;
}
```

`proxy_pass` 中存在 URI `/`，Nginx 会用它替换匹配到的 `/my-app/`：

```text
浏览器请求                        前端容器收到
/my-app/                         /
/my-app/assets/app.js            /assets/app.js
/my-app/api/message              /api/message
```

但当前前端容器只配置了 `/my-app/` 和 `/my-app/api/`，所以路径会匹配失败。

这不是说带 `/` 永远错误，而是它代表不同的路径设计。如果前端容器只认识 `/` 和 `/api/`，带 `/` 可能正是想要的行为。

## 前端容器 Nginx：替换 API 前缀

```nginx
location ^~ /my-app/api/ {
    proxy_pass http://web:3000/api/;
}
```

这里 `proxy_pass` 地址包含 URI `/api/`。Nginx 会把匹配到的：

```text
/my-app/api/
```

替换为：

```text
/api/
```

所以：

```text
/my-app/api/message
  ↓
http://web:3000/api/message
```

这符合 Next.js 后端真实路由：

```text
apps/web/app/api/message/route.ts
```

## 一条实用的路径判断方法

看到代理配置时，不要只问“有没有斜杠”，而要拆成三部分：

```text
location 匹配了什么前缀？
proxy_pass 是否包含 URI？
上游最终应该收到什么路径？
```

当前两处配置可以写成替换公式：

```text
服务器层：
/my-app/api/message
  → 原样保留
/my-app/api/message

容器层：
/my-app/api/ + message
  → /api/ + message
/api/message
```

## `web` 为什么可以当作域名使用

前端容器配置：

```nginx
proxy_pass http://web:3000/api/;
```

这里的 `web` 是 Compose 服务名。`docs` 和 `web` 同时连接到 `backend` 网络后，Docker 提供内部 DNS：

```text
web → 当前 web 容器的内部 IP
```

因此不需要把容器 IP 写入配置。容器重建后 IP 可能变化，但服务名保持不变。

这与浏览器使用的公网 DNS 不同：

```text
公网 DNS     example.com → 服务器公网 IP
Docker DNS   web → web 容器内部 IP
```

浏览器无法解析 `web`，只有连接到对应 Docker 网络的容器才能使用这个名称。

## 为什么后端不需要发布端口

Compose 中 `web` 没有：

```yaml
ports:
```

但它仍然可以在 Docker 网络中监听 3000：

```text
docs 容器 → backend 网络 → web:3000
```

`ports` 用于把容器端口发布到宿主机，不是容器互相访问的前提。

这样外部无法直接请求：

```text
服务器IP:3000
```

所有公开 API 都先经过两层 Nginx。

## 代理请求头有什么用

服务器 Nginx 使用：

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

这些请求头帮助后面的服务了解原始请求：

| 请求头              | 常见含义                    |
| ------------------- | --------------------------- |
| `Host`              | 用户访问的域名              |
| `X-Real-IP`         | 当前代理看到的客户端 IP     |
| `X-Forwarded-For`   | 请求经过的客户端/代理 IP 链 |
| `X-Forwarded-Proto` | 原始协议是 HTTP 还是 HTTPS  |

如果不传这些信息，后端通常只能看到前一层 Nginx 的内部地址和 HTTP 连接，无法准确知道用户最初访问的域名、协议和来源 IP。

前端容器继续使用：

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $http_x_forwarded_proto;
```

目的是继续传递服务器 Nginx 已经提供的信息。

## 正向代理和反向代理

正向代理代表客户端：

```text
客户端 → 正向代理 → 外部网站
```

反向代理代表服务端：

```text
浏览器 → 反向代理 → 内部服务
```

用户访问的是 Nginx，而 Nginx 决定请求最终由哪个内部服务处理。当前两层 Nginx 都属于反向代理。

## 常见错误

### API 返回 404

先检查每一层实际收到的 URI：

```text
浏览器：/my-app/api/message
前端容器：应该仍是 /my-app/api/message
后端：应该是 /api/message
```

任意一层多删或少删 `/my-app` 都会导致路由不匹配。

### API 返回 502 Bad Gateway

502 通常表示 Nginx 已经匹配到代理规则，但无法连接上游。检查：

- `web` 容器是否运行且健康；
- `web` 是否监听 `0.0.0.0:3000`；
- `docs` 和 `web` 是否共享 `backend` 网络；
- `proxy_pass` 中的服务名和端口是否正确；
- 后端是否在 Nginx 启动后更换了不可用地址。

### 前端容器直接返回 `index.html`

说明 API 请求可能没有匹配 `/my-app/api/`，而是进入了 SPA 静态回退。检查请求是否缺少结尾路径、前缀是否拼写错误，以及更具体的 API `location` 是否存在。

## 本篇速记

```text
proxy_pass 没有 URI：通常保留原始 URI
proxy_pass 包含 URI：用该 URI 替换 location 匹配部分

服务器层：
proxy_pass http://127.0.0.1:3001;
/my-app/api/message → /my-app/api/message

容器层：
proxy_pass http://web:3000/api/;
/my-app/api/message → /api/message

web 是 Docker 服务名，不是公网域名。
```

## 自测问题

1. 为什么服务器 `proxy_pass` 不写结尾 `/`？
2. 前端容器为什么反而要在 `proxy_pass` 中写 `/api/`？
3. `web` 这个名称由谁解析？
4. 没有 `ports` 的后端容器能否被前端容器访问？
5. 404 和 502 分别更可能代表哪一类问题？
