---
title: "Nginx 部署与排障篇：两层 Nginx 的完整请求链路"
date: 2026-08-06
draft: false
description: "把服务器入口、前端 Nginx、React 静态文件和 Docker 内部后端组合起来，并按请求链路排查 404、502 和资源错误。"
tags: ["Nginx", "Docker Compose", "部署", "排障"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 5
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 最终架构

```text
互联网
  │
  │ https://example.com/my-app/*
  ▼
服务器 Nginx
  │
  │ http://127.0.0.1:3001/my-app/*
  ▼
docs 容器 Nginx
  ├─ /my-app/*
  │    └─ /usr/share/nginx/html/my-app/*
  │
  └─ /my-app/api/*
       └─ http://web:3000/api/*
                    │
                    ▼
                 web 容器
```

服务器 Nginx 是整台机器的入口，前端容器 Nginx 是当前应用的入口。后端只存在于 Docker 内部网络。

## 第一步：确认项目配置

前端运行镜像使用 Nginx：

```dockerfile
FROM nginx:alpine AS runner

COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/docs/dist /usr/share/nginx/html/my-app
```

Compose 只发布前端容器：

```yaml
services:
  docs:
    ports:
      - "127.0.0.1:3001:80"

  web:
    # 不配置 ports
```

绑定 `127.0.0.1` 表示只有服务器本机可以直接连接 3001。公网入口仍然是服务器 Nginx 的 80/443 端口。

前端和后端共享内部网络：

```yaml
networks:
  backend:
    internal: true
```

`internal: true` 用于限制该网络的外部访问能力，但不能代替应用鉴权、防火墙和密钥管理。

## 第二步：构建并启动 Compose

安装并启动 Docker 后，在项目根目录执行：

```sh
docker compose up -d --build
```

查看状态：

```sh
docker compose ps
```

预期：

- `web` 先启动并通过健康检查；
- `docs` 随后启动；
- 两个服务最终都是 `healthy`；
- `docs` 显示宿主机 `127.0.0.1:3001` 到容器 80 的映射；
- `web` 没有宿主机端口映射。

当前电脑尚未安装 Docker，因此上述容器级结果属于待验证清单，不能只根据代码构建成功就假设已经通过。

## 第三步：验证前端容器 Nginx

先检查配置语法：

```sh
docker compose exec docs nginx -t
```

成功时应看到类似：

```text
syntax is ok
test is successful
```

查看 Nginx 实际加载的完整配置：

```sh
docker compose exec docs nginx -T
```

直接从服务器本机验证前端页面：

```sh
curl -I http://127.0.0.1:3001/my-app/
```

验证静态 HTML：

```sh
curl http://127.0.0.1:3001/my-app/
```

验证 API 代理：

```sh
curl http://127.0.0.1:3001/my-app/api/message
```

这一步绕过服务器 Nginx，可以单独证明前端容器的静态文件和内部 API 转发是否正常。

## 第四步：配置服务器 Nginx

项目提供的核心配置：

```nginx
server {
    listen 80;
    server_name example.com;

    location = /my-app {
        return 301 /my-app/;
    }

    location /my-app/ {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

需要将 `example.com` 改成真实域名，并把配置放进服务器 Nginx 实际加载的目录。不同 Linux 发行版可能使用：

```text
/etc/nginx/conf.d/*.conf
```

或：

```text
/etc/nginx/sites-available/
/etc/nginx/sites-enabled/
```

修改后先测试：

```sh
sudo nginx -t
```

只有语法检查通过后再重新加载：

```sh
sudo systemctl reload nginx
```

重新加载通常不会像停止再启动那样直接中断已有连接。

## 第五步：验证服务器入口

确认 DNS 已经指向服务器 IP后访问：

```sh
curl -I http://example.com/my-app/
curl http://example.com/my-app/api/message
```

也可以在 DNS 生效前临时指定请求目标和 `Host`：

```sh
curl -H "Host: example.com" http://服务器IP/my-app/
```

如果服务器上存在多个 `server`，正确的 `Host` 对验证 `server_name` 匹配很重要。

## 页面请求的完整处理过程

请求：

```text
GET /my-app/
```

处理：

```text
1. DNS 将 example.com 解析到服务器 IP
2. 服务器 Nginx 根据 server_name 选择网站
3. location /my-app/ 匹配请求
4. 请求原样转发到 127.0.0.1:3001/my-app/
5. 前端容器 Nginx 匹配静态规则
6. try_files 找到 /usr/share/nginx/html/my-app/index.html
7. HTML 经两层 Nginx 返回浏览器
8. 浏览器继续请求 /my-app/assets/*
```

## API 请求的完整处理过程

请求：

```text
GET /my-app/api/message
```

处理：

```text
1. 服务器 Nginx 保留完整 URI
2. 前端容器收到 /my-app/api/message
3. location ^~ /my-app/api/ 接管请求
4. proxy_pass 将前缀替换为 /api/
5. Docker DNS 把 web 解析为后端容器地址
6. 后端收到 GET /api/message
7. 后端生成 JSON
8. JSON 经前端 Nginx、服务器 Nginx 返回浏览器
```

## 按层排障，而不是一次猜完整链路

遇到问题时从内向外逐层验证：

```text
后端是否正常
  ↓
前端容器能否访问后端
  ↓
前端容器 Nginx 是否正常
  ↓
宿主机能否访问 127.0.0.1:3001
  ↓
服务器 Nginx 是否正确转发
  ↓
DNS、HTTPS 和浏览器是否正常
```

这样可以快速确定错误发生在哪一层。

## 排查 404 Not Found

404 表示某一层成功处理了请求，但没有找到对应资源或路由。

先记录原始请求：

```text
/my-app/api/message
```

再确认每一层 URI：

```text
服务器 Nginx 上游 URI：/my-app/api/message
前端 Nginx 上游 URI：/api/message
Next.js 路由：/api/message
```

常见原因：

- 服务器 `proxy_pass` 多写了结尾 `/`，提前删除 `/my-app`；
- Vite `base` 仍然是 `/`；
- 静态文件没有复制到 `html/my-app`；
- API 请求没有匹配专用 `location`；
- 后端真实路由与代理后的路径不一致；
- 请求落到了错误的 `server_name`。

## 排查 502 Bad Gateway

502 通常说明 Nginx 选择了代理规则，但连接上游失败。

先看容器状态和日志：

```sh
docker compose ps
docker compose logs --tail 100 docs
docker compose logs --tail 100 web
```

从前端容器直接请求后端：

```sh
docker compose exec docs wget -qO- http://web:3000/api/message
```

检查名称解析：

```sh
docker compose exec docs ping -c 3 web
```

如果前端容器访问后端正常，但服务器 Nginx 仍然 502，再检查服务器能否访问：

```sh
curl http://127.0.0.1:3001/my-app/
```

## 排查静态资源 404

浏览器开发者工具中观察失败的地址：

```text
错误：/assets/index-xxxx.js
正确：/my-app/assets/index-xxxx.js
```

检查构建结果：

```sh
pnpm --filter docs build
```

打开 `apps/docs/dist/index.html`，确认资源 URL 以 `/my-app/` 开头。

进入容器检查文件：

```sh
docker compose exec docs find /usr/share/nginx/html/my-app -maxdepth 2 -type f
```

如果 URL 正确且文件存在，再检查服务器 Nginx 是否保留了 `/my-app`。

## 排查重定向循环

当前前端容器将 `/` 重定向到 `/my-app/`：

```nginx
location = / {
    return 302 /my-app/;
}
```

如果服务器 Nginx 把 `/my-app/` 删除后转发为 `/`：

```text
浏览器 /my-app/
  → 服务器删除 /my-app/
  → 前端容器收到 /
  → 前端重定向到 /my-app/
  → 再次被服务器删除
```

这会形成循环。检查服务器代理是否错误写成：

```nginx
proxy_pass http://127.0.0.1:3001/;
```

当前设计应当是：

```nginx
proxy_pass http://127.0.0.1:3001;
```

## 排查配置修改没有生效

服务器 Nginx：

```sh
sudo nginx -t
sudo nginx -T
sudo systemctl reload nginx
```

容器 Nginx 配置已经构建进镜像，修改后需要重建并重新创建容器：

```sh
docker compose up -d --build --force-recreate docs
```

如果只重启旧容器，镜像中的旧配置不会自动更新。

## 常用观察命令

```sh
# Compose 状态
docker compose ps

# 两个服务的日志
docker compose logs --tail 100 docs
docker compose logs --tail 100 web

# 容器 Nginx 语法与完整配置
docker compose exec docs nginx -t
docker compose exec docs nginx -T

# 宿主机直连前端容器
curl -I http://127.0.0.1:3001/my-app/

# 通过前端 Nginx 访问 API
curl http://127.0.0.1:3001/my-app/api/message

# 绕过前端 Nginx，验证容器间通信
docker compose exec docs wget -qO- http://web:3000/api/message
```

## 当前方案的边界

这套配置适合学习和单机部署思路，但不是完整生产模板：

- 服务器示例只有 HTTP，没有实际 TLS 证书配置；
- 没有缓存策略和静态资源长期缓存头；
- 没有限流、认证和安全响应头；
- 没有多实例负载均衡；
- 没有集中日志、指标和告警；
- 没有自动发布、回滚和镜像版本管理。

先理解本次请求链路，再逐项扩展，比一开始复制一份复杂生产配置更容易判断每条指令的作用。

## 本篇速记

```text
服务器 Nginx：
域名、HTTPS、/my-app 项目入口

前端容器 Nginx：
静态文件、SPA 回退、API 分流

后端容器：
只在 Docker backend 网络监听 web:3000

排障顺序：
后端 → 容器网络 → 前端 Nginx → 宿主机端口 → 服务器 Nginx → DNS/HTTPS

404：通常是路径或资源匹配问题
502：通常是上游连接问题
```

## 自测问题

1. 为什么 `docs` 绑定 `127.0.0.1:3001` 而不是直接绑定所有公网地址？
2. 如何绕过服务器 Nginx，单独验证前端容器？
3. 如何绕过前端 Nginx，单独验证后端容器？
4. 静态资源 404 时应该检查哪三类路径？
5. 为什么修改容器 Nginx 配置后只执行 `docker compose restart` 可能没有效果？
