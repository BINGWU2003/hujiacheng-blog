---
title: "聊天室：修改密码、修改信息"
date: 2025-06-28
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["WebSocket 与聊天室"]
series_order: 8
---

这节继续实现下修改密码、修改个人信息的接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ffb13cf8ba14.png)

对应这两个页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6d5ad58eab7f.png)

![](<https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/26ce08e936b34f138187ce4a2c520ced~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1208&h=844&s=41235&e=png&b=ffffff>)

不过在修改信息之前，需要先实现查询用户信息的接口，用来回显数据。

在 UserController 添加一个 /user/info 接口：

```javascript
@Get('info')
@RequireLogin()
async info(@UserInfo('userId') userId: number) {
  return this.userService.findUserDetailById(userId);
}
```
加上 @RequireLogin 装饰，这样 LoginGuard 就会对 /user/info 的请求做登录检查，并把 user 信息放到 request 上。

然后用前面封装的自定义装饰器 @UserInfo 从 reqeust.user 取 userId 注入 handler。

在 UserService  实现 findUserDetailById 方法：

```javascript
async findUserDetailById(userId: number) {
    const user =  await this.prismaService.user.findUnique({
        where: {
            id: userId
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
    return user;
}
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d920d9189e21.png)

登录，拿到 token。

然后带上 token 访问 /user/info

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/df747ec67335.png)

成功拿到了 user 的信息。

然后实现修改密码的接口：

```javascript
@Post('update_password')
async updatePassword(@Body() passwordDto: UpdateUserPasswordDto) {
  console.log(passwordDto);
  return 'success';
}
```
创建 src/user/dto/update-user-password.dto.ts

```javascript
import { IsEmail, IsNotEmpty, MinLength } from "class-validator";

export class UpdateUserPasswordDto {    
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
        message: '用户名不能为空'
    })
    username: string;
    
    @IsNotEmpty({
        message: '验证码不能为空'
    })
    captcha: string;
}
```
需要传的是用户名、邮箱、密码、验证码。

确认密码在前端和密码对比就行，不需要传到后端。

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d5b4ec936fd4.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a7fb5fc458b5.png)

然后实现下具体的更新密码的逻辑：

在 UserController 里调用 UserService 的方法：

```javascript
@Post('update_password')
async updatePassword(@Body() passwordDto: UpdateUserPasswordDto) {
    return this.userService.updatePassword(passwordDto);
}
```
UserService 实现具体的逻辑：
```javascript
async updatePassword(passwordDto: UpdateUserPasswordDto) {
  const captcha = await this.redisService.get(`update_password_captcha_${passwordDto.email}`);

  if(!captcha) {
      throw new HttpException('验证码已失效', HttpStatus.BAD_REQUEST);
  }

  if(passwordDto.captcha !== captcha) {
      throw new HttpException('验证码不正确', HttpStatus.BAD_REQUEST);
  }

  const foundUser = await this.prismaService.user.findUnique({
    where: {
        username: passwordDto.username
    }
  });

  foundUser.password = passwordDto.password;

  try {
    await this.prismaService.user.update({
      where: {
        id: foundUser.id
      },
      data: foundUser
    });
    return '密码修改成功';
  } catch(e) {
    this.logger.error(e, UserService);
    return '密码修改失败';
  }
}
```
先查询 redis 中相对应的验证码，检查通过之后根据 email 查询用户信息，修改密码之后 save。

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8b80015d9ac5.png)

在 redis 里手动添加 update_password_captcha_邮箱 的 key，值为 111111

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d9019ebd4c52.png)

半小时过期。

注意，我们现在连的是 db2

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c1bd3fb39b44.png)

然后再试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/80105c95daa6.png)

修改成功。

我们为了开发方便没对密码做加密，可以直观看出来密码修改成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ecb738bb93bd.png)

然后再加上发送邮箱验证码的接口：
```javascript
@Get('update_password/captcha')
async updatePasswordCaptcha(@Query('address') address: string) {
    if(!address) {
      throw new BadRequestException('邮箱地址不能为空');
    }
    const code = Math.random().toString().slice(2,8);

    await this.redisService.set(`update_password_captcha_${address}`, code, 10 * 60);

    await this.emailService.sendMail({
      to: address,
      subject: '更改密码验证码',
      html: `<p>你的更改密码验证码是 ${code}</p>`
    });
    return '发送成功';
}
```

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9cf210e6add5.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2057debf16c.png)

然后再来写下修改个人信息的接口：

![](<https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/26ce08e936b34f138187ce4a2c520ced~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1208&h=844&s=41235&e=png&b=ffffff>)

回显数据的接口就用 /user/info 这个。

然后加一个 /user/update 接口：

```javascript
@Post('update')
@RequireLogin()
async update(@UserInfo('userId') userId: number, @Body() updateUserDto: UpdateUserDto) {
  return await this.userService.update(userId, updateUserDto); 
}
```
创建 src/user/dto/udpate-user.dto.ts

```javascript
import { IsEmail, IsNotEmpty } from "class-validator";

export class UpdateUserDto {

    headPic: string;

    nickName: string;
    
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
headPic 和 nickName 不用加非空约束，可以不传。

然后在 UserService 实现 update 方法：

```javascript
async update(userId: number, updateUserDto: UpdateUserDto) {
    const captcha = await this.redisService.get(`update_user_captcha_${updateUserDto.email}`);

    if(!captcha) {
        throw new HttpException('验证码已失效', HttpStatus.BAD_REQUEST);
    }

    if(updateUserDto.captcha !== captcha) {
        throw new HttpException('验证码不正确', HttpStatus.BAD_REQUEST);
    }

    const foundUser = await this.prismaService.user.findUnique({
      where: {
        id: userId
      }
    });

    if(updateUserDto.nickName) {
        foundUser.nickName = updateUserDto.nickName;
    }
    if(updateUserDto.headPic) {
        foundUser.headPic = updateUserDto.headPic;
    }

    try {
      await this.prismaService.user.update({
        where: {
          id: userId
        },
        data: foundUser
      })
      return '用户信息修改成功';
    } catch(e) {
      this.logger.error(e, UserService);
      return '用户信息修改成功';
    }
}
```
根据 userId 查询用户，修改信息后 update 到数据库。

这里需要用到验证码，我们加一个发送验证码的接口：

```javascript
@Get('update/captcha')
async updateCaptcha(@Query('address') address: string) {
    if(!address) {
      throw new BadRequestException('邮箱地址不能为空');
    }
    const code = Math.random().toString().slice(2,8);

    await this.redisService.set(`update_user_captcha_${address}`, code, 10 * 60);

    await this.emailService.sendMail({
      to: address,
      subject: '更改用户信息验证码',
      html: `<p>你的验证码是 ${code}</p>`
    });
    return '发送成功';
}
```

测试下：

首先拿到验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0ff3998ce07a.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/454b9004962e.png)

登录账号拿到 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/196073964364.png)

带上 token 访问 /user/update 接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/640de104e30f.png)

更改成功。

查询下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5ac8a1db6b80.png)

确实修改了。

代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/chat-room-backend)。

## 总结

这节我们实现了修改密码、修改用户信息的接口。

分别实现了 /user/info 用于回显用户信息，/user/update_password 用于修改密码，/user/update 用于修改用户信息。

以及 /user/update/captcha 和 /user/update_password/captcha 用于发送验证码。

其中 /user/info 和 /user/update 接口需要登录，然后通过之前封装的 @UserInfo 装饰器从 request.user 取用户信息。

至此，用户模块的功能就完成了。