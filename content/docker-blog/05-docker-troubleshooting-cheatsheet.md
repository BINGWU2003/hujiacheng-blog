---
title: "Docker 排障与速查篇：真实错误复盘和常用命令"
date: 2026-08-06
draft: false
description: "整理本次 Docker 学习中遇到的真实错误、分层诊断方法、常用命令和安全清理原则。"
tags: ["Docker", "排障", "命令速查", "Docker Compose"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 5
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 排障的基本原则

不要只看浏览器页面，也不要看到报错就立即重装 Docker。按照从底层到上层的顺序缩小范围：

```text
1. Docker CLI 是否可用
2. Docker Engine 是否运行
3. 镜像是否构建成功
4. 容器是否存在和运行
5. 进程是否监听预期端口
6. Docker 网络和 DNS 是否正常
7. HTTP 是否返回正确状态
8. 代理路径和业务数据是否正确
9. 浏览器是否仍在使用缓存
```

每一层都使用对应证据，不要凭感觉判断。

## 错误一：找不到 `docker` 命令

### 现象

```text
The term 'docker' is not recognized...
```

### 原因

Docker Desktop 已安装，但 Docker CLI 所在目录没有进入当前终端的 `PATH`。

本次安装位置：

```text
C:\Users\LX\AppData\Local\Programs\DockerDesktop\resources\bin
```

### 临时处理

PowerShell：

```powershell
$env:Path += ';C:\Users\LX\AppData\Local\Programs\DockerDesktop\resources\bin'
```

验证：

```sh
docker version
```

如果只有 Client、没有 Server，应检查 Docker Desktop 和 Docker Engine 是否已启动。

## 错误二：`invalid reference format`

### 现象

```text
docker: invalid reference format
```

### 原因

我在 CMD 中复制了 PowerShell 多行命令，反引号被当成普通字符，Docker 最终无法正确解析镜像引用。

### 处理

使用单行命令：

```sh
docker run -d --name docker-demo-web -p 3000:3000 docker-demo-web:v1
```

续行符：

```text
CMD        → ^
PowerShell → `
```

## 错误三：成功后输出一串长字符串

### 现象

```text
fca356fb0b764095e038434073c47b44c9cb07cae44feae8856539bd6b23ba9e
```

### 结论

这不是错误，是后台模式 `-d` 启动成功后输出的容器 ID。

查看容器：

```sh
docker ps
```

可以使用名称、完整 ID 或唯一 ID 前缀操作容器。

## 错误四：`docker image ls` 传入两个仓库名

### 现象

```text
docker: 'docker image ls' requires at most 1 argument
```

### 原因

`docker image ls` 最多接受一个位置参数：

```sh
docker image ls docker-demo-web docker-demo-docs
```

这种写法无效。

### 处理

分别查询：

```sh
docker image ls docker-demo-web
docker image ls docker-demo-docs
```

或者使用过滤器：

```sh
docker image ls --filter "reference=docker-demo-*"
```

## 错误五：构建成功，但页面仍是旧内容

### 现象

- 本机源码已经修改；
- `docker compose build web` 成功；
- 浏览器仍显示旧文案。

### 原因

新镜像已经生成，但运行中的容器仍引用旧镜像 ID。镜像不可变，已有容器不会原地变成新镜像。

### 诊断

查看镜像：

```sh
docker image inspect docker-demo-web:v1
```

查看容器引用的镜像：

```sh
docker inspect docker-demo-web-1
```

### 处理

```sh
docker compose up -d --force-recreate web
```

构建和替换一起执行：

```sh
docker compose up -d --build --force-recreate web
```

最后再使用 `Ctrl+F5` 强制刷新浏览器。

## 错误六：容器显示 `unhealthy`

### 现象

```text
Up ... (unhealthy)
```

但从 Windows 浏览器访问页面正常。

### 原因

健康检查使用 `localhost`，容器内优先解析到 IPv6 `::1`，应用只监听 IPv4。

### 诊断

```sh
docker inspect docker-demo-web-1
```

健康日志显示：

```text
wget: can't connect to remote host: Connection refused
```

在容器中测试明确的 IPv4 地址：

```sh
docker compose exec web wget --spider http://127.0.0.1:3000
```

### 处理

```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--spider", "http://127.0.0.1:3000"]
```

## 错误七：Ping 成功，但 HTTP 返回 403

### 现象

```sh
docker compose exec web ping -c 3 docs
```

成功且 0% 丢包。

但：

```sh
docker compose exec web wget --spider http://docs:3001
```

返回：

```text
HTTP/1.1 403 Forbidden
```

### 原因

Docker DNS 和网络均正常，Vite Preview Server 拒绝了 Host 为 `docs` 的请求。

### 处理

```ts
preview: {
  allowedHosts: ["docs"],
}
```

这个案例说明 Ping 只验证较底层的网络连通性，不能证明 HTTP 应用一定接受请求。

## 错误八：`docker compose ps` 为什么只看到当前项目

### 原因

Compose 读取当前目录的 `compose.yaml`，获得项目名，然后通过容器标签筛选当前项目资源。

查看全部 Compose 项目：

```sh
docker compose ls
```

查看全部运行容器：

```sh
docker ps
```

查看当前 Compose 项目：

```sh
docker compose ps
```

## 分层诊断清单

### 1. Docker 层

```sh
docker version
docker info
```

检查 CLI 和 Engine。

### 2. 镜像层

```sh
docker image ls
docker image inspect docker-demo-web:v1
docker history docker-demo-web:v1
```

检查镜像是否存在、标签指向什么镜像以及镜像层组成。

### 3. 容器层

```sh
docker ps
docker ps -a
docker compose ps
docker inspect docker-demo-web-1
```

检查容器是否退出、使用哪个镜像、健康状态和端口配置。

### 4. 日志层

```sh
docker compose logs --tail 100 web
docker compose logs --follow docs
```

先看服务启动日志，再看请求日志和错误日志。

### 5. 进程和文件层

```sh
docker compose exec web sh
```

容器内可以执行：

```sh
pwd
ls
ps
node --version
```

### 6. DNS 和网络层

```sh
docker compose exec docs ping -c 3 web
docker network ls
docker network inspect docker-demo_backend
```

### 7. HTTP 层

```sh
docker compose exec docs wget --spider http://web:3000
docker compose exec docs wget -qO- http://web:3000/api/message
```

### 8. 宿主机入口

```sh
curl http://localhost:3001/api/message
```

如果容器内部请求成功、宿主机失败，重点检查 `ports`、宿主机防火墙和端口占用。

## Docker 常用命令速查

### 镜像

```sh
docker image ls
docker image ls --filter "reference=docker-demo-*"
docker image inspect IMAGE
docker image rm IMAGE
docker pull IMAGE
docker tag SOURCE TARGET
```

### 容器

```sh
docker ps
docker ps -a
docker run -d --name NAME -p HOST:CONTAINER IMAGE
docker stop NAME
docker start NAME
docker restart NAME
docker logs NAME
docker logs --follow NAME
docker exec -it NAME sh
docker inspect NAME
docker rm NAME
```

### Compose

```sh
docker compose config
docker compose up -d
docker compose up -d --build
docker compose ps
docker compose images
docker compose logs --tail 50
docker compose logs --follow SERVICE
docker compose exec SERVICE COMMAND
docker compose stop
docker compose start
docker compose restart SERVICE
docker compose build SERVICE
docker compose up -d --force-recreate SERVICE
docker compose down
docker compose ls
```

### 网络

```sh
docker network ls
docker network inspect NETWORK
```

### 磁盘占用

```sh
docker system df
```

## 安全清理原则

暂停项目但保留容器：

```sh
docker compose stop
```

删除当前项目的容器和网络，保留镜像：

```sh
docker compose down
```

删除明确指定的旧镜像：

```sh
docker image rm docker-demo-web:single-stage
```

不要在不了解影响范围时直接执行：

```sh
docker system prune -a
docker compose down -v
```

风险：

- `docker system prune -a` 可能删除其他项目未使用的镜像和缓存；
- `docker compose down -v` 会删除 Compose 管理的数据卷；
- 数据卷中的数据库数据可能无法恢复。

清理前先执行：

```sh
docker system df
docker ps -a
docker image ls
docker volume ls
```

确认目标后再删除。

## 最终心智模型

```text
源码
  ↓ Dockerfile + docker build
镜像
  ↓ docker run / compose up
容器
  ├─ 进程
  ├─ 文件系统
  ├─ 网络
  ├─ 健康状态
  └─ 日志

多个容器
  ↓ Compose 网络和服务发现
服务系统
  ↓ 端口发布或反向代理
外部访问
```

## 最终自测

1. 镜像、容器和 Compose 服务分别是什么？
2. 为什么修改源码后需要重新构建并创建容器？
3. `localhost` 在宿主机和容器中分别指向谁？
4. `ports`、`EXPOSE` 和内部容器端口有什么区别？
5. `Up` 与 `healthy` 有什么区别？
6. 服务名、容器名和容器 IP 哪个最适合应用间连接？
7. `wget --spider` 与反向代理有什么区别？
8. 删除容器、镜像和 Volume 的风险分别是什么？

能够顺利回答这些问题，说明已经掌握了本次 Docker 实践的核心知识。
