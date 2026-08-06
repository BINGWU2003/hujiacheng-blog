---
title: "Docker 基础篇：镜像、容器、端口与生命周期"
date: 2026-08-06
draft: false
description: "从 hello-world 开始理解 Docker 镜像、容器、端口映射、容器 ID 和常见生命周期命令。"
tags: ["Docker", "镜像", "容器", "端口映射"]
categories: ["Docker 学习笔记"]
series: ["Docker 快速入门"]
series_order: 1
showTableOfContents: true
showReadingTime: true
showWordCount: true
---

## 最先建立的心智模型

Docker 最重要的两个对象是镜像和容器。

```text
Dockerfile
    │ docker build
    ▼
镜像 Image
    │ docker run
    ▼
容器 Container
```

可以用下面的类比帮助记忆：

```text
镜像 ≈ 只读模板或安装包
容器 ≈ 使用模板创建出来的运行实例
```

同一个镜像可以创建多个容器。删除容器不会自动删除镜像，因此容器删除后仍然可以从镜像重新创建。

## 验证 Docker 环境

启动 Docker Desktop，等待 Docker Engine 正常运行，然后执行：

```sh
docker version
```

输出中同时存在 `Client` 和 `Server`，说明：

- Docker CLI 可以使用；
- CLI 已经连接到 Docker Engine；
- Docker Desktop 后端正常运行。

第一次实践时，我的 Docker Desktop 安装在用户目录，但终端找不到 `docker`：

```text
C:\Users\LX\AppData\Local\Programs\DockerDesktop\resources\bin
```

在 PowerShell 中可以临时加入当前会话的 `PATH`：

```powershell
$env:Path += ';C:\Users\LX\AppData\Local\Programs\DockerDesktop\resources\bin'
```

该修改只影响当前终端。重新打开终端后如果仍然找不到 Docker，应把安装目录加入用户环境变量。

## 第一个容器：hello-world

```sh
docker run --rm hello-world
```

当本地没有 `hello-world` 镜像时，Docker 会依次完成：

1. 在本地查找 `hello-world:latest`；
2. 从 Docker Hub 拉取镜像；
3. 从镜像创建一个容器；
4. 启动容器并执行镜像定义的程序；
5. 将程序输出传回终端；
6. 程序结束后，因为存在 `--rm`，自动删除容器。

镜像仍然保留：

```sh
docker image ls hello-world
```

容器已经被删除：

```sh
docker ps -a
```

## `docker ps` 中的 `ps` 是什么

`ps` 通常理解为 `process status`，名称来自 Unix/Linux 的 `ps` 命令。

```sh
docker ps
```

只列出正在运行的容器。

```sh
docker ps -a
```

`-a` 是 `--all`，会列出所有容器，包括已经停止的容器。

语义更完整的等价命令是：

```sh
docker container ls
docker container ls --all
```

## 构建第一个项目镜像

在项目根目录执行：

```sh
docker build -t docker-demo-web:v1 .
```

参数含义：

```text
docker build                  构建镜像
-t docker-demo-web:v1         设置仓库名和标签
.                             使用当前目录作为构建上下文
```

`docker-demo-web` 是镜像仓库名，`v1` 是标签。标签常用于区分版本，但它本质上只是指向某个镜像的可读名称。

查看镜像：

```sh
docker image ls docker-demo-web
```

## 从镜像创建容器

```sh
docker run -d --name docker-demo-web -p 3000:3000 docker-demo-web:v1
```

参数含义：

| 参数                     | 含义                          |
| ------------------------ | ----------------------------- |
| `-d`                     | 后台运行，即 detached mode    |
| `--name docker-demo-web` | 为容器指定容易记忆的名称      |
| `-p 3000:3000`           | 将宿主机 3000 映射到容器 3000 |
| `docker-demo-web:v1`     | 用于创建容器的镜像            |

端口映射的方向是：

```text
-p 宿主机端口:容器端口
```

因此浏览器访问：

```text
http://localhost:3000
```

请求会进入容器的 3000 端口。

## 那串很长的字符串是什么

后台启动成功后，Docker 会输出类似：

```text
fca356fb0b764095e038434073c47b44c9cb07cae44feae8856539bd6b23ba9e
```

这是容器 ID，用于唯一标识容器。日常命令可以使用：

- 完整容器 ID；
- 不冲突的 ID 前缀，例如 `fca356`；
- 自己设置的容器名称，例如 `docker-demo-web`。

名称通常更容易阅读：

```sh
docker logs docker-demo-web
```

## 容器生命周期

查看容器：

```sh
docker ps
docker ps -a
```

停止容器：

```sh
docker stop docker-demo-web
```

重新启动已存在的容器：

```sh
docker start docker-demo-web
```

查看日志：

```sh
docker logs docker-demo-web
docker logs --follow docker-demo-web
```

按 `Ctrl+C` 只会退出日志跟随，不会停止容器。

进入正在运行的容器：

```sh
docker exec -it docker-demo-web sh
```

进入后可以观察容器文件系统和运行环境：

```sh
pwd
ls
node --version
exit
```

`exit` 只退出交互终端，不会停止容器。

删除容器：

```sh
docker stop docker-demo-web
docker rm docker-demo-web
```

删除镜像使用的是另一个命令：

```sh
docker image rm docker-demo-web:v1
```

## 用删除和重建理解镜像与容器

执行：

```sh
docker stop docker-demo-web
docker rm docker-demo-web
docker image ls docker-demo-web
```

容器消失，但镜像仍然存在。重新运行：

```sh
docker run -d --name docker-demo-web -p 3000:3000 docker-demo-web:v1
```

应用又恢复了。这说明：

```text
镜像是可重复使用的模板
容器是可以删除和重建的实例
```

对于无状态服务，应该尽量让容器可重建。需要长期保存的数据不应只放在容器可写层中，而应使用 Volume 或外部存储。

## Shell 续行符踩坑

我曾在 CMD 中输入带 PowerShell 反引号的命令：

```text
docker run -d ` --name ...
```

结果出现：

```text
docker: invalid reference format
```

原因不是镜像坏了，而是不同 Shell 的续行符不一样：

```text
CMD        → ^
PowerShell → `
```

最稳妥的方式是使用单行命令：

```sh
docker run -d --name docker-demo-web -p 3000:3000 docker-demo-web:v1
```

## 本篇速记

```text
Dockerfile --build--> 镜像 --run--> 容器

image ls      查看镜像
ps            查看运行中的容器
ps -a         查看全部容器
run           从镜像创建并启动容器
stop/start    停止/恢复已有容器
logs          查看容器日志
exec          在运行中的容器内执行命令
rm            删除容器
image rm      删除镜像
```

## 自测问题

1. 删除容器后，镜像是否还存在？
2. `docker start` 和 `docker run` 的区别是什么？
3. `-p 8080:3000` 中哪个是宿主机端口？
4. `docker logs --follow` 后按 `Ctrl+C` 会不会停止容器？
5. 为什么同一个镜像可以创建多个容器？

如果这些问题能直接回答，就已经掌握了 Docker 最基础的对象模型。
