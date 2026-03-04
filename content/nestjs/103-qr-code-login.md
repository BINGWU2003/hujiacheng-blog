---
title: "实现扫二维码登录"
date: 2025-04-13
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["实战技巧"]
series_order: 23
---

扫码登录是常见的功能，基本各种网站都支持。

比如掘金的登录就支持 APP 扫码的方式：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a155868251b.png)

如果你 APP 没登录，扫码后会跳到登录页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/080df855a2d3.gif)

登录之后，会进入确认界面，你可以选择授权登录或者取消：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e9c8370959a4.gif)

这边确认之后，pc 网站就登录了。

知乎，b 站等也是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/35c9ddb5e3ab.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1718ca6f3aa5.png)

有没有感觉很神奇，为什么一扫二维码，然后确认下，那边就自动登录了呢？

其实原理也很简单。

我们先用解析工具解码下二维码的内容：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/072ba98f1b3e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ad27b1f0dbfa.png)

可以看到，二维码的内容是一个 url，如果在手机浏览器打开，是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a363224635a7.png)

会让你下载 APP。

而在 APP 里打开，就是登录确认界面了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/97d576558d43.jpg)

那确认的是哪个二维码呢？

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ad27b1f0dbfa.png)

二维码这里是有个唯一 id 的，通过这个 id 就知道是哪个二维码。

这个二维码有 5 个状态：

- 未扫描
- 已扫描，等待用户确认
- 已扫描，用户同意授权
- 已扫描，用户取消授权
- 已过期

最开始是未扫描状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b2f071c9207d.png)

扫码后会进入等待用户确认状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4bd3028105d0.png)

确认后会进入同意授权状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a7fab46f473f.png)

取消的话会进入取消授权状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b2f071c9207d.png)

长时间不操作会进入过期状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/308dc6e237dd.png)

也就是说，扫码后进行不同的操作就是修改这个 id 对应的二维码的状态。

另一边修改了状态，这边是怎么知道二维码状态变了呢？

websocket 么？

不用，一般都是轮询来做。

比如掘金：

二维码出现后，会有一个每秒一次的轮询请求来查询二维码状态：

最开始是 new：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c9f2447ebb9e.png)

扫码后会变成 scanned：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bbc5837785c7.png)

知乎也是一样：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a221e6b7405b.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f58cdb8d3453.png)

这时候，手机会进入登录确认页面：

bilibili 的登录确认页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8788685a2758.png)

知乎的登录确认页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/abb51b6d2e8f.png)

这边点击确认登录或者取消之后，会发请求修改 id 对应的二维码的状态。

那边一直在轮询，自然就知道了二维码状态的变更。

也就是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/08eb7080167d.png)

服务端有个 qrcode/generate 接口，会生成一个随机的二维码 id，存到 redis 里，并返回二维码。

还有个 qrcode/check 接口，会返回 redis 里的二维码状态，浏览器里可以轮询这个接口拿到二维码状态。

然后手机 APP 扫码之后，如果没登录，会先跳转到登录页面，登录之后会进入登录确认页面。

这个时候就从二维码中拿到了 id，然后调用 qrcode/scan、qrcode/cancel、qrcode/confirm 就是修改二维码为不同的状态。

这时候用户是登录了的，jwt 的登录认证方式会携带 token，服务端只要从 token 中取出用户信息，存入 redis 即可。

然后另一边的轮询接口发现是确认状态，会根据用户信息生成 jwt 返回。

这样，手机 APP 里确认之后，pc 的浏览器就自动登录了该用户账号。

这里的 jwt 是保存登录状态的一种方案，会把用户信息放在 token 里返回，然后每次访问接口带上 authorization 的 header，携带 token。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/494f87ea52f8.png)

思路理清了，我们来实现一下吧！

创建个 nest 项目：
```
npm install -g @nestjs/cli

nest new qrcode-login
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7ad9154e351d.png)

把它跑起来：

```
npm run start:dev
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/62a38c5fd1c5.png)

浏览器访问 http://localhost:3000 就可以可以看到 hello world，就代表服务跑起来了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6f591a891c6b.png)

然后我们实现下生成二维码的接口：

安装下用到的包：

```
npm install qrcode @types/qrcode
```

添加一个路由：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/efa3699a1dca.png)

```javascript
import { randomUUID } from 'crypto';
import * as qrcode from 'qrcode';
```
```javascript
@Get('qrcode/generate')
async generate() {
    const uuid = randomUUID();
    const dataUrl = await qrcode.toDataURL(uuid);
    return {
      qrcode_id: uuid,
      img: dataUrl
    }
}
```
这里用 node 的 crypto 模块生成一个随机的 uuid。

然后用 qrcode 生成二维码，只不过转成 base64 返回。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8358eac5f6a1.png)

我们在 html 里把它渲染出来看一下：

新建 static/index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>扫码登录</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <img src="data:image/png;base64,这里填入你生成的 url" alt=""/>
</body>
</html>

```
然后在 main.ts 里支持这个目录下静态资源的访问，用 pages 作为前缀：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7f5fcb12e672.png)

```javascript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  app.useStaticAssets('static', { prefix: '/pages'});

  await app.listen(3000);
}
bootstrap();
```

这样你访问 http://localhost:3000/pages/index.html 就可以看到二维码了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/66644824a212.png)

我们用在线解码工具解码下看看：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/772c14644e95.png)

确实，内容就是生成的 uuid。

然后，其实这个二维码扫出的应该是个网址。

比如掘金的二维码解析出的内容：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3e5bf7c95a10.png)

如果用手机浏览器扫这个码的话，打开的就是下载 APP 的页面：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5baad5ed7d84.png)

而如果用掘金 APP 扫码，扫出的就是登录确认页面了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c6c6d01fe0b3.png)

这个很正常，因为如果随便一个浏览器都能扫码打开登录确认页面，那谁还下载掘金 APP 呢？

所以掘金的二维码只能掘金 APP 扫，微信的二维码只能用微信 APP 扫。

这个页面做了检查，判断是 APP 打开的还是其他方式打开的，分别会显示不同的内容。

这里我们也改成一个 url：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/50aa49d0f1f9.png)

扫码就会打开这个页面，而这个页面就是登录确认页面。

我们写一下这个页面：

新建 static/confirm.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码登录确认</title>
</head>
<body>
    <button>确认登录</button>
    <button>取消</button>
</body>
</html>
```
但这里有个问题，开发服务是在电脑上的，手机怎么访问呢？

这里需要用 charles 来做代理：

[下载 charles](https://www.charlesproxy.com/download/)，打开

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5e12e9f4e7a8.png)

让电脑和手机连接同一个 wifi，然后在手机的 wifi 设置那里设置代理：

代理的 ip 是电脑 ip，端口号就是 charles 代理服务的默认端口 8888

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9b5b05a6414a.png)

这时候电脑上会收到连接提醒，同意下就好了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/60d029f8a305.png)

然后手机就可以访问电脑上的 nest 服务：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ac8a4b6ce0af.png)

看到这个 hello world 了没？

这就是电脑上的这个 nest 服务返回的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f058771eb4fe.png)

那个登录确认页面在电脑访问是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ac5967f2eca1.png)

然后我把二维码的内容改为这个：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e4f9b8771068.png)

修改下展示二维码的页面：

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>扫码登录</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/axios@1.5.0/dist/axios.min.js"></script>
</head>
<body>
    <img id="img" src="" alt=""/>

    <script>
        axios.get('http://localhost:3000/qrcode/generate').then(res => {
            document.getElementById('img').src = res.data.img;
        })
    </script>
</body>
</html>
```
用 axios 请求生成二维码的接口，然后修改图片 src。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ca92523545f7.png)

用手机扫码下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/afa2cf37a3d2.gif)

用微信扫码，可以看到，打开了登录确认页面。

按钮有点小，我们设置下样式。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码登录确认</title>
    <style>
        #info {
            height: 400px;
            line-height: 400px;
            font-size: 20px;
            padding: 20px;
        }
        #confirm, #cancel{
            display: block;
            width: 80%;
            line-height: 40px;
            font-size: 20px;
            margin-bottom: 20px;
        }
        #confirm {
            background: skyblue;
        }
    </style>
</head>
<body>
    <div id="info">
        是否确认登录 xxx 网站？
    </div>
    <button id="confirm">确认登录</button>
    <button id="cancel">取消</button>
</body>
</html>
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9d798665c109.gif)

好看多了。

二维码的内容解码后是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/85fd1f2bdab9.png)

然后我们来实现剩下的接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ec15c20ddf69.png)

生成二维码之后，要在 redis 里保存一份，这里我们简化一下，直接用个 map 保存吧。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3305d4579645.png)

```javascript
const map = new Map<string, QrCodeInfo>();

interface QrCodeInfo{
  status: 'noscan' | 'scan-wait-confirm' | 'scan-confirm' | 'scan-cancel' | 'expired',
  userInfo?: {
    userId: number;
  }
}
// noscan 未扫描
// scan-wait-confirm -已扫描，等待用户确认
// scan-confirm 已扫描，用户同意授权
// scan-cancel 已扫描，用户取消授权
// expired 已过期
```
```javascript
map.set(`qrcode_${uuid}`, {
  status: 'noscan'
});
```
然后加一个 qrcode/check 接口，用来查询二维码状态：

```javascript
@Get('qrcode/check')
async check(@Query('id') id: string) {
    return map.get(`qrcode_${id}`);
}
```
测试下：

访问 /qrcode/generate 生成二维码和 id

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ce5205296738.png)

然后访问 /qrcode/check 拿到这个 id 的状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0af4f06e07f9.png)

然后再实现 /qrcode/confirm、/qrcode/cancel、/qrcode/scan 这三个接口：

```javascript
@Get('qrcode/scan')
async scan(@Query('id') id: string) {
    const info = map.get(`qrcode_${id}`);
    if(!info) {
      throw new BadRequestException('二维码已过期');
    }
    info.status = 'scan-wait-confirm';
    return 'success';
}

@Get('qrcode/confirm')
async confirm(@Query('id') id: string) {
    const info = map.get(`qrcode_${id}`);
    if(!info) {
      throw new BadRequestException('二维码已过期');
    }
    info.status = 'scan-confirm';
    return 'success';
}

@Get('qrcode/cancel')
async cancel(@Query('id') id: string) {
    const info = map.get(`qrcode_${id}`);
    if(!info) {
      throw new BadRequestException('二维码已过期');
    }
    info.status = 'scan-cancel';
    return 'success';
}
```
测试下：

先 qrcode/generate 生成二维码，拿到 id：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a123de6f0a73.png)

然后调用 qrcode/scan 修改状态，之后调用 qrcode/check 查询下状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/928c5dbcf843.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/123e697a9cd8.png)

同样的方式测试 qrcode/cancel 和 qrcode/confirm 接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e5336f5e77f2.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7a896d6938e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0f5ef0ff0fca.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a2f45f816974.png)

如果 id 不存在，会返回 400 的状态码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f32f7885f852.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4ae6e049d76d.png)

然后就可以在 static/index.html 里加上 qrcode/check 接口来轮询二维码状态了。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>扫码登录</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/axios@1.5.0/dist/axios.min.js"></script>
</head>
<body>
    <img id="img" src="" alt=""/>
    <div id="info"></div>
    <script>
        axios.get('http://localhost:3000/qrcode/generate').then(res => {
            document.getElementById('img').src = res.data.img;

            queryStatus(res.data.qrcode_id);
        })

        function queryStatus(id) {
            axios.get('http://localhost:3000/qrcode/check?id=' + id).then(res => {
                const status = res.data.status;

                let content = '';
                switch(status) {
                    case 'noscan': content = '未扫码'; break;
                    case 'scan-wait-confirm': content = '已扫码，等待确认'; break;
                    case 'scan-confirm': content = '已确认'; break;
                    case 'scan-cancel': content = '已取消'; break;
                }
                document.getElementById('info').textContent = content;

                if(status === 'noscan' || status === 'scan-wait-confirm') {
                    setTimeout(() => queryStatus(id), 1000);
                }
            })
        }
    </script>
</body>
</html>
```
生成二维码之后，就开始轮询状态了。

根据状态分别显示不同的文字，如果不是已确认或者已取消就在一秒后继续下次轮询。

然后，在登录确认页面也加上接口调用：

改下 static/confirm.html

使用 URLSearchParams 的 api 拿到 url 中的 id：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d7a9f0cf5f76.png)

然后修改这个 id 对应的二维码的状态。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码登录确认</title>
    <script src="https://unpkg.com/axios@1.5.0/dist/axios.min.js"></script>
    <style>
        #info {
            height: 400px;
            line-height: 400px;
            font-size: 20px;
            padding: 20px;
        }
        #confirm, #cancel{
            display: block;
            width: 80%;
            line-height: 40px;
            font-size: 20px;
            margin-bottom: 20px;
        }
        #confirm {
            background: skyblue;
        }
    </style>
</head>
<body>
    <div id="info">
        是否确认登录 xxx 网站？
    </div>
    <button id="confirm">确认登录</button>
    <button id="cancel">取消</button>

    <script>
        const params = new URLSearchParams(window.location.search.slice(1));

        const id = params.get('id');

        axios.get('http://192.168.31.56:3000/qrcode/scan?id=' + id).catch(e => {
            alert('二维码已过期');
        });
        
        document.getElementById('confirm').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/qrcode/confirm?id=' + id).catch(e => {
                alert('二维码已过期');
            });
        });

        document.getElementById('cancel').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/qrcode/cancel?id=' + id).catch(e => {
                alert('二维码已过期');
            });
        });
    </script>
</body>
</html>
```
进入这个页面，就访问 qrcode/scan 接口，来把 id 对应的二维码改为已扫描状态。

点击确认或者取消按钮也分别修改状态为确认和取消。

注意，这个页面是在手机打开的，需要通过 ip 的方式访问接口。

测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bc26cadb9521.png)

打开页面后，生成二维码，这时候就开始轮询二维码状态。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1cf6aef1397d.gif)

手机扫码，进入登录确认页面。

这时候二维码页面的状态变为了等待确认：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/314fc35cc53e.png)

然后确认登录，这时候 pc 页面变为了已确认状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c59b6c92ea6e.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/68e022183f63.png)

如果点击取消，那就会变为已取消状态：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9e9270bb58d6.png)

这就是扫码之后，pc 上的二维码同步改变状态的原理。

当然，最终我们是要做登录的。

确认之后，就要拿到这边的登录状态，从中取出用户信息。

当然，现在我们还没做登录。

我们通过 jwt 搞一下：

引入 jwt 的 包：

```
npm install @nestjs/jwt
```

在 AppModule 里引入它：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d258dc633720.png)

然后实现登录接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8a889ec0f9ff.png)

这里我们没有用数据库，只有 2 个用户，如果信息匹配，就返回 jwt 的 token：
```javascript
@Inject(JwtService)
private jwtService: JwtService;

private users = [
    {id: 1, username: 'dong', password: '111'},
    {id: 2, username: 'guang', password: '222'},
];

@Get('login')
async login(@Query('username') username: string, @Query('password') password: string) {

    const user = this.users.find(item => item.username === username);

    if(!user) {
      throw new UnauthorizedException('用户不存在');
    }
    if(user.password !== password) {
      throw new UnauthorizedException('密码错误');
    }

    return {
      token: await this.jwtService.sign({
      userId: user.id
    })
}
```
postman 里测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1ac5e875c12f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c7a4e1a3e52a.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2d76c9770fb.png)

登录成功后，会返回 token。

这个 token 一般都是在访问接口的时候放在 authorization 的 header 里，通过 Bearer xxx 的方式。

我们添加一个 userInfo 的接口来拿到用户信息：

```javascript
@Get('userInfo')
async userInfo(@Headers('Authorization') auth: string) {
    try{
      const [, token] = auth.split(' ');
      const info = await this.jwtService.verify(token);

      const user = this.users.find(item => item.id == info.userId);
      return user;
    } catch(e) {
      throw new UnauthorizedException('token 过期，请重新登录');
    }
}
```
它会从 header 中取出 token，解析出其中的信息，从而拿到 userId，然后查询 id 对应的用户信息返回。

我们加上 authorization 的 header，访问下 userInfo 接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1d9f92edd3ca.png)

可以看到，拿到了用户的信息。

然后我们在登录确认页面加上登录：

添加两个按钮：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/35daf731ff11.png)

这俩按钮分别是登录不同的账号，拿到 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a096b403b5a1.png)

访问 confirm 接口时带上这个 token：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/25e6ffdf0b09.png)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码登录确认</title>
    <script src="https://unpkg.com/axios@1.5.0/dist/axios.min.js"></script>
    <style>
        #info {
            height: 400px;
            line-height: 400px;
            font-size: 20px;
            padding: 20px;
        }
        #confirm, #cancel{
            display: block;
            width: 80%;
            line-height: 40px;
            font-size: 20px;
            margin-bottom: 20px;
        }
        #confirm {
            background: skyblue;
        }
    </style>
</head>
<body>
    <button id="guang">登录光光账号</button>
    <button id="dong">登录东东账号</button>

    <div id="info">
        是否确认登录 xxx 网站？
    </div>
    <button id="confirm">确认登录</button>
    <button id="cancel">取消</button>

    <script>
        const params = new URLSearchParams(window.location.search.slice(1));

        const id = params.get('id');

        let token = '';
        document.getElementById('dong').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/login', {
                params: {
                    username: 'dong',
                    password: '111'
                }
            }).then(res => {
                token = res.data.token;
            });
        });

        document.getElementById('guang').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/login', {
                params: {
                    username: 'guang',
                    password: '222'
                }
            }).then(res => {
                token = res.data.token;
            });
        });

        axios.get('http://192.168.31.56:3000/qrcode/scan?id=' + id).catch(e => {
            alert('二维码已过期');
        });
        
        document.getElementById('confirm').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/qrcode/confirm?id=' + id, {
                headers: {
                    authorization: 'Bearer ' + token
                }
            }).catch(e => {
                alert('二维码已过期');
            });
        });

        document.getElementById('cancel').addEventListener('click', () => {
            axios.get('http://192.168.31.56:3000/qrcode/cancel?id=' + id).catch(e => {
                alert('二维码已过期');
            });
        });
    </script>
</body>
</html>
```
然后我们在 qrcode/confirm 接口里把 token 取出来，拿到其中的用户信息，保存到 map 里：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/aaf602d6dbd6.png)

```javascript
@Get('qrcode/confirm')
async confirm(@Query('id') id: string, @Headers('Authorization') auth: string) {
    let user;
    try{
      const [, token] = auth.split(' ');
      const info = await this.jwtService.verify(token);

      user = this.users.find(item => item.id == info.userId);
    } catch(e) {
      throw new UnauthorizedException('token 过期，请重新登录');
    }

    const info = map.get(`qrcode_${id}`);
    if(!info) {
      throw new BadRequestException('二维码已过期');
    }
    info.status = 'scan-confirm';
    info.userInfo = user;
    return 'success';
}
```
这样，当扫码确认后，那边就能拿到用户信息：

我们改下 static/index.html

确认的时候展示下登录用户的信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a958df1e70e8.png)

加上登录之后，我们再测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0df2343118fc.png)

手机扫码，点击登录光的账号，然后确认登录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/35102538cb15.gif)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8d4b1b9e051f.png)

刷新页面，重新扫码，然后登录东东账号。

这时候 pc 网站就显示了当前登录用户是 dong

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e1e36714c9a3.png)

当然，登录状态需要一个 jwt，我们返回下就好了。

```javascript
@Get('qrcode/check')
async check(@Query('id') id: string) {
    const info = map.get(`qrcode_${id}`);
    if(info.status === 'scan-confirm') {
        return {
          token: await this.jwtService.sign({
            userId: info.userInfo.userId
          }),
          ...info
        }
    }
    return info;
}
```
这样，当那边确认登录之后，这边就拿到了 jwt 的 token，也就是完成了登录了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b6afd27602fa.png)

对比下掘金的扫码登录流程：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/65de663e130c.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8db4b5431090.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2e78207e0356.png)

是不是一摸一样？

扫码登录就是这样实现的。

案例代码上传了[小册仓库](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/qrcode-login)

## 总结
扫码登录是常用的功能，掘金、知乎、b 站等各大网站都有。

流程是在 pc 选择扫码登录的方式，用 APP 扫码，在 app 上登录之后进入登录确认页面。

可以点击确认登录或者取消，如果确认登录，那 pc 网站就会自动登录该账号。

它的实现原理是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/55f85618764a.png)

pc 端生成二维码，然后不断轮询二维码状态。

APP 里扫码拿到 qrcode_id，然后分别调用 scan、confirm、cancel 来修改二维码状态。

并且登录之后会把 token 带过去。

在 redis 里保存着二维码的状态和用户信息，然后这边确认之后，另一边就可以用 userInfo 生成 jwt 的 token，从而实现登录。

这就是扫码登录的实现原理。

