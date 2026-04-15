---
title: "Vue computed 源码解析"
date: 2026-04-15
draft: false
description: ""
tags: ["Vue", "源码解析"]
categories: ["笔记"]
---

## 1. 创建阶段：lazy 的本质

`computed()` 接收 getter，把它包装成一个带 scheduler 的 `ReactiveEffect`，但**不会立即执行 getter**。

```js
// packages/reactivity/src/computed.ts
export function computed(getter) {
  const cEffect = new ReactiveEffect(getter, () => {
    // scheduler：依赖变化时执行，但不重跑 getter
    if (!cEffect.dirty) {
      cEffect.dirty = true
      triggerRefValue(cRef)
    }
  })

  const cRef = {
    _value: undefined,
    get value() {
      trackRefValue(cRef)       // 收集「谁在用我」
      if (cEffect.dirty) {      // 只有 dirty 时才重新计算
        cEffect.dirty = false
        cRef._value = cEffect.run()
      }
      return cRef._value
    }
  }
}
```

**lazy = 不主动执行，等被读取时才执行。** 

仅仅创建 `computed(() => state.prop + 'hi')` 不会触发 getter，`state.prop` 的 dep 里也不会记录这个 effect，即使之后修改 `state.prop` 也不会有任何响应。只有第一次读取 `.value` 时，getter 才执行，依赖才被收集。

---

## 2. 两个方向的依赖收集

首次读取 `.value` 时，getter 内部同时进行两个方向的依赖收集：

```
computed.value 被读取
  │
  ├── trackRefValue(cRef)         ← 方向①：收集「谁在用我」
  │     activeEffect（如渲染函数）→ cRef.dep
  │
  └── cEffect.run()               ← 方向②：收集「我依赖了谁」
        activeEffect = cEffect
        读取 state.prop → state.prop 的 dep.add(cEffect)
```

| | 目的 | 收集的是 |
|---|---|---|
| `trackRefValue` | 上游订阅 | 当前读取 `.value` 的那个 effect（如渲染函数） |
| `cEffect.run()` | 下游依赖 | getter 内部用到的 `state.prop` 等响应式数据 |

两者缺一不可：`trackRefValue` 建立「computed → 上层消费者」的联系，`cEffect.run()` 建立「底层 state → computed」的联系。

---

## 3. dirty 标志位与缓存

`dirty` 充当一个**缓存有效位**，控制是否复用上次的计算结果：

```
① 创建时          dirty = true    （未计算过，缓存无效）
② 首次读取        run() → dirty = false    （结果存入 _value，缓存建立）
③ 依赖变化        scheduler → dirty = true （缓存失效，但不立即重算）
④ 再次读取        dirty === true → run() → dirty = false    （重算，缓存重建）
```

**缓存 = `dirty` 为 false 时，多次读取 `.value` 直接返回 `_value`，getter 一次都不执行。**

scheduler 里只标脏、不重算，是因为 computed 是懒的——依赖变了但没人读，重算也没有意义。

---

## 4. 依赖变化后的完整更新链路

```
state.prop = newVal
  │
  ▼
proxy setter → trigger(state, 'prop')
  │
  ▼
遍历 dep → 执行 cEffect 的 scheduler()
  │
  ├── dirty = true           （标脏，缓存失效）
  └── triggerRefValue(cRef)  （通知 cRef.dep 里的上层 effect）
        │
        ▼
      渲染 effect 推入调度队列（异步，微任务）
        │
        ▼（同步代码执行完毕后）
      flushJobs() → 渲染 effect 执行
        │
        ▼
      读取 computed.value
        │
        ├── dirty === true → cEffect.run() → getter 重新执行
        └── 返回新值，dirty = false
```

---

## 5. 异步调度：批量更新的基础

渲染 effect 使用异步调度器，被触发时推入微任务队列，而非立即执行：

```js
// 渲染 effect 的 scheduler
() => queueJob(effect)

function queueJob(job) {
  if (!queue.includes(job)) queue.push(job)
  queueFlush()
}

function queueFlush() {
  if (!isFlushing) {
    isFlushing = true
    Promise.resolve().then(flushJobs)  // 微任务，同步代码跑完再执行
  }
}
```

这也是 `state.prop` 连续赋值两次，getter 只执行一次的根本原因：

```
── 同步 ─────────────────────────────────────
state.prop = 'a'
  → scheduler: dirty=true, 渲染 effect 推入队列

state.prop = 'b'
  → scheduler: dirty 已是 true，if (!dirty) 守卫拦截，什么都不做

── 微任务 ───────────────────────────────────
flushJobs()
  → 渲染 effect 执行，读取 computed.value
  → dirty===true → run() → 拿到最终值 'b'
```

`if (!cEffect.dirty)` 这个守卫同时解决了两个问题：同一依赖多次触发时只标脏一次，上层 effect 也只进入调度队列一次。

---

## 6. 三个核心概念对比

| 概念 | 含义 | 发生时机 |
|---|---|---|
| **lazy** | 创建时不执行 getter，等读取 `.value` 才执行 | 首次 `.value` 读取 |
| **缓存** | `dirty=false` 时跳过 `run()`，直接返回 `_value` | 每次 `.value` 读取 |
| **异步调度** | 渲染 effect 推入微任务队列，同步代码跑完后批量执行 | 依赖变化触发上层 effect |

---

## 7. 与 `watchEffect` 的对比

```js
// watchEffect：flush: 'sync' 模式下同步执行，不合并
watchEffect(() => {
  console.log(computed.value)
}, { flush: 'sync' })

state.prop = 'a'   // 立即执行，打印 'a'
state.prop = 'b'   // 立即执行，打印 'b'
```

默认异步模式下，`watchEffect` 和渲染 effect 一样走微任务队列，两次赋值只触发一次回调，拿到最终值 `'b'`。