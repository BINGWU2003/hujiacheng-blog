---
title: "TypeORM 一对一的映射和关联 CRUD"
date: 2025-02-24
draft: false
description: ""
tags: ["nestjs", "typeorm"]
categories: ["NestJS"]
series: ["MySQL 与 TypeORM"]
series_order: 11
---

在数据库里，表和表之间是存在关系的。

比如用户和身份证是一对一的关系，部门和员工是一对多的关系，文章和标签是多对多的关系。

我们是通过外键来存储这种关系的，多对多的话还要建立中间表。

TypeORM 是把表、字段、表和表的关系映射成 Entity 的 class、属性、Entity 之间的关系，那如何映射这种一对一、一对多、多对多的关系呢？

我们来试一下。

这次创建个新的 database 来用：

```sql
create database typeorm_test;
```

执行它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5c701df5ac90.png)

点击刷新，就可以看到这个新的 database 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/30efeb21da44.png)

我们用 typeorm 连上它来自动创建表。

```sql
npx typeorm@latest init --name typeorm-relation-mapping --database mysql
```

创建个 typeorm 项目。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f0b53082a2c1.png)

修改 DataSource 的配置：

```javascript
import "reflect-metadata"
import { DataSource } from "typeorm"
import { User } from "./entity/User"

export const AppDataSource = new DataSource({
    type: "mysql",
    host: "localhost",
    port: 3306,
    username: "root",
    password: "guang",
    database: "typeorm_test",
    synchronize: true,
    logging: true,
    entities: [User],
    migrations: [],
    subscribers: [],
    poolSize: 10,
    connectorPackage: 'mysql2',
    extra: {
        authPlugin: 'sha256_password',
    }
})
```

安装驱动包  mysql2

    npm install --save mysql2

然后跑起来：

    npm run start

可以看到，它生成了建表 sql 和插入数据的 sql：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/10a52af3c656.png)

点击刷新，在 workbench 里也可以看到这个新建的表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/639df18069bc.png)

点击新建 sql，执行 select，也是可以看到插入的数据的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2f5d82352bc2.png)

然后我们再创建个身份证表。

通过 typeorm entity:create 命令创建：

```sql
npx typeorm entity:create src/entity/IdCard
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/891dc4cd0131.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c9f1c20adf81.png)

填入属性和映射信息：

```javascript
import { Column, Entity, PrimaryGeneratedColumn } from "typeorm"

@Entity({
    name: 'id_card'
})
export class IdCard {
    @PrimaryGeneratedColumn()
    id: number

    @Column({
        length: 50,
        comment: '身份证号'
    })
    cardName: string
}
```

在 DataSource 的 entities 里引入下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/36a54e73fce3.png)

重新 npm run start：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2eff6b4df004.png)

可以看到生成了这条建表 sql。

workbench 里也可以看到这个表：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/746ffe9530db.png)

现在 user 和 id\_card 表都有了，怎么让它们建立一对一的关联呢？

先把这两个表删除：

```sql
drop table id_card,user;
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/73b468d6e0f6.gif)

在 IdCard 的 Entity 添加一个 user 列，指定它和 User 是 @OneToTone 一对一的关系。

还要指定 @JoinColum 也就是外键列在 IdCard 对应的表里维护：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a2bff3b347ba.png)

重新 npm run start：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/77bd46bcf477.png)

仔细看生成的这 3 条 sql 语句。

前两个是建表 sql，创建 id\_card 和 user 表。

最后一个是给修改 id\_card 表，给 user\_id 列添加一个外建约束，引用 user 表的 id 列。

在 workbench 里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4270129ca425.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/56146a1fcf6c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/34e16931ff6d.png)

生成的表都是对的。

但是这个级联关系还是默认的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6304edacbbd5.png)

如果我们想设置 CASCADE 应该怎么做呢？

在第二个参数指定：

![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0fa870375791.png)

删除这两个表：

```sql
drop table id_card,user;
```

重新 npm run start：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/08d200ab74c2.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f1052da7d870.png)

这样就设置了级联删除和级联更新。

我们再来试下增删改查：

```javascript
import { AppDataSource } from "./data-source"
import { IdCard } from "./entity/IdCard"
import { User } from "./entity/User"

AppDataSource.initialize().then(async () => {

    const user = new User();
    user.firstName = 'guang';
    user.lastName = 'guang';
    user.age = 20;
    
    const idCard = new IdCard();
    idCard.cardName = '1111111';
    idCard.user = user;
    
    await AppDataSource.manager.save(user);
    await AppDataSource.manager.save(idCard);

}).catch(error => console.log(error))
```

创建 user 和 idCard 对象，设置 idCard.user 为 user，也就是建立关联。

然后先保存 user，再保存 idCard。

跑 npm run start，生成的 sql 如下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/98f613a06511.png)

可以看到后面插入 id\_card 的时候，已经有 userId 可以填入了。

数据都插入成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1be607e9704c.gif)

但是我还要分别保存 user 和 idCard，能不能自动按照关联关系来保存呢？

可以的，在 @OneToOne 那里指定 cascade 为 true：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1d22a81220ef.png)

这个 cascade 不是数据库的那个级联，而是告诉 typeorm 当你增删改一个 Entity 的时候，是否级联增删改它关联的 Entity。

这样我们就不用自己保存 user 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/13c3c49f3c2c.png)

重新 npm run start：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/21dc6b16a0e8.png)

可以看到它同样是先插入了 user，再插入了 id\_card，并且设置了正确的 userId。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aa40731ba396.gif)

保存了之后，怎么查出来呢？

我们用 find 来试下：

```javascript
const ics = await AppDataSource.manager.find(IdCard);
console.log(ics);
```

跑下 npm run start：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0eee23ca818f.png)

可以看到 idCard 查出来了，但是关联的 user 没查出来。

只需要声明下 relations 关联查询就好了：

```javascript
const ics = await AppDataSource.manager.find(IdCard, {
    relations: {
        user: true
    }
});
console.log(ics);
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/34498aa22f9e.png)

再跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e5b6f1969baa.png)

现在 idCard 关联的 user 就被查出来了。

当然，你也可以用 query builder 的方式来查询：

```javascript
const ics = await AppDataSource.manager.getRepository(IdCard)
    .createQueryBuilder("ic")
    .leftJoinAndSelect("ic.user", "u")
    .getMany();

console.log(ics);
```

先 getRepository 拿到操作 IdCard 的 Repository 对象。

再创建 queryBuilder 来连接查询，给 idCard 起个别名 ic，然后连接的是 ic.user，起个别名为 u：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b60fe9b8a478.png)

或者也可以直接用 EntityManager 创建 queryBuilder 来连接查询：

```javascript
const ics = await AppDataSource.manager.createQueryBuilder(IdCard, "ic")
    .leftJoinAndSelect("ic.user", "u")
    .getMany();
console.log(ics);
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9d6fb60eaa55.png)

再来试下修改：

现在数据是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8aab85d9cb86.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/db145abe3080.png)

我们给它加上 id 再 save：

```javascript
const user = new User();
user.id = 1;
user.firstName = 'guang1111';
user.lastName = 'guang1111';
user.age = 20;

const idCard = new IdCard();
idCard.id = 1;
idCard.cardName = '22222';
idCard.user = user;

await AppDataSource.manager.save(idCard);
```

这样数据就被修改了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8e34c373f0bc.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a8795e68dddc.png)

看下生成的 sql：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/150418edf2e6.png)

在一个事务内，执行了两条 update 的 sql。

最后再试试删除。

因为设置了外键的 onDelete 是 cascade，所以只要删除了 user，那关联的 idCard 就会跟着被删除。

```javascript
await AppDataSource.manager.delete(User, 1)
```

如果不是没有这种级联删除，就需要手动删了：

```javascript
const idCard = await AppDataSource.manager.findOne(IdCard, {
    where: {
        id: 1
    },
    relations: {
        user: true
    }
})
await AppDataSource.manager.delete(User, idCard.user.id)
await AppDataSource.manager.delete(IdCard, idCard.id)
```

不过现在我们只是在 idCard 里访问 user，如果想在 user 里访问 idCard 呢？

同样需要加一个 @OneToOne 的装饰器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6b0e160837a7.png)

不过需要有第二个参数。

因为如果是维持外键的那个表，也就是有 @JoinColumn 的那个 Entity，它是可以根据外键关联查到另一方的。

但是没有外键的表怎么查到另一方呢？

所以这里通过第二个参数告诉 typeorm，外键是另一个 Entity 的哪个属性。

我们查一下试试：

```javascript
const user = await AppDataSource.manager.find(User, {
    relations: {
        idCard: true
    }
});
console.log(user);
```

可以看到，同样关联查询成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c896d76ad11a.png)

这就是一对一关系的映射和增删改查。

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/typeorm-relation-mapping)。

## 总结

TypeORM 里一对一关系的映射通过 @OneToOne 装饰器来声明，维持外键列的 Entity 添加 @JoinColumn 装饰器。

如果是非外键列的 Entity，想要关联查询另一个 Entity，则需要通过第二个参数指定外键列是另一个 Entity 的哪个属性。

可以通过 @OneToOne 装饰器的 onDelete、onUpdate 参数设置级联删除和更新的方式，比如 CASCADE、SET NULL 等。

还可以设置 cascade，也就是 save 的时候会自动级联相关 Entity 的 save。

增删改分别通过 save 和 delete 方法，查询可以通过 find 也可以通过 queryBuilder，不过要 find 的时候要指定 relations 才会关联查询。

这就是 TypeORM 里一对一的映射和增删改查，下节我们继续学习一对多的映射。
