---
title: "ExecutionContext：切换不同上下文"
date: 2025-01-14
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["NestJS 基础"]
series_order: 14
---

Nest 支持创建多种类型的服务：

包括 HTTP 服务、WebSocket 服务，还有基于 TCP 通信的微服务。

这三种服务都会支持 Guard、Interceptor、Exception Filter 功能。

那么问题来了：

不同类型的服务它能拿到的参数是不同的，比如 http 服务可以拿到 request、response 对象，而 websocket 服务就没有。

也就是说你不能在 Guard、Interceptor、Exception Filter 里直接操作 request、response，不然就没法复用了，因为 websocket 没有这些。

那如何让同一个 Guard、Interceptor、Exception Filter 在不同类型的服务里复用呢？

Nest 的解决方法是 ArgumentHost 这个类。

我们来看一下：

创建个项目：
```
nest new argument-host
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e285785ff35a.png)

然后创建一个 filter：
```
nest g filter aaa --flat --no-spec
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/70be07e43ace.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/238514f6a1fb.png)

Nest 会 catch 所有未捕获异常，如果是 Exception Filter 声明的异常，那就会调用 filter 来处理。

那 filter 怎么声明捕获什么异常的呢？

我们创建一个自定义的异常类：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/175654fa5995.png)

```javascript
export class AaaException {
    constructor(public aaa: string, public bbb: string) {
        
    }
}
```

在 @Catch 装饰器里声明这个 filter 处理该异常：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8e111954a9c1.png)

然后需要启用它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8e70885eb860.png)

路由级别启用 AaaFilter，并且在 handler 里抛了一个 AaaException 类型的异常。

也可以全局启用：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/37234adb1bb6.png)
```javascript
app.useGlobalFilters(new AaaFilter());
```

访问 <http://localhost:3000> 就可以看到 filter 被调用了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/95f7a194c689.png)

filter 的第一个参数就是异常对象，那第二个参数呢？

可以看到，它有这些方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bdf84bfdd2fc.png)

我们用调试的方式跑一下：

点击 create launch.json file 创建一个调试配置文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6e00c07e69aa.png)

在 .vscode/launch.json 添加这样的调试配置：

```json
{
    "type": "pwa-node",
    "request": "launch",
    "name": "debug nest",
    "runtimeExecutable": "npm",
    "args": [
        "run",
        "start:dev",
    ],
    "skipFiles": [
        "<node_internals>/**"
    ],
    "console": "integratedTerminal",
}
```

点击调试启动：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e75821b4f065.gif)

打个断点：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fe6cda9bc643.png)

浏览器访问 <http://localhost:3000> 就可以看到它断住了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7cae13caf303.png)

我们分别调用下这些方法试试：

在 debug console 输入 host，可以看到它有这些属性方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1a449a678471.png)

host.getArgs 方法就是取出当前上下文的 reqeust、response、next 参数。

因为当前上下文是 http 服务，如果是 WebSocket 服务，这里拿到的就是别的东西了。

host.getArgByIndex 方法是根据下标取参数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9de0d611fce1.png)

当然，一般不会根据 index 来取，而且这样用：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/385c559115d8.png)

调用 switchToHttp 切换到 http 上下文，然后再调用 getRequest、getResponse 方法。

如果是 websocket、基于 tcp 的微服务等上下文，就分别调用 host.swtichToWs、host.switchToRpc 方法。

这样，就可以在 filter 里处理多个上下文的逻辑，跨上下文复用 filter了。

加个 if else 判断即可：

```javascript
import { ArgumentsHost, Catch, ExceptionFilter } from '@nestjs/common';
import { Response } from 'express';
import { AaaException } from './AaaException';

@Catch(AaaException)
export class AaaFilter implements ExceptionFilter {
  catch(exception: AaaException, host: ArgumentsHost) {
    if(host.getType() === 'http') {
      const ctx = host.switchToHttp();
      const response = ctx.getResponse<Response>();
      const request = ctx.getRequest<Request>();

      response
        .status(500)
        .json({
          aaa: exception.aaa,
          bbb: exception.bbb
        });
    } else if(host.getType() === 'ws') {

    } else if(host.getType() === 'rpc') {

    }
  }
}
```

刷新页面，就可以看到 filter 返回的响应：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d25e6f575b5f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/95cc2e6a3e76.png)

所以说，**ArgumentHost 是用于切换 http、websocket、rpc 等上下文类型的，可以根据上下文类型取到对应的 argument，让 Exception Filter 等在不同的上下文中复用**。

那 guard 和 interceptor 里呢？

我们创建个 guard 试一下：
```
nest g guard aaa --no-spec --flat
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3d094189c4be.png)

可以看到它传入的是 ExecutionContext：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5441ca00ac34.png)

有这些方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/414e5ff5a179.png)

是不是很眼熟？

没错，ExecutionContext 是 ArgumentHost 的子类，扩展了 getClass、getHandler 方法。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d310168165e1.png)

多加这两个方法是干啥的呢？

我们调试下看看：

路由级别启用 Guard：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/48aa9fa63d35.png)

在 Guard 里打个断点：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/48af41703659.png)

调用下 context.getClass 和 getHandler：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3b96a36e5a4d.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/06860f22db50.png)

会发现这俩分别是要调用的 controller 的 class 以及要调用的方法。

为什么 ExecutionContext 里需要拿到目标 class 和 handler 呢？

因为 Guard、Interceptor 的逻辑可能要根据目标 class、handler 有没有某些装饰而决定怎么处理。

比如权限验证的时候，我们会先定义几个角色：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/854b3a0ce565.png)

然后定义这样一个装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ab02251ae24c.png)

它的作用是往修饰的目标上添加 roles 的 metadata。

然后在 handler 上添加这个装饰器，参数为 admin，也就是给这个 handler 添加了一个 roles 为 admin 的metadata。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/866961b92d02.png)

这样在 Guard 里就可以根据这个 metadata 决定是否放行了：

```javascript
import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Observable } from 'rxjs';
import { Role } from './role';

@Injectable()
export class AaaGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {

    const requiredRoles = this.reflector.get<Role[]>('roles', context.getHandler());

    if (!requiredRoles) {
      return true;
    }

    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.some((role) => user && user.roles?.includes(role));
  }
}
```

我们在 Guard 里通过 ExecutionContext 的 getHandler 方法拿到了目标 handler 方法。

然后通过 reflector 的 api 拿到它的 metadata。

判断如果没有 roles 的 metadata 就是需要权限，那就直接放行。

如果有，就是需要权限，从 user 的 roles中判断下又没有当前 roles，有的话就放行。

刷新页面，可以看到返回的是 403：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c2a1915df3ff.png)

这说明 Guard 生效了。

这就是 Guard 里的 ExecutionContext 参数的用法。

同样，在 interceptor 里也有这个：
```
nest g interceptor aaa --no-spec --flat
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e5ec1699d264.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/13547f4d0e63.png)

同样可以通过 reflector 取出 class 或者 handler 上的 metdadata。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/argument-host)。

## 总结

为了让 Filter、Guard、Exception Filter 支持 http、ws、rpc 等场景下复用，Nest 设计了 ArgumentHost 和 ExecutionContext 类。

ArgumentHost 可以通过 getArgs 或者 getArgByIndex 拿到上下文参数，比如 request、response、next 等。

更推荐的方式是根据 getType 的结果分别 switchToHttp、switchToWs、swtichToRpc，然后再取对应的 argument。

而 ExecutionContext 还提供 getClass、getHandler 方法，可以结合 reflector 来取出其中的 metadata。

在写 Filter、Guard、Exception Filter 的时候，是需要用到这些 api 的。
