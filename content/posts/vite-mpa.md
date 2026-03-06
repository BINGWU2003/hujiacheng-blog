---
title: "Vite MPA 多入口：让扫码 H5 页面与主系统彻底解耦"
date: 2026-03-06
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 背景

项目是一个基于 Vue 3 + Vite 的 MES（制造执行系统），主系统装载了大量重型依赖：

- **UI 框架**：Element Plus、Avue
- **表格**：VxeTable
- **图表**：ECharts（含地图包）
- **工具**：lodash-es、dayjs
- **其他**：vue-plugin-hiprint、avue-plugin-ueditor、@saber/nf-design-base-elp ...

其中有一个供外部扫二维码访问的质检报告 H5 页面（`/h5/displayQualityReportH5`），页面本身极其简单——只有几个文字字段和一张表格，逻辑不超过 100 行。但因为它注册在主系统的 SPA 路由里，用户扫码后要把整个系统的 JS 包全部下载解析完才能看到内容，在移动网络下首屏耗时长达 5~15 秒。

## 根因分析

问题的本质是**依赖链污染**。H5 页面虽然通过动态 `import()` 懒加载，但 `main.js` 启动时会同步执行所有全局插件注册：

```js
// main.js —— 主系统入口（部分）
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import Avue from "@smallwei/avue";
import * as echarts from "echarts";
import VxeUIBase from "vxe-pc-ui";
import VxeUITable from "vxe-table";
// ...
```

这些包在浏览器访问任何路由时都会被加载，H5 页面无法逃脱。

同时，H5 的 API 文件也通过 `import request from '@/axios'` 引入了主系统的全局 axios，而这个 axios 又依赖 `store`、`router`、`element-plus` 等，形成完整的依赖链：

```
displayQualityReportH5.vue
  └─ @/api/h5/displayQualityReportH5.js
       └─ @/axios.js
            └─ @/store/  @/router/  element-plus  ...
```

## 解决方案：Vite MPA 多入口

Vite 原生支持 MPA（多页应用）模式，通过配置多个 HTML 入口，可以产出相互独立的 JS 包。

### 整体思路

```
用户扫码
  │
  ▼
Nginx 判断路径前缀
  ├─ /h5/*  →  返回 index-h5.html  →  加载极小 H5 包（仅 Vue + axios）
  └─ 其他   →  返回 index.html     →  加载主系统完整包
```

### 第一步：新建 H5 独立 HTML 入口

```html
<!-- index-h5.html -->
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
    />
    <title>质检详情</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main-h5.js"></script>
  </body>
</html>
```

注意：相比主系统的 `index.html`，这里**不引入任何 CDN 脚本**（ECharts、Sortable、MQTT 等）。

### 第二步：新建极简 main-h5.js

```js
// src/main-h5.js
import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import h5Routes from "./router/h5";
import App from "./App.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_APP_BASE),
  routes: h5Routes,
});

createApp(App).use(router).mount("#app");
```

只有 `vue` + `vue-router`，不注册任何全局组件和插件。

### 第三步：新建 H5 专用路由表

```js
// src/router/h5.js
export default [
  {
    path: "/h5/displayQualityReportH5",
    name: "质量报告",
    component: () =>
      import("@/views/h5/displayQualityReportH5/displayQualityReportH5.vue"),
  },
  // 未来新增 H5 页面在此追加
];
```

### 第四步：新建轻量 axios 实例

主系统的 `@/axios` 依赖 store / router / element-plus，H5 不需要这些。单独创建一个极简 axios：

```js
// src/utils/axios-h5.js
import axios from "axios";
import { Base64 } from "js-base64";
import website from "@/config/website";

const baseUrl = import.meta.env.VITE_APP_API ?? "";

const h5Request = axios.create({
  baseURL: baseUrl,
  timeout: 15000,
  withCredentials: true,
});

h5Request.interceptors.request.use((config) => {
  config.headers["Blade-Requested-With"] = "BladeHttpRequest";
  config.headers["Authorization"] = `Basic ${Base64.encode(
    `${website.clientId}:${website.clientSecret}`,
  )}`;
  return config;
});

export default h5Request;
```

然后把 H5 的 API 文件改用这个轻量实例：

```js
// src/api/h5/displayQualityReportH5.js
import request from "@/utils/axios-h5"; // 改掉原来的 @/axios
```

### 第五步：vite.config.mjs 配置多入口

```js
build: {
  rollupOptions: {
    input: {
      main: resolve(__dirname, 'index.html'),     // 主系统入口
      h5:   resolve(__dirname, 'index-h5.html'),  // H5 独立入口
    },
    output: {
      manualChunks: {
        // 原有 chunk 分割保持不变
        'vendor-vue': ['vue', 'vue-router', 'vuex'],
        // ...
      },
    },
  },
},
```

构建后 `dist/` 会同时产出 `index.html` 和 `index-h5.html`，以及对应的独立 JS 包。

### 第六步：开发环境支持 —— 自定义 Vite 插件

Vite dev server 默认所有未匹配的路径都回退到 `index.html`（主系统），导致本地访问 `/h5/` 路径时加载的是主系统而非 H5 入口。

通过一个内联插件，在 dev server 的中间件层做路由分发，完美模拟 Nginx 行为：

```js
plugins: [
  ...createVitePlugins(env, command === 'build'),
  {
    name: 'h5-dev-fallback',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        if (req.url?.startsWith('/h5/')) {
          req.url = '/index-h5.html'; // 重写为 H5 入口
        }
        next();
      });
    },
  },
],
```

本地开发时直接访问真实路径即可，和生产环境体验一致：

```
http://localhost:2888/h5/displayQualityReportH5?code=xxx
```

### 第七步：生产环境 Nginx 配置

```nginx
# H5 扫码页走独立轻量入口
location /h5/ {
    try_files $uri $uri/ /index-h5.html;
}

# 其余路径走主系统
location / {
    try_files $uri $uri/ /index.html;
}
```

二维码 URL 本身**不需要改变**，Nginx 根据路径前缀决定返回哪个 HTML 文件。

## 效果对比

| 指标            | 优化前                                         | 优化后         |
| --------------- | ---------------------------------------------- | -------------- |
| 需加载的 JS 包  | Element Plus + Avue + VxeTable + ECharts + ... | 仅 Vue + axios |
| JS 体积（估算） | 5 MB+                                          | ~60 KB         |
| 移动网络首屏    | 5~15 秒                                        | < 1 秒         |
| 依赖隔离        | 无                                             | 完全隔离       |

## 关键收获

1. **SPA 不是银弹**。当同一个域下混合了「重型管理系统」和「轻量扫码 H5」两类使用场景，MPA 多入口是比懒加载更彻底的解法。
2. **依赖链要追到底**。单改页面懒加载不够，API 层的 `@/axios` 同样会把 store/router/element-plus 拖进来，必须断掉整条链。
3. **Vite 插件系统很灵活**。`configureServer` 钩子可以在开发阶段完美模拟 Nginx 的路由分发逻辑，不需要额外启动反向代理。
4. **H5 入口要保持克制**。`index-h5.html` 里不放任何 CDN script 标签，`main-h5.js` 里不注册任何用不到的全局插件，保证依赖边界清晰。
