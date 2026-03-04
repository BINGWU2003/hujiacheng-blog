---
title: "基于 Redis 实现各种排行榜（周榜、月榜、年榜）"
date: 2025-06-03
draft: false
description: ""
tags: ["nestjs", "redis"]
categories: ["NestJS"]
series: ["Redis 高级应用"]
series_order: 3
---

生活中各种排行榜可太多了。

比如经常有瓜的微博文娱榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/041a9256b4e2.jpg)

掘金的文章榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2f249b11b2fd.png)

作者榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3d034ea0185d.png)

微信的步数排行榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0a0317bf7981.jpg)

我最近订的自习室也有学习时长排行榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9b3c777f272d.jpg)

排行的依据各有不同，有的是根据学习时长，有的是根据阅读数、点赞数，有的是根据搜索次数等。

那这些排行榜是怎么实现的呢？

有的同学说，在 mysql 里加一个排序的字段，比如热度，然后根据根据这个字段来排序不就行了？

这样是能完成功能，但是效率太低了。

数据库的读写性能比 Redis 低很多，而且可能这个排序的依据只是一个临时数据，不需要存到数据库里。

一般涉及到排行榜，都是用 Redis 来做，因为它有一个专为排行榜准备的数据结构：有序集合 ZSET。

它有这些命令：

**ZADD**：往集合中添加成员

**ZREM**：从集合中删除成员

**ZCARD**：集合中的成员个数

**ZSCORE**：某个成员的分数

**ZINCRBY**：增加某个成员的分数

**ZRANK**：成员在集合中的排名

**ZRANGE**：打印某个范围内的成员

**ZRANGESTORE**：某个范围内的成员，放入新集合

**ZCOUNT**：集合中分数在某个返回的成员个数

**ZDIFF**：打印两个集合的差集

**ZDIFFSTORE**：两个集合的差集，放入新集合

**ZINTER**：打印两个集合的交集

**ZINTERSTORE**：两个集合的交集，放入新集合

**ZINTERCARD**：两个集合的交集的成员个数

**ZUNION**：打印两个集合的并集

**ZUNIONSTORE**：两个集合的并集，放回新集合

我们依次来试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7c2ec2252d2a.png)

```redis
ZADD set1 1 mem1 2 mem2 3 mem3
```

在 RedisInsight 里输入命令，点击执行。

点击刷新就可以看到这个集合：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/743eb51f1f06.png)

三个成员，分数分别是 1、2、3

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bece46396361.png)

用命令看的话就是 ZRANGE：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d2dbbb0b1374.png)

```
ZRANGE set1 0 -1
```

范围从 0 到 -1 就是返回全部。

默认是分数从小到大排序，也可以从大到小，加个 REV 就行：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f6493db57073.png)

```
ZRANGE set1 0 -1 REV
```
还可以用 ZRANGESTORE 把它存入新集合：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f7ee37777b73.png)

```
ZRANGESTORE rangeset set1 0 -1
```

查看下新集合：

```
ZRANGE rangeset 0 -1
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f5a5fb077f75.png)

删除个成员试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f29f6f31efdc.png)

```
ZREM set1 mem1
```
再查看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ee4b597d2769.png)

```
ZRANGE set1 0 -1
```

用 ZCARD 查看集合的成员个数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8cbb8a0182aa.png)

```
ZCARD set1
```
用 ZSCORE 查看某个成员的分数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/38c353a8bb74.png)

用 ZRANK 查看成员在集合内的排名：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cde4c3843518.png)

```
ZRANK set1 mem2
```

然后用 ZINCRBY 给成员增加分数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8f2ba8a1dc6e.png)
```
ZINCRBY set1 3 mem2
```
看下新排名：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5b20099dd7d5.png)

```
ZRANGE set1 0 -1
```

mem2 就到下面去了。

再创建一个集合 set2：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1d86867394b1.png)

```
ZADD set2 4 aaa 6 bbb
```
用 ZUNION 合并下：

```
ZUNION 2 set1 set2
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7fbdb3d09ec2.png)

还可以加上分数一起：
```
ZUNION 2 set1 set2 WITHSCORES
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/00eb6bf4a396.png)

或者把合并后放到另一个集合：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aae0ade1f392.png)

```
ZUNIONSTORE set3 2 set1 set2
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b4f8da354f93.png)

```
ZRANGE set3 0 -1
```
交集和差集的命令也差不多，就不一个个试了。

并集合并的时候相同的 key 的 score 会求和。

```
ZADD s1 1 aa 2 bb

ZADD s2 1 aa 3 cc

ZUNIONSTORE s3 2 s1 s2
```

在 s1 和 s2 集合中都有 aa，合并到 s3 之后 aa 的分数也合并了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eb83b3501155.png)

周榜、月榜、年榜就是这么实现的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9b3c777f272d.jpg)

月榜就是对周榜的合并，然后年榜就是月榜的合并，最后就会算出一个新的排行榜。

我们用 Nest 实现下类似的排行榜功能：

```
nest new ranking-list-test
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/524c6c072f6a.png)

安装 redis 的包：

```
npm install --save redis
```

然后创建个 redis 模块：

```
nest g module redis
nest g service redis
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/05fe13cd2d84.webp)

在 RedisModule 创建连接 redis 的 provider，导出 RedisService，并把这个模块标记为 @Global 模块

```javascript
import { Global, Module } from '@nestjs/common';
import { createClient } from 'redis';
import { RedisService } from './redis.service';

@Global()
@Module({
  providers: [
    RedisService,
    {
      provide: 'REDIS_CLIENT',
      async useFactory() {
        const client = createClient({
            socket: {
                host: 'localhost',
                port: 6379
            }
        });
        await client.connect();
        return client;
      }
    }
  ],
  exports: [RedisService]
})
export class RedisModule {}
```

然后在 RedisService 里注入 REDIS_CLIENT，并封装一些方法：

```javascript
import { Inject, Injectable } from '@nestjs/common';
import { RedisClientType } from 'redis';

@Injectable()
export class RedisService {

    @Inject('REDIS_CLIENT') 
    private redisClient: RedisClientType;

    async zRankingList(key: string, start: number = 0, end: number = -1) {
        const keys = await this.redisClient.zRange(key, start, end, {
            REV: true
        });
        const rankingList = {};
        for(let i = 0; i< keys.length; i++){
            rankingList[keys[i]] = await this.zScore(key, keys[i]);
        }
        return rankingList;
    }

    async zAdd(key: string, members: Record<string, number>) {
        const mems = [];
        for(let key in members) {
            mems.push({
                value: key,
                score: members[key]
            });        
        }
        return  await this.redisClient.zAdd(key, mems);
    }

    async zScore(key: string, member: string) {
        return  await this.redisClient.zScore(key, member);
    }

    async zRank(key: string, member: string) {
        return  await this.redisClient.zRank(key, member);
    }

    async zIncr(key: string, member: string, increment: number) {
        return  await this.redisClient.zIncrBy(key, increment, member)
    }

    async zUnion(newKey: string, keys: string[]) {
        if(!keys.length) {
            return []
        };
        if(keys.length === 1) {
            return this.zRankingList(keys[0]);
        }

        await this.redisClient.zUnionStore(newKey, keys);

        return this.zRankingList(newKey);
    }

    async keys(pattern: string) {
        return this.redisClient.keys(pattern);    
    }
}
```
这里我们对 zset 的命令进行了封装，比如 zRange 只会返回成员名，我们顺带把分数也取出来。

暴露 zAdd、zScore、zRank、zIncr 等方法。

zUnion 要做下边界的处理，如果只传了一个 set 的名字，就染回这个 set 的内容，否则才合并。

创建一个 ranking 模块：

```
nest g module ranking
nest g controller ranking --no-spec
nest g service ranking --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/94df7e74de8f.png)

我们就实现下自习室学习时长的月榜和年榜吧。

实现下 RankingService：

```javascript
import { RedisService } from './../redis/redis.service';
import { Inject, Injectable } from '@nestjs/common';
import * as dayjs from 'dayjs';

@Injectable()
export class RankingService {

    @Inject(RedisService)
    redisService: RedisService;

    private getMonthKey() {
        const dateStr = dayjs().format('YYYY-MM');
        return `learning-ranking-month:${dateStr}`;
    }

    private getYearKey() {
        const dateStr = dayjs().format('YYYY');
        return `learning-ranking-year:${dateStr}`;
    }

    async join(name: string) {
        await this.redisService.zAdd(this.getMonthKey(), { [name]: 0 });
    }

    async addLearnTime(name:string, time: number) {
        await this.redisService.zIncr(this.getMonthKey(), name, time);
    }

    async getMonthRanking() {
        return this.redisService.zRankingList(this.getMonthKey(), 0, 10);
    }

    async getYearRanking() {
        const dateStr = dayjs().format('YYYY');
        const keys = await this.redisService.keys(`learning-ranking-month:${dateStr}-*`);

        return this.redisService.zUnion(this.getYearKey(), keys);
    }
}
```
这里用到了 dayjs，安装下：

```
npm install --save dayjs
```

月份的榜单是 learning-ranking-mongth:2024-01、learning-ranking-mongth:2024-02 这样的格式。

年份的榜单是 learning-ranking-mongth:2023、learning-ranking-mongth:2024 这样的格式。

我们用 dayjs 拿到当前的年份和月份，拼接出需要的 key。

年份的榜单就是拿到用 learning-ranking-month:当前年份- 开头的所有 zset，做下合并。

在 RankingController 加一下接口：

```javascript
import { Controller, Get, Inject, Query } from '@nestjs/common';
import { RankingService } from './ranking.service';

@Controller('ranking')
export class RankingController {

    @Inject(RankingService)
    rankingService: RankingService;

    @Get('join')
    async join(@Query('name') name: string) {
        await this.rankingService.join(name);
        return 'success';
    }

    @Get('learn')
    async addLearnTime(@Query('name') name:string, @Query('time') time: string) {
        await this.rankingService.addLearnTime(name, parseFloat(time));
        return 'success';
    }

    @Get('monthRanking')
    async getMonthRanking() {
        return this.rankingService.getMonthRanking();
    }

    @Get('yearRanking')
    async getYearRanking() {
        return this.rankingService.getYearRanking();
    }   
}
```
join 是加入自习室，learn 是增加学习时长，monthRanking 和 yearRanking 是拿到月榜和年榜。

把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c9dddd41f899.png)

在 postman 里调用下：

```
localhost:3000/ranking/join?name=guang
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e760bac3ca23.png)

```
localhost:3000/ranking/join?name=dong
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/042199f97d8c.png)
```
localhost:3000/ranking/join?name=xiaohong
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/89afec8d50d0.png)

调用 join 接口，加入三个同学。

看下现在的月榜：

```
localhost:3000/ranking/monthRanking
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ccbfbe6305f5.png)

在 RedisInsight 里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e9b529c9821d.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/245fa060e234.png)

然后调用 learn 接口，增加学习时长：

```
localhost:3000/ranking/learn?name=dong&time=1
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5b8c81f8f234.png)

```
localhost:3000/ranking/learn?name=guang&time=2
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ca6761a398e3.png)

```
localhost:3000/ranking/learn?name=xiaohong&time=5
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a02e9f35bbee.png)

```
localhost:3000/ranking/monthRanking
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8425304ff124.png)

我们改下本地时间（mac 和 windows 改本地时间的方式不一样）：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c27aba44e01d.png)

然后再调用 join 接口：

```
localhost:3000/ranking/join?name=guang
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e760bac3ca23.png)

```
localhost:3000/ranking/join?name=dong
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/042199f97d8c.png)
```
localhost:3000/ranking/join?name=xiaogang
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5727ee3d9281.png)

之后增加学习时长：


```
localhost:3000/ranking/learn?name=dong&time=2
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b1e5e11a5cd1.png)

```
localhost:3000/ranking/learn?name=guang&time=3
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8d7dae27de2a.png)
```
localhost:3000/ranking/learn?name=xiaogang&time=4
```

然后看下 3 月份的月榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5e3e2c94b165.png)

还有年榜：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/179dbd00a87d.png)

可以看到，年榜是合并了所有月榜的结果。

在 RedisInsight 里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bcf83b8b9636.png)

每个月榜和年榜都是单独的 zset。

这样我们就实现了学习时长的排行榜。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9b3c777f272d.jpg)

至于用户自己的排名和时长，就用 zScore、zRank 来实现。

也就是这个我的排名功能：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e1257c440210.png)

案例代码上传了[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/ranking-list-test)

## 总结

生活中我们经常会见到各种排行榜，以及它们的周榜、月榜、年榜等。

这些排行榜的功能都是用 redis 的 zset 有序集合实现的。

它保存的值都有一个分数，会自动排序。

多个集合之间可以求并集、交集、差集。

通过并集的方式就能实现月榜合并成年榜的功能。

以后见到各种排行榜，你会不会想到 Redis 的 zset 呢？
