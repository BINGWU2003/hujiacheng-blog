---
title: "聊天室：全部功能测试"
date: 2025-07-12
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["WebSocket 与聊天室"]
series_order: 22
---

做完项目之后，我们整体测试一下。

按照之前的需求分析来测：

![](<https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f78413f01d2c43cf82ca2db9daf8ebd9~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=944&h=1100&s=126010&e=png&b=ffffff>) 

把 backend 服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/562b86424874.png)

然后把 frontend 项目跑起来：

```
npm run dev
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a15cb3af396.png)

### 注册

首先填入信息，发送验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55da6bf6e44c.gif)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1c69bb2b6395.png)

注册成功后我们登录下：

### 登录

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/452ae5eef4f2.gif)

刚才注册的账号可以登录。

忘了密码可以修改：

### 修改密码

填入用户名、邮箱，点击发送验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7fce22c1fef6.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c7d0e3a5e83a.png)

修改成功，再登录下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e53ea3771f22.gif)

### 修改个人信息

登录后可以修改个人信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ceeafaf6bf8.gif)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4c980d6ac826.png)

修改完之后，右上角头像就变了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2ccd0d9312f9.png)

### 添加好友

现在没有好友，我们添加一个：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/36d4f83f3ea3.gif)

输入添加好友的 username，填写添加理由，就会发送好友请求。

在通知列表可以看到所有好友请求的状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4d036db83f45.gif)

登录 guang 的账号，通过下好友请求：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a68a6e6c431a.gif)

通过后就可以在好友列表里看到这个好友。

回到 catcat 的账号：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/23c0e0671334.gif)

可以看到好友请求变成了通过状态，好友列表里也可以看到这个好友了。

## 聊天

点击好友列表里的聊天按钮，可以和对应好友聊天：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/76f703c0c219.gif)

可以发送表情、图片、文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/afd04f017d3d.gif)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b19e706f218a.gif)

文件点击就可以下载。

双方是实时通信的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/791bbb51678b.gif)

## 群聊

除了和好友聊天，还可以创建群聊：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9310ea689277.gif)

创建后成员只有当前用户。

可以添加成员：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/378f3e34dff6.gif)

然后进入群聊：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a85401e7f1a5.gif)

qiang 和 guang 也会收到消息，因为都在这个群聊里：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c0ca614cded3.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/52c10fd073c4.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3fdbc5fff5d0.png)

可以一起聊天。

## 收藏

聊天记录可以双击收藏：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0a4966ea974b.gif)

收藏可以删除：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c016ca5ac783.gif)

这就是聊天室的全部功能了。

看下之前的需求分析：

![](<https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f78413f01d2c43cf82ca2db9daf8ebd9~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=944&h=1100&s=126010&e=png&b=ffffff>) 

基本都完成了。

## 总结

我们过了一遍聊天室的功能。

首先是注册、登录、修改密码、修改个人信息这些功能。

然后可以添加好友、查看好友列表，和好友聊天。

可以创建群聊、加入群聊、查看群聊成员、在群聊聊天。

聊天可以发送表情、图片、文件，文件可以下载。

聊天记录可以收藏，在收藏列表里查看，也可以删除收藏。

这就是聊天室的全部功能。

项目部署上线之后，就可以和别的用户聊天了。