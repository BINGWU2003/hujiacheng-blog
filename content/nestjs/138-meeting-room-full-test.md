---
title: "会议室预订系统：全部功能测试"
date: 2025-05-18
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["会议室预订系统"]
series_order: 30
---

做完项目之后，我们整体测试一下。

按照当时的分析出的功能来测：

首先是普通用户的：

## 普通用户

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fe6b3ef4922f.png)

进入 backend 和 frontend_user 项目，跑起来。

```
npm run start:dev
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6f1b6012dde8.png)

```
npm run start
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3b650fa0cdf1.png)

### 注册

首先填入信息，发送验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9515d23c2590.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f62c8cb2b941.png)

用户名要求唯一：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/71ec151933c7.gif)

注册成功后我们登录下：

### 登录

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/301a5f5713e6.gif)

刚才注册的账号可以登录。

然后还可以 google 账号直接登录，不需要注册：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/20fd54c10202.gif)

### 修改密码

填入用户名、邮箱，点击发送验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/54ca2baeeb71.png)

（其实当时邮箱应该添加唯一约束，也就是能唯一确定用户，这样就可以不需要填用户名了）

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0347c8ef9a46.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3adffa598a9b.gif)

修改成功。

再登录下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dbb9965abecf.gif)

没问题。

### 修改个人信息

继续看当时分析的普通用户的需求：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/285c71b22fd2.png)

登录后可以修改个人信息。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e83f6cd9a322.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4d522745a3a9.png)

修改下头像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0899190d6c60.gif)

没问题。

### 会议室列表

可以查看会议室列表，根据名称、容纳人数、设备来搜索会议室：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0213e574085d.gif)

### 提交预定申请

选择好会议室之后可以提交预定申请：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/07de0be73715.gif)

填入预定时间、备注之后，可以提交预定申请：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/640ac84daedd.gif)

然后在预定历史里就可以看到这次预定。

当然，你可以可以取消预定：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4c00d747f67b.gif)

这样该预定记录就会回到已解除状态。

## 管理员

接下来我们进入管理员界面：

登录和修改密码和普通用户差不多。

我们来测试下各种管理功能：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/963758183888.png)

### 用户管理

进入 frontend_admin 项目，跑起来：

```
npm run start
```
然后登录下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f0ba983c5468.gif)

可以按照用户名、昵称、邮箱来搜索用户：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7ef857e3bfdb.gif)

（这个冻结功能目前没啥用，可以去掉）

### 会议室管理

可以按照名称、人数、设备来搜索会议室：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/46c4abdf2a96.gif)

可以添加会议室：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/94181445f506.gif)

之后在用户端这边也可以看到这个会议室了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/94d5c4461b4c.png)

当然，也可以更新信息和删除：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1a1403c85217.gif)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e5a5fc01cc1d.gif)

### 预定管理

预定管理可以按照预定人、会议室名称、预定时间、位置等来搜索预定申请：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/80e6336f3502.gif)

比如我们在用户端申请一个：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/45aacf3e3224.gif)

这时候管理端就可以看到这个申请了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b0a6d1cee92f.png)

点击通过，然后在用户端就可以看到审批通过了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8f0379faf992.gif)

这时候该会议室该时间段就不能再被预定：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55c642d1f551.gif)

### 统计

这个模块就是可以查看哪些会议室在过去一段时间内被预定的频率高，哪些用户使用会议室的频率高：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e90a6f04fd71.gif)

## 总结

我们按照最初的需求分析来过了一遍系统的功能。

我们首先测了注册、登录、修改密码、google 登录这些通用功能。

用户端可以搜索会议室、提交预定申请。

管理端可以审批预定申请，管理会议室、查看统计等。

整个流程是没问题的。

项目部署上线之后，就可以投入使用了。
