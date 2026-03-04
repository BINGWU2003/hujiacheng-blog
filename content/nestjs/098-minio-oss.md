---
title: "用 minio 自己搭一个 OSS 服务"
date: 2025-04-08
draft: false
description: ""
tags: ["nestjs", "minio", "oss"]
categories: ["NestJS"]
series: ["实战技巧"]
series_order: 18
---

文件上传是常见需求，一般我们不会直接把文件保存在服务器的某个目录下，因为服务器的存储容量是有限的，这样不好扩展。

我们会用 OSS （Object Storage Service）对象存储服务来存文件，它是支持分布式扩展的，不用担心存储容量问题，而且也好管理。

比如阿里云的 OSS 服务。

但是有一些业务场景下，数据需要保密，要求私有部署，也就是要在自己的机房里部署一套 OSS 服务。

这时候怎么办呢？

这种需求一般我们会用 minio 来做。

它可以实现和阿里云 OSS 一样的功能。

首先，我们用一下阿里云的 OSS 服务。

OSS 里的文件是放在一个个 Bucekt（桶）里的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1519a00fd2c4.png)

我们创建个 Bucket：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6ba976b5dc38.png)

然后进入文件列表，就可以上传文件了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f0e9e85e6612.png)

因为创建的 Bucket 设置了公共读，所以可以直接访问：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b709baa7fcaa.png)

此外，阿里云 OSS 还可以通过 SDK 来上传文件。

创建个项目：

```
mkdir minio-test
cd minio-test
npm init -y
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/69da6d908e78.png)

进入项目，安装 ali-oss：

```
npm install ali-oss
```

创建 index.js

```javascript
const OSS = require('ali-oss')

const client = new OSS({
    region: 'oss-cn-beijing',
    bucket: 'guang-666',
    accessKeyId: '',
    accessKeySecret: '',
});

async function put () {
  try {
    const result = await client.put('smile.png', './smile.png');
    console.log(result);
  } catch (e) {
    console.log(e);
  }
}

put();
```
填入 region、bucket 和 accessKeyId、accessKeySecret

这里的 region 可以从概览里看到：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/554a2aab438e.png)

acessKey 是在这里看：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/484cd9edbe86.png)

具体创建 accessKey 的流程看[之前 OSS 那节](https://juejin.cn/book/7226988578700525605/section/7324620995183968293)

然后跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9f5b16125d18.png)

上传成功之后就可以通过 OSS 服务访问这个图片了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2f027a0aa41d.png)

也可以通过 sdk 下载图片：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8daac0ceb1b5.png)

执行后可以看到，图片被下载下来了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6d975fc84021.png)

这就是阿里云 OSS 的用法。

那我们用 minio 自己搭呢？

首先，我们需要安装 [docker 桌面端](https://www.docker.com/)：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5b43267dc406.png)

打开后可以看到本地的所有镜像和容器：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5d9b151b4d7b.png)

搜索下 minio（这步需要科学上网）：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f331d231afc1.png)

填入一些信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d89807ae6070.png)

name 是容器名。

port 是映射本地 9000 和 9001 端口到容器内的端口。

volume 是挂载本地目录到容器内的目录

这里挂载了一个本地一个目录到容器内的数据目录 /bitnami/minio/data，这样容器里的各种数据都保存在本地了。

还要指定两个环境变量，MINIO_ROOT_USER 和 MINIO_ROOT_PASSWORD，是用来登录的。

点击 run，跑起来之后可以看到数据目录被标记为 mounted，端口也映射成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b84d73a56446.png)

访问下 http://localhost:9001

输入刚才环境变量填的用户名密码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9859f8cbde4f.png)

进入管理界面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6795b8b66aab.png)

这个 bucket 就是管理桶的地方，而 object browser 就是管理文件列表的地方。

和阿里云 OSS 用法一样。

我们创建个 bucket：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/05016f81e9e3.png)

然后在这个 bucket 下上传一个文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/70114daeaea0.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b932dbbe1bad.png)

点击 share 就可以看到这个文件的 url：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f1a8270d5579.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6d7d5726cc7d.png)

现在倒是能在浏览器访问，只不过需要带后面的一长串东西：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9619f6753416.png)

不带的话会提示拒绝访问：


![image.png](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e725253ec285.png)

因为现在文件访问权限不是公开的。

我们设置下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/92783e045cfd.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f9153b5bdc56.png)

添加一个 / 的匿名的访问规则。

然后就可以直接访问了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b3ce74c89932.png)

是不是感觉用起来和阿里云的 OSS 差不多？

我们再来试试 sdk 的方式：

```
npm install minio
```
安装 minio 包。

然后创建 index2.js

```javascript
var Minio = require('minio')

var minioClient = new Minio.Client({
  endPoint: 'localhost',
  port: 9000,
  useSSL: false,
  accessKey: '',
  secretKey: '',
})

function put() {
    minioClient.fPutObject('aaa', 'hello.png', './smile.png', function (err, etag) {
        if (err) return console.log(err)
        console.log('上传成功');
    });
}

put();
```

创建用到的 accessKey：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eed46e1ed256.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6650b2db5b48.png)

跑一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/daa80be45fa8.png)

可以看到，文件上传成功了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bbbabfc3eec1.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/19a2f116eaa2.png)

同样，也可以下载文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2d3365ea2eff.png)

```javascript
const fs = require('fs');

function get() {
    minioClient.getObject('aaa', 'hello.png', (err, stream) => {
        if (err) return console.log(err)
        stream.pipe(fs.createWriteStream('./xxx.png'));
    });
}

get();
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a0949130b4e6.png)

用起来和阿里云 OSS 几乎一毛一样。

更多的 api 用法可以看 [minio 文档](https://min.io/docs/minio/linux/developers/javascript/minio-javascript.html)。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ac0ecc5f0c07.png)

最后，还记得我们跑 docker 容器的时候指定了挂载目录么：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b1b75910c73b.png)

这样，数据就会保存在本地的那个目录下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7d32e3f3c69d.png)

那为什么 OSS 服务都这么相似呢？

因为它们都是遵循 AWS 的 Simple Storage Service（S3）规范的，简称 S3 规范。

所以不管哪家的 OSS，用起来都是差不多的。

案例代码上传了[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/minio-test)。

## 总结

文件上传一般我们都是用 OSS 服务来存储，比如阿里云的 OSS。

但是 OSS 是收费的，而且有些敏感数据不能传到云上，需要私有部署，这种就可以自己搭一个 OSS 服务。

我们用 docker 跑了一个 minio 的容器，然后分别在管理界面和用 npm 包的方式做了文件上传和下载。

用法和阿里云 OSS 差不多，因为他们都是亚马逊 S3 规范的实现。

你公司内部有没有自己用 minio 搭 OSS 服务呢？
