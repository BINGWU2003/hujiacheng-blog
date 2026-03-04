---
title: "会议室预订系统：前端项目部署到阿里云"
date: 2025-05-10
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["会议室预订系统"]
series_order: 22
---

上节把后端项目部署到了阿里云，可以在任意电脑上访问。

这节来部署下前端项目。

项目跑起来是这样的架构：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e4256edb138d.png)

在之前 docker compose 的基础上加上 nginx 容器就好了。

我们进入 frontend-admin 项目，加一下 nginx 配置文件：

```
upstream nest-server {
    server 192.168.31.56:3005;
}

server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    location ^~ /api {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://nest-server;
    }

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

nginx 的两个核心功能就是静态资源托管、反向代理。

我们配置了 /api 下的请求走反向代理，转发请求到 nest 服务。

/ 下的静态资源请求返回 index.html。

这里的 ip 是我宿主机的，你可以换成你本地的。

用 nginx 做了反向代理之后，访问的 url 要改一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ee91976c46a8.png)

不再是直接访问 nest 服务了，而是通过 nginx 反向代理到 nest 服务。

然后加一下 Dockerfile

```docker
# build stage
FROM node:18 as build-stage

WORKDIR /app

COPY package.json ./

RUN npm config set registry https://registry.npmmirror.com/

RUN npm install

COPY . .

RUN npm run build

# production stage
FROM nginx:stable as production-stage

COPY --from=build-stage /app/build /usr/share/nginx/html

COPY --from=build-stage /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```
用多阶段构建，第一个阶段把代码复制到容器，执行 npm run build，第二个阶段把上个阶段的产物还有 nginx 配置文件复制过来，把 nginx 服务跑起来。

这里的 CMD 启动命令看别的 nginx 镜像的启动命令就行：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b307a7905c53.png)

加一下 .dockerignore

```
node_modules/
.vscode/
.git/
build/
```

然后 build 下镜像：

```
docker build -t fe-container:first .
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4cac3d6104e7.png)

然后在 docker desktop 里搜索这个镜像，点击 run：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a7cb7ff9ba07.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f7fda270ad3a.png)

进入 backend 项目，把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ecf6ab630f25.png)

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c9b8af2c6833.png)

界面正常渲染，访问接口的 url 也换成了 nginx 的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ecc6175cc248.png)

接口也正常返回了数据。

说明 nginx 的反向代理和静态资源托管都成功了。

但是，当你切换到修改信息界面，会跳到 /login 的 url，这时候返回了 404:

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/76694c88310d.png)

因为我们用的是 browser 路由，也就是 /xxx 的方式，而不是 hash 路由，也就是 ?#/xxx 的方式。

需要在 nginx 里面支持下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/065b5e6cbec1.png)

```
location / {
    root   /usr/share/nginx/html;
    index  index.html index.htm;
    try_files $uri $uri/ /index.html;
}
```
加上这条 try_files，当访问 /login 的时候会先匹配 /login 然后是 /login/ 然后是 /index.html

这样就交给了前端页面来处理 /login 路由。

重新 build 一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/937a561dac8c.png)

把之前的 container 停止、删除，然后重新跑。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/59476b55a6f8.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1549b229b32f.png)

现在你就会发现所有的路由都能正常访问了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/93300f4481df.png)


![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bcda689fb634.png)

当然，我们现在是单独跑的 nginx 的容器，而且反向代理 nest 服务时用的是 ip。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4ab91f553f4c.png)

这样肯定是不好的。

我们希望可以把它也放到 docker-compose.yml 的配置文件里。

直接 docker compose up 一起跑。

我们知道，docker compose 跑的多个容器之间可以通过容器名相互访问。

改一下 nginx 配置，把 ip 换成 nest 服务的容器名：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a8f7bfc651d6.png)

重新 build：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cf37343e0a47.png)

然后在 backend 项目的 docker-compose.yml 里配置下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0e70ed36b774.png)

```yml
version: '3.8'
services:
  fe-app:
    image: fe-container:first
    ports:
      - 80:80
    depends_on:
      - nest-app
    networks:
      - common-network
  nest-app:
    build:
      context: ./
      dockerfile: ./Dockerfile
    depends_on:
      - mysql-container
      - redis-container
    networks:
      - common-network
  mysql-container:
    image: mysql
    volumes:
      - /Users/guang/mysql-data:/var/lib/mysql
    environment:
      MYSQL_DATABASE: meeting_room_booking_system
      MYSQL_ROOT_PASSWORD: guang
    networks:
      - common-network
  redis-container:
    image: redis
    volumes:
      - /Users/guang/redis-data:/data
    networks:
      - common-network
networks:
  common-network:
    driver: bridge
```
把 env 里的 url 改回来：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7132b7f45262.png)

然后跑一下（最好把本地的其他 mysql 和 redis 容器停掉再跑）：

```
docker-compose up
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bb3d7e238148.png)

跑起来之后，浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f86b4c74783f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5deb3a01ebd3.png)

这样，我们就通过 docker compose 一次性跑了 nest、nginx 还有 mysql 和 redis 服务。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/60dd8017db43.png)

但是 fe-container 这个镜像只存在于本地，在阿里云跑 docker compose 的话会找不到这个镜像。

所以我们需要这个镜像上传到阿里云的镜像仓库。

当然，这里直接在服务器上下载代码然后 build 镜像也可以，这里只是为了用一下阿里云的镜像仓库。

阿里云的[容器镜像服务](https://www.aliyun.com/product/acr)个人用是免费的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/300ab4ef446a.png)

进入管理控制台：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1210b692e501.png)

点击创建镜像仓库。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0f1a3961177a.png)

它会让你先创建命名空间。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dbac0fc5a356.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/74291ca1e280.png)

直接说明了如何登陆阿里云镜像仓库和 push 镜像上去：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/da26d9694edc.png)

我们在本地 build 下镜像。

复制下你买的服务器的公网 ip：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d878bfb596f1.png)

改一下项目里的 baseURL，改成服务器的 ip：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dae5d8ca2eba.png)

然后 build 出镜像：
```
docker build -t fe-container:first .
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/38011ad722da.png)

然后分别执行 docker login、docker tag、docker push 把镜像 push 到镜像仓库（直接复制命令就行）：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0bdc19b0119e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e30bc18c9d69.png)

上传之后，点击镜像版本就可以看到这个版本号的镜像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b072f239e738.png)

然后改一下 backend 项目里的 docker-compose.yml 文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/851de86a4ffc.png)

image 改成阿里云镜像仓库里的。

接下来我们在服务器上把它跑起来就行。

保存代码，然后 git push 到代码仓库：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4c4ab421b76b.png)

然后登录服务器，把最新代码 clone 下来（如果你clone 过了，只要 git pull 就行）。

然后跑一下：

```
docker login --username=用户名 registry.cn-qingdao.aliyuncs.com
 
docker-compose up
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f84c310ac343.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ed4dd96b96fd.png)

之后在安全组添加 80 端口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a10bfb4b3830.png)

但是这时你用 ip 访问，会发现没返回东西：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/12a6e7bb2b33.png)

为什么呢？

往上翻一下日志，可能会有这个报错：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ed42739dd0f.png)

说是 docker 镜像的 platform 不匹配。

因为我本地是 m1 芯片的 mac ，build 出来的镜像在 linux 上跑不了。

当然，你不一定遇到这个问题，如果没遇到这个问题下面的步骤可以跳过。

如果遇到这个问题，那就需要 build 的时候加上 platform 了：

```
docker build -t fe-container:first --platform linux/amd64 .
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/75e9ffc50f60.png)

我重新 build 了一下镜像，指定了目标 platform。

然后重新 docker login、docker tag、docker push 来上传镜像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/34642c8a2377.png)

上传之后在服务器把之前镜像删掉，重新跑：

```
docker-compose down --rmi all

docker login --username=用户名 registry.cn-qingdao.aliyuncs.com

docker-compose up
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2507b7f9d5cb.png)

这时浏览器就可以看到页面正常渲染了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e0fbd0bfa8bb.png)

如果你没遇到 platform 的问题，那直接就可以在浏览器看到结果。

请求的 url 也是对的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/01931db955e0.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6d83be5469af.png)

只是现在没有数据，后面加一下初始数据就好了。

这样，我们前端部分也部署完成了。

代码在小册仓库：

[backend](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_backend)。

[frontend-admin](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_frontend_admin)。

## 总结

我们通过 nginx 部署了前端项目，用它来做静态资源托管和 nest 服务的反向代理。

通过 Dockerfile 的多阶段构建，第一个阶段 npm run build 出产物，第二个阶段把产物和 nginx 配置文件复制过去跑 nginx 服务。

之后用 docker build 构建出镜像，把它上传到阿里云镜像仓库。

在另一边的 docker compose 配置文件里添加这个 nginx 的容器配置。

这样服务端那边就可以用 docker compose up 一次性跑起 nginx、nest、mysql、redis 等容器，前后端服务一键启动。

这就是 docker compose 的作用。

过程中如果遇到 platform 不一致的问题，那就 build 的时候指定下 platform 再上传就好了。

这样，我们就通过 docker-compose 把前后端项目都部署到了阿里云：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/67915ee66bfa.png)
