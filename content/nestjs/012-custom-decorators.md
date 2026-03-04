---
title: "Nest 如何自定义装饰器"
date: 2025-01-12
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["NestJS 基础"]
series_order: 12
---

Nest 内置了很多装饰器，大多数功能都是通过装饰器来使用的。

但当这些装饰器都不满足需求的时候，能不能自己开发呢？

装饰器比较多的时候，能不能把多个装饰器合并成一个呢？

自然是可以的。

很多内置装饰器我们都可以自己实现。

我们来试试看：

    nest new custom-decorator -p npm

创建个 nest 项目。

执行

    nest g decorator aaa --flat

创建个 decorator。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/777b762f273c.png)

这个装饰器就是自定义的装饰器。

之前我们是这样用的 @SetMetadata

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0d123bc2521d.png)

然后加个 Guard 取出来做一些判断：

    nest g guard aaa --flat --no-spec

guard 里使用 reflector 来取 metadata：

```javascript
import { CanActivate, ExecutionContext, Inject, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Observable } from 'rxjs';

@Injectable()
export class AaaGuard implements CanActivate {
  @Inject(Reflector)
  private reflector: Reflector;

  canActivate(
    context: ExecutionContext,
  ): boolean | Promise<boolean> | Observable<boolean> {

    console.log(this.reflector.get('aaa', context.getHandler()));

    return true;
  }
}
```
加到路由上：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/15aa753af642.png)

把服务跑起来：

```
npm run start:dev
```
然后访问 http://localhost:3000 可以看到打印的 metadata

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f567d99f3d2e.png)

但是不同 metadata 有不同的业务场景，有的是用于权限的，有的是用于其他场景的。

但现在都用 @SetMetadata 来设置太原始了。

这时候就可以这样封装一层：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/80c04fb7eae1.png)

装饰器就可以简化成这样：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ea8760676a61.png)

还有，有没有觉得现在装饰器太多了，能不能合并成一个呢？

当然也是可以的。

这样写：

```javascript
import { applyDecorators, Get, UseGuards } from '@nestjs/common';
import { Aaa } from './aaa.decorator';
import { AaaGuard } from './aaa.guard';

export function Bbb(path, role) {
  return applyDecorators(
    Get(path),
    Aaa(role),
    UseGuards(AaaGuard)
  )
}
```

在自定义装饰器里通过 applyDecorators 调用其他装饰器。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/682df33f63d1.png)

这三个 handler 的装饰器都是一样的效果。

这就是自定义方法装饰器。

此外，也可以自定义参数装饰器：

```javascript
import { createParamDecorator, ExecutionContext } from '@nestjs/common';

export const Ccc = createParamDecorator(
  (data: string, ctx: ExecutionContext) => {
    return 'ccc';
  },
);
```

先用用看：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fff28031cb9e.png)

大家猜这个 c 参数的值是啥？

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5cfc61011f66.png)

没错，就是 ccc，也就是说参数装饰器的返回值就是参数的值。

回过头来看看这个装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/99b1b8d44af2.png)

data 很明显就是传入的参数，而 ExecutionContext 前面用过，可以取出 request、response 对象。

这样那些内置的 @Param、@Query、@Ip、@Headers 等装饰器，我们是不是能自己实现了呢？

我们来试试看：

```javascript
import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { Request } from 'express';

export const MyHeaders = createParamDecorator(
  (key: string, ctx: ExecutionContext) => {
    const request: Request = ctx.switchToHttp().getRequest();
    return key ? request.headers[key.toLowerCase()] : request.headers;
  },
);
```

通过 ExecutionContext 取出 request 对象，然后调用 getHeader 方法取到 key 对应的请求头返回。

效果如下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6f3cb19ff79d.png)

分别通过内置的 @Headers 装饰器和我们自己实现的 @MyHeaders 装饰器来取请求头，结果是一样的。

再来实现下 @Query 装饰器：

```javascript
export const MyQuery = createParamDecorator(
    (key: string, ctx: ExecutionContext) => {
        const request: Request = ctx.switchToHttp().getRequest();
        return request.query[key];
    },
);
```

用一下试试看：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9dbd08535dd6.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b4ca1174f159.png)

和内置的 Query 用起来一毛一样！

同理，其他内置参数装饰器我们也能自己实现。

而且这些装饰器和内置装饰器一样，可以使用 Pipe 做参数验证和转换：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e5b1236b918a.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ccaa8f6e8135.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/18952b55bade.png)

知道了如何自定义方法和参数的装饰器，那 class 的装饰器呢？

其实这个和方法装饰器的定义方式一样：

比如单个装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e1e147afdfff.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/003c1666eaba.png)

可以看到自定义装饰器生效了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d7466a90a386.png)

也可以通过 applyDecorators 组合多个装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7cde08d63682.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/91cc1d675e6b.png)

在 guard 里加一条打印：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/25bcc8c0b7b1.png)

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5a70672a95b1.png)

可以看到 metadata 也设置成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1dff74e882b3.png)

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/custom-decorator)

## 总结

内置装饰器不够用的时候，或者想把多个装饰器合并成一个的时候，都可以自定义装饰器。

方法的装饰器就是传入参数，调用下别的装饰器就好了，比如对 @SetMetadata 的封装。

如果组合多个方法装饰器，可以使用 applyDecorators api。

class 装饰器和方法装饰器一样。

还可以通过 createParamDecorator 来创建参数装饰器，它能拿到 ExecutionContext，进而拿到 reqeust、response，可以实现很多内置装饰器的功能，比如 @Query、@Headers 等装饰器。

通过自定义方法和参数的装饰器，可以让 Nest 代码更加的灵活。
