---
title: "Node.js 性能优化实践"
date: 2026-01-20
draft: false
description: "总结 Node.js 项目中常见的性能问题和优化方案。"
tags: ["Node.js", "性能优化", "后端"]
categories: ["后端开发"]
---

## 事件循环优化

避免阻塞事件循环是 Node.js 性能优化的核心原则。

### 避免同步操作

```javascript
// ❌ 不推荐
const data = fs.readFileSync("/path/to/file");

// ✅ 推荐
const data = await fs.promises.readFile("/path/to/file");
```

### CPU 密集型任务

对于 CPU 密集型任务，使用 Worker Threads：

```javascript
import { Worker, isMainThread, parentPort } from "worker_threads";

if (isMainThread) {
  const worker = new Worker(new URL(import.meta.url));
  worker.on("message", (result) => {
    console.log("计算结果:", result);
  });
  worker.postMessage({ data: largeArray });
} else {
  parentPort.on("message", ({ data }) => {
    const result = heavyComputation(data);
    parentPort.postMessage(result);
  });
}
```

## 内存管理

### 流式处理大文件

```javascript
import { createReadStream, createWriteStream } from "fs";
import { pipeline } from "stream/promises";
import { createGzip } from "zlib";

await pipeline(
  createReadStream("input.log"),
  createGzip(),
  createWriteStream("input.log.gz"),
);
```

## 缓存策略

```javascript
import NodeCache from "node-cache";

const cache = new NodeCache({ stdTTL: 300 });

async function getUserById(id) {
  const cached = cache.get(`user:${id}`);
  if (cached) return cached;

  const user = await db.users.findById(id);
  cache.set(`user:${id}`, user);
  return user;
}
```

性能优化是一个持续的过程，关键是找到瓶颈并针对性地解决。
