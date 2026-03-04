---
title: "Prisma Client 多表 CRUD 的全部 api"
date: 2025-05-30
draft: false
description: ""
tags: ["nestjs", "prisma"]
categories: ["NestJS"]
series: ["Prisma"]
series_order: 5
---

上节我们过了一遍 Prisma Client 做 CRUD 的 api，但那只是针对单表的，这节我们把涉及到多表的 CRUD 的 api 过一遍。

创建个新项目：

```bash
mkdir prisma-client-api2 
cd prisma-client-api2 
npm init -y
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2133d2d825b4.webp)

进入项目，执行 init 命令：

```csharp
npx prisma init
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bd3ff34e3865.webp)

生成了 .env 和 schema 文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/51f59c562f1c.webp)

然后改下 .env 文件的数据库连接信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/82d4f6e76f4f.webp)

```ini
DATABASE_URL="mysql://root:guang@localhost:3306/prisma_test"
```

改一下 datasource 的 provider 为 mysql，并且添加 model

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c4681d6fee70.webp)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "mysql"
  url      = env("DATABASE_URL")
}

model Department {
  id        Int    @id @default(autoincrement())
  name      String  @db.VarChar(20)
  createTime DateTime @default(now())
  updateTime DateTime @updatedAt
  employees     Employee[]
}

model Employee {
  id         Int       @id @default(autoincrement())
  name      String     @db.VarChar(20)
  phone     String     @db.VarChar(30)  

  deaprtmentId Int
  department     Department      @relation(fields: [deaprtmentId], references: [id])
}
```

之后执行 migrate reset 重置下：

```perl
npx prisma migrate reset
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/30e57195fef5.webp)

然后用 migrate dev 创建新的迁移：

```css
npx prisma migrate dev --name aaa
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9c62c6902b3f.webp)

生成了 client 代码，还有 sql 文件。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9fac284c4d85.webp)

数据库中也多了这 2 个表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7249585595b4.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ea8f073ea825.webp)

然后来写下 client 的 crud 代码。

首先安装 ts、ts-node 包：

```sql
npm install typescript ts-node @types/node --save-dev
```

创建 tsconfig.json

```csharp
npx tsc --init
```

把注释删掉，保留这些配置就行：

```json
{
  "compilerOptions": {
    "target": "es2016",
    "module": "commonjs",
    "types": ["node"],
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```

创建 src/index.ts

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
}

main();
```

然后分别做下 CRUD。

首先是插入数据：

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

async function test1() {
   await prisma.department.create({
        data: {
            name: '技术部',
            employees: {
                create: [
                    {
                        name: '小张',
                        phone: '13333333333'
                    },
                    {
                        name: '小李',
                        phone: '13222222222'
                    }
                ]
            }
        }
   })
}

test1();
```

插入关联 model 的数据的时候，也是用 create 指定：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/142fd42e882d.webp)

测试下：

```bash
npx ts-node ./src/index.ts
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/dc0e029616ad.webp)

在 mysql workbench 里看下结果：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3e498f0da28f.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ef3c10350354.webp)

确实，数据都被正确插入了。

当然，你也可以用这种写法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/110401d4e867.webp)

```javascript
async function test2() {
    await prisma.department.create({
         data: {
             name: '技术部',
             employees: {
                 createMany: {
                    data: [
                        {
                            name: '小王',
                            phone: '13333333333'
                        },
                        {
                            name: '小周',
                            phone: '13222222222'
                        }
                    ],

                 }
             }
         }
    })
}

test2();
```

跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/97a8ff87ee5d.webp)

效果一样：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d17daf2b7545.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9501d9c66e72.webp)

那如何关联查询呢？

可以这样写：

```javascript
async function test3() {
    const res1 = await prisma.department.findUnique({
        where: {
            id: 1
        },
        include: {
            employees: true
        }
    });
    console.log(res1);

    const res2 = await prisma.department.findUnique({
        where: {
            id: 1
        },
        include: {
            employees: {
                where: {
                    name: '小张'
                },
                select: {
                    name: true
                }
            }
        }
    });
    console.log(res2);

    const res3 = await prisma.department.findUnique({
        where: {
            id: 1
        }
    }).employees();
    console.log(res3);
}

test3();
```

查询 department 的时候，通过 include 指定关联查询出 employees。

include 还可以指定 where 等查询的参数，进一步过滤。

此外，你也可以在查出 department 后调用 empolyees() 方法来查询。

可以看到，都能正确查出关联数据：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8469cc1e4afd.webp)

再就是关联更新：

```javascript
async function test4() {
    const res1 = await prisma.department.update({
        where: {
            id: 1
        },
        data: {
            name: '销售部',
            employees: {
                create: [
                    {
                        name: '小刘',
                        phone: '13266666666'
                    }
                ]
            }
        }
    });
    console.log(res1);
}

test4();
```

比如我在更新 department 的时候关联插入了一条 employee 的记录。

跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/317c002455e5.webp)

在 mysql workbench 里可以看到，id 为 1 的 department 更新了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8a1cb1d65596.webp)

关联插入了一条 employee 的记录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/629fc528a8bc.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4a1d81740ee0.webp)

更新 department 的时候，除了可以插入 empolyee 的数据，也可以和别的 empolyee 建立关联。

比如 id 为 4 的 empolyee：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b5df0819b418.webp)

现在他关联的是 id 为 2 的 department。

我们 update 的时候使用 connect 和它关联：

```javascript
async function test5() {
    const res1 = await prisma.department.update({
        where: {
            id: 1
        },
        data: {
            name: '销售部',
            employees: {
                connect: [
                    {
                        id: 4
                    }
                ]
            }
        }
    });
    console.log(res1);
}
test5();
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/63881b4f6d35.webp)

跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3a31b85d420a.webp)

刷新可以看到，id 为 4 的 employee 关联的 department 就变了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/85459c60b20a.webp)

如果是某个 id 的数据存在就 connect，不存在就 create 呢？

可以这样写：

```javascript
async function test6() {
    const res1 = await prisma.department.update({
        where: {
            id: 1
        },
        data: {
            name: '销售部',
            employees: {
                connectOrCreate: {
                    where: {
                        id: 6
                    },
                    create: {
                        id: 6,
                        name: '小张',
                        phone: '13256665555'
                    }
                }
            }
        }
    });
    console.log(res1);
}
test6();
```

第一次跑，执行的是 insert：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/026b4faca8ba.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/83ff0deb2d57.webp)

第二次跑，就是 update 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fbf5f7534eb0.webp)

也就是说，update 的时候可以通过 create、connect、connectOrCreate 来插入新的关联 model 的记录或者关联已有的记录。

当然，create 的时候也可以这样：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/88ea1c106e2b.webp)

效果一样，就不一个个测试了。

再就是删除：

如果我们想删除 id 为 1 的 department 的所有 empolyee，可以这样写：

```javascript
async function test7() {
    await prisma.employee.deleteMany({
        where: {
            department: {
                id: 1
            }
        },
    });
}
test7();
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/50d5dfa8d7f0.webp)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a3f355bddc07.webp)

这就是多个 model 关联时的 CRUD。

此外，Prisma 还可以直接执行 sql：

```javascript
async function test8() {
    await prisma.$executeRaw`TRUNCATE TABLE Employee`;

    const res = await prisma.$queryRaw`select * from Department`;
    console.log(res);
}
test8();
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ee31cb758381.webp)

这样，当上面的 api 都不能满足需求的时候，你就可以直接执行 sql。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/prisma-client-api2)

## 总结

这节我们过了一遍多 model 关联的时候涉及到多个表的 CRUD 方法。

还是 findXxx、updateXxx、deleteXxx、createXxx 那些方法，只不过查询的时候可以通过 include 包含关联记录，新增修改的时候可以通过 create、connect、connectOrCreate 来关联或者插入记录。

此外，你还可以直接执行 sql。

通过这些 api，我们就能完成各种 CRUD 需求了。