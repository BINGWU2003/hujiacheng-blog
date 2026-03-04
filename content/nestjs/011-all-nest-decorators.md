---
title: "一网打尽 Nest 全部装饰器"
date: 2025-01-11
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["NestJS 基础"]
series_order: 11
---

Nest 的功能都是大多通过装饰器来使用的，这节我们就把所有的装饰器过一遍。

我们创建个新的 nest 项目：

    nest new all-decorator -p npm

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/710285627e9b.png)

Nest 提供了一套模块系统，通过 @Module声明模块：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d4b8451a9259.png)

通过 @Controller、@Injectable 分别声明其中的 controller 和 provider：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8f36a35ced6c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9ba1650c89da.png)

这个 provider 可以是任何的 class：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fd87cda2fa21.png)

注入的方式可以是构造器注入：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e3d7d1887ff0.png)

或者属性注入：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/063345407175.png)

属性注入要指定注入的 token，可能是 class 也可能是 string。

你可以通过 useFactory、useValue 等方式声明 provider：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bda6c0fd5629.png)

这时候也需要通过 @Inject 指定注入的 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0ecb41592627.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1eb3fa49cdc5.png)

这些注入的依赖如果没有的话，创建对象时会报错。但如果它是可选的，你可以用 @Optional 声明一下，这样没有对应的 provider 也能正常创建这个对象。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e04df804d881.png)

如果模块被很多地方都引用，为了方便，可以用 @Global 把它声明为全局的，这样它 exports 的 provider 就可以直接注入了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3fddecffabaa.png)

filter 是处理抛出的未捕获异常的，通过 @Catch 来指定处理的异常：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ecd7dd75452a.png)

然后通过 @UseFilters 应用到 handler 上：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1491bbd56ada.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d5cc3cd54a74.png)

除了 filter 之外，interceptor、guard、pipe 也是这样用：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d3c1e09b2f64.png)

当然，pipe 更多还是单独在某个参数的位置应用：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/51b9962eb893.png)

这里的 @Query 是取 url 后的 ?bbb=true，而 @Param 是取路径中的参数，比如 /xxx/111 种的 111

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/52c3779f5d8c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e640ded44a80.png)

此外，如果是 @Post 请求，可以通过 @Body 取到 body 部分：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b20486f5d13f.png)

我们一般用 dto 的 class 来接受请求体里的参数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8d8a1befae67.png)

nest 会实例化一个 dto 对象：

用 postman 发个 post 请求：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0a361ce85a61.png)

可以看到 nest 接受到了 body 里的参数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c2ba8480ef40.png)

除了 @Get、@Post 外，还可以用 @Put、@Delete、@Patch、@Options、@Head 装饰器分别接受 put、delete、patch、options、head 请求：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d1a31f8a91e4.png)

handler 和 class 可以通过 @SetMetadata 指定 metadata：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6cfbed6f7b92.png)

然后在 guard 或者 interceptor 里取出来：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c45dd3432361.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5d1bb90fe87f.png)

你可以通过 @Headers 装饰器取某个请求头 或者全部请求头：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a8e323bed50e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/76ad5f799cfa.png)

通过 @Ip 拿到请求的 ip：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2d40cc2c9245.png)

通过 @Session 拿到 session 对象：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e4aa73019e42.png)

但要使用 session 需要安装一个 express 中间件：

    npm install express-session

在 main.ts 里引入并启用：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6fb3424c3860.png)

指定加密的密钥和 cookie 的存活时间。

然后刷新页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/729a805e0f10.png)

会返回 set-cookie 的响应头，设置了 cookie，包含 sid 也就是 sesssionid。

之后每次请求都会自动带上这个 cookie：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ec3d239e627d.png)

这样就可以在 session 对象里存储信息了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ccfb3691c902.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/29becd24308f.gif)

@HostParam 用于取域名部分的参数：

我们再创建个 controller：

    nest g controller aaa --no-spec --flat

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/100631a1e6af.png)

这样指定 controller 的生效路径：

```javascript
import { Controller, Get, HostParam } from '@nestjs/common';

@Controller({ host: ':host.0.0.1', path: 'aaa' })
export class AaaController {
    @Get('bbb')
    hello() {
        return 'hello';
    }
}
```

controller 除了可以指定某些 path 生效外，还可以指定 host：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/074a175e7fe8.png)

然后再访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2b703200e7e2.gif)

这时候你会发现只有 host 满足 xx.0.0.1 的时候才会路由到这个 controller。

host 里的参数就可以通过 @HostParam 取出来：

```javascript
import { Controller, Get, HostParam } from '@nestjs/common';

@Controller({ host: ':host.0.0.1', path: 'aaa' })
export class AaaController {
    @Get('bbb')
    hello(@HostParam('host') host) {
        return host;
    }
}
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d48824b9c420.gif)

前面取的这些都是 request 里的属性，当然也可以直接注入 request 对象：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/be72c11e4af9.png)

通过 @Req 或者 @Request 装饰器，这俩是同一个东西：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/85d7c46017db.png)

注入 request 对象后，可以手动取任何参数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bddc1055ff03.png)

当然，也可以 @Res 或者 @Response 注入 response 对象，只不过 response 对象有点特殊：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/78d32fb8e737.png)

当你注入 response 对象之后，服务器会一直没有响应：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/de6c32f4d8a5.png)

因为这时候 Nest 就不会再把 handler 返回值作为响应内容了。

你可以自己返回响应：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8450a89095d8.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a76ef30d067.png)

Nest 这么设计是为了避免你自己返回的响应和 Nest 返回的响应的冲突。

如果你不会自己返回响应，可以通过 passthrough 参数告诉 Nest：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dbc3f65b4881.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a76ef30d067.png)

除了注入 @Res 不会返回响应外，注入 @Next 也不会：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/320f68d173d2.png)

当你有两个 handler 来处理同一个路由的时候，可以在第一个 handler 里注入 next，调用它来把请求转发到第二个 handler：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9396c7b03b51.png)

Nest 不会处理注入 @Next 的 handler 的返回值。

handler 默认返回的是 200 的状态码，你可以通过 @HttpCode 修改它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f5217f44c87c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/63a5e8d42940.png)

当然，你也可以修改 response header，通过 @Header 装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1d42847c5de6.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/de1600eb74c7.png)

此外，你还可以通过 @Redirect 装饰器来指定路由重定向的 url：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/20c10159ca26.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ed46081a4c57.gif)

或者在返回值的地方设置 url：

```javascript
@Get('xxx')
@Redirect()
async jump() {
    return {
      url: 'https://www.baidu.com',
      statusCode: 302
    }  
}
```

你还可以给返回的响应内容指定渲染引擎，不过这需要先这样设置：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4b542eb860a3.png)

```javascript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'path';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  app.useStaticAssets(join(__dirname, '..', 'public'));
  app.setBaseViewsDir(join(__dirname, '..', 'views'));
  app.setViewEngine('hbs');

  await app.listen(3000);
}
bootstrap();

```

分别指定静态资源的路径和模版的路径，并指定模版引擎为 handlerbars。

当然，还需要安装模版引擎的包 hbs：

    npm install --save hbs

然后准备图片和模版文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ddbad9afb56f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8ecba5b4e660.png)

在 handler 里指定模版和数据：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/091ad562950a.png)

就可以看到渲染出的 html 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d4abe5ca90cb.png)

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/all-decorator)。

## 总结

这节我们梳理了下 Nest 全部的装饰器

*   @Module： 声明 Nest 模块
*   @Controller：声明模块里的 controller
*   @Injectable：声明模块里可以注入的 provider
*   @Inject：通过 token 手动指定注入的 provider，token 可以是 class 或者 string
*   @Optional：声明注入的 provider 是可选的，可以为空
*   @Global：声明全局模块
*   @Catch：声明 exception filter 处理的 exception 类型
*   @UseFilters：路由级别使用 exception filter
*   @UsePipes：路由级别使用 pipe
*   @UseInterceptors：路由级别使用 interceptor
*   @SetMetadata：在 class 或者 handler 上添加 metadata
*   @Get、@Post、@Put、@Delete、@Patch、@Options、@Head：声明 get、post、put、delete、patch、options、head 的请求方式
*   @Param：取出 url 中的参数，比如 /aaa/:id 中的 id
*   @Query: 取出 query 部分的参数，比如 /aaa?name=xx 中的 name
*   @Body：取出请求 body，通过 dto class 来接收
*   @Headers：取出某个或全部请求头
*   @Session：取出 session 对象，需要启用 express-session 中间件
*   @HostParm： 取出 host 里的参数
*   @Req、@Request：注入 request 对象
*   @Res、@Response：注入 response 对象，一旦注入了这个 Nest 就不会把返回值作为响应了，除非指定 passthrough 为true
*   @Next：注入调用下一个 handler 的 next 方法
*   @HttpCode： 修改响应的状态码
*   @Header：修改响应头
*   @Redirect：指定重定向的 url
*   @Render：指定渲染用的模版引擎

把这些装饰器用熟，就掌握了 nest 大部分功能了。
