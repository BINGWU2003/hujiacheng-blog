---
title: "如何灵活创建 DTO"
date: 2025-03-25
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["实战技巧"]
series_order: 4
---

Pdto 是 data transfer object，用于封装请求参数，后端应用常见对象。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dfd84b0fa042.png)

当开发 CRUD 接口的时候，你会发现 create 的 dto 对象和 update 的 dto 对象很类似。

那能不能不从头创建，而是基于已有的对象来创建呢？

可以的。

我们来试一下：

```
nest new dto-vo-test
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aff35e429a8e.png)

创建个 nest 项目。

进入项目，创建 aaa 的 crud 模块：

```
nest g resource aaa
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6576d9850a4e.png)

可以看到，它自动创建了 CreateAaaDto、UpdateAaaDto 用来封装 create、update 的参数：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3e0f3396bdff.png)

改下 aaa.entity.ts

```javascript
export class Aaa {

    id: number;

    name: string;

    age: number;

    sex: boolean;
    
    email: string;

    hoobies: string[]
}
```

Entity 有 id、name、age、sex、email、hobbies 这些字段。

那 CreateAaaDto 里要有 name、age、sex、email、hobbies 这些字段

而 UpdateAaaDto 里也是 name、age、sex、email、hobbies 这些字段。

```javascript
export class CreateAaaDto {
    name: string;

    age: number;

    sex: boolean;

    email: string;

    hoobies: string[]
}
```

```javascript
export class UpdateAaaDto  {

    name: string;

    age: number;

    sex: boolean;

    email: string;

    hoobies: string[]
}
```

而且我们还要用 ValidationPipe 加上参数校验。

安装用到的包：

```
npm install --save class-validator class-transformer
```
然后在 CreateAaaDto 和 UpdateAaaDto 加一下验证：

```javascript
import { IsBoolean, IsEmail, IsNotEmpty, IsNumber, Length, MaxLength, MinLength } from "class-validator";

export class CreateAaaDto {
    @IsNotEmpty()
    @MinLength(4)
    @MaxLength(20)
    name: string;

    @IsNotEmpty()
    @IsNumber()
    age: number;

    @IsNotEmpty()
    @IsBoolean()
    sex: boolean;

    @IsNotEmpty()
    @IsEmail()
    email: string;

    hoobies: string[]
}
```

```javascript
import { IsBoolean, IsEmail, IsNotEmpty, IsNumber, Length, MaxLength, MinLength } from "class-validator";

export class UpdateAaaDto {
    @IsNotEmpty()
    @MinLength(4)
    @MaxLength(20)
    name: string;

    @IsNotEmpty()
    @IsNumber()
    age: number;

    @IsNotEmpty()
    @IsBoolean()
    sex: boolean;

    @IsNotEmpty()
    @IsEmail()
    email: string;

    hoobies: string[]
}
```
然后全局启用 ValidationPipe：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/31b987a7d4bf.png)

```javascript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe({
    transform: true
  }))

  await app.listen(3000);
}
bootstrap();
```
transform 指定为 true，这样会自动把参数的 js 对象转换为 dto 类型对象。

打印下 dto 对象：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/740ad69c04cf.png)

测试下：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7a51da2750e.png)

create 接口，当参数没通过校验时：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b65fe5ed05e5.png)

参数通过校验后：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d6f6a3fb2eb6.png)

可以看到，打印的是 CreateAaaDto 的对象，说明 ValidationPipe 的 transform 生效了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/71b07c8a32a2.png)

再试下 update 接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f920211e4754.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bc716eb84b09.png)

也没问题。

虽然没问题，但是现在 CreateAaaDto 和 UpdateAaaDto 明显重复太多了。

很多字段重复写了两次。

有什么办法能避免这种重复呢？

很简单呀，继承不就行了？

```javascript
import { CreateAaaDto } from "./create-aaa.dto";

export class UpdateAaaDto extends CreateAaaDto {
}
```
试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6a4a3f53425f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/15ef7e32d46e.png)

没啥问题。

当然，现在所有字段都是必填的，比如 name、age、email 等。

其实更新的时候可以只更新 name 或者 email。

这时候直接继承就不行了。

可以用 PartialType 处理下：

```javascript
import { PartialType } from '@nestjs/mapped-types';
import { CreateAaaDto } from "./create-aaa.dto";

export class UpdateAaaDto extends PartialType(CreateAaaDto) {

}
```
试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5e4308594816.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a62cfadd8ef0.png)

现在只填部分字段依然校验通过了。

好神奇，我们不是指定了 @IsNotEmpty 了么？

咋继承过来就没了呢？

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/84ac418e4f98.png)

这是因为 PartialType 内部做了处理。

简单看下源码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b992c0cef1ec.png)

它创建了一个新的 class 返回，继承了传入的 class 的属性，和 validation metadata。

但是添加一个一个 @IsOptional 的装饰器。

这样可不就变为可选的了么？

类似的这样的方法还有几个：

比如 PickType：

```javascript
import { PartialType, PickType } from '@nestjs/mapped-types';
import { CreateAaaDto } from "./create-aaa.dto";

export class UpdateAaaDto extends PickType(CreateAaaDto, ['age', 'email']) {

}

```
现在可以只传 age、email 这两个字段：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/497072e25456.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/842253ec5b31.png)

但它和 PartialType 不同，Pick 出来的字段并不会变为可选：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b51056016c12.png)

或者也可以用 OmitType，从之前的 dto 删除几个字段：

```javascript
import { OmitType, PartialType, PickType } from '@nestjs/mapped-types';
import { CreateAaaDto } from "./create-aaa.dto";

export class UpdateAaaDto extends OmitType(CreateAaaDto, ['name', 'hoobies', 'sex']) {

}
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/16434b542f78.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/426716395aef.png)

效果一样。

PickType 是从中挑选几个，OmitType 是从中去掉几个取剩下的。

此外，如果你有两个 dto 想合并，可以用 IntersectionType。

创建个 xxx.dto.ts

```javascript
import { IsNotEmpty, IsNumber, MinLength } from "class-validator";

export class XxxDto {
    @IsNotEmpty()
    @MinLength(4)
    xxx: string;

    @IsNotEmpty()
    @IsNumber()
    yyy: number;
}

```
用 CreateAaaDto 和 XxxDto 来创建 UpdateAaaDto：

```javascript
import { IntersectionType } from '@nestjs/mapped-types';
import { CreateAaaDto } from "./create-aaa.dto";
import { XxxDto } from './xxx.dto';

export class UpdateAaaDto extends IntersectionType(CreateAaaDto, XxxDto) {

}
```

可以看到，现在会提示你这些字段都是必填的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/54dd4296b790.png)

这些字段都填上之后，校验就通过了：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/064716a4bd01.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/793618b4b9ea.png)

服务端接收到了 dto 的数据。

当然，PartialType、PickType、OmitType、IntersectionType 经常会组合用：

```javascript
import { IntersectionType, OmitType, PartialType, PickType } from '@nestjs/mapped-types';
import { CreateAaaDto } from "./create-aaa.dto";
import { XxxDto } from './xxx.dto';

export class UpdateAaaDto extends IntersectionType(
    PickType(CreateAaaDto, ['name', 'age']), 
    PartialType(OmitType(XxxDto, ['yyy']))
) {

}
```
从 CreateAaaDto 里拿出 name 和 age 属性，从 XxxDto 里去掉 yyy 属性变为可选，然后两者合并。

试一下效果：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f22e98b366a9.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/02729bb5d99c.png)

name 必填、xxx 不是必填。

这样创建 dto 对象可太灵活了，随意组合已有的 dto 就行。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/dto-vo-test)

## 总结

开发 CRUD 接口的时候，经常会发现 update 的 dto 和 create 的 dto 很类似，而我们要重复的写两次。

这时候可以用 @nestjs/mapped-types 的 PartialType、PickType、OmitType、IntersectionType 来避免重复。

PickType 是从已有 dto 类型中取某个字段。

OmitType 是从已有 dto 类型中去掉某个字段。

PartialType 是把 dto 类型变为可选。

IntersectionType 是组合多个 dto 类型。

灵活运用这些方法，可以轻松的基于已有 dto 创建出新的 dto。
