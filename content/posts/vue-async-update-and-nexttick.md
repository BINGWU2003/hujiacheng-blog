---
title: "Vue nextTick 深度解析"
date: 2026-04-15
draft: false
description: ""
tags: ["Vue", "源码解析"]
categories: ["笔记"]
---

## 一、是什么

`nextTick` 是 Vue 提供的一个工具函数，用于在**下一次 DOM 更新完成后**执行回调。

```ts
// 两种等价写法
nextTick(() => { console.log(el.value.textContent) })

await nextTick()
console.log(el.value.textContent)
```

---

## 二、核心源码（Vue 3）

```ts
// packages/runtime-core/src/scheduler.ts

const resolvedPromise = Promise.resolve()
let currentFlushPromise: Promise<void> | null = null

export function nextTick(fn?) {
  const p = currentFlushPromise || resolvedPromise
  return fn ? p.then(fn) : p
}
```

只有 5 行，没有任何队列操作，本质是一个 **Promise `.then()` 的挂载点**。

---

## 三、调度系统全貌

`nextTick` 并不孤立，它依附于 Vue 的整个调度器体系，核心由三部分组成：

### 3.1 两个队列

```ts
const queue: SchedulerJob[] = []          // 主队列
let pendingPostFlushCbs: SchedulerJob[] = [] // post 队列
```

| 队列 | 写入方式 | 使用者 | 执行时机 |
|---|---|---|---|
| 主队列 | `queueJob(job)` | 组件更新、`watch pre` | patch **之前** |
| post 队列 | `queuePostFlushCb(job)` | `watch post`、`onUpdated` | patch **之后** |

### 3.2 队列触发

`queueJob` 和 `queuePostFlushCb` 最终都会调用 `queueFlush`：

```ts
function queueFlush() {
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true
    // 把整次 flush 包成一个 Promise，赋给 currentFlushPromise
    currentFlushPromise = resolvedPromise.then(flushJobs)
  }
}
```

这一步是关键：`currentFlushPromise` 就是 `nextTick` 挂载的目标。

### 3.3 flushJobs 执行结构

```ts
function flushJobs() {
  // ① 主队列：按 job.id 排序（父组件先于子组件）
  queue.sort(comparator)
  for (flushIndex = 0; flushIndex < queue.length; flushIndex++) {
    queue[flushIndex]()   // pre watch 回调 + 组件 patch
  }

  // ② post 队列：所有 patch 完成后执行
  flushPostFlushCbs()     // post watch 回调 + onUpdated

  isFlushing = false
  currentFlushPromise = null

  // ③ 如果 flush 过程中产生了新 job，递归再 flush
  if (queue.length || pendingPostFlushCbs.length) {
    flushJobs()
  }
}
```

---

## 四、三者执行顺序

```
响应式数据变更
      │
      ├── queueJob          → 主队列
      ├── queuePostFlushCb  → post 队列
      │
      │   [同步代码继续，可能多次变更，统一去重入队]
      │
      ↓ 同步代码结束，微任务开始

  flushJobs()
    │
    ├── ① 主队列（pre watch 回调 + 组件 patch）
    │
    └── ② post 队列（post watch 回调 + onUpdated）
    
  flushJobs 完成，currentFlushPromise resolved
    │
    └── ③ nextTick(fn) 的回调执行   ← 始终在最后
```

**优先级**：`queueJob` < `queuePostFlushCb` < `nextTick`

---

## 五、watch 与两个队列的关系

`watch` 的 `flush` 选项直接决定使用哪个队列：

```ts
// doWatch 内部的 scheduler 构造逻辑
if (flush === 'sync') {
  scheduler = job                          // 不入队，同步执行

} else if (flush === 'post') {
  scheduler = () => queuePostFlushCb(job)  // 进 post 队列

} else {
  // 默认 'pre'
  job.pre = true
  job.id = instance.uid
  scheduler = () => queueJob(job)          // 进主队列
}
```

```ts
// ❌ 默认 flush:'pre'，DOM 还未 patch
watch(count, () => {
  console.log(el.value.textContent) // 旧 DOM
})

// ✅ flush:'post'，DOM 已 patch
watch(count, () => {
  console.log(el.value.textContent) // 新 DOM
}, { flush: 'post' })

// ✅ 等价语法糖
watchPostEffect(() => {
  console.log(el.value.textContent)
})
```

---

## 六、Vue 2 vs Vue 3

| | Vue 2 | Vue 3 |
|---|---|---|
| 微任务方案 | Promise → MutationObserver → setImmediate → setTimeout 降级 | 纯 Promise，不降级 |
| 原因 | 需兼容 IE | Vue 3 放弃 IE，保证有 Promise |
| 队列管理 | `nextTick` 内维护 `callbacks[]` | 独立 `scheduler.ts`，`queueJob` 管理 |

Vue 2 降级链（历史包袱）：

```js
if (typeof Promise !== 'undefined') {
  timerFunc = () => Promise.resolve().then(flushCallbacks)
} else if (typeof MutationObserver !== 'undefined') {
  // 用 MO 触发微任务
} else if (typeof setImmediate !== 'undefined') {
  timerFunc = () => setImmediate(flushCallbacks)
} else {
  timerFunc = () => setTimeout(flushCallbacks, 0)
}
```

---

## 七、常见问题

**Q：没有响应式更新时，nextTick 还有效吗？**

有效。此时 `currentFlushPromise` 为 `null`，退化为 `Promise.resolve().then(fn)`，下一个微任务立即执行。

**Q：连续多次修改数据，会触发多次渲染吗？**

不会。`queueJob` 有入队去重逻辑（`queue.includes(job)`），同一组件的更新任务只入队一次。

**Q：nextTick 和 setTimeout 的区别？**

`nextTick` 是**微任务**，`setTimeout` 是**宏任务**。微任务在当前宏任务结束后、下一个宏任务开始前执行，时机更早、响应更及时。

---

## 八、一句话总结

> `queueJob` 和 `queuePostFlushCb` 负责往队列里放任务，`queueFlush` 把这次 flush 包成一个 `currentFlushPromise`，`nextTick` 则挂在这个 Promise 的 `.then()` 上——不入队，只等队列跑完，所以始终能拿到最新的 DOM。