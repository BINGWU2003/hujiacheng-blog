---
title: "考试系统：整体测试"
date: 2025-06-19
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["考试系统"]
series_order: 16
---

项目做完后我们整体测试下。

首先注册一个账号：

![2024-08-27 20.24.17.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/677af6c2b47c.gif)

填入邮箱后点击发送验证码。


![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/61277b49ec01.png)

输入验证码后点击注册。

![2024-08-27 20.25.28.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/014f2370587f.gif)

然后用这个账号登录下：

![2024-08-27 20.25.52.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/36cc1bd30896.gif)

登录成功进入试卷列表页面。

如果忘了密码可以重置：


![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0a0f7a0ee145.png)

试卷列表可以创建试卷：


![2024-08-27 20.28.11.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7c0e21db0b0e.gif)

删除试卷会放入回收站：

![2024-08-27 20.28.29.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dccac2d0b2ff.gif)

我们编辑下试卷：


![2024-08-27 20.29.38.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1035afbc4a1b.gif)

可以拖拽题目到试卷，选中后在右侧编辑：


![2024-08-27 20.33.03.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ab0cf8defeaf.gif)

我们添加一个单选，一个多选：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b3475fb72e18.png)

可以预览编辑好的试卷，然后点击保存：

![2024-08-27 20.34.38.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3d3a06a5a934.gif)

之后返回列表页。

![2024-08-27 20.36.30.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/db10490a0649.gif)

可以看到考试的链接，把它分享出去，大家就可以来答题了。

![2024-08-27 20.37.29.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cc4663c684c2.gif)

答完后会马上有分数，并在下面显示正确答案。

可以看到所有考生的分数排行榜，并可以下载所有答卷：

![2024-08-27 20.40.36.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9b2b7ee4b5dd.gif)

![2024-08-27 20.40.51.gif](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1cac039b0936.gif)

这就是考试系统的全部功能。

看下之前的需求分析：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8543e871a187.png)

都完成了。

对比下问卷星的流程：

它的问卷类型支持考试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9bc94fa75e08.png)

创建考试后，进入编辑器，可以添加不同的题型：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ed1b80dbfb18.gif)

每道题目都可以设置分数、答案解析：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ca906fad94a.png)

保存后，点击发布，会生成链接和二维码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2c9bb9dd2fdf.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0cd776b29284.png)

用户扫码后就可以答题了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b3174263375b.png)

并且答完点提交会立刻判卷，给出分数，还可以查看正确答案和解析：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1b92f412ed6e.png)

我们再答一份，然后可以在后台看到所有的答卷数据：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2f2269fc1f4.png)

可以下载答卷数据为 excel：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c0a9c8387c30.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5daf2bc75ff8.png)

可以查看考试排行榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cd247dc4e396.png)

虽然我们简化了一些，但整体流程和功能是一样的。
