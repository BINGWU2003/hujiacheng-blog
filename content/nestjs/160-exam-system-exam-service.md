---
title: "考试系统：考试微服务"
date: 2025-06-09
draft: false
description: ""
tags: ["nestjs", "microservice"]
categories: ["NestJS"]
series: ["考试系统"]
series_order: 6
---

这节我们来实现考试微服务的功能。

首先创建考试表：

| 字段名 | 数据类型 | 描述 |
| --- | --- | --- |
| id | INT | 考试ID |
| createUserId| INT | 创建者ID |
| name | VARCHAR(50) |考试名 |
| isPublish | BOOLEAN | 是否发布 |
| isDelete | BOOLEAN | 是否删除 |
| content | TEXT |试卷内容 JSON |
| create_time | DATETIME | 创建时间 |
| update_time | DATETIME | 更新时间 |

改下 prisma 的 shema 文件：

```
model User {
  id  Int @id @default(autoincrement())
  username String @db.VarChar(50) @unique
  password String @db.VarChar(50)
  email String @db.VarChar(50)
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt

  exams  Exam[]
}

model Exam {
  id  Int @id @default(autoincrement())
  name String @db.VarChar(50)
  isPublish Boolean @default(false)
  isDelete Boolean @default(false)
  content String @db.Text 
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt

  createUserId Int
  createUser     User  @relation(fields: [createUserId], references: [id])
}
```
除了基本字段外，还要加一个多对一的关联：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/12d00bb389e2.png)

生成这个表：

```
npx prisma migrate dev --name exam
```
![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/82107ac38150.png)

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/105ace5ba906.png)

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7cadd162e375.png)

然后实现下 exam 的几个接口：

| 接口路径 | 请求方式 | 描述 |
| -- |-- |-- |
| /exam/add | POST | 创建考试 |
| /exam/delete | DELETE | 删除考试|
| /exam/list | GET | 考试列表 |
| /exam/save | POST | 保存试卷内容 |
| /exam/publish | GET | 发布考试 |

在 exam 微服务改一下 ExamController：

```javascript
@Post('add')
@RequireLogin()
async add(@Body() dto: ExamAddDto, @UserInfo('userId') userId: number) {
    return this.examService.add(dto, userId);
}
```
创建考试需要关联用户，所以需要登录，拿到用户信息。

加一下全局的 Guard：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/631a0e203c84.png)
```javascript
{
  provide: APP_Guard,
  useClass: AuthGuard
}
```

创建用到的 dto：

dto/exam-add.dto.ts
```javascript
import { IsNotEmpty } from "class-validator";

export class ExamAddDto {
    @IsNotEmpty({ message: '考试名不能为空' })
    name: string;
}
```
还有  service：

引入 PrismaModule：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c3e961ef7d62.png)

注入 PrismaService，实现关联插入：
```javascript
import { Inject, Injectable } from '@nestjs/common';
import { ExamAddDto } from './dto/exam-add.dto';
import { PrismaService } from '@app/prisma';

@Injectable()
export class ExamService {
  getHello(): string {
    return 'Hello World!';
  }

  @Inject(PrismaService)
  private prismaService: PrismaService;

  async add(dto: ExamAddDto, userId: number) {

    return this.prismaService.exam.create({
      data: {
        name: dto.name,
        content: '',
        createUser: {
          connect: {
              id: userId
          }
        }
      }
    })
  }
}

```
然后在 main.ts 加一下 ValidationPipe：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8b381f053369.png)

```javascript
app.useGlobalPipes(new ValidationPipe({ transform: true }));
```
把 user 和 exam 服务跑起来：
```
npm run start:dev user
npm run start:dev exam
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b2fa4103af61.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55e19f7fe0cd.png)

它会提示你找不到 JwtService：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/465850dbf02a.png)

我们之前在 UserModule 用的时候是引入了 JwtModule 所以才能找到：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/412588148a7b.png)

但每个微服务都引入 JwtService 明显不好。

在 CommonModule 里引入就好了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c352c5214fe2.png)

```javascript
JwtModule.registerAsync({
  global: true,
  useFactory() {
    return {
      secret: 'guang',
      signOptions: {
        expiresIn: '30m' // 默认 30 分钟
      }
    }
  }
}),
```
然后在 UserModule、ExamModule 里引入 CommonModule，自然也就引入了 JwtModule：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fff7b1a0ce0d.png)

再跑下：


![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cd3063421942.png)

带上 token 访问接口。

可以看到创建成功了。

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cf75a8b148f3.png)

然后我们再实现下 list 接口：

添加一个路由：

```javascript
@Get('list')
@RequireLogin()
async list(@UserInfo('userId') userId: number) {
    return this.examService.list(userId);
}
```

在 service 实现 list 方法：

```javascript
async list(userId: number) {
    return this.prismaService.exam.findMany({
      where: {
        createUserId: userId
      }
    })
}
```
查询当前用户的所有考试。

测试下：

先创建一个：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2df9eea047f9.png)

查询下：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/71200560a979.png)

没啥问题。

然后继续实现删除考试接口：

```javascript
@Delete('delete/:id')
@RequireLogin()
async del(@UserInfo('userId') userId: number, @Param('id') id: string) {
  return this.examService.delete(userId, +id);
}
```
在 service 里实现下：

```javascript
async delete(userId: number, id: number) {
    return this.prismaService.exam.update({
      where: {
        id,
        createUserId: userId
      },
      data: {
        isDelete: true
      }
    })
  }
```
因为有回收站功能，所以这里只做逻辑删除，把 isDelete 设置为 true 就行。

试下效果：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/51321a2c237f.png)



![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/88083a99c05b.png)

当然，这个 list 接口也得改下：

```javascript
@Get('list')
@RequireLogin()
async list(@UserInfo('userId') userId: number, @Query('bin') bin: string) {
    return this.examService.list(userId, bin);
}
```
只要传了 bin 参数，就查询回收站中的，否则返回正常的列表。

```javascript
async list(userId: number, bin: string) {
    return this.prismaService.exam.findMany({
      where: bin !== undefined ? {
        createUserId: userId,
        isDelete: true
      } : {
        createUserId: userId,
      }
    })
}
```

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eb49e72c1bf6.png)

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b56c2fc3e435.png)


接下里实现保存考试内容的功能。

| 接口路径 | 请求方式 | 描述 |
| -- |-- |-- |
| /exam/add | POST | 创建考试 |
| /exam/delete | DELETE | 删除考试|
| /exam/list | GET | 考试列表 |
| /exam/save | POST | 保存试卷内容 |
| /exam/publish | GET | 发布考试 |

这个就是修改 content：

添加路由：

```javascript
@Post('save')
@RequireLogin()
async save(@Body() dto: ExamSaveDto) {
    return this.examService.save(dto);
}
```
创建 dto：
dto/exam-save.dto.ts

```javascript
import { IsNotEmpty, IsString } from "class-validator";

export class ExamSaveDto {
    @IsNotEmpty({ message: '考试 id 不能为空' })
    id: number;

    @IsString()
    content: string;
}
```
实现下 service：

```javascript
async save(dto: ExamSaveDto) {
    return this.prismaService.exam.update({
      where: {
        id: dto.id
      },
      data: {
        content: dto.content
      }
    })
}
```

测试下：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/87e12bcc876f.png)

保存成功。

最后再来实现发布方法：

这个其实也是改个字段，把 exam 的 isPublish 改为 true 就好了：

```javascript
@Get('publish/:id')
@RequireLogin()
async publish(@UserInfo('userId') userId: number, @Param('id') id: string) {
    return this.examService.publish(userId, +id);
}
```

```javascript
async publish(userId: number, id: number) {
    return this.prismaService.exam.update({
      where: {
        id,
        createUserId: userId
      },
      data: {
        isPublish: true
      }
    })
}
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/20091984a3d6.png)

这样，考试微服务的接口就完成了。

代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/exam-system)。

## 总结

这节我们实现了考试微服务的接口，包括考试列表、考试创建、考试删除、发布考试、保存试卷内容的接口。

当然，具体试卷内容的 JSON 格式还没定，等写前端代码的时候再说。
