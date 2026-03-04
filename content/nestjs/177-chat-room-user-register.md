---
title: "聊天室：用户注册"
date: 2025-06-26
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["WebSocket 与聊天室"]
series_order: 6
---

这节正式进入开发，我们先来开发注册功能。

创建个 nest 项目：

```
nest new chat-room-backend
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d5963d2e93c8.png)

在 docker desktop 里把 mysql 的容器跑起来：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c4436f7b5587.png)

进入项目，安装 prisma

```
npm install prisma --save-dev
```
然后执行 prisma init 创建 schema 文件：

```
npx prisma init
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2838042fbcda.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eb087f71dfe9.png)

改下 .env 的配置：

```
DATABASE_URL="mysql://root:你的密码@localhost:3306/chat-room"
```
并且修改下 schema 里的 datasource 部分：

```
datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}
```

然后创建 model。

上节分析过用户表的结构：

| 字段名 | 数据类型 | 描述 |
| --- | --- | --- |
| id | INT | 用户ID |
| username | VARCHAR(50) |用户名 |
| password | VARCHAR(50) |密码 |
| nick_name | VARCHAR(50) |昵称 |
| email | VARCHAR(50) | 邮箱 |
| head_pic| VARCHAR(100) | 头像 |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

创建对应的 modal：

```
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}

model User {
  id  Int @id @default(autoincrement())
  username String @db.VarChar(50) @unique
  password String @db.VarChar(50)
  nickName String @db.VarChar(50)
  email String @db.VarChar(50)
  headPic String @db.VarChar(100) @default("")
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt
}
```
注意，这里 username 要添加唯一约束。

在 mysql workbench 里创建 chat-room 的数据库：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/20ca4ace1153.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/202b7b43b2a9.png)

先 migrate reset，重置下数据库：

```
npx prisma migrate reset 
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4123d9612454.png)

然后创建新的 migration:

```
npx prisma migrate dev --name user
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c30a0190c2e6.png)

这时就生成了迁移文件，包含创建 user 表的 sql 语句：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/11ae6bf31de8.png)

在 mysql workbench 里可以看到创建好的 user 表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6dbf2c9fa442.png)

并且 migrate dev 还会生成 client 代码，接下来我们就可以直接来做 CRUD 了。

创建个 module 和 service：

```
nest g module prisma
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/073c551406bb.png)
```
nest g service prisma --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6223d59c428b.png)

改下 PrismaService，继承 PrismaClient，这样它就有 crud 的 api 了：

```javascript
import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {

    constructor() {
        super({
            log: [
                {
                    emit: 'stdout',
                    level: 'query'
                }
            ]
        })
    }

    async onModuleInit() {
        await this.$connect();
    }
}
```

在 constructor 里设置 PrismaClient 的 log 参数，也就是打印 sql 到控制台。

在 onModuleInit 的生命周期方法里调用 $connect 来连接数据库。

然后把 PrismaService 导出，并且设置 PrismaModule 为全局模块：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7a67b5f310c.png)

这样各处就都可以注入 PrismaService 用了。

然后创建 user 模块：

```
nest g resource user
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/186afa977a54.png)

在 UserService 里注入 PrismaService 来做 crud：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/59addffffe47.png)

```javascript
import { Inject, Injectable } from '@nestjs/common';
import { PrismaService } from 'src/prisma/prisma.service';
import { Prisma } from '@prisma/client';

@Injectable()
export class UserService {

  @Inject(PrismaService)
  private prisma: PrismaService;

  async create(data: Prisma.UserCreateInput) {
      return await this.prisma.user.create({
          data,
          select: {
              id: true
          }
      });
  }
}
```
写代码的时候你会发现，参数的类型 prisma 都给你生成好了，直接用就行：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ce6a03c519e6.png)

user 模块有这些接口：

| 接口路径 | 请求方式 | 描述 |
| -- |-- |-- |
| /user/login | POST | 用户登录 |
| /user/register | POST | 用户注册 |
| /user/update | POST | 用户个人信息修改|
| /user/update_password | POST |用户修改密码|

我们这节实现注册：

在 UserController 增加一个 post 接口：

```javascript
import { Controller, Get, Post, Body, Patch, Param, Delete } from '@nestjs/common';
import { UserService } from './user.service';
import { RegisterUserDto } from './dto/register-user.dto';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('register')
  async register(@Body() registerUser: RegisterUserDto) {
      return await this.userService.create(registerUser);
  }
}
```
dto 是封装 body 里的请求参数的，根据界面上要填的信息，创建 dto：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c97fa0140804.png)

创建 user/dto/register-user.dto.ts

```javascript
export class RegisterUserDto{
    username: string;

    password: string;

    nickName: string;

    email: string;

    captcha: string;
}
```

把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f0ea1660b531.png)

在 postman 里调用下试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d5a2c188de9f.png)
```javascript
{
    "username": "guang",
    "nickName": "神说要有光",
    "password": "123456",
    "email": "xxxx@xx.com",
    "captcha": "abc123"
}
```
报错了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c8d5cdb51d1c.png)

数据库中没有 captcha 的字段。

我们要在调用 service 之前删掉它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dfcb3b348e0f.png)

再试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/75b45c1fd76d.png)

服务端打印了 insert 的 sql 语句：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4af914e5a085.png)

数据库里也可以看到这条记录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2b30171c19fc.png)

然后加一下 ValidationPipe，来对请求体做校验。

安装用到的包：

```
npm install --save class-validator class-transformer
```

全局启用 ValidationPipe：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/211aea91ae8d.png)

```javascript
app.useGlobalPipes(new ValidationPipe());
```

然后加一下校验规则：

```javascript
import { IsEmail, IsNotEmpty, MinLength } from "class-validator";

export class RegisterUserDto {

    @IsNotEmpty({
        message: "用户名不能为空"
    })
    username: string;
    
    @IsNotEmpty({
        message: '昵称不能为空'
    })
    nickName: string;
    
    @IsNotEmpty({
        message: '密码不能为空'
    })
    @MinLength(6, {
        message: '密码不能少于 6 位'
    })
    password: string;
    
    @IsNotEmpty({
        message: '邮箱不能为空'
    })
    @IsEmail({}, {
        message: '不是合法的邮箱格式'
    })
    email: string;
    
    @IsNotEmpty({
        message: '验证码不能为空'
    })
    captcha: string;
}
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5353e5a69ea3.png)

没啥问题。

然后实现注册的逻辑。

注册的逻辑是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ca3bd5f802c9.png)

我们需要先封装个 redis 模块。

```
nest g module redis
nest g service redis --no-spec
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/298343ceeee1.png)

安装 redis 的包：

```
npm install --save redis
```
确保 redis 的 docker 容器是启动的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/743e328bf3d1.png)

添加连接 redis 的 provider

```javascript
import { Global, Module } from '@nestjs/common';
import { RedisService } from './redis.service';
import { createClient } from 'redis';

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
            },
            database: 2
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
用 @Global() 把它声明为全局模块，这样只需要在 AppModule 里引入，别的模块不用引入也可以注入 RedisService 了。

database 指定为 2，默认是 0

这个 database 就是把存储的 key-value 的数据放到不同命名空间下，避免冲突。

然后写下 RedisService

```javascript
import { Inject, Injectable } from '@nestjs/common';
import { RedisClientType } from 'redis';

@Injectable()
export class RedisService {

    @Inject('REDIS_CLIENT') 
    private redisClient: RedisClientType;

    async get(key: string) {
        return await this.redisClient.get(key);
    }

    async set(key: string, value: string | number, ttl?: number) {
        await this.redisClient.set(key, value);

        if(ttl) {
            await this.redisClient.expire(key, ttl);
        }
    }
}
```

注入 redisClient，实现 get、set 方法，set 方法支持指定过期时间。

然后继续实现 register 方法。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ca3bd5f802c9.png)

```javascript
import { HttpException, HttpStatus, Inject, Injectable, Logger } from '@nestjs/common';
import { PrismaService } from 'src/prisma/prisma.service';
import { RedisService } from 'src/redis/redis.service';
import { RegisterUserDto } from './dto/register-user.dto';

@Injectable()
export class UserService {

  @Inject(PrismaService)
  private prismaService: PrismaService;

  @Inject(RedisService)
  private redisService: RedisService;

  private logger = new Logger();

  async register(user: RegisterUserDto) {
      const captcha = await this.redisService.get(`captcha_${user.email}`);

      if(!captcha) {
          throw new HttpException('验证码已失效', HttpStatus.BAD_REQUEST);
      }

      if(user.captcha !== captcha) {
          throw new HttpException('验证码不正确', HttpStatus.BAD_REQUEST);
      }

      const foundUser = await this.prismaService.user.findUnique({
        where: {
          username: user.username
        }
      });

      if(foundUser) {
        throw new HttpException('用户已存在', HttpStatus.BAD_REQUEST);
      }

      try {
        return await this.prismaService.user.create({
          data: {
            username: user.username,
            password: user.password,
            nickName: user.nickName,
            email: user.email
          },
          select: {
            id: true,
            username: true,
            nickName: true,
            email: true,
            headPic: true,
            createTime: true
          }
        });
      } catch(e) {
        this.logger.error(e, UserService);
        return null;
      }
  }
}
```
先检查验证码是否正确，如果正确的话，检查用户是否存在，然后用 prismaService.create 插入数据。

失败的话用 Logger 记录错误日志。

这里的 md5 方法放在 src/utils.ts 里，用 node 内置的 crypto 包实现。
```javascript
import * as crypto from 'crypto';

export function md5(str) {
    const hash = crypto.createHash('md5');
    hash.update(str);
    return hash.digest('hex');
}
```
在 UserController 里调用下：

```javascript
import { Controller, Get, Post, Body, Patch, Param, Delete } from '@nestjs/common';
import { UserService } from './user.service';
import { RegisterUserDto } from './dto/register-user.dto';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('register')
  async register(@Body() registerUser: RegisterUserDto) {
    return await this.userService.register(registerUser);
  }
}
```
然后在 postman 里测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/872acb916fe1.png)

因为还没实现发送邮箱验证码的逻辑，这里我们手动在 redis 添加一个 key：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aac42e4039a8.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/80a29ad88927.png)

测试下：

带上错误的验证码，返回验证码不正确；


![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d52e325ff758.png)
带上正确的验证码，注册成功：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2333e52ac1a0.png)
这时可以在数据库里看到这条记录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/120969d4f84c.png)

然后我们来实现发送邮箱验证码的功能。

封装个 email 模块：

```
nest g resource email --no-spec
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ec207011e93.png)

安装发送邮件用的包：

```
npm install nodemailer --save
```
在 EmailService 里实现 sendMail 方法

```javascript
import { Injectable } from '@nestjs/common';
import { createTransport, Transporter} from 'nodemailer';

@Injectable()
export class EmailService {

    transporter: Transporter
    
    constructor() {
      this.transporter = createTransport({
          host: "smtp.qq.com",
          port: 587,
          secure: false,
          auth: {
              user: '你的邮箱地址',
              pass: '你的授权码'
          },
      });
    }

    async sendMail({ to, subject, html }) {
      await this.transporter.sendMail({
        from: {
          name: '聊天室',
          address: '你的邮箱地址'
        },
        to,
        subject,
        html
      });
    }
}
```
把邮箱地址和授权码改成你自己的。

具体怎么生成授权码，看前面的 [node 发送邮件](https://juejin.cn/book/7226988578700525605/section/7247327089496424505)那节。

把 EmailModule 声明为全局的，并且导出 EmailService

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/33baa295a799.png)

然后在 UserController 里添加一个 get 接口：

```javascript
@Inject(EmailService)
private emailService: EmailService;

@Inject(RedisService)
private redisService: RedisService;

@Get('register-captcha')
async captcha(@Query('address') address: string) {
    const code = Math.random().toString().slice(2,8);

    await this.redisService.set(`captcha_${address}`, code, 5 * 60);

    await this.emailService.sendMail({
      to: address,
      subject: '注册验证码',
      html: `<p>你的注册验证码是 ${code}</p>`
    });
    return '发送成功';
}
```

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/04be26441e4e.png)

邮件发送成功：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2ec33a3148a.png)

redis 里也保存了邮箱地址对应的验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/860a7c6933cf.png)

通过邮件发送验证码之后，保存到 redis，注册的时候取出邮箱地址对应的验证码来校验。

这样，整个注册的流程就完成了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/414a519fadc7.png)

代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/chat-room-backend)。

## 总结

这节我们创建了 nest 项目，并引入了 prisma 和 redis。

通过 prisma 的 migrate 功能，生成迁移 sql 并同步到数据库。

此外，prisma 会生成 client 的代码，我们封装了 PrismaService 来做 CRUD。

我们实现了 /user/register 和 /user/register-captcha 两个接口。

/user/register-captcha 会向邮箱地址发送一个包含验证码的邮件，并在 redis 里存一份。

/user/register 会根据邮箱地址查询 redis 中的验证码，验证通过会把用户信息保存到表中。

这样，注册功能就完成了。
