---
title: "class-validator 的内置装饰器，如何自定义装饰器"
date: 2025-03-26
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["实战技巧"]
series_order: 5
---

我们会用 class-validator 的装饰器对 dto 对象做校验。

那 class-validator 都有哪些装饰器可用呢？

这节我们来过一遍。

```
nest new class-validator-decorators
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/59c6cd30128c.png)

创建个 CRUD 模块：

```
nest g resource aaa --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/18a0239de5fe.png)

全局启用 ValidationPipe，对 dto 做校验：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1e782aac4995.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/84189ba54fe3.png)

```javascript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe());

  await app.listen(3000);
}
bootstrap();
```

安装用到的 class-validator 和 class-transformer 包：

```
npm install --save class-validator class-transformer
```
然后在 create-aaa.dto.ts 加一下校验：

```javascript
import { IsEmail, IsNotEmpty, IsString } from "class-validator";

export class CreateAaaDto {

    @IsNotEmpty({message: 'aaa 不能为空'})
    @IsString({message: 'aaa 必须是字符串'})
    @IsEmail({}, {message: 'aaa 必须是邮箱'})
    aaa: string;

}
```
把服务跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ffd6a9a8d5bd.png)

postman 里访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/49115547f813.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7d560010ce49.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5d5d81f23fba.png)

这就是 class-validator 的装饰器的用法。

类似这种装饰器有很多。

和 @IsNotEmpty 相反的是 @IsOptional：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e072ee54b58e.png)

加上之后就是可选的了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/026897571929.png)

上节学的 PartialType 就是用的 IsOptional 装饰器实现的。

@IsIn 可以限制属性只能是某些值：

```javascript
@IsNotEmpty({message: 'aaa 不能为空'})
@IsString({message: 'aaa 必须是字符串'})
@IsEmail({}, {message: 'aaa 必须是邮箱'})
@IsIn(['aaa@aa.com', 'bbb@bb.com'])
aaa: string;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/292052a8067c.png)

还有 @IsNotIn，可以限制属性不能是某些值：

```javascript
@IsNotEmpty({message: 'aaa 不能为空'})
@IsString({message: 'aaa 必须是字符串'})
@IsEmail({}, {message: 'aaa 必须是邮箱'})
@IsNotIn(['aaa@aa.com', 'bbb@bb.com'])
aaa: string;
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f5c77094d7ec.png)

@IsBoolean、@IsInt、@IsNumber、@IsDate 这种就不说了。

@IsArray 可以限制属性是 array：

```javascript
@IsArray()
bbb:string;
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b8317260e393.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e978fa0d1fc2.png)

@ArrayContains 指定数组里必须包含的值：

```javascript
@IsArray()
@ArrayContains(['aaa'])
bbb:string;
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e654cba55e08.png)

类似的还有 @ArrayNotContains 就是必须不包含的值。

@ArrayMinSize 和 @ArrayMaxSize 限制数组的长度。

@ArrayUnique 限制数组元素必须唯一：

```javascript
@IsArray()
@ArrayNotContains(['aaa'])
@ArrayMinSize(2)
@ArrayMaxSize(5)
@ArrayUnique()
bbb:string;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/88ab1acf7ec8.png)

前面讲过 @IsNotEmpty，和它类似的还有 @IsDefined。

@IsNotEmpty 检查值是不是 ''、undefined、null。

@IsDefined 检查值是不是 undefined、null。

当你允许传空字符串的时候就可以用 @IsDefined。

```javascript
@IsDefined()
ccc: string;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d9bf31ca8aa8.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bd68bc5151ae.png)

如果是 @IsNotEmpty，那空字符串也是不行的：

```javascript
// @IsDefined()
@IsNotEmpty()
ccc: string;
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f72ef7e50376.png)

数字可以做更精准的校验：

```javascript
@IsPositive()
@Min(1)
@Max(10)
@IsDivisibleBy(2)
ddd:number;
```
@IsPositive 是必须是正数、@IsNegative 是必须是负数。

@Min、@Max 是限制范围。

@IsDivisibleBy 是必须被某个数整除。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55e1f29121d5.png)

@IsDateString 是 ISO 标准的日期字符串：

```javascript
@IsDateString()
eee: string;
```
也就是这种：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1ae4d72eea31.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/01cc202b819d.png)

还有几个字符串相关的：

@IsAlpha 检查是否只有字母

@IsAlphanumeric 检查是否只有字母和数字

@Contains 是否包含某个值

```javascript
@IsAlphanumeric()
@Contains('aaa')
fff: string;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5ce081458d9c.png)

字符串可以通过 @MinLength、@MaxLength、@Length 来限制长度：

```javascript
@MinLength(2)
@MaxLength(6)
ggg: string;
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b9e9a3910ae9.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/efedf1d8cb30.png)

也可以用 @Length：

```javascript
@Length(2, 6)
ggg: string;
```
还可以校验颜色值的格式：@IsHexColor、@IsHSL、@IsRgbColor

校验 IP 的格式：@IsIP

校验端口： @IsPort

校验 JSON 格式 @IsJSON

常用的差不多就这些，更多的可以看 [class-validator 的文档](https://www.npmjs.com/package/class-validator#validation-decorators)。

此外，如果某个属性是否校验要根据别的属性的值呢？

这样：

```javascript
@IsBoolean()
hhh: boolean;

@ValidateIf(o => o.hhh === true)
@IsNotEmpty()
@IsHexColor()
iii: string;
```
如果 hhh 传了 true，那就需要对 iii 做校验，否则不需要。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/da0bfd54e4c4.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d24e715cde88.png)

此外，如果这些内置的校验规则都不满足需求呢？

那就自己写！

创建 my-validator.ts

```javascript
import { ValidationArguments, ValidatorConstraint, ValidatorConstraintInterface } from "class-validator";

@ValidatorConstraint()
export class MyValidator implements ValidatorConstraintInterface {
    validate(text: string, validationArguments: ValidationArguments) {
        console.log(text, validationArguments)
        return true;
    }
}
```
用 @ValidatorConstraint 声明 class 为校验规则，然后实现 ValidatorConstraintInterface 接口。

用一下：
```javascript
@Validate(MyValidator, [11, 22], {
    message: 'jjj 校验失败',
})
jjj: string;
```

访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7b16b25b8ab.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2da0fa4026e9.png)

第一个参数传入的字段值，第二个参数包含更多信息，比如 @Validate 指定的参数在 constraints 数组里。

这样，我们只要用这些做下校验然后返回 true、false 就好了。

比如这样：

```javascript
import { ValidationArguments, ValidatorConstraint, ValidatorConstraintInterface } from "class-validator";

@ValidatorConstraint()
export class MyValidator implements ValidatorConstraintInterface {
    validate(text: string, validationArguments: ValidationArguments) {
        // console.log(text, validationArguments)
        return text.includes(validationArguments.constraints[0]);
    }
}
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d5506d4d2309.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9fb355aa9fa7.png)

内容包含 11 的时候才会校验通过。

那如果这个校验是异步的呢？

返回 promise 就行：

```javascript
import { ValidationArguments, ValidatorConstraint, ValidatorConstraintInterface } from "class-validator";

@ValidatorConstraint()
export class MyValidator implements ValidatorConstraintInterface {
    async validate(text: string, validationArguments: ValidationArguments) {
        // console.log(text, validationArguments)
        return new Promise<boolean>((resolve) => {
            setTimeout(() => {
                resolve(text.includes(validationArguments.constraints[0]));
            }, 3000);
        })
    }
}
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c5afb771e67f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b021fc1bb927.png)

这样用起来还是不如内置装饰器简单：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/45c650081e98.png)

可以用我们前面学的创建自定义装饰器的方式来包装一下：

创建 my-contains.decorator.ts

```javascript
import { applyDecorators } from '@nestjs/common';
import { Validate, ValidationOptions } from 'class-validator';
import { MyValidator } from './my-validator';

export function MyContains(content: string, options?: ValidationOptions) {
  return applyDecorators(
     Validate(MyValidator, [content], options)
  )
}
```
用 applyDecorators 组合装饰器生成新的装饰器。

然后用起来就可以这样：

```javascript
@MyContains('111', {
    message: 'jjj 必须包含 111'
})
jjj: string;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2f1369fe9edd.png)

我们封装出了 @Contains，其实内置的那些装饰器我们都可以自己封装出来。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/class-validator-decorators)

## 总结

我们过了一遍 class-validator 的常用装饰器。

它们可以对各种类型的数据做精确的校验。

然后 @ValidateIf 可以根据别的字段来决定是否校验当前字段。

如果内置的装饰器不符合需求，完全可以自己实现，然后用 @Validate 来应用，用自定义装饰器 applyDecorators 包一层之后，和 class-validator 的内置装饰器就一模一样了。

所有的 class-validator 内置装饰器我们完全可以自己实现一遍。
