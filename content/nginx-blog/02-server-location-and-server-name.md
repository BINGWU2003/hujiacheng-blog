---
title: "Nginx 配置篇：listen、server_name 与 location"
date: 2026-08-06
draft: false
description: "理解 Nginx 配置的层级，以及如何根据端口、域名和 URL 路径选择处理规则。"
tags: ["Nginx", "server_name", "location", "虚拟主机"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 2
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 从一份最小配置开始

```nginx
server {
    listen 80;
    server_name example.com;

    location /my-app/ {
        proxy_pass http://127.0.0.1:3001;
    }
}
```

可以把它读成一句话：

```text
接收 80 端口上属于 example.com 的请求，
当路径以 /my-app/ 开头时，把请求转发到 127.0.0.1:3001。
```

最值得先记住的分工是：

```text
listen       → 哪个端口
server_name  → 哪个网站
location     → 网站里的哪个路径
```

## Nginx 配置层级

完整的 Nginx 主配置通常包含下面的层级：

```nginx
events {
}

http {
    server {
        location / {
        }
    }
}
```

Docker 官方 Nginx 镜像已经提供主配置，并在 `http` 中加载：

```nginx
include /etc/nginx/conf.d/*.conf;
```

所以项目只需要把自己的 `server` 配置复制到：

```text
/etc/nginx/conf.d/default.conf
```

这就是 `Dockerfile.docs` 中下面一行的作用：

```dockerfile
COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf
```

## `listen`：请求从哪个端口进入

```nginx
listen 80;
```

表示 Nginx 在容器内监听 80 端口。

Compose 再把宿主机端口映射到容器端口：

```yaml
ports:
  - "127.0.0.1:3001:80"
```

方向是：

```text
宿主机 127.0.0.1:3001 → docs 容器 80
```

所以服务器 Nginx 访问 `127.0.0.1:3001`，请求最终进入容器 Nginx 的 80 端口。

`listen` 和 Docker 端口映射不是一回事：

- `listen 80`：进程在容器内部监听 80；
- `127.0.0.1:3001:80`：Docker 把宿主机 3001 转到容器 80。

## `server_name`：请求属于哪个网站

同一台服务器可以只有一个 IP，却运行多个域名：

```nginx
server {
    listen 80;
    server_name blog.example.com;
}

server {
    listen 80;
    server_name shop.example.com;
}
```

浏览器发送的 HTTP 请求包含 `Host`：

```http
GET / HTTP/1.1
Host: blog.example.com
```

Nginx 根据 `Host` 选择 `blog.example.com` 对应的 `server`。

一个站点也可以配置多个名称：

```nginx
server_name example.com www.example.com;
```

还可以配置通配域名：

```nginx
server_name *.example.com;
```

## `server_name _` 是什么意思

前端容器配置使用：

```nginx
server_name _;
```

`_` 不是 Nginx 的特殊通配符，而是一个通常不会成为真实域名的名称。容器中只有一个 `server` 时，它自然会接收没有其他规则匹配的请求。

想明确声明默认站点，可以写：

```nginx
listen 80 default_server;
server_name _;
```

服务器 Nginx 需要用真实域名选择项目，因此 `server_name` 很重要；前端容器已经是某个项目的内部入口，通常不需要再按域名区分。

## `server_name` 不负责 DNS

下面的配置：

```nginx
server_name example.com;
```

不会让 `example.com` 自动指向服务器。仍然需要在 DNS 服务商处配置：

```text
example.com → 服务器公网 IP
```

可以这样区分：

```text
DNS          把请求送到正确服务器
server_name  在服务器内部选择正确网站
```

## `location`：根据路径选择规则

```nginx
location /my-app/ {
    try_files $uri $uri/ /my-app/index.html;
}
```

表示匹配所有以 `/my-app/` 开头的路径，例如：

```text
/my-app/
/my-app/assets/app.js
/my-app/users
```

精确匹配使用 `=`：

```nginx
location = /my-app {
    return 301 /my-app/;
}
```

它只匹配 `/my-app`，不会匹配 `/my-app/` 或 `/my-app/users`。

## 为什么要把 `/my-app` 跳转到 `/my-app/`

当前应用基础路径是：

```text
/my-app/
```

因此使用：

```nginx
location = /my-app {
    return 301 /my-app/;
}
```

统一结尾斜杠可以避免相对路径解析不一致，也让后面的 `/my-app/` 前缀规则更容易理解。

## `^~` 在 API 规则中的作用

前端容器配置：

```nginx
location ^~ /my-app/api/ {
    proxy_pass http://web:3000/api/;
}
```

`^~` 表示匹配到这个前缀后，不再继续检查正则 `location`。当前配置没有额外正则规则，因此它不是绝对必需，但可以明确表达：

```text
/my-app/api/ 是专门的 API 前缀，不应该被静态文件规则接管
```

同时 `/my-app/api/` 比 `/my-app/` 更长，普通前缀匹配时也会优先选择它。

## 当前配置如何选择规则

前端容器的主要规则可以简化为：

```nginx
location = / {
    return 302 /my-app/;
}

location = /my-app {
    return 301 /my-app/;
}

location ^~ /my-app/api/ {
    proxy_pass http://web:3000/api/;
}

location /my-app/ {
    try_files $uri $uri/ /my-app/index.html;
}

location / {
    return 404;
}
```

匹配结果：

| 请求路径                | 使用的规则                 | 结果              |
| ----------------------- | -------------------------- | ----------------- |
| `/`                     | `location = /`             | 跳转到 `/my-app/` |
| `/my-app`               | `location = /my-app`       | 补上结尾 `/`      |
| `/my-app/`              | `location /my-app/`        | 返回前端页面      |
| `/my-app/assets/app.js` | `location /my-app/`        | 返回静态文件      |
| `/my-app/api/message`   | `location ^~ /my-app/api/` | 转发到后端        |
| `/unknown`              | `location /`               | 返回 404          |

## 同一端口找不到匹配域名时怎么办

Nginx 会在相同地址和端口的 `server` 中选择默认服务器：

- 显式标记了 `default_server` 的配置；
- 如果没有显式标记，通常是该地址端口上第一个加载的 `server`。

因此 `server_name` 不匹配不一定立即产生错误，也可能落到另一个默认站点。排查“为什么访问到了错误网站”时，应同时检查：

- DNS 是否指向正确 IP；
- 请求的 `Host` 是否正确；
- `server_name` 是否包含该域名；
- 哪个配置是 `default_server`；
- 配置文件的加载顺序。

## 本篇速记

```text
listen       选择地址和端口
server_name  根据域名选择 server
location     根据 URL 路径选择处理规则

=            精确匹配
普通前缀      匹配以某段路径开头的请求
^~           命中前缀后不再检查正则 location

DNS 和 server_name 不是同一件事：
DNS 找服务器，server_name 找网站。
```

## 自测问题

1. `listen 80` 和 `3001:80` 分别属于哪一层？
2. `server_name` 是否会自动创建 DNS 解析？
3. 为什么服务器 Nginx 使用真实域名，而容器 Nginx 可以使用 `_`？
4. `/my-app/api/message` 会匹配哪条 `location`？
5. `location = /my-app` 为什么不会匹配 `/my-app/users`？
