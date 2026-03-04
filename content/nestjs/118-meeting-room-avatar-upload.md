---
title: "会议室预订系统：用户管理模块--头像上传"
date: 2025-04-28
draft: false
description: ""
tags: ["nestjs"]
categories: ["NestJS"]
series: ["会议室预订系统"]
series_order: 10
---

上节我们实现了用户信息的修改：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5f8651b018d4.png)

但是头像是直接填的路径，这里应该做成图片的展示，以及图片的上传。

我们需要添加个上传图片的接口：

在 UserController 里添加这个 handler：

```javascript
@Post('upload')
@UseInterceptors(FileInterceptor('file', {
  dest: 'uploads'
}))
uploadFile(@UploadedFile() file: Express.Multer.File) {
  console.log('file', file);
  return file.path;
}
```
安装用到的类型包：

```
npm install @types/multer
```
在 postman 里测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/629bd09fbda3.png)

选择 form-data 类型，然后添加 file 字段，选择一个文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d799fe54191b.png)

返回了服务端保存路径，并且打印了文件信息：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/eb88561026f3.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e83f8e9cfa83.png)

我们限制下只能上传图片：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/4898e1c593e1.png)

```javascript
import * as path from 'path';
```
```javascript
@Post('upload')
@UseInterceptors(FileInterceptor('file', {
  dest: 'uploads',
  fileFilter(req, file, callback) {
    const extname = path.extname(file.originalname);        
    if(['.png', '.jpg', '.gif'].includes(extname)) {
      callback(null, true);
    } else {
      callback(new BadRequestException('只能上传图片'), false);
    }
  }
}))
uploadFile(@UploadedFile() file: Express.Multer.File) {
  console.log('file', file);
  return file.path;
}
```
callback 的第一个参数是 error，第二个参数是是否接收文件。

然后我们上传一个非图片文件试一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f634158b0f77.png)

返回了错误信息。

上传图片是正常的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fc458775dfd6.png)

然后限制下图片大小，最大 3M:

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/60ce434f084f.png)

```javascript
limits: {
    fileSize: 1024 * 1024 * 3
}
```
当你上传超过 3M 的图片时，会提示错误：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9bf2b7ece522.png)

然后我们改下保存的文件名，这需要自定义 storage。

前面讲 multer 文件上传那节讲过，直接拿过来（忘了的同学可以回头看一下）：

添加 src/my-file-storage.ts

```javascript
import * as multer from "multer";
import * as fs from 'fs';

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        try {
            fs.mkdirSync('uploads');
        }catch(e) {}

        cb(null, 'uploads')
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9) + '-' + file.originalname
        cb(null, uniqueSuffix)
    }
});

export { storage };
```
这个就是自己指定怎么存储，multer.distkStorage 是磁盘存储，通过 destination、filename 的参数分别指定保存的目录和文件名。

指定 storage：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1d3fba95b81e.png)

然后测试下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/bf0925604622.png)

这样路径就能看出来是什么文件了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/8bc3e7fce205.png)

我们把这个目录设置为静态文件目录，这样能直接访问上传的图片。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7cf3e360f09e.png)

在 main.ts 里添加 uploads 目录为静态目录：

```javascript
app.useStaticAssets('uploads', {
    prefix: '/uploads'
});
```
指定通过 /uploads 的前缀访问。

然后我们把路径复制，在浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/7e6a1ef4a58f.png)

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e421d8b65617.png)

这样就可以访问到上传的文件了。

也就是说，上传头像之后，可以直接拿到图片的 url。

我们在页面里加一下：

在 src/page/update_info  下增加一个 HeadPicUpload.tsx

```javascript
import { Button, Input } from "antd";

interface HeadPicUploadProps {
    value?: string;
    onChange?: Function
}

export function HeadPicUpload(props: HeadPicUploadProps) {
    return props?.value ? <div>
        {props.value}
        <Button>上传</Button>
    </div>: <div>
        <Button>上传</Button>
    </div>
}
```
在上传头像的地方引入下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/b60a3847f4c1.png)

为什么是 value 和 onChange 两个参数呢？

因为 antd 的 Form.Item 在渲染时会给子组件传这两个参数。

现在渲染出来的是这样的：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/80e83a5deadb.png)

我们在 postman 里上传个图片，比如这个：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/552c889ec1a8.png)

拿到它的路径：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/9f2d251f74cc.png)

然后手动去数据库里改一下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/e2ae19222aa5.png)

点击 apply。

刷新下页面，可以看到确实变了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/065384eeb5ef.png)

然后把它改成图片：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/db642fd93d35.png)

```javascript
<img src={'http://localhost:3005/' + props.value} alt="头像" width="100" height="100"/>
```

头像就显示出来了：
![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d3ed2b26afdc.png)

然后我们把后面的上传按钮改为 antd 的拖拽上传组件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/5516a9c2f946.png)

```javascript
import { InboxOutlined } from "@ant-design/icons";
import { Button, Input, message } from "antd";
import Dragger, { DraggerProps } from "antd/es/upload/Dragger";

interface HeadPicUploadProps {
    value?: string;
    onChange?: Function
}

const props: DraggerProps = {
    name: 'file',
    action: 'http://localhost:3005/user/upload',
    onChange(info) {
        const { status } = info.file;
        if (status === 'done') {
            console.log(info.file.response);    
            message.success(`${info.file.name} 文件上传成功`);
        } else if (status === 'error') {
            message.error(`${info.file.name} 文件上传失败`);
        }
    }
};

const dragger = <Dragger {...props}>
    <p className="ant-upload-drag-icon">
        <InboxOutlined />
    </p>
    <p className="ant-upload-text">点击或拖拽文件到这个区域来上传</p>
</Dragger>

export function HeadPicUpload(props: HeadPicUploadProps) {
    return props?.value ? <div>
        <img src={'http://localhost:3005/' + props.value} alt="头像" width="100" height="100"/>
        {dragger}
    </div>: <div>
        {dragger}
    </div>
}
```
测试下，提示上传成功：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/1b8d26830ab9.gif)

控制台打印了文件路径：

![i](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3c33fcccbbb4.png)

服务端也确实有了这个文件：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/21b6a92eda14.png)

我们浏览器访问下：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/341d95dd795e.png)

能够正常访问。

接下来就通过 onChange 回调传给 Form 就好了。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/29a68c6c01f7.png)

这样表单的值就会改，触发重新渲染，就可以看到新的头像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/c964d03f62b9.gif)

不过现在还没更新到数据库。

点击发送验证码：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/fff86fb01c1e.png)

填入验证码，点击修改：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/f98626b76f58.png)

提示更新成功。

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/0cc37271c717.png)

数据库里确实更新了：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/3eb4483ba785.png)

刷新下页面，可以看到依然是这个头像：

![](https://bing-wu-doc-1318477772.cos.ap-nanjing.myqcloud.com/nestjs/d621d77ddeb9.png)

代表修改成功了。

至此，我们完成了用户信息修改的前后端。

案例代码在小册仓库：

[用户端前端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_frontend_user)

[后端代码](https://github.com/QuarkGluonPlasma/nestjs-course-code/tree/main/meeting_room_booking_system_backend)

## 总结

这节我们基于 multer 实现了头像上传。

通过自定义 storage 实现了文件路径的自定义，并且限制了文件的大小和类型。

然后把上传的目录作为静态文件目录，这样可以直接访问。

这样，头像上传功能就完成了。
