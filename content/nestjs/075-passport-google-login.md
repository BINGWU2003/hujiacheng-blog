---
title: "passport 实现 Google 三方账号登录"
date: 2025-03-16
draft: false
description: ""
tags: ["nestjs", "passport"]
categories: ["NestJS"]
series: ["认证与权限"]
series_order: 14
---

上节我们实现了 Github 登录，这节继续来实现下 Google 登录。

创建个 nest 项目：

```
nest new google-login
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/04f7de4c3c2f.png)

进入项目，安装 passport 的包：

```
npm install --save passport @nestjs/passport
```
然后安装 google 的策略包。

这个可以去 [passport 的网站](https://www.passportjs.org/packages/)搜索：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c5385f9be7b3.png)


找下载量最多的那个。

然后安装下：

```
npm install --save passport-google-oauth20
npm install --save-dev @types/passport-google-oauth20
```

我们先做 google 登录，很明显，最关键的也是要获取 client id 和 client secret。

打开 google cloud 的控制台页面https://console.cloud.google.com/welcome

点击左上角的按钮，然后点击 new project：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2ac528941686.gif)

填入项目名后点击 create：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c213d05fa03c.png)

点击左上角的按钮切换到你刚刚创建的 project：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5aca2d3e0d30.png)

进入 api & service 页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6a01eeb7506f.png)

点击 OAuth consent screen，然后勾选 external，点击 create：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fa59c1bc7ba5.png)

输入三个必填信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c0c2e46c19d0.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/698ee4b2d154.png)

点击 save and continue。

然后点击 Credentials 创建凭证：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9690b3db323f.png)

输入应用类型、name、填入授权的域名、回调的 url，点击 create：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f6c6cc6d74a9.png)

这样 client id 和 client secret 就生成好了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3137b9fe52a8.png)

接下来写代码：

```
nest g module auth
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3d518ffe8d3f.png)

生成 auth 模块，然后创建 auth/google.strategy.ts

```javascript
import { Injectable } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { Strategy } from 'passport-google-oauth20';

@Injectable()
export class GoogleStrategy extends PassportStrategy(Strategy, 'google') {
  constructor() {
    super({
      clientID: '122695705559-9nr9alq0s53e2pr3vkiv2h7vau917ic4.apps.googleusercontent.com',
      clientSecret: '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',
      callbackURL: 'http://localhost:3000/callback/google',
      scope: ['email', 'profile'],
    });
  }

  validate (accessToken: string, refreshToken: string, profile: any) {
    const { name, emails, photos } = profile
    const user = {
      email: emails[0].value,
      firstName: name.givenName,
      lastName: name.familyName,
      picture: photos[0].value,
      accessToken
    }
    return user;
  }
}
```

这里填入刚刚的 clientID、clientSecret、callbackURL。

然后在 AuthModule 引入：

```javascript
import { Module } from '@nestjs/common';
import { GoogleStrategy } from './google.strategy';

@Module({
    providers: [GoogleStrategy]
})
export class AuthModule {}
```

之后在 AppController 添加两个路由：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0fc0bd6f7bfa.png)

```javascript
import { Controller, Get, Req, UseGuards } from '@nestjs/common';
import { AppService } from './app.service';
import { AuthGuard } from '@nestjs/passport';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }

  @Get('google')
  @UseGuards(AuthGuard('google'))
  async googleAuth() {}

  @Get('callback/google')
  @UseGuards(AuthGuard('google'))
  googleAuthRedirect(@Req() req) {
    if (!req.user) {
      return 'No user from google'
    }

    return {
      message: 'User information from google',
      user: req.user
    }
  }
}
```
一个是登录的，一个是回调的。

把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d4f234d39080.png)
测试下：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7f93a06ebc92.gif)

可以看到，google 的用户信息拿到了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/23415ab863dc.png)

这里没有 github 返回的那种有 id，但这里返回了 email，同样可以唯一标识用户。

你可以试下 [medium.com](https://medium.com/) 的三方登录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d826489e3346.gif)

用 google 账号登录之后，会让你完善一些信息，然后 create count。

也就是基于你 google 账号里的东西，再让你填一些东西之后，完成账号注册。

之后你 google 登录，就会查到这个账号，从而直接登录，不用输密码。

或者 [hub.docker.com](https://hub.docker.com/signup) 的三方登录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/501186b39b5c.gif)

也是在 github 账号登录后，让你填一些其余信息，完成注册。

之后三方账号授权后，直接登录。

我们也来实现下：

引入下 TypeORM 来操作数据库：

```bash
npm install --save @nestjs/typeorm typeorm mysql2
```
AppModule 里引入 TypeOrmModule：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/76bd3813694d.png)

```javascript
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    AuthModule, 
    TypeOrmModule.forRoot({
      type: "mysql",
      host: "localhost",
      port: 3306,
      username: "root",
      password: "guang",
      database: "google-login",
      synchronize: true,
      logging: true,
      entities: [],
      poolSize: 10,
      connectorPackage: 'mysql2',
      extra: {
          authPlugin: 'sha256_password',
      }
    })
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}

```

在 mysql workbench 创建这个 database：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d128498bdede.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4abcacc9a8d2.png)

添加 src/user.entity.ts

```javascript
import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn, UpdateDateColumn } from "typeorm";

export enum RegisterType {
    normal = 1,
    google = 2
}
@Entity()
export class User {

    @PrimaryGeneratedColumn()
    id: number;

    @Column({
        length: 50
    })
    email: string;

    @Column({
        length: 20
    })
    password: string;

    @Column({
        comment: '昵称',
        length: 50
    })
    nickName: string;

    @Column({
        comment: '头像 url',
        length: 200
    })
    avater: string;

    @Column({
        comment: '注册类型: 1.用户名密码注册 2. google自动注册',
        default: 1
    })
    registerType: RegisterType;

    @CreateDateColumn()
    createTime: Date;

    @UpdateDateColumn()
    updateTime: Date;
}
```

有 id、email、nickName、avater、registerType、createTime、updateTime 7 个字段。

registerType 用来标识哪种注册方式，正常注册是 1，google 账号自动注册是 2。

这里要区分是因为 google 方式注册就不用 password 了，验证逻辑不一样。

在 entities 里引入：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a1e6306da10.png)

跑一下试试：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/79c4a1bbfefc.png)

这部分和我们单独跑 typeorm 没啥区别：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/19c1fec5c80f.png)

然后是增删改查，我们可以注入 EntityManager：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f63d1688a6b3.png)

自动创建了对应的表。

在 mysql workbench 里也可以看到：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a8d3ca9a48c3.png)

然后在 AppService 里注入 EntityManager 来操作 user 表：

```javascript
import { Injectable } from '@nestjs/common';
import { InjectEntityManager } from '@nestjs/typeorm';
import { EntityManager } from 'typeorm';
import { User } from './user.entity';

export interface GoogleInfo {
  email: string;
  firstName: string;
  lastName: string;
  picture: string;
}

@Injectable()
export class AppService {

  @InjectEntityManager()
  entityManager: EntityManager;

  getHello(): string {
    return 'Hello World!';
  }

  async registerByGoogleInfo(info: GoogleInfo) {
    const user = new User();

    user.nickName = `${info.firstName}_${info.lastName}`;
    user.avater = info.picture;
    user.email = info.email;
    user.password = '';
    user.registerType = 2;

    return this.entityManager.save(User, user);
  }

  async findGoogleUserByEmail(email: string) {
    return this.entityManager.findOneBy(User, {
      registerType: 2,
      email
    });
  }
}
```

实现了 findGoogleUserByEmail 方法，可以根据 email 查询 google 注册的账号。

实现了 registerByGoogleInfo 方法，根据 google 返回的信息自动注册账号。

然后在 AppController 里改下 callback 的逻辑：

```javascript
@Get('callback/google')
@UseGuards(AuthGuard('google'))
async googleAuthRedirect(@Req() req) {
    const user = await this.appService.findGoogleUserByEmail(req.user.email);

    if(!user) {
      const newUser = this.appService.registerByGoogleInfo(req.user);
      return newUser;
    } else {
      return user;
    }
}
```
首先根据 email 查询 google 方式登录的 user，如果有，就自动登录。

否则自动注册然后登录。

这里因为 google 返回的信息是全的，就直接自动注册了。

如果不全，需要再跳转一个页面填写其余信息之后再自动注册。

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f3d4f8036523.gif)

因为前面登录过 google 账号并授权了，短时间内不需要再次授权，所以这里直接触发了注册并登录了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1683e83e95dd.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2c191b0ad6cb.png)

当你用这个 google 账号登录，就会直接登录，不需要再注册了。

当然，网站登录后一般都会重定向到首页，那这时候怎么返回 jwt 的token 呢？

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/222c35eebfc6.gif)

看下 https://hub.docker.com 怎么做的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d523a8a0a209.png)

可以看到，它并不是直接返回 jwt 的 token，而是重定向回首页，在 cookie 里携带 token。

这样前端只要判断下如果 cookie 里有这些 token 就自动登录就好了。

这就是三方账号登录的实现原理。

案例代码上传了[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/google-login)

## 总结

我们实现了基于 google 的三方账号登录。

首先搜索对应的 passport 策略，然后生成 client id 和 client secret。

在 nest 项目里使用这个策略，添加登录和 callback 的路由。

之后基于 google 返回的信息来自动注册，如果信息不够，可以重定向到一个 url 让用户填写其余信息。

之后再次用这个 google 账号登录的话，就会自动登录。

现在，你可以在你的应用中加上 docker.com 这种三方账号登录了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ccbcefeec87b.png)
