---
title: "聊天室：收藏"
date: 2025-07-11
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["WebSocket 与聊天室"]
series_order: 21
---

最后我们再来实现下收藏功能：

![](<https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/574dcb4751974f3f8f38a9c90236f1e7~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1440&h=972&s=62875&e=png&b=ffffff>)

聊天的时候可以收藏某条消息，然后在收藏列表查看。

消息分为文字、图片、文件三类，收藏也是这三类。

我们先加一个收藏表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cb3690106428.png)

```javascript
model Favorite {
  id Int @id @default(autoincrement())
  chatHistoryId Int
  uerId Int
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt
}
```
每个收藏只要记录对应的 chatHistoryId 和 userId 即可。

这里我们同样没有用外键。

用 migrate dev 生成表：

```
npx prisma migrate dev --name favorite
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5819b7dec180.png)

sql 没啥问题：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4ec692082d56.png)

然后创建一个模块：

```
nest g resource favorite
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/50905918cf0b.png)

在 FavorateController 添加三个路由：

```javascript
import { Controller, Get, Query } from '@nestjs/common';
import { FavoriteService } from './favorite.service';
import { RequireLogin, UserInfo } from 'src/custom.decorator';

@Controller('favorite')
@RequireLogin()
export class FavoriteController {
  constructor(private readonly favoriteService: FavoriteService) {}

  @Get('list')
  async list(@UserInfo('userId') userId: number) {
    return this.favoriteService.list(userId);
  }

  @Get('add')
  async add(@UserInfo('userId') userId: number, @Query('chatHistoryId') chatHistoryId: number) {
    return this.favoriteService.add(userId, chatHistoryId);
  }

  @Get('del')
  async del(@Query('id') id: number) {
    return this.favoriteService.del(id);
  }
}

```
list、add、del 这三个路由都需要登录，在 Controller 上加上 @RequireLogin 装饰器。

然后取 request.user 里的 userId 传入 handler。

分别在 service 实现这三个方法：

```javascript
import { Inject, Injectable } from '@nestjs/common';
import { PrismaService } from 'src/prisma/prisma.service';

@Injectable()
export class FavoriteService {

    @Inject(PrismaService)
    private prismaService: PrismaService;

    async list(userId: number) {
        const favorites = await this.prismaService.favorite.findMany({
            where: {
                uerId: userId
            }
        })
        const res = [];
        for(let i = 0; i< favorites.length; i++) {
            const chatHistory = await this.prismaService.chatHistory.findUnique({
                where: {
                    id: favorites[i].chatHistoryId
                }
            })
            res.push({
                ...favorites[i],
                chatHistory
            })
        }
        return res;
    }

    async add(userId: number, chatHistoryId: number) {
        return this.prismaService.favorite.create({
            data: {
                uerId: userId,
                chatHistoryId
            }
        })
    }

    async del(id: number) {
        return this.prismaService.favorite.deleteMany({
            where: {
                id
            }
        })
    }

}
```
list 方法把关联的 chatHistory 查出来。

测试下：

添加两条收藏：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/529a0f94ba2e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ea82cfabf14c.png)

查看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e511958e1b8a.png)

删除一条：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e9bd9f50cd3b.png)

查看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/94e65f6d6e82.png)

这样，接口就都完成了。

我们再写下前端页面：

先在 interfaces 添加几个接口：

```javascript
export async function queryFavoriteList() {
    return axiosInstance.get(`/favorite/list`);
}

export async function favoriteAdd(chatHistoryId: number) {
    return axiosInstance.get(`/favorite/add`, {
        params: {
            chatHistoryId
        }
    });
}

export async function favoriteDel(id: number) {
    return axiosInstance.get(`/favorite/del`, {
        params: {
            id
        }
    });
}
```
写下页面 src/pages/Collection/index.tsx

```javascript
import {  Table, message } from "antd";
import { useEffect, useState } from "react";
import { ColumnsType } from "antd/es/table";
import { queryFavoriteList } from "../../interfaces";

interface Favorite {
    id: number
    chatHistory: {
        id: number
        content: string
        type: number
        createTime: Date
    }
}

export function Collection() {
    const [favoriteList, setFavoriteList] = useState<Array<Favorite>>([]);

    const columns: ColumnsType<Favorite> = [
        {
            title: 'ID',
            dataIndex: 'id'
        },
        {
            title: '内容',
            render:  (_, record) => (
                <div>
                    {
                        record.chatHistory.type === 0 
                            ? record.chatHistory.content 
                            : record.chatHistory.type === 1
                                ? <img src={record.chatHistory.content} style={{maxHeight: 200}}/>
                                : <a href={record.chatHistory.content} download>{record.chatHistory.content}</a>
                    }
                </div>
            )
        },
        {
            title: '发表时间',
            render: (_, record) => (
                <div>
                    {new Date(record.chatHistory.createTime).toLocaleString()}
                </div>
            )
        },
        {
            title: '操作',
            render: (_, record) => (
                <div>
                    <a href="" onClick={() => {}}>删除</a>
                </div>
            )
        }
    ]

    const query = async () => {
        try{
            const res = await queryFavoriteList();

            if(res.status === 201 || res.status === 200) {
                setFavoriteList(res.data.map((item: Favorite) => {
                    return {
                        ...item,
                        key: item.id
                    }
                }));
            }
        } catch(e: any){
            message.error(e.response?.data?.message || '系统繁忙，请稍后再试');
        }
    };

    useEffect(() => {
        query();
    }, []);


    return <div id="friendship-container">
        <div className="favorite-table">
            <Table columns={columns} dataSource={favoriteList} style={{width: '1000px'}}/>
        </div>

    </div>
}
```
就是请求列表接口，用 table 展示。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7a9a30fbd27b.png)

我们实现下收藏功能。

简化下交互，双击聊天记录触发收藏：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/635e8e3b9e4e.png)
```javascript
onDoubleClick={() => {
    addToFavorite(item.id)
}}
```
```javascript
async function addToFavorite(chatHistoryId: number) {
    try{
        const res = await favoriteAdd(chatHistoryId);

        if(res.status === 201 || res.status === 200) {
            message.success('收藏成功')
        }
    } catch(e: any){
        message.error(e.response?.data?.message || '系统繁忙，请稍后再试');
    }
}
```
我们收藏几条消息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8bd2f12e56b8.gif)

提示收藏成功，之后在收藏页面就可以看到了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dca5fbd108fc.png)

然后再做下删除：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/408ec62701b0.png)

```javascript
<Popconfirm
    title="删除收藏"
    description="确认删除吗？"
    onConfirm={() => delFavorite(record.id)}
    okText="Yes"
    cancelText="No"
>  
    <a href="#" >删除</a>
</Popconfirm>
```

```javascript
async function delFavorite(id: number) {
    try{
        const res = await favoriteDel(id);

        if(res.status === 201 || res.status === 200) {
            message.success('删除成功');
            query();
        }
    } catch(e: any){
        message.error(e.response?.data?.message || '系统繁忙，请稍后再试');
    }
}
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9ca22e520a54.gif)

没啥问题。

这样，收藏功能就完成了。

[前端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/chat-room-frontend)

[后端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/chat-room-backend)

## 总结

这节我们实现了收藏功能。

首先创建了收藏表，关联 user 和 chatHistory。

然后创建了 list、add、del 三个接口。

之后在前端通过 table 展示 list 接口的数据，然后双击聊天记录的时候调用 add 添加收藏，点击删除的时候调用 del 删除收藏

这样就实现了收藏功能。
