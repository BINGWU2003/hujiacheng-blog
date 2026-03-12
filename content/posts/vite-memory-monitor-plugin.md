---
title: "Vite 构建内存监控插件"
date: 2026-03-12
draft: false
description: ""
tags: ["Vite", "Vue", "构建工具", "前端工程化"]
categories: ["笔记"]
---

##

用于分析 Vite/Rollup 构建过程中各阶段的内存消耗，定位 OOM 崩溃发生的具体环节。

## 使用场景

- 构建时出现 `JavaScript heap out of memory` 错误
- 想知道内存在哪个阶段暴涨
- 优化前后做内存对比

## 插件代码

在 `vite.config.js` 顶部引入 `fs`，然后将插件加入 `plugins` 数组：

```js
import fs from "fs";
import { resolve } from "path";
```

```js
// vite.config.js plugins 数组中添加（用完删除）
(() => {
  const logFile = resolve(__dirname, 'build-memory.log');
  let phase = 'init';
  let peak = 0;
  let timer = null;
  const write = msg => fs.appendFileSync(logFile, msg + '\n');
  const mb = () => process.memoryUsage().heapUsed / 1024 / 1024;

  return {
    name: 'memory-monitor',
    buildStart() {
      phase = 'buildStart';
      peak = 0;
      fs.writeFileSync(logFile, `=== 构建开始 ${new Date().toLocaleString()} ===\n`);
      timer = setInterval(() => {
        const cur = mb();
        if (cur > peak) {
          peak = cur;
          write(`[峰值更新] 阶段: ${phase} | ${cur.toFixed(1)} MB`);
        }
      }, 500);
      process.on('exit', () => {
        write(`\n[进程退出] 最后阶段: ${phase} | 峰值: ${peak.toFixed(1)} MB`);
      });
      write(`[buildStart] ${mb().toFixed(1)} MB`);
      console.log(`\n[内存] 构建开始: ${mb().toFixed(1)} MB，日志输出至 build-memory.log`);
    },
    buildEnd() {
      phase = 'buildEnd';
      write(`[buildEnd] ${mb().toFixed(1)} MB`);
    },
    renderStart() {
      phase = 'renderStart';
      write(`[renderStart] ${mb().toFixed(1)} MB`);
      console.log(`\n[内存] renderStart（代码生成开始）: ${mb().toFixed(1)} MB`);
    },
    renderChunk(_code, chunk) {
      phase = `renderChunk:${chunk.fileName}`;
    },
    generateBundle() {
      phase = 'generateBundle';
      write(`[generateBundle] ${mb().toFixed(1)} MB`);
      console.log(`\n[内存] generateBundle（产物生成）: ${mb().toFixed(1)} MB`);
    },
    closeBundle() {
      clearInterval(timer);
      write(`[closeBundle] ${mb().toFixed(1)} MB\n[内存峰值] ${peak.toFixed(1)} MB`);
      console.log(`\n[内存峰值] ${peak.toFixed(1)} MB`);
    },
  };
})(),
```

## 输出说明

构建结束后在项目根目录生成 `build-memory.log`，格式如下：

```
=== 构建开始 2026/3/12 13:00:52 ===
[buildStart] 66.5 MB
[峰值更新] 阶段: buildStart | 1017.8 MB      ← 模块解析阶段内存爬升
[buildEnd] 4234.8 MB                          ← 模块图构建完成
[renderStart] 4236.1 MB                       ← 开始代码生成
[峰值更新] 阶段: renderChunk:main.js | 5597.3 MB  ← OOM 高危阶段
[进程退出] 最后阶段: renderChunk:xxx | 峰值: 6059.4 MB  ← OOM 崩溃记录
```

> OOM 时 `process.on('exit')` 会在进程退出前最后写入一行，日志已落盘不会丢失。

## Rollup 构建阶段说明

| 阶段             | 说明                                   | 内存特征                             |
| ---------------- | -------------------------------------- | ------------------------------------ |
| `buildStart`     | 解析所有模块、构建依赖图               | 随模块数量线性增长                   |
| `buildEnd`       | 模块图构建完成                         | 内存达到第一个高峰                   |
| `renderStart`    | 开始代码生成                           | 略有上升                             |
| `renderChunk`    | 对每个 chunk 生成代码、压缩、sourcemap | **内存最高危阶段**，chunk 越大越危险 |
| `generateBundle` | 所有 chunk 生成完毕                    | 趋于稳定                             |
| `closeBundle`    | 写入磁盘，构建结束                     | 开始释放                             |

## 本项目实测数据（2026-03）

**无 manualChunks（OOM）：**

- buildStart → buildEnd：66 MB → 4234 MB（模块解析消耗 ~4 GB）
- renderChunk 阶段：4236 MB → 崩溃（>6 GB）
- 崩溃位置：`renderChunk:assets/html-!~{0jv}~.js`（所有依赖打进一个巨型 chunk）

**有 manualChunks（成功）：**

- 构建峰值：5366 MB
- 将 Element Plus、VxE Table、ECharts 等拆为 7 个独立 vendor chunk
- 二次访问缓存：传输量从 5.8 MB → 35.9 KB（降幅 99%）

## 注意事项

- 此插件仅用于临时分析，**数据收集完后删除**
- `build-memory.log` 加入 `.gitignore`，不需要提交
- `__dirname` 在 ESM 模式下不可用，需替换为 `new URL('.', import.meta.url).pathname`
