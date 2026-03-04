---
title: "Nest 的 Monorepo 和 Library"
date: 2025-05-21
draft: false
description: ""
tags: ["nestjs", "monorepo"]
categories: ["NestJS"]
series: ["微服务"]
series_order: 2
---

上节我们学习微服务时创建了 2 个 Nest 项目，如果微服务多了，可能会创建更多项目。

那问题来了，如果有 10 个微服务，我们就创建 10 个 Nest 项目的 git 仓库么？

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/173df781ccfe.png)

那肯定不行，太难维护了。

这时候我们就需要 monorepo 了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/610eb4a569a8.png)

这样，同一个 git 仓库中存放多个 Nest 项目，外层叫做 workspace。

这样就算是 10 个微服务项目，也能在一个 Git 仓库里管理起来。

Nest 是支持这种 monorepo 的方式的，我们来试试看：

```
nest new monorepo-test
```
创建个 nest 项目

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/266c371b7556.png)

我们添加一个 aaa 的路由：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5fde40ec1154.png)

```javascript
@Get('aaa')
aaa() {
    return 'aaa';
}
```
改下端口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fb7c6e3ec805.png)

然后把它跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8eebde44c714.png)

浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2eb50ca5e7f7.png)

没啥问题。

然后我们再添加一个 nest 项目：

```
nest g app app2
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2cd67a45240.png)

它删除了 src 和 test，并创建了 apps 目录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/42270257546b.png)

这里的 apps/monorepo-test 就是之前的 src、test 代码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a199681d7902.png)

而 apps/app2 就是新创建的 nest 项目，或者叫 nest app。
 
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f09aff8d09db.png)

把之前的服务停掉，重新跑:

```
npm run start:dev
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/11328f458a68.png)

可以看到，跑的还是之前的那个 nest 项目，只不过换成了 webpack 编译。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7c313e176d2.png)

为什么同样都是 nest run start:dev，换成 monorepo 的形式之后，还是跑之前项目呢？

答案在 nest-cli.json 里：

之前 nest-cli.json 是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/755e4217c2bb.png)

现在变成了这样：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f1948abb95a3.png)

projects 下保存着多个 nest 项目的信息，比如根目录、入口文件、src 目录、编译配置文件。

然后 sourceRoot 和 root 分别指向了默认项目的 src 目录和根目录。

所以跑 nest start 的时候，才会依然跑的是之前的项目。

很明显，如果想跑另一个项目，就要这样：

```
npm run start:dev app2
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b92b0ead5bce.png)

比如我在 app2 添加一个 bbb 的路由：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/943bb2980985.png)

```javascript
@Get('bbb')
bbb() {
    return 'bbb';
}
```
浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1ed1e3c47851.png)

这样，app2 的服务就跑起来了。

原理也很简单，就是 nest cli 会根据 app 名字去读取对应的 tscofnig 文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9c08565bf65c.png)

这就是 nest 的 monorepo。

项目多了以后，难免有一些公共代码，这种公共代码怎么复用呢？

这就涉及到 nest 的另一个特性了：library。

创建一个 library：

```
nest g lib lib1
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8b60ced89a13.png)

它会让你指定一个前缀，这里用默认的 @app。

然后会生成 libs/lib1 目录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fdaeda91cfbc.png)

在 src 下生成了 module、service 并把它们导出了。

还在 tsconfig.json 的 paths 下添加了对应的别名配置：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/33bc1994c9f4.png)

在 nest-cli.json 里也多了这样一个 projects 配置：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/63d9438ff44e.png)

我们在 LibService 添加一个 xxx 方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/304de20dcb55.png)

```javascript
xxx() {
    return 'xxx';
}
```
然后在 monorepo-test 的 app 里导入 Lib1Module：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ea996f99f66b.png)

在 controller 里注入 Lib1Service 并调用它的方法：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2c5e5f6794a3.png)

```javascript
@Inject(Lib1Service)
private lib : Lib1Service;

@Get('aaa')
aaa() {
    return 'aaa' + this.lib.xxx();
}
```
同样的方式，在 app2 里也导入并使用它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cb8a4e46c7af.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/76d30cd00645.png)

```javascript
@Inject(Lib1Service)
private lib : Lib1Service;

@Get('bbb')
bbb() {
    return 'bbb' + this.lib.xxx();
}
```
然后分别把两个服务跑起来：

```
npm run start:dev

npm run start:dev app2
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/570975921752.png)


![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fb51a2fb8232.png)

浏览器访问下 http://localhost:3001/aaa 和 http://localhost:3000/bbb

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/69ad2a9ce49f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/09d4cca374bf.png)

可以看到，引入的 library 中的模块生效了。

如果你只是改 lib 下的代码，不想跑服务时，可以单独编译 lib 代码：

```
npm run start:dev lib1
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f45fe6bf406f.png)

nest 的 monorepo 和 libray 用起来都挺简单的。

还有个问题，现在 build 之后的代码是什么样的呢？

删掉 dist，然后执行：

```
npm run build
```
产生了一个 apps/monorepo-test/main.js，因为现在换成 webpack 了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/40b0deff347d.png)

然后执行：

```
npm run build app2
```
现在就多了 apps/app2/main.js 
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4a2d23beb0a7.png)

lib1 也是同理：
```
npm run build lib1
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3276f0c3c409.png)

之所以 application 或者 library 都能知道输出目录在哪，是因为在 tsconfig.json 里配了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5cc9b03a0d5c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/87f0a70d0003.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6230331a2711.png)

案例代码在[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/monorepo-test)

## 总结

微服务项目可能会有很多个项目，为了方便管理，我们会使用 monorepo 的方式。

monorepo 就是在一个 git 仓库里管理多个项目。

nest cli 支持 monorepo，只要执行 nest g app xxx 就会把项目变为 monorepo 的，在 apps 下保存多个 nest 应用。

nest-cli.json 里配置了多个 projects 的信息，以及默认的 project。

npm run start:dev 或者 npm run build 可以加上应用名来编译对应的 app。

此外，多个项目可能有公共代码，这时候可以用 nest g lib xxx 创建 library。

library 保存在 libs 目录下，和 apps 一样可以有多个。

nest 会为 libs 创建别名，可以在其他 app 或者 lib 里用别名引入。

这就是 nest 里创建 monorepo 以及通过 library 复用代码的方式，用起来还是比较简单的。
