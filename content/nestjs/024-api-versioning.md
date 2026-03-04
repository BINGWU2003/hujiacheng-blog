---
title: "接口如何实现多版本共存"
date: 2025-01-24
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["NestJS 基础"]
series_order: 24
---

应用开发完一版上线之后，还会不断的迭代。

后续可能需要修改已有的接口，但是为了兼容，之前版本的接口还要保留。

那如何同时支持多个版本的接口呢？

Nest 内置了这个功能，我们来试一下：

```
nest new version-test
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bedd6e9943cd.png)

创建个 nest 项目。

进入项目，创建 aaa 模块：

```
nest g resource aaa --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d54c2ebe489e.png)

把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/122e43f2e761.png)

postman 里访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d7d122d42153.png)

这是版本一的接口。

假设后面我们又开发了一版接口，但路由还是 aaa，怎么做呢？

这样：


![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/71fbb21617ed.png)

在 controller 上标记为 version 1，这样默认全部的接口都是 version 1。

然后单独用 @Version 把 version 2 的接口标识一下。

在 main.ts 里调用 enableVersioning 开启接口版本功能：

```javascript
import { VersioningType } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableVersioning({
    type: VersioningType.HEADER,
    header: 'version'
  })
  await app.listen(3000);
}
bootstrap();
```
开启接口版本功能，指定通过 version 这个 header 来携带版本号。

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5f27cc7f1e1c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fe33fa2a93d3.png)

可以看到，带上 version:1 的 header，访问的就是版本 1 的接口。

带上 version:2 的 header，访问的就是版本 2 的接口。

它们都是同一个路由。

但这时候有个问题：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/88defc33e939.png)

如果不带版本号就 404 了。

这个也很正常，因为这就是版本一的接口嘛，只有显式声明版本才可以。

如果你想所有版本都能访问这个接口，可以用 VERSION_NEUTRAL 这个常量：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2c6f3d4c4cab.png)

现在带不带版本号，不管版本号是几都可以访问这些接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/478f5c6de732.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2ef199da096b.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/44a5dbe9928b.png)

但是现在因为从上到下匹配，版本 2 的接口不起作用了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b33cfd709e5f.png)

这时候或者可以把它移到上面去：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8079a29b4cd0.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fda2533b9fda.png)

或者单独建一个 version 2 的 controller
```
nest g controller aaa/aaa-v2 --no-spec --flat
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/057ec3bedb56.png)

把 AaaController 里 version 2 的接口删掉，移到这里来：

```javascript
import { Controller, Get,Version } from '@nestjs/common';
import { AaaService } from './aaa.service';

@Controller({
    path: 'aaa',
    version: '2'
})
export class AaaV2Controller {
    constructor(private readonly aaaService: AaaService) {}

    @Get()
    findAllV2() {
      return this.aaaService.findAll() + '222';
    }
}
```
现在版本 2 就走的 AaaV2Controller：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fa62ab8e4d2c.png)

其他版本走 AaaController：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/89bbfd0580f3.png)

一般我们就是这样做的，有一个 Controller 标记为 VERSION_NEUTRAL，其他版本的接口放在单独 Controller 里。

注意，controller 之间同样要注意顺序，前面的 controller 先生效：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/effd5a3f6ac6.png)

试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0931b8c366df.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c4c94dac6c56.png)

除了用自定义 header 携带版本号，还有别的方式：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d21abeaa5b89.png)

```javascript
app.enableVersioning({
    type: VersioningType.MEDIA_TYPE,
    key: 'vv='
})
```
MEDIA_TYPE 是在 accept 的 header 里携带版本号：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/424122364b28.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/63a9a0bc8afd.png)

你也可以用 URI 的方式：

```javascript
app.enableVersioning({
    type: VersioningType.URI
})
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c19868fe6fe2.png)


但是这种方式不支持 VERSION_NEUTRAL，你要指定明确的版本号才可以：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d7e34613311e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/29c33a364c1d.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b1667b437f23.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e06424677372.png)

此外，如果觉得这些指定版本号的方式都不满足需求，可以自己写：

```javascript
import { VersioningType } from '@nestjs/common';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { Request } from 'express';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  const extractor = (request: Request)=> {
    if(request.headers['disable-custom']) {
      return '';
    }
    return request.url.includes('guang') ? '2' : '1';
  }

  app.enableVersioning({
    type: VersioningType.CUSTOM,
    extractor
  })

  await app.listen(3000);
}

bootstrap();
```
我们自己实现了一个版本号的逻辑，如果 url 里包含 guang，就返回版本 2 的接口，否则返回版本 1 的。

此外，如果有 disable-custom 的 header 就返回 404。

试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7f5c9de316c3.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2d41523ecbe1.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/db169e50d62c.png)

这样，就能实现各种灵活的版本号规则。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/version-test)。
## 总结

今天我们学了如何开发一个接口的多个版本。

Nest 内置了这个功能，同一个路由，指定不同版本号就可以调用不同的接口。

只要在 main.ts 里调用 enableVersioning 即可。

有 URI、HEADER、MEDIA_TYPE、CUSTOM 四种指定版本号的方式。

HEADER 和 MEDIA_TYPE 都是在 header 里置顶，URI 是在 url 里置顶，而 CUSTOM 是自定义版本号规则。

可以在 @Controller 通过 version 指定版本号，或者在 handler 上通过 @Version 指定版本号。

如果指定为 VERSION_NEUTRAL 则是匹配任何版本号（URI 的方式不支持这个）。

这样，当你需要开发同一个接口的多个版本的时候，就可以用这些内置的功能。
