---
title: "会议室预订系统：文件上传 OSS"
date: 2025-05-12
draft: false
description: ""
tags: ["nestjs", "oss"]
categories: ["NestJS"]
series: ["会议室预订系统"]
series_order: 24
---

前面我们实现了头像的上传：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1aa738581344.gif)

图片是保存在服务器 uploads 目录下的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6821ed3b7c88.png)

然后把这个目录设置为静态文件目录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6c52afdb93c6.png)

这样图片就能直接访问了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b656148e874f.png)

数据库里保存的也是这个路径：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1e97533c98b3.png)

这样是能完成功能，但有一些问题：

文件直接保存在某个目录下，服务器磁盘空间是有上限的，如果满了怎么办？

这些文件都没有一个管理界面来管理，很不方便。

所以，一般没人这么干，都会用 OSS 来做文件的管理，比如阿里云 OSS、或者我们用 minio 自己搭的 OSS 服务。

这节我们就把头像上传到用 minio 搭的 OSS。

把 minio 的 docker 镜像跑起来：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1c4432e49351.png)

指定本地的某个目录，映射到容器里的 /bitnami/minio/data 目录。

指定端口 9000 和 9001 的映射。(9000 是文件访问的端口，9001 是管理页面的端口)

然后指定登录的用户名、密码 MINIO_ROOT_USER、MINIO_ROOT_PASSWORD

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/93d50e72c644.png)

跑起来之后，访问下 http://localhost:9001

输入用户名密码后点击登录：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f2e5cf83bd9c.png)

创建个 bucket：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8a9fd6dbf719.png)

设置下可以公开访问：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/15012e6e1404.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/abd414f6750c.png)

然后上传个文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/12024c530b38.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ecf3cbab7f81.png)

复制路径，然后浏览器访问下：

http://localhost:9000/meeting-room-booking-system/headpic1.jpg

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4541797f6350.png)

这样，文件就上传到了 OSS 里的 bucket，并且能够访问了。

这不比直接把文件放到文件目录下方便的多？

然后我们直接前端直传 minio 就好了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/371b09ce855b.png)

上传完之后把 url 给服务端保存到数据库就行。

但是这个 accessKey 也不能暴露到前端代码里，需要在服务端做预签名。

这个在[前端直传文件到 minio](https://juejin.cn/book/7226988578700525605/section/7364018227191496704)那节讲过。

我们进入 backend 的项目，安装 minio 的包：
```
npm install --save minio
```
然后创建个 minio 模块：

```
nest g module minio
```
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/96806cc6bd2f.png)

```javascript
import { Global, Module } from '@nestjs/common';
import * as Minio from 'minio';

@Global()
@Module({
    providers: [
        {
            provide: 'MINIO_CLIENT',
            async useFactory() {
                const client = new Minio.Client({
                        endPoint: 'localhost',
                        port: 9000,
                        useSSL: false,
                        accessKey: '',
                        secretKey: ''
                    })
                return client;
            }
          }
    ],
    exports: ['MINIO_CLIENT']
})
export class MinioModule {}
```
把 minio client 封装成 provider，放到 exports 里，并设置模块为 @Global。

用到 accessKey 和 secretKey 在这里创建：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/95543df5a66f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4b143993ac96.png)

这些当然也可以放到配置文件里配置：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/6c9b67ced5c6.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/21c2355ecdf9.png)

```
# minio 配置
minio_endpoint=localhost
minio_port=9000
minio_access_key=xxx
minio_secret_key=xxx
```

因为 ConfigModule 声明为了全局模块：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1770e578710e.png)

所以可以直接在 MinioModule 里注入 ConfigService：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/018ae90bbe9a.png)
```javascript
import { Global, Module } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as Minio from 'minio';

@Global()
@Module({
    providers: [
        {
            provide: 'MINIO_CLIENT',
            async useFactory(configService: ConfigService) {
                const client = new Minio.Client({
                    endPoint: configService.get('minio_endpoint'),
                    port: +configService.get('minio_port'),
                    useSSL: false,
                    accessKey: configService.get('minio_access_key'),
                    secretKey: configService.get('minio_secret_key')
                })
                return client;
            },
            inject: [ConfigService]
          },
    ],
    exports: ['MINIO_CLIENT']
})
export class MinioModule {}
```

然后创建 MinioController

```
nest g controller minio --no-spec
```

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a7f7aaad5e78.png)

注入 Minio Client：

```javascript
import { Controller, Get, Inject, Query } from '@nestjs/common';
import * as Minio from 'minio';

@Controller('minio')
export class MinioController {

    @Inject('MINIO_CLIENT')
    private minioClient: Minio.Client;

    @Get('presignedUrl') 
    presignedPutObject(@Query('name') name: string) {
        return this.minioClient.presignedPutObject('meeting-room-booking-system', name, 3600);
    }
}
```

presignedPutObject 第一个参数是 buckectName，第二个参数是 objectName，第三个参数是 expires。

bucketName 就是 meeting-room-booking-system，这个也可以抽到 .env 文件里，用 configService 读取。

objectName 需要上传文件的时候拿到 file.name 作为参数传入。

expires 是生成的临时签名的过期时间，我们指定 3600 秒，也就是一小时。

调用下这个接口试试：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/a3fdb46326fa.png)

可以看到，返回了 aaa.png 的预签名的 url，这样前端不需要 accessKey 也可以用这个 url 来上传文件到 minio 了。

我们在 frontend_user 项目里用一下：

之前是指定了 action 参数，当选择文件后，antd 的 Dragger 组件会自动上传文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/cee9d3d66632.png)

它还支持函数的形式，会传入 file 然后做处理后返回 url：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ec15b2fdc7d6.png)

这里很显然就可以调用 presignedUrl 接口，拿到直传 minio 的 url。

我们在 interfaces.ts 添加一个接口：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/ec5d908b5882.png)

```javascript
export async function presignedUrl(fileName: string) {
    return axiosInstance.get(`/minio/presignedUrl?name=${fileName}`);
}
```

然后 action 这里调用下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f9549c5e67e5.png)
```javascript
action: async (file) => {
    const res = await presignedUrl(file.name);
    return res.data.data;
},
async customRequest(options) {
    const { onSuccess, file, action } = options;

    const res = await axios.put(action, file);

    onSuccess!(res.data);
},
```

为什么要 customRequest 呢？

因为默认 Dragger 是用 FormData 的格式上传的，也就是 key value 的格式。

我们指定的 name 就是 key。

但是 minio 要求直接把文件放到 body 里。

所以我们要用 customRequest 自定义请求方式。

试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8e563946927a.gif)

提示上传成功。

在 minio 管理界面也可以看到这个文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2fde1c441a12.gif)

接下来只要改下 onChange 的值，以及回显的图片的 url 就好了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/27a208cc3627.png)

```javascript
onChange('http://localhost:9000/meeting-room-booking-system/' + info.file.name);
```

试下效果：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/75e40644d748.gif)

输入验证码，点击修改，会提示更新成功：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/2a6bffccfd3d.gif)

去数据库里看下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9a6f56196c2f.png)

确实改过来了。

这样，基于 minio 搭的 OSS 服务的图片上传功能就完成了。

然后我们改下右上角按钮，改成显示用户头像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/420148d00340.png)

首先，用户信息更新完后，同步修改下 localStorage 里的 user_info

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e7363e110ed9.png)

```javascript
const userInfo = localStorage.getItem('user_info');
if(userInfo) {
    const info = JSON.parse(userInfo);
    info.headPic = values.headPic;
    info.nickName = values.nickName;

    localStorage.setItem('user_info', JSON.stringify(info));
}
```
测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/247a9ca9374d.gif)

可以看到，点击修改后，localStorage 里的数据也同步更新了。

然后右上角的按钮也可以从 localStorage 里取最新的 headPic：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9f60b8f3e582.png)

```javascript
import { UserOutlined } from "@ant-design/icons";
import { Link, Outlet } from "react-router-dom";
import './index.css';
import { useEffect, useState } from "react";

export function Index() {

    const [headPic, setHeadPic] = useState();

    useEffect(() => {
        const userInfo = localStorage.getItem('user_info');
        if(userInfo) {
            const info = JSON.parse(userInfo);
            setHeadPic(info.headPic);
        }
    }, []);

    return <div id="index-container">
        <div className="header">
            <h1>会议室预定系统</h1>
            <Link to={'/update_info'} >
                {
                    headPic ? <img src={headPic} width={40} height={40} className="icon"/> : <UserOutlined className="icon"/>
                }                
            </Link>
        </div>
        <div className="body">
            <Outlet></Outlet>
        </div>
    </div>
}
```
useState 创建一个状态来保存 headPic。

在 useEffect 里读取 localStrage 里的值，调用 setHeadPic。

渲染的时候如果 headPic 有值就渲染 img，否则渲染默认的 icon。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/197339c6ecbd.png)

这样，头像就正确显示了。

代码在小册仓库：

[backend](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_backend)

[frontend_user](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_frontend_user)

## 总结

这节我们把文件上传从基于 multer 实现，保存在项目目录下，换成了基于 minio 实现的 OSS 服务。

我们是用前端直传 OSS，然后把文件 url 发给应用服务器的方式。

但是又不想在前端代码暴露 accessKey，所以是用的预签名的方式，服务端用 presignedPutObject 返回一个预签名 url 给前端。前端用这个 url 来发送 put 请求，来把文件直传 minio。

antd 的 Dragger 组件默认用 form data 来发送请求，我们通过 customRequest 来重写了上传逻辑。

这样，文件就都保存在了 minio 服务里，可以更方便的管理。
