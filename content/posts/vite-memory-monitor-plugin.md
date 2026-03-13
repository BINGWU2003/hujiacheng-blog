---
title: "Vite 构建内存监控 & 耗时统计插件"
date: 2026-03-12
draft: false
description: ""
tags: ["Vite", "Vue", "构建工具", "前端工程化"]
categories: ["笔记"]
---

## 使用场景

- 构建时出现 `JavaScript heap out of memory` 错误
- 想知道内存在哪个阶段暴涨、构建时间花在哪里
- 压缩器选型对比（esbuild vs terser）
- 优化前后做内存与耗时对比

## 插件代码

两个插件独立存放，用完删除。

### memory-monitor.js

```js
import { resolve } from "path";
import fs from "fs";

export default function createMemoryMonitorPlugin() {
  const logFile = resolve(process.cwd(), "build-memory.log");
  let phase = "init";
  let peak = 0;
  let timer = null;
  const write = (msg) => fs.appendFileSync(logFile, msg + "\n");
  const mb = () => process.memoryUsage().heapUsed / 1024 / 1024;

  return {
    name: "memory-monitor",
    buildStart() {
      phase = "buildStart";
      peak = 0;
      fs.writeFileSync(
        logFile,
        `=== 构建开始 ${new Date().toLocaleString()} ===\n`,
      );
      timer = setInterval(() => {
        const cur = mb();
        if (cur > peak) {
          peak = cur;
          write(`[峰值更新] 阶段: ${phase} | ${cur.toFixed(1)} MB`);
        }
      }, 500);
      process.once("exit", () => {
        write(`\n[进程退出] 最后阶段: ${phase} | 峰值: ${peak.toFixed(1)} MB`);
      });
      write(`[buildStart] ${mb().toFixed(1)} MB`);
      console.log(
        `\n[内存] 构建开始: ${mb().toFixed(1)} MB，日志输出至 build-memory.log`,
      );
    },
    buildEnd() {
      phase = "buildEnd";
      write(`[buildEnd] ${mb().toFixed(1)} MB`);
    },
    renderStart() {
      phase = "renderStart";
      write(`[renderStart] ${mb().toFixed(1)} MB`);
      console.log(
        `\n[内存] renderStart（代码生成开始）: ${mb().toFixed(1)} MB`,
      );
    },
    renderChunk(_code, chunk) {
      phase = `renderChunk:${chunk.fileName}`;
    },
    generateBundle() {
      phase = "generateBundle";
      write(`[generateBundle] ${mb().toFixed(1)} MB`);
      console.log(`\n[内存] generateBundle（产物生成）: ${mb().toFixed(1)} MB`);
    },
    closeBundle() {
      clearInterval(timer);
      write(
        `[closeBundle] ${mb().toFixed(1)} MB\n[内存峰值] ${peak.toFixed(1)} MB`,
      );
      console.log(`\n[内存峰值] ${peak.toFixed(1)} MB`);
    },
  };
}
```

### build-timer.js

```js
import { resolve } from "path";
import fs from "fs";

export default function createBuildTimerPlugin() {
  const logFile = resolve(process.cwd(), "build-memory.log");
  const write = (msg) => fs.appendFileSync(logFile, msg + "\n");
  const phases = {};
  let buildStartTime = 0;

  const mark = (name) => {
    phases[name] = Date.now();
  };
  const elapsed = (from, to) =>
    ((phases[to] - phases[from]) / 1000).toFixed(2) + "s";

  return {
    name: "build-timer",
    buildStart() {
      buildStartTime = Date.now();
      mark("buildStart");
    },
    buildEnd() {
      mark("buildEnd");
    },
    renderStart() {
      mark("renderStart");
    },
    generateBundle() {
      mark("generateBundle");
    },
    closeBundle() {
      mark("closeBundle");
      const total = ((Date.now() - buildStartTime) / 1000).toFixed(2);
      write(
        [
          "",
          `=== 构建耗时 ===`,
          `  模块解析 (buildStart→buildEnd):       ${elapsed("buildStart", "buildEnd")}`,
          `  代码生成 (renderStart→generateBundle): ${elapsed("renderStart", "generateBundle")}`,
          `  总耗时:                                ${total}s`,
        ].join("\n"),
      );
      console.log(`\n[构建耗时] 总计 ${total}s`);
    },
  };
}
```

### 接入方式

```js
// vite.config.js
import createMemoryMonitorPlugin from "./vite/plugins/memory-monitor";
import createBuildTimerPlugin from "./vite/plugins/build-timer";

plugins: [
  // 临时内存监控 + 耗时插件（数据收集完后删除）
  createMemoryMonitorPlugin(),
  createBuildTimerPlugin(),
];
```

> `build-memory.log` 加入 `.gitignore`，不需要提交。

## 日志格式

构建结束后在项目根目录生成 `build-memory.log`，两个插件共用同一文件：

```
=== 构建开始 2026/3/12 13:00:52 ===
[buildStart] 66.5 MB
[峰值更新] 阶段: buildStart | 1017.8 MB
[buildEnd] 4234.8 MB
[renderStart] 4236.1 MB
[峰值更新] 阶段: renderChunk:assets/main.js | 5366.2 MB
[generateBundle] 5201.3 MB
[closeBundle] 4987.6 MB
[内存峰值] 5366.2 MB

=== 构建耗时 ===
  模块解析 (buildStart→buildEnd):       18.34s
  代码生成 (renderStart→generateBundle): 24.51s
  总耗时:                                47.23s
```

OOM 时 `process.once('exit')` 会在进程退出前最后写入一行，日志不会丢失：

```
[进程退出] 最后阶段: renderChunk:assets/html-!~{0jv}~.js | 峰值: 8347.6 MB
```

## Rollup 构建阶段说明

| 阶段             | 说明                        | 内存特征                             |
| ---------------- | --------------------------- | ------------------------------------ |
| `buildStart`     | 解析所有模块、构建依赖图    | 随模块数量线性增长                   |
| `buildEnd`       | 模块图构建完成              | 内存达到第一个高峰                   |
| `renderStart`    | 开始代码生成                | 略有上升                             |
| `renderChunk`    | 对每个 chunk 生成代码并压缩 | **内存最高危阶段**，chunk 越大越危险 |
| `generateBundle` | 所有 chunk 生成完毕         | 趋于稳定                             |
| `closeBundle`    | 写入磁盘，构建结束          | 开始释放                             |

## 本项目实测数据（2026-03）

项目规模：7900+ 模块，双入口（main + h5）。

### 无 manualChunks（OOM 崩溃）

| 阶段        | 内存                |
| ----------- | ------------------- |
| buildStart  | 66 MB               |
| buildEnd    | 4234 MB             |
| renderChunk | >8300 MB → OOM 崩溃 |

崩溃位置：`renderChunk:assets/html-!~{0jv}~.js`，所有依赖打进单一巨型 chunk，压缩时 AST 全量装载进内存。

### 有 manualChunks（成功）+ esbuild 压缩

将 Element Plus、VxE Table、ECharts 等重型依赖拆为 7 个独立 vendor chunk：

```js
manualChunks: {
  'vendor-vue':              ['vue', 'vue-router', 'vuex', 'vue-demi'],
  'vendor-element':          ['element-plus', '@element-plus/icons-vue'],
  'vendor-vxe':              ['vxe-table', 'vxe-pc-ui', 'xe-utils'],
  'vendor-echarts':          ['echarts'],
  'vendor-utils':            ['lodash-es', 'dayjs', 'axios'],
  'vendor-nf-design-base-elp': ['@saber/nf-design-base-elp'],
  'vendor-highlight':        ['highlight.js'],
}
```

| 指标                  | 优化前   | 优化后                     |
| --------------------- | -------- | -------------------------- |
| 构建结果              | OOM 崩溃 | 成功                       |
| 内存峰值              | 8.3 GB   | 5.4 GB（降幅 35%）         |
| 构建总耗时（esbuild） | -        | ~47s                       |
| 构建总耗时（terser）  | -        | ~77s（慢约 30s）           |
| 二次访问传输量        | 5.8 MB   | 35.9 KB（vendor 命中缓存） |

## 注意事项

- `process.once('exit')` 而非 `process.on('exit')`：watch 模式下多次重建不会重复注册监听
- 监控的是 `heapUsed`（V8 堆），实际进程内存（RSS）会更高，但 OOM 的根因就是堆撑爆，此指标足够
- 500ms 轮询间隔可能漏掉极短暂的峰值，对秒级 chunk 处理场景无影响
