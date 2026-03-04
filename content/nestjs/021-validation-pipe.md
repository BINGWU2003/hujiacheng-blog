---
title: "如何使用 ValidationPipe 验证 post 请求参数"
date: 2025-01-21
draft: false
description: ""
tags: ["nestjs", "pipe"]
categories: ["NestJS"]
series: ["NestJS 基础"]
series_order: 21
---

上节我们学了 pipe 来对参数做验证和转换，但那些都是 get 请求的参数，如果是 post 请求呢？

post 请求的数据是通过 @Body 装饰器来取，并且要有一个 dto class 来接收：

（dto 是 data transfer object，数据传输对象，用于封装请求体的数据）

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1f0cd4005fe5.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/58f8a1e6e9a1.png)

我们用 postman 来发个 post 请求。

(postman 在这里下载： <https://www.postman.com/downloads>)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/387fc03587ac.png)

content-type 指定为 json。

点击 send，就可以看到服务端接收到了数据，并且把它转为了 dto 类的对象：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/00856ee712ab.png)

但如果我们 age 传一个浮点数，服务端也能正常接收：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6b5069aae3bf.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2d8c3aa6d7d7.png)

因为它也是 number。

而这很可能会导致后续的逻辑出错。

所以我们要对他做参数验证。

怎么做呢？

这就需要用到这节的 ValidationPipe 了。

它需要两个依赖包：
```
npm install class-validator class-transformer
```
然后在 @Body 里添加这个 pipe：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2af37710a960.png)

在 dto 这里，用 class-validator 包的 @IsInt 装饰器标记一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/de4f0f0665e4.png)

再次请求，你就会发现它检查出了参数里的错误：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/587aec0eaa55.png)

那它是怎么实现的呢？

[class-validator](https://www.npmjs.com/package/class-validator) 包提供了基于装饰器声明的规则对对象做校验的功能：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/31f469d376c6.png)

而 [class-transformer](https://www.npmjs.com/package/class-transformer) 则是把一个普通对象转换为某个 class 的实例对象的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cdfebae34dc4.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1735590e7cc4.png)

这两者一结合，那 ValidationPipe 是怎么实现的不就想明白了么：

**我们声明了参数的类型为 dto 类，pipe 里拿到这个类，把参数对象通过 class-transformer 转换为 dto 类的对象，之后再用 class-validator 包来对这个对象做验证。**

我们自己写写看：

```javascript
import { PipeTransform, Injectable, ArgumentMetadata, BadRequestException } from '@nestjs/common';
import { validate } from 'class-validator';
import { plainToInstance } from 'class-transformer';

@Injectable()
export class MyValidationPipe implements PipeTransform<any> {
  async transform(value: any, { metatype }: ArgumentMetadata) {
    if (!metatype) {
      return value;
    }
    const object = plainToInstance(metatype, value);
    const errors = await validate(object);
    if (errors.length > 0) {
      throw new BadRequestException('参数验证失败');
    }
    return value;
  }
}
```

pipe 里拿到的 metatype 就是这部分：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/36bd8750a916.png)

如果没有声明这部分，那就没法转换和验证，直接返回 value。

否则，通过 class-transformer 包的 plainToInstance 把普通对象转换为 dto class 的实例对象。

之后调用 class-validator 包的 validate api 对它做验证。如果验证不通过，就抛一个异常。

我们来用下看：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8d6ee5ba0d76.png)

替换为我们自己实现的 MyValidationPipe。

再次请求下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/17a4969b6405.png)

确实检查出了错误。

当然，我们做的并不够完善，还是直接用内置的 ValidationPipe 好了。

pipe 里也是可以注入依赖的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8076093434d3.png)

比如，我们指定 @Inject 注入 token 为 validation\_options 的对象。

因为标记了 @Optional，没找到对应的 provider 也不会报错：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0c025f77a67e.png)

但当我们在 module 里添加了这个 provider：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/179150b4c305.png)

就可以正常注入了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/90c3de8cd215.png)

当然，这种方式就不能用 new 的方式了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6a71333058f8.png)

直接指定 class，让 Nest 去创建对象放到 ioc 容器里。

如果是全局的 pipe，要通过这种方式来创建才能注入依赖：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/de5d62d4fafc.png)

这就和我们之前创建全局 interceptor 一样。

同理，其余的 filter、guard 也可以通过这种方式声明为全局生效的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1414c1c760d7.png)

现在我们就可以把 handler 里的 ValidationPipe 去掉了

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7d11635ff72e.png)

再次访问，它依然是生效的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a07ca1c2d972.png)

当然，这里我们没有注入什么依赖，所以这种方式也可以：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/40873fd8b13c.png)

会用 ValidationPipe 之后，我们回过头来再看看 class-validator 都支持哪些验证方式：

我们声明这样一个 dto class：

```javascript
import { Contains, IsDate, IsEmail, IsFQDN, IsInt, Length, Max, Min } from 'class-validator';

export class Ppp {
    @Length(10, 20)
    title: string;
  
    @Contains('hello')
    text: string;
  
    @IsInt()
    @Min(0)
    @Max(10)
    rating: number;
  
    @IsEmail()
    email: string;
  
    @IsFQDN()
    site: string;
}
```

其中 @IsFQDN 是是否是域名的意思。

然后添加一个 post 的 handler：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/529f59f237c9.png)

在 postman 里发送 post 请求。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6744864bcd8d.png)
```json
{
    "title": "aaaaaaaaaaaaaaa",
    "text": "hello aaa",
    "rating": 10,
    "email": "aaa@qq.com",
    "site": "aaa.guang.com",
    "createDate": "2023-05-28T01:45:37.803Z"
}
```
参数正确的时候是不会报错的。

当参数不正确，ValidationPipe 就会返回 class-validator 的报错：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2936d85c9b0.png)

这个错误消息也是可以定制的：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a3be40cd99e8.png)

添加一个 options 对象，传入 message 函数，打印下它的参数：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/64350204441e.png)

可以拿到对象、属性名、属性值、class 名等各种信息，然后你可以返回自定义的 message：
```typescript
@Length(10, 20, {
    message({targetName, property, value, constraints}) {
        return `${targetName} 类的 ${property} 属性的值 ${value} 不满足约束: ${constraints}`
    }
})
title: string;
```
再次访问，返回的就是自定义的错误消息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/78d691c50d6d.png)

更多的装饰器可以看 [class-validator 文档](https://www.npmjs.com/package/class-validator)。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/pipe-test)。

## 总结

接收 post 请求的方式是声明一个 dto class，然后通过 @Body 来取请求体来注入值。

对它做验证要使用 ValidationPipe。

它的实现原理是基于 class-tranformer 把参数对象转换为 dto class 的对象，然后通过 class-validator 基于装饰器对这个对象做验证。

我们可以自己实现这样的 pipe，pipe 里可以注入依赖。

如果是全局 pipe 想注入依赖，需要通过 APP\_PIPE 的 token 在 AppModule 里声明 provider。

class-validator 支持很多种验证规则，比如邮箱、域名、长度、值的范围等，而且错误消息也可以自定义。

ValidationPipe 是非常常用的 pipe，后面会大量用到。
