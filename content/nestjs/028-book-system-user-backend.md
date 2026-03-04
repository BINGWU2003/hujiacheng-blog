---
title: "图书管理系统：用户模块后端开发"
date: 2025-01-28
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["图书管理系统"]
series_order: 2
---

我们做了需求分析，并画了原型图，这节开始写下后端代码。

创建个 nest 项目：

```
nest new book-management-system-backend
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ffe38cec439e.png)

进入项目，把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d8bc936b38cc.png)

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fe6d843a78ca.png)

服务跑起来了。

然后我们先实现下登录、注册。

创建一个 user 模块：

```
nest g resource user --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8c83c1143a12.png)

--no-spec 是不生成单测代码。

可以看到，src 下多了 user 模块的代码，并自动在 AppModule 里引入了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e61bdb6bd306.png)

然后我们在 UserConstructor 添加注册接口：

```javascript
import { Controller, Post, Body} from '@nestjs/common';
import { UserService } from './user.service';
import { RegisterUserDto } from './dto/register-user.dto';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('register')
  register(@Body() registerUserDto: RegisterUserDto) {
    console.log(registerUserDto);
    return 'done';
  }
}
```

路由是 /user/register 的 POST 接口。

创建 dto/register-user.dto.ts

```javascript
export class RegisterUserDto {
    username: string;
    password: string;
}
```

然后在 postman 里调用下这个接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1e648bf00750.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dfc1a8e746cb.png)

可以看到，服务端接收到了请求体的参数，并且返回了响应。

我们还要对参数做一些校验，校验请求体的参数需要用到 ValidationPipe

在 main.ts 里全局启用 ValidationPipe：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7c8cfeca29c9.png)

```javascript
app.useGlobalPipes(new ValidationPipe());
```
然后安装用到的包：

```
npm install --save class-transformer class-validator
```
之后就可以在 dto 里添加 class-validator 的校验规则了：

```javascript
import { IsNotEmpty, MinLength } from "class-validator";

export class RegisterUserDto {
    @IsNotEmpty({ message: '用户名不能为空' })
    username: string;

    @IsNotEmpty({ message: '密码不能为空' })
    @MinLength(6, { message: '密码最少 6 位'})
    password: string;
}
```
试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/32b01466106b.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6b2dea3afa99.png)

校验生效了。

现在接收到的参数是普通对象：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/915e101e4a4d.png)

在 ValidationPipe 指定 transform: true 之后，就会转为 dto 的实例了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3ff0d90b227a.png)

然后我们来实现下具体的注册逻辑。

我们还没有学习数据库，这里就用 json 文件来存储数据吧。

创建一个 db 模块：

```
nest g module db
nest g service db
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7549316a8850.png)

这里没指定 --no-spec 也没生成单测文件是因为我在 nest-cli.json 里配了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/74c3dfebd4b0.png)

我们希望 DbModule 用的时候可以传入 json 文件的存储路径：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bf2043e60c11.png)

在 UserModule 里用的时候，path 是 users.json，在 BookModule 用的时候，path 是 books.json

这种需要传参的模块就是动态模块了。

而且不同模块里用传不同的参数，我们会用 register 作为方法名。

写下 db.module.ts

```javascript
import { DynamicModule, Module } from '@nestjs/common';
import { DbService } from './db.service';

export interface DbModuleOptions {
  path: string
}

@Module({})
export class DbModule {
  static register(options: DbModuleOptions ): DynamicModule {
    return {
      module: DbModule,
      providers: [
        {
          provide: 'OPTIONS',
          useValue: options,
        },
        DbService,
      ],
      exports: [DbService]
    };
  }
}
```
在 register 方法里接收 options 参数，返回 providers、exports 等模块配置。

把传入的 options 用 useValue 来声明为 provider，token 为 OPTIONS。

在 DbService 里实现下 read、write 方法：

```javascript
import { Inject, Injectable } from '@nestjs/common';
import { DbModuleOptions } from './db.module';
import { access, readFile, writeFile } from 'fs/promises';

@Injectable()
export class DbService {

    @Inject('OPTIONS')
    private options: DbModuleOptions;

    async read() {
        const filePath  = this.options.path;

        try {
            await access(filePath)
        } catch(e) {
            return [];
        }

        const str = await readFile(filePath, {
            encoding: 'utf-8'
        });
        
        if(!str) {
            return []
        }

        return JSON.parse(str);
        
    }

    async write(obj: Record<string, any>) {
        await writeFile(this.options.path, JSON.stringify(obj || []), {
            encoding: 'utf-8'
        });
    }
}
```
read 方法就是读取文件内容，然后 JSON.parse 一下转为对象。如果文件不存在就返回孔数组

write 方法是 JSON.stringify 之后写入文件。

DbModule 封装好了，接下来就可以继续写注册逻辑了：

在 UserController 里调用下 UserService 的 register 方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f4a0d06c4a6e.png)

```javascript
@Post('register')
async register(@Body() registerUserDto: RegisterUserDto) {
    return this.userService.register(registerUserDto);
}
```

然后在 UserService 里实现这个方法：

```javascript
import { BadRequestException, Inject, Injectable } from '@nestjs/common';
import { RegisterUserDto } from './dto/register-user.dto';
import { DbService } from 'src/db/db.service';
import { User } from './entities/user.entity';

@Injectable()
export class UserService {

    @Inject(DbService)
    dbService: DbService;

    async register(registerUserDto: RegisterUserDto) {
        const users: User[] = await this.dbService.read();
        
        const foundUser = users.find(item => item.username === registerUserDto.username);

        if(foundUser) {
            throw new BadRequestException('该用户已经注册');
        }

        const user = new User();
        user.username = registerUserDto.username;
        user.password = registerUserDto.password;
        users.push(user);

        await this.dbService.write(users);
        return user;
    }
}
```
注入 DbService 来读写数据。

首先读取出 users 的数据，如果找到当前 username，那就返回 400 的响应提示用户已注册。

否则创建一个新的用户，写入文件中。

user.entity.ts 也要改下：

```javascript
export class User {
    username: string;
    password: string;
}
```

在 postman 里调用下试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e539d70fa3f0.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0e133d5887c9.png)

注册成功，创建了 users.json 文件，并写入了数据。

再注册一个：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/942e06ebfc85.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e53e4e11c8d2.png)

也没问题。

再次注册同样的 username 会返回 400

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ec1b4db0b5ed.png)

注册完成了，然后再实现下登录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3a097601cde7.png)

```javascript
@Post('login')
async login(@Body() loginUserDto: LoginUserDto) {
  return this.userService.login(loginUserDto);
}
```
添加 user/dto/login-user.dto.ts

```javascript
import { IsNotEmpty, MinLength } from "class-validator";

export class LoginUserDto {
    @IsNotEmpty({ message: '用户名不能为空' })
    username: string;

    @IsNotEmpty({ message: '密码不能为空' })
    @MinLength(6, { message: '密码最少 6 位'})
    password: string;
}
```
和注册的校验规则一样。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dd687492a5f4.png)

```javascript
async login(loginUserDto: LoginUserDto) {
    const users: User[] = await this.dbService.read();

    const foundUser = users.find(item => item.username === loginUserDto.username);

    if(!foundUser) {
        throw new BadRequestException('用户不存在');
    }

    if(foundUser.password !== loginUserDto.password) {
        throw new BadRequestException('密码不正确');
    }

    return foundUser;
}
```
测试下：

当不满足校验规则时：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/66b7e246ecb7.png)

当用户不存在时：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b808295647f3.png)

当密码不正确时：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/00fd67f25c80.png)

登录成功时：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/304bbc05c3a7.png)

这样，我们登录注册就都完成了。

案例代码上传了[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/book-management-system-backend/)

## 总结

这节我们实现了用户模块的登录、注册功能。

通过读写文件实现了数据存储，封装了一个动态模块，用到时候传入 path，然后模块内的 service 里会读写这个文件的内容，通过 JSON.parse、JSON.stringify 和对象互转。

通过 ValidationPipe + class-validator 实现了 dto 的校验。

然后实现了注册和登录的业务逻辑。

这样，用户模块的功能就完成了。
