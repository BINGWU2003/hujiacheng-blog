---
title: "单 token 无限续期，实现登录状态无感刷新"
date: 2025-03-13
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["认证与权限"]
series_order: 11
---

上节我们基于双 token 实现了登录状态的无感刷新。

这当然是能实现功能的，很多公司也这样用。

但是双 token 实现起来还是挺麻烦的。

所以实际上单 token 自动续期的方式用的也非常多。

单 token 的原理也很简单，就是登录后返回 jwt，每次请求接口带上这个 jwt，然后**每次访问接口返回新的 jwt，然后前端更新下本地的 jwt token**。

比如这个 token 是 7 天过期，那只要 7 天内访问一次系统，就会刷新 token。

7 天内不访问系统，token 过期，就需要重新登录了。

这种方案也能实现无感刷新，而且代码简单的多。

我们来写一下：

```
nest new single-token-refresh
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2612537908a4.png)

进入项目，添加一个 user 模块：

```
nest g resource user --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3a17bac66614.png)

加一个 login 的路由：

```javascript
import { Body, Controller, Post } from '@nestjs/common';
import { UserService } from './user.service';
import { LoginUserDto } from './dto/login-user.dto';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Post('login')
  async login(@Body() loginDto: LoginUserDto) {
    console.log(loginDto)
  }
}
```
对应的 user/dto/login-user.dto.ts

```javascript
export class LoginUserDto {
    username: string;
    password: string;
}
```
把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/00bc9a5a09d7.png)

postman 访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8ef1d396f1e7.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7f4b6ab41618.png)

登录成功返回 jwt，安装下用到的包：

```
npm install --save @nestjs/jwt
```
在 AppModule 引入：

```javascript
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UserModule } from './user/user.module';
import { JwtModule } from '@nestjs/jwt';

@Module({
  imports: [UserModule, 
    JwtModule.register({
      global: true,
      secret: 'guang'
    })
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}

```
然后 login 的时候返回 jwt

```javascript
import { BadRequestException, Body, Controller, Inject, Post } from '@nestjs/common';
import { UserService } from './user.service';
import { LoginUserDto } from './dto/login-user.dto';
import { JwtService } from '@nestjs/jwt';

@Controller('user')
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Inject(JwtService)
  jwtService: JwtService;

  @Post('login')
  async login(@Body() loginDto: LoginUserDto) {
    if(loginDto.username !== 'guang' || loginDto.password !== '123456') {
      throw new BadRequestException('用户名或密码错误');
    }
    const jwt = this.jwtService.sign({
      username: loginDto.username
    }, {
      secret: 'guang',
      expiresIn: '7d'
    });
    return jwt;
  }
}
```
登录后返回 jwt，过期时间是 7 天。

访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/30978e571c3a.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/40ec770b2c9f.png)

可以看到，登录后返回了 jwt。

然后加一个 Guard 来解析 jwt：

```
nest g guard login --flat --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/173819a2a84e.png)

登录鉴权逻辑和之前一样：

```javascript
import { JwtService } from '@nestjs/jwt';
import { CanActivate, ExecutionContext, Inject, Injectable, UnauthorizedException } from '@nestjs/common';
import { Request } from 'express';
import { Observable } from 'rxjs';

@Injectable()
export class LoginGuard implements CanActivate {

  @Inject(JwtService)
  private jwtService: JwtService;

  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {

    const request: Request = context.switchToHttp().getRequest();

    const authorization = request.headers.authorization;

    if(!authorization) {
      throw new UnauthorizedException('用户未登录');
    }

    try{
      const token = authorization.split(' ')[1];
      const data = this.jwtService.verify(token);

      return true;
    } catch(e) {
      throw new UnauthorizedException('token 失效，请重新登录');
    }
  }
}
```

取出 authorization header 中的 jwt token

jwt 有效就可以继续访问，否则返回 token 失效，请重新登录。

然后在 AppController 添加个接口加上登录鉴权：

```javascript
@Get('aaa')
aaa() {
    return 'aaa';
}

@Get('bbb')
@UseGuards(LoginGuard)
bbb() {
    return 'bbb';
}
```

aaa 接口可以直接访问，bbb 接口需要登录后才能访问。

访问 aaa
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c50775a4a843.png)
访问 bbb

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f93371f0905f.png)

登录拿到 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b16097a167b8.png)

带上 token 访问 bbb：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ef61cf1366f8.png)

带上 token 就可以访问需要登录的接口了。

这样就完成了登录和鉴权。

但这个 token 是有过期时间的，过期了就要重新登录了，所以要刷新 token。

上节实现了双 token 的无感刷新，今天实现单 token 刷新。

方式很简单，就是访问接口后返回新 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/97c7452b6bcf.png)

```javascript
import { JwtService } from '@nestjs/jwt';
import { CanActivate, ExecutionContext, Inject, Injectable, UnauthorizedException } from '@nestjs/common';
import { Request, Response } from 'express';
import { Observable } from 'rxjs';

@Injectable()
export class LoginGuard implements CanActivate {

  @Inject(JwtService)
  private jwtService: JwtService;

  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {

    const request: Request = context.switchToHttp().getRequest();
    const response: Response = context.switchToHttp().getResponse();

    const authorization = request.headers.authorization;

    if(!authorization) {
      throw new UnauthorizedException('用户未登录');
    }

    try{
      const token = authorization.split(' ')[1];
      const data = this.jwtService.verify(token);

      response.setHeader('token', this.jwtService.sign({
        username: data.username
      }, {
        expiresIn: '7d'
      }));

      return true;
    } catch(e) {
      throw new UnauthorizedException('token 失效，请重新登录');
    }
  }
}
```
试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/44508f2c0489.gif)

这样每次返回新 token，不就永不过期了？

而且实现还特别简单。

所以单 token 自动续期的方案用的挺多的。

我们写下前端代码：

```
npx create-vite single-token-refresh-frontend
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5edb0b8c1196.png)

进入项目，把服务跑起来：

```
npm install
npm run dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/92671be24c4e.png)

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fe283511a36c.png)

项目跑起来后，我们调用下后端接口。

首先后端要开启跨域：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/53c54f7a5de3.png)

然后前端页面调用下：

改下 App.tsx

```javascript
import { useEffect, useState } from 'react'
import './App.css'
import axios from 'axios';

function App() {
  const [content, setContent] = useState('')

  async function query() {
    try {
      const res = await axios.get('http://localhost:3000/bbb');
      setContent(res.data);
    } catch(e: any) {
      console.log(e.response.data.message);
    }
  }

  useEffect(() => {
    query();
  }, []);

  return (
    <div style={{fontSize: '100px'}}>{content}</div>
  )
}

export default App
```
在页面调用 bbb 接口，把结果显示到页面。

安装 axios：

```
npm install --save axios
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5e73bb06aa0b.png)

提示未登录（打印两次是 main.tsx 里的 StrictMode 导致的，去掉就好了）

我们登录下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/06c8ee7ae1fb.png)

```javascript
import { useEffect, useState } from 'react'
import './App.css'
import axios from 'axios';

function App() {
  const [content, setContent] = useState('')

  async function query() {
    try {
      const res = await axios.post('http://localhost:3000/user/login', {
        username: 'guang',
        password: '123456'
      });
      console.log(res.data);

      const res2 = await axios.get('http://localhost:3000/bbb', {
        headers: {
          Authorization: `Bearer ${res.data}`
        }
      });
      setContent(res2.data);
    } catch(e: any) {
      console.log(e.response.data.message);
    }
  }

  useEffect(() => {
    query();
  }, []);

  return (
    <div style={{fontSize: '100px'}}>{content}</div>
  )
}

export default App
```
现在接口就请求成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9abc4ed0fafa.png)

这个 token 我们一般都放到 localstorage 里，每次请求都带上。

这段逻辑我们上节写过：

```javascript
axios.interceptors.request.use(function (config) {
  const accessToken = localStorage.getItem('access_token');

  if(accessToken) {
    config.headers.authorization = 'Bearer ' + accessToken;
  }
  return config;
})
```
那单 token 如何刷新呢？

很简单，拦截器里把 header 里的新 token 更新到 localStorage 就好了：

```javascript
axios.interceptors.response.use(
  (response) => {
    const newToken = response.headers['token'];
    if(newToken) {
      localStorage.setItem('token ', newToken);
    }
    return response;
  }
)
```
但这样有个问题：

打印下 header

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2cd8b4c33045.png)

没有 token

但我们明明返回了啊：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eea71f61fa97.png)

这也是跨域的问题，默认你能访问的 header 是有限的。

如果想在代码访问别的 header，需要在后端支持下，在 Access-Controll-Expose-Headers 里加上这个 header

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dede7ac41b5f.png)

现在就可以访问这个 header 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8b685e6b45a8.png)

这样更新完 localStorage 里的 token，不就实现无感刷新了么？

案例代码在小册仓库：

[后端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/single-token-refresh)

[前端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/single-token-refresh-frontend)

## 总结

这节我们实现了单 token 的无感刷新，它也是在公司里用的非常多的一种方案。

好处就是简单，只要每次请求接口的时候返回新的 token，然后刷新下本地 token 就可以了。

我们在 axios 的 response 拦截器里可以轻松做到这个，比双 token 的无感刷新可简单太多了。

要注意的是在代码里访问其他 header，需要后端配置下 expose headers 才可以。

你们公司里是用双 token 还是单 token 实现登录状态无感刷新呢？

（这节写的有点问题，单 token 应该在快过期的时候返回新 token，后面优化下）
