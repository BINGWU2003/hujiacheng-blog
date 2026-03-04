---
title: "Prisma 的全部命令"
date: 2025-05-27
draft: false
description: ""
tags: ["nestjs", "prisma"]
categories: ["NestJS"]
series: ["Prisma"]
series_order: 2
---

上节我们入门了 prisma，定义了 model 和表的映射，并且做了 CRUD。

这节来过一遍 Prisma 的全部命令。

```
npx prisma -h
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/328fb4d626a9.png)

有这些：

- init：创建 schema 文件

- generate： 根据 shcema 文件生成 client 代码

- db：同步数据库和 schema

- migrate：生成数据表结构更新的 sql 文件

- studio：用于 CRUD 的图形化界面

- validate：检查 schema 文件的语法错误

- format：格式化 schema 文件

- version：版本信息


我们一个个来过一遍。

先创建个新项目：

```
mkdir prisma-all-command
cd prisma-all-command
npm init -y
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9329ec6753d9.png)

全局安装 prisma，这个是命令行工具的包：

```
npm install -g prisma
```
## prisma init
首先来试一下 init 命令：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/79215f7cea35.png)

这个就是创建 schema 文件的，可以指定连接的 database，或者指定 url。

我们试一下：

```
prisma init
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b680c7e10e8e.png)

执行 init 命令后生成了 prisma/shcema.prisma 和 .env 文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/38430c567c95.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5a19ebca6cdb.png)

包含了 db provider，也就是连接的数据库，以及连接的 url：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ae35ae78a5c9.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/436d3ac59205.png)

删掉这俩文件，重新生成。

```
prisma init --datasource-provider mysql
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f322349d2ac4.png)

这样生成的就是连接 mysql 的 provider 和 url 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/286452069bba.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1f1cc0f0363a.png)

其实就是改这两处的字符串，prisma init 之后自己改也行。

再删掉这俩文件，我们重新生成。

```
prisma init --url mysql://root:guang@localhost:3306/prisma_test
```
这次指定连接字符串。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/92f590929c52.png)

可以看到，provider 会根据你指定的 url 来识别，并且 .env 里的 url 就是我们传入的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/067d35d016ea.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/74d3c57ef52b.png)

## prisma db

创建完 schema 文件，如何定义 model 呢？

其实 init 命令的打印提示了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/31eaab42fcc5.png)

你可以执行 prisma db pull 把数据库里的表同步到 schema 文件。

我们试一下：

```
prisma db pull
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9ff37c150631.png)

提示发现了 2 个 model 并写入了 schema 文件。

现在连接的 prisma_test 数据库里是有这两个表的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b6c12ec6abe7.png)

生成的 model 定义是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7d84c3662730.png)

其中，@@index 是定义索引，这里定义了 authorId 的外键索引。

此外，db 命令还有别的功能：

```
prisma db -h
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7f56ffd74e15.png)

试下 prisma db push 命令：

首先在 mysql workbench 里把这两个表删掉：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/836196b26427.png)

然后执行 db push：

```
prisma db push
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/59c903439e4c.png)

提示同步到了 database，并且生成了 client 代码。

在 mysql workbench 里可以看到新的表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e385209e99cb.png)

seed 命令是执行脚本插入初始数据到数据库。

我们用 ts 来写，先安装相关依赖：

```
npm install typescript ts-node @types/node --save-dev
```
创建 tsconfig.json

```
npx tsc --init
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f1e8aeb2e965.png)

然后写下初始化脚本 prisma/seed.ts

```javascript
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient({
  log: [
    {
      emit: 'stdout',
      level: 'query'
    },
  ],
});

async function main() {
    const user = await prisma.user.create({
        data: {
            name: '东东东',
            email: 'dongdong@dong.com',
            Post: {
                create: [
                    {
                        title: 'aaa',
                        content: 'aaaa'
                    },
                    {
                        title: 'bbb',
                        content: 'bbbb'
                    }
                ]
            },
        },
    })
    console.log(user)
}

main();
```
在 package.json 添加 seed 命令的配置：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1eed451fd827.png)

```json
"prisma": {
    "seed": "npx ts-node prisma/seed.ts"
},
```
然后执行 seed：

```
prisma db seed
```

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bff079c4dc4f.png)

在 mysql workbench 里可以看到数据被正确插入了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0d9d642c4ff2.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ed4775444993.png)

其实 seed 命令就是把跑脚本的过程封装了一下，和直接用 ts-node 跑没啥区别。

然后是 prisma db execute，这个是用来执行 sql 的。

比如我写一个 prisma/test.sql 的文件：

```sql
delete from Post WHERE id = 2;
```
然后执行 execute：

```
prisma db execute --file prisma/test.sql --schema prisma/schema.prisma
```

这里 --file 就是指定 sql 文件的。

而 --schema 指定 schema 文件，主要是从中拿到数据库连接信息。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4f7cabd144d8.png)

然后去 mysql workbench 里看一下，确实 id 为 2 的 Post 数据没有了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/abf9881a55ee.png)

这就是 db 的 4 个命令。

## prisma migrate

mirgrate 是迁移的意思，在这里是指表的结构变化。

prisma migrate 有这些子命令：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dab087c8dcc5.png)

我们分别来看一下。

首先是 prisma migrate dev。

这个我们前面用过，它会根据 schema 的变化生成 sql 文件，并执行这个 sql，还会生成 client 代码。

```
prisma migrate dev --name init
```

因为之前创建过表，并且有数据。

它会提示是否要 reset：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2509c14dc7a2.png)

选择是，会应用这次 mirgration，生成 sql 文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d151a5610a5c.png)

并且会生成 client 代码，而且会自动执行 prisma db seed，插入初始化数据。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b36336c9435e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7ecf42736677.png)

这样就既创建了表，又插入了初始数据，还生成了 client。

我们开发的时候经常用这个命令。

在 prisma/migrations 下会保存这次 migration 的 sql 文件。

目录名是 “年月日时分秒_名字” 的格式：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dafa75f166a0.png)

那如果我们改一下 schema 文件，再次执行 migrate dev 呢？

在 Post 的 model 定义里添加 tag 字段：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/afb3aec35bcc.png)

```
tag       String  @default("")
```
然后 migrate dev：

```
prisma migrate dev --name age-field
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e3715175aaac.png)

这次生成的 sql 只包含了修改表结构的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fcbc8ac9f3dc.png)

在数据库中有个 _prisma_migrations 表，记录着数据库 migration 的历史：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7278cdcdb27a.png)

如果把这个表删掉，再次 mirgate dev 就会有前面的是否 reset 的提示了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2509c14dc7a2.png)

如果你想手动触发reset，可以用 reset 命令：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3e995f5d0d58.png)

它会清空数据然后执行所有 migration

```
prisma migrate reset
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e24ef9379750.png)

会提示会丢失数据，确认后就会重置表，然后执行所有 migration：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7fa43907483b.png)

还会生成 client 代码，并且执行 prisma db seed 来初始化数据。

## prisma generate

generate 命令只是用来生成 client 代码的，他并不会同步数据库：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/97644249fb8d.png)

只是根据 schema 定义，在 node_modules/@prisma/client 下生成代码，用于 CRUD。

## prisma studio

这个是可以方便 CRUD 数据的图形界面：

```
prisma studio
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b5f1aedd0d8f.png)

选择一个 model：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e9ca2af73875.png)

会展示它的所有数据：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7c3776facf8f.png)

可以编辑记录：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4276d8cf5911.png)

删除记录：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/20be283b0c61.png)

新增记录：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/943520272a62.png)

不过一般我们都用 mysql workbench 来做。

## prisma validate

这个是用来检查 schema 文件是否有语法错误的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/805f4e506e91.png)

比如我写错一个类型，然后执行 validate：

```
prisma validate
```
会提示这里有错误：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5aea03ff0b24.png)

当然，我们安装了 prisma 的插件之后，可以直接在编辑器里看到这个错误：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7a7cb3ca9e83.png)

就和 eslint 差不多。

## prisma format

这个是用来格式化 prisma 文件的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5bcd4eb3aca5.gif)

当然，你安装了 prisma 的 vscode 插件之后，也可以直接用编辑器的 format：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d66a2adf8ab8.gif)

## prisma version

这个就是展示一些版本信息的，比较简单：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3892a0c5ad8f.png)

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/prisma-all-command)

## 总结

这节我们学习了 prisma 的全部命令：

- init：创建 schema 文件

- generate： 根据 shcema 文件生成 client 代码

- db：同步数据库和 schema

- migrate：生成数据表结构更新的 sql 文件

- studio：用于 CRUD 的图形化界面

- validate：检查 schema 文件的语法错误

- format：格式化 schema 文件

- version：版本信息

其中，prisma init、prisma migrate dev 是最常用的。

prisma db pull、prisma db push 也可以方便的用来做 schema 和数据库的同步。

常用的命令也没有几个，多拥几遍就熟了。