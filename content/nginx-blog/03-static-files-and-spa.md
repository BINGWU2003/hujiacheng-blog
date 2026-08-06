---
title: "Nginx 静态部署篇：Vite 构建产物、子路径与 SPA 回退"
date: 2026-08-06
draft: false
description: "把 Vite + React 构建产物部署到 /my-app/，理解 root、try_files、基础路径和前端路由刷新。"
tags: ["Nginx", "Vite", "React", "SPA", "静态部署"]
categories: ["Nginx 学习笔记"]
series: ["Nginx 快速入门"]
series_order: 3
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 前端构建和前端运行是两件事

开发阶段运行：

```sh
pnpm --filter docs dev
```

Vite 会启动开发服务器，提供热更新和源码转换。它适合开发，却不是正式部署普通静态前端的必要条件。

构建阶段运行：

```sh
pnpm --filter docs build
```

Vite 将前端转换成浏览器可以直接使用的文件：

```text
apps/docs/dist/
├─ index.html
├─ favicon.ico
├─ *.svg
└─ assets/
   ├─ index-xxxx.js
   └─ index-xxxx.css
```

正式运行时，Nginx 只需要返回这些文件：

```text
构建：Node + pnpm + Vite
运行：Nginx + dist 静态文件
```

## 为什么使用多阶段 Docker 构建

`Dockerfile.docs` 分成两个阶段：

```dockerfile
FROM node:22-alpine AS builder

RUN corepack enable
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm --filter docs build

FROM nginx:alpine AS runner

COPY nginx/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/apps/docs/dist /usr/share/nginx/html/my-app

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

第一阶段包含 Node、pnpm、源码和构建依赖。第二阶段只保留：

- Nginx；
- Nginx 配置；
- 已经生成的静态文件。

最终运行镜像不需要 Vite 开发服务器，也不需要完整源码和 `node_modules`。

## 为什么文件复制到 `html/my-app`

构建产物被复制到：

```text
/usr/share/nginx/html/my-app
```

Nginx 配置了：

```nginx
root /usr/share/nginx/html;
```

于是 URL 和文件路径形成直接对应：

```text
URL /my-app/index.html
  ↓ root + URI
/usr/share/nginx/html/my-app/index.html
```

同理：

```text
/my-app/assets/app.js
  ↓
/usr/share/nginx/html/my-app/assets/app.js
```

这种目录设计避免了在 `alias` 和 `try_files` 组合中处理额外的路径替换。

## 子路径部署为什么需要配置 Vite `base`

应用不是部署在域名根路径 `/`，而是：

```text
/my-app/
```

因此 Vite 配置需要设置基础路径：

```ts
export const APP_BASE_PATH = "/my-app/";

export default defineConfig({
  base: APP_BASE_PATH,
});
```

构建后的 `index.html` 会引用：

```html
<script src="/my-app/assets/index-xxxx.js"></script>
<link href="/my-app/assets/index-xxxx.css" rel="stylesheet" />
```

如果没有设置 `base`，通常会生成：

```html
<script src="/assets/index-xxxx.js"></script>
```

浏览器就会请求：

```text
https://example.com/assets/index-xxxx.js
```

而真正的项目入口是 `/my-app/`，因此服务器可能返回 404 或另一个项目的资源。

## 代码中的图片和 API 也要尊重基础路径

仅设置 Vite `base` 还不够。源码中手写的绝对路径：

```tsx
<img src="/window.svg" />
```

仍然从域名根路径请求。当前项目集中定义：

```ts
export const APP_BASE_PATH = "/my-app/";
```

然后使用：

```tsx
<img src={`${APP_BASE_PATH}window.svg`} />
```

API 同样使用：

```ts
fetch(`${APP_BASE_PATH}api/message`);
```

最后生成的地址是：

```text
/my-app/window.svg
/my-app/api/message
```

把基础路径集中管理可以避免配置文件、图片路径和接口路径各写一套字符串。

## `try_files` 如何返回静态文件

当前配置：

```nginx
location /my-app/ {
    try_files $uri $uri/ /my-app/index.html;
}
```

对于请求：

```text
/my-app/assets/index-xxxx.js
```

Nginx 依次检查：

```text
1. /usr/share/nginx/html/my-app/assets/index-xxxx.js
2. /usr/share/nginx/html/my-app/assets/index-xxxx.js/
3. /usr/share/nginx/html/my-app/index.html
```

第一项存在时直接返回 JavaScript 文件，不会走到最后的 `index.html`。

## SPA 刷新为什么容易出现 404

假设 React Router 中存在：

```text
/my-app/users
```

在应用内部点击链接时，React 可以直接切换页面。但用户刷新浏览器后，会产生真实 HTTP 请求：

```http
GET /my-app/users
```

服务器文件系统中通常没有：

```text
/usr/share/nginx/html/my-app/users
```

如果 Nginx 只查找真实文件，就会返回 404。

`try_files` 最后的回退解决了这个问题：

```nginx
try_files $uri $uri/ /my-app/index.html;
```

处理过程：

```text
/my-app/users 文件不存在
  → 回退到 /my-app/index.html
  → 浏览器加载 React
  → React Router 根据当前 URL 渲染 users 页面
```

这通常称为 SPA history fallback。

## 为什么 API 不能也回退到 `index.html`

如果 `/my-app/api/message` 没有独立的 API `location`，它可能进入静态文件规则：

```text
找不到 /my-app/api/message 文件
  → 返回 index.html
```

前端代码原本期待 JSON，结果得到 HTML，可能出现：

```text
Unexpected token '<'
```

因此需要更具体的规则先接管 API：

```nginx
location ^~ /my-app/api/ {
    proxy_pass http://web:3000/api/;
}

location /my-app/ {
    try_files $uri $uri/ /my-app/index.html;
}
```

## `/my-app` 和 `/my-app/` 的区别

当前项目把不带结尾斜杠的路径统一跳转：

```nginx
location = /my-app {
    return 301 /my-app/;
}
```

原因包括：

- 与 Vite `base: "/my-app/"` 保持一致；
- 避免浏览器解析相对 URL 时出现差异；
- 让后续前缀规则统一处理 `/my-app/`。

访问容器根路径时也会进入应用：

```nginx
location = / {
    return 302 /my-app/;
}
```

这主要方便直接访问本地映射端口进行学习和验证。

## 验证构建产物的路径

不启动 Docker 也可以先执行：

```sh
pnpm --filter docs build
```

然后检查：

```text
apps/docs/dist/index.html
```

资源地址应当以 `/my-app/` 开头：

```html
<script src="/my-app/assets/..."></script>
<link href="/my-app/assets/..." rel="stylesheet" />
```

这只能证明构建路径正确，不能替代容器中的 Nginx 配置验证。

## 常见错误

### 页面 HTML 能打开，但 JS 和 CSS 全部 404

优先检查：

- Vite `base` 是否为 `/my-app/`；
- 源码是否存在以 `/assets` 开头的手写绝对路径；
- 构建产物是否复制到 `/usr/share/nginx/html/my-app`；
- 服务器 Nginx 是否保留 `/my-app` 前缀。

### 刷新二级页面返回 404

检查静态规则是否包含：

```nginx
try_files $uri $uri/ /my-app/index.html;
```

### API 返回了 HTML

检查 `/my-app/api/` 是否被更具体的代理规则接管，而不是落入 SPA 回退。

## 本篇速记

```text
Vite build         生成静态文件
Nginx root         定义文件根目录
Vite base          定义浏览器请求的基础路径
try_files          先找真实文件，再做 SPA 回退

URL /my-app/assets/app.js
  → /usr/share/nginx/html/my-app/assets/app.js

URL /my-app/users
  → 找不到真实文件
  → /my-app/index.html
  → React Router 渲染页面
```

## 自测问题

1. 为什么正式运行镜像不需要保留 Vite？
2. `base: "/my-app/"` 解决了什么问题？
3. `root` 如何与请求 URI 组合成文件路径？
4. `try_files` 为什么要以 `index.html` 作为最后回退？
5. 为什么 API 请求不能落入 SPA 回退？
