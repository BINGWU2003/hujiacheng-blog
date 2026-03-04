---
title: "TypeORM 如何保存任意层级的关系？"
date: 2025-02-28
draft: false
description: ""
tags: ["nestjs", "typeorm"]
categories: ["NestJS"]
series: ["MySQL 与 TypeORM"]
series_order: 15
---

我们经常会见到一些多级分类的场景：

比如京东的商品分类：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d88c0392eab4.png)

新闻网站的新闻分类：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3baa32eed9f7.png)

这种多层级的数据怎么存储呢？

有同学会说，很简单啊，这不就是一对多么，二级分类就用两个表，三级分类就用三个表。

这样是可以，但是都是分类，表结构是一样的，分到多个表里是不是有点冗余。

更重要的是，如果层级关系经常调整呢？

比如有的时候会变成二级分类，有的时候会更多级分类呢？

这时候用普通的多表之间的一对多就不行了。

一般这种多级分类的业务，我们都会在一个表里存储，然后通过 parentId 进行子关联来实现。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/586546405b05.png)

在 TypeORM 里也对这种场景做了支持。

我们新建个项目：

```
nest new typeorm-tree-entity-test
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/937090147bd6.png)

进入项目目录，创建一个 CRUD 模块：

```
nest g resource city --no-spec
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/131537d21c0c.png)

然后安装 TypeORM 的包：
```bash
npm install --save @nestjs/typeorm typeorm mysql2
```
在 app.module.ts 引入下 TypeOrmModule：

```javascript
import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { CityModule } from './city/city.module';
import { TypeOrmModule } from '@nestjs/typeorm';

@Module({
  imports: [
    CityModule,
    TypeOrmModule.forRoot({
      type: "mysql",
      host: "localhost",
      port: 3306,
      username: "root",
      password: "guang",
      database: "tree_test",
      synchronize: true,
      logging: true,
      entities: [City],
      poolSize: 10,
      connectorPackage: 'mysql2',
      extra: {
          authPlugin: 'sha256_password',
      }
    })
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
```
在 mysql workbench 里创建这个 database：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/23e9b12b5704.png)

指定字符集为 utf8mb4，点击 apply。

然后改下 city.entity.ts

```javascript
import { Column, CreateDateColumn, Entity, PrimaryGeneratedColumn, Tree, TreeChildren, TreeParent, UpdateDateColumn } from "typeorm";

@Entity()
@Tree('closure-table')
export class City {
    @PrimaryGeneratedColumn()
    id: number;

    @Column({ default: 0 })
    status: number;

    @CreateDateColumn()
    createDate: Date;

    @UpdateDateColumn()
    updateDate: Date;
    
    @Column()
    name: string;

    @TreeChildren()
    children: City[];

    @TreeParent()
    parent: City;
}
```
把服务跑起来：

```
npm run start:dev
```
可以看到，自动创建了 2 个表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55c99466b8bf.png)

我们在 mysql workbench 里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/85308868f5c1.png)

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f5f3a9e2fe0c47b6a2fc61659598d5d1~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1518&h=660&s=184583&e=png&b=f2f0ef)

可以看到 parentId 引用了自身的 id。

并且还有个 city_closure 表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/25b17160363e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f17a337e719f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ce6bee4f1081.png)

两个外键都引用了 city 表的 id。

先不着急解释为什么是这样的，我们插入一些数据试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c746f7c9eefd.png)

在 CityService 的 findAll 方法里插入数据，然后再查出来。

```javascript
@InjectEntityManager()
entityManager: EntityManager;

async findAll() {
    const city = new City();
    city.name = '华北';
    await this.entityManager.save(city);

    const cityChild = new City()
    cityChild.name = '山东'
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '华北'
      }
    });
    if(parent){
      cityChild.parent = parent
    }
    await this.entityManager.save(City, cityChild)

    return this.entityManager.getTreeRepository(City).findTrees();
}
```
这里创建了两个 city 的 entity，第二个的 parent 指定为第一个。

用 save 保存。

然后再 getTreeRepository 调用 findTrees 把数据查出来。

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0ec3c902b25e.png)

可以看到数据插入成功了，并且返回了树形结构的结果。

在 mysql workbench 里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bf2dc5c77d61.png)

在 city 表里保存着 city 记录之间的父子关系，通过 parentId 关联。

![](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0b8848e1726f4c9798b2881bd214eade~tplv-k3u1fbpfcp-jj-mark:0:0:0:0:q75.image#?w=1074&h=346&s=94811&e=png&b=ebe7e6)

在 city_closure 表里记录了也记录了父子关系。

把插入数据的代码注释掉：


![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b96d1799925d.png)

重新插入数据：

```javascript
async findAll() {
    const city = new City();
    city.name = '华南';
    await this.entityManager.save(city);

    const cityChild1 = new City()
    cityChild1.name = '云南'
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '华南'
      }
    });
    if(parent){
      cityChild1.parent = parent
    }
    await this.entityManager.save(City, cityChild1)

    const cityChild2 = new City()
    cityChild2.name = '昆明'

    const parent2 = await this.entityManager.findOne(City, {
      where: {
        name: '云南'
      }
    });
    if(parent){
      cityChild2.parent = parent2
    }
    await this.entityManager.save(City, cityChild2)

return this.entityManager.getTreeRepository(City).findTrees();
}
```

跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cdee408404e5.png)

可以看到，二层和三层的关系都可以正常的存储和查询。

把插入数据的代码注释掉，我们测试下其他方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9940992181ec.png)

findRoots 查询的是所有根节点：

```javascript
async findAll() {
    return this.entityManager.getTreeRepository(City).findRoots()
}
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/924b043709cf.png)

```javascript
async findAll() {
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '云南'
      }
    });
    return this.entityManager.getTreeRepository(City).findDescendantsTree(parent)
}
```

findDescendantsTree 是查询某个节点的所有后代节点。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/39c5725e14f2.png)

```javascript
async findAll() {
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '云南'
      }
    });
    return this.entityManager.getTreeRepository(City).findAncestorsTree(parent)
}
```

findAncestorsTree 是查询某个节点的所有祖先节点。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/890e84504c3e.png)

这里换成 findAncestors、findDescendants 就是用扁平结构返回：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f6a264fa3e78.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f6acb1102baa.png)

把 findTrees 换成 find 也是会返回扁平的结构：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/22175a86e1f1.png)

还可以调用 countAncestors 和 countDescendants 来计数：

```javascript
async findAll() {
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '云南'
      }
    });
    return this.entityManager.getTreeRepository(City).countAncestors(parent)
}
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/afec0a6c609b.png)

这些 api 都是很实用的。

回过头来，再看下 @Tree 的 entity：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1cead031def5.png)

通过 @TreeChildren 声明的属性里存储着它的 children 节点，通过 @TreeParent 声明的属性里存储着它的 parent 节点。

并且这个 entity 要用 @Tree 声明。

参数可以指定 4 中存储模式：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5f4e4c9a2a4a.png)

我们一般都是用 closure-table，或者 materialized-path。

其余两种有点问题：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/766bec11a41b.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0a31d2102752.png)

把两个表删掉：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f15f21f213b3.png)

改成 materialized-path 重新跑：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4010a3ad3a2b.png)

可以看到，现在只生成了一个表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/162b89658ce5.png)

只是这个表多了一个 mpath 字段。

我们添加点数据：

```javascript
async findAll() {
    const city = new City();
    city.name = '华北';
    await this.entityManager.save(city);

    const cityChild = new City()
    cityChild.name = '山东'
    const parent = await this.entityManager.findOne(City, {
      where: {
        name: '华北'
      }
    });
    if(parent){
      cityChild.parent = parent
    }
    await this.entityManager.save(City, cityChild)

    return this.entityManager.getTreeRepository(City).findTrees();
}
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/607269b171a4.png)

可以看到，它通过 mpath 路径存储了当前节点的访问路径，从而实现了父子关系的记录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e95f56ac0b60.png)

其实这些存储细节我们不用关心，不管是 closure-table 用两个表存储也好，或者 materialized-path 用一个表多加一个 mpath 字段存储也好，都能完成同样的功能。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/typeorm-tree-entity-test)。

## 总结

这节我们基于 TyepORM 实现了任意层级的关系的存储。

在 entity 上使用 @Tree 标识，然后通过 @TreeParent 和 @TreeChildren 标识存储父子节点的属性。

之后可以用 getTreeRepository 的 find、findTrees、findRoots、findAncestorsTree、findAncestors、findDescendantsTree、findDescendants、countDescendants、countAncestors 等 api 来实现各种关系的查询。

存储方式可以指定 closure-table 或者 materialized-path，这两种方式一个用单表存储，一个用两个表，但实现的效果是一样的。

以后遇到任意层级的数据的存储，就是用 Tree Entity 吧。
