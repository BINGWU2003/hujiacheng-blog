---
title: "考试系统：用户注册"
date: 2025-06-07
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["考试系统"]
series_order: 4
---

这节正式进入开发，我们先来开发注册功能。

在 docker desktop 里把 mysql 的容器跑起来：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c4436f7b5587.png)

安装 prisma

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
DATABASE_URL="mysql://root:你的密码@localhost:3306/exam-system"
```
并且修改下 schema 里的 datasource 部分：

```
datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}
```

然后创建 model。

前面分析过用户表的结构：

| 字段名 | 数据类型 | 描述 |
| --- | --- | --- |
| id | INT | 用户ID |
| username | VARCHAR(50) |用户名 |
| password | VARCHAR(50) |密码 |
| email | VARCHAR(50) | 邮箱 |
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
  email String @db.VarChar(50)
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt
}
```
这里 username 要添加唯一约束。

在 mysql workbench 里创建 exam-system 的数据库：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ce918a3b494d.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f877b8bbf64e.png)

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

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6a6951c3989c.png)

在 mysql workbench 里可以看到创建好的 user 表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5c13f5e37b4c.png)

并且 migrate dev 还会生成 client 代码，接下来我们就可以直接来做 CRUD 了。

创建个公共 lib

```
nest g lib prisma
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c834136fec0a.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a4853d01dece.png)

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

这样各处就都可以注入 PrismaService 用了。

在 user 微服务引入 PrismaModule：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/44f29175a6a4.png)

然后在 UserService 里注入 PrismaService 来做 crud：

```javascript
import { PrismaService } from '@app/prisma';
import { Inject, Injectable } from '@nestjs/common';
import { Prisma } from '@prisma/client';

@Injectable()
export class UserService {
  getHello(): string {
    return 'Hello World!';
  }

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

创建 dto/register-user.dto.ts

```javascript
export class RegisterUserDto{
    username: string;

    password: string;

    email: string;

    captcha: string;
}
```

把服务跑起来：

```
npm run start:dev user
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f0ea1660b531.png)

在 postman 里调用下试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ae5886c3d0d.png)

```javascript
{
    "username": "guang",
    "password": "123456",
    "email": "xxxx@xx.com",
    "captcha": "abc123"
}
```
报错了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/df6697f29056.png)

数据库中没有 captcha 的字段。

我们要在调用 service 之前删掉它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0f4ff0996674.png)

再试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/db95d432c6dd.png)

服务端打印了 insert 的 sql 语句：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/73bda7b9325a.png)

数据库里也可以看到这条记录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fd4827d86faf.png)

然后加一下 ValidationPipe，来对请求体做校验。

安装用到的包：

```
npm install --save class-validator class-transformer
```

全局启用 ValidationPipe：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a3ff0a122b53.png)

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

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8335687ad0a2.png)

没啥问题。

然后实现注册的逻辑。

注册的逻辑是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ca3bd5f802c9.png)

继续实现 UserService 的 register 方法：

```javascript
import { HttpException, HttpStatus, Inject, Injectable, Logger } from '@nestjs/common';
import { PrismaService } from '@app/prisma';
import { RedisService } from '@app/redis';
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
            email: user.email
          },
          select: {
            id: true,
            username: true,
            email: true,
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

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c547972bb768.png)

因为还没实现发送邮箱验证码的逻辑，这里我们手动在 redis 添加一个 key：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/87e585a388c5.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/add50983bf8a.png)


测试下：

带上错误的验证码，返回验证码不正确；

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5468ec5bfc28.png)

带上正确的验证码，注册成功：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/86373ccff6be.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d7dd5b1d801d.png)
这时可以在数据库里看到这条记录：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/518268432e6e.png)

然后我们来实现发送邮箱验证码的功能。

封装个 email 的 lib：

```
nest g lib email

```

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a2fd566217ad.png)

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
          name: '考试系统',
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

引入 EmailModule：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2b1da815e74c.png)

然后在 UserController 里添加一个 get 接口：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ef3c75def968.png)

```javascript
import { Controller, Get, Post, Body, Patch, Param, Delete, Inject, Query } from '@nestjs/common';
import { UserService } from './user.service';
import { RegisterUserDto } from './dto/register-user.dto';
import { EmailService } from '@app/email';
import { RedisService } from '@app/redis';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

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

  @Post('register')
  async register(@Body() registerUser: RegisterUserDto) {
    return await this.userService.register(registerUser);
  }
}
```

测试下：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a5a980c1da99.png)

邮件发送成功：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/be0f52d7e051.png)

redis 里也保存了邮箱地址对应的验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aaf894487bf2.png)

通过邮件发送验证码之后，保存到 redis，注册的时候取出邮箱地址对应的验证码来校验。

这样，整个注册的流程就完成了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/414a519fadc7.png)

代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/exam-system)。

## 总结

这节我们引入了 prisma，封装了 prisma、email 这两个 lib。

通过 prisma 的 migrate 功能，生成迁移 sql 并同步到数据库。

此外，prisma 会生成 client 的代码，我们封装了 PrismaService 来做 CRUD。

我们实现了 /user/register 和 /user/register-captcha 两个接口。

/user/register-captcha 会向邮箱地址发送一个包含验证码的邮件，并在 redis 里存一份。

/user/register 会根据邮箱地址查询 redis 中的验证码，验证通过会把用户信息保存到表中。

这样，注册功能就完成了。
