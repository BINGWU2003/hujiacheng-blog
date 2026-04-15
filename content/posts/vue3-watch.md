---
title: "Vue watch 源码解析"
date: 2026-04-15
draft: false
description: ""
tags: ["Vue", "源码解析"]
categories: ["笔记"]
---

## 一、整体链路

`watch` 本质是对 `ReactiveEffect` 的封装，完整链路如下：

```
watch(source, cb)
  → 规范化 source 为 getter 函数
    → new ReactiveEffect(getter, scheduler)
      → effect.run() 首次执行 getter，触发 track 收集依赖
        → 数据变化 → trigger → scheduler → queueJob
          → nextTick → job() → cb(newVal, oldVal, onCleanup)
```

---

## 二、`doWatch`：核心实现

`watch` 和 `watchEffect` 都收敛到内部函数 `doWatch`，区别在于有没有 `cb`。

### 2.1 规范化 source → getter

不同类型的 source 被统一转换为一个 getter 函数：

```ts
if (isRef(source)) {
  getter = () => source.value           // ref → 读 .value
} else if (isReactive(source)) {
  getter = () => source
  deep = true                           // reactive 默认深度监听
} else if (isArray(source)) {
  getter = () => source.map(s => { ... }) // 遍历每个 source
} else if (isFunction(source)) {
  getter = source                       // 函数直接作为 getter
}
```

### 2.2 deep 的惰性包装

开启 `deep` 时，不会立即执行 getter，只是用 `traverse` 做一层包装：

```ts
if (deep) {
  const baseGetter = getter             // 闭包捕获原始 getter
  getter = () => traverse(baseGetter()) // 替换为新函数，不执行
}
```

真正的执行推迟到 `effect.run()` 调用 `getter` 时才发生：

```
effect.run()
  → getter()
    → traverse(baseGetter())
      → baseGetter() 访问 source 顶层   → 触发 track
      → traverse 递归访问所有子属性      → 触发每一层 track
```

`traverse` 内部通过递归访问对象所有属性（触发 `get` trap）来完成深度依赖收集，并用 `Set` 防止循环引用。

### 2.3 创建 ReactiveEffect + scheduler

```ts
const effect = new ReactiveEffect(getter, scheduler)
// ↑ 仅初始化挂载属性，不执行 getter
```

`scheduler` 决定依赖变化后 `job` 的执行时机：

| flush | 执行时机 |
|-------|---------|
| `'pre'`（默认） | 组件更新前，`queueJob` 入队 |
| `'post'` | 组件更新后，`queuePostFlushCb` 入队，DOM 已是新的 |
| `'sync'` | 数据变化时同步立即执行，不入队 |

### 2.4 首次执行：依赖收集

构造完 `ReactiveEffect` 后，依赖收集发生在显式的 `effect.run()` 调用：

```ts
if (cb) {
  if (immediate) {
    job()                   // immediate: 立即执行，触发 cb
  } else {
    oldValue = effect.run() // 只跑 getter 收集依赖，记录初始值，不触发 cb
  }
} else {
  effect.run()              // watchEffect: 立即跑，收集依赖，执行副作用
}
```

---

## 三、数据变化触发链路

```
setter 被调用
  → trigger(target, key)
    → 遍历 dep 中所有 effect
      → effect.scheduler 存在 → 调用 scheduler
        → queueJob(job)
          → nextTick flush
            → job()
              → effect.run() 执行 getter，获取新值
                → hasChanged(newVal, oldVal)
                  → cb(newVal, oldVal, onCleanup)
```

---

## 四、cleanup 机制

### 闭包结构

`cleanup`、`job`、`onCleanup` 三者都定义在 `doWatch` 的词法作用域内：

```
doWatch 词法作用域
│
├── cleanup  ◄─────────────────────────┐
│                                      │
├── onCleanup = (fn) => { cleanup = fn } ← 写入（在 cb 外部调用）
│
└── job = () => { cleanup?.() ... }    ← 读取（在 scheduler 外部调用）
```

`job` 和 `onCleanup` 各自形成闭包，捕获的是**同一个 `cleanup` 变量**，所以 `onCleanup` 写入的值，`job` 下次执行时能直接读到。

### 多次触发时的执行顺序

```
prop 第 1 次变化
  → job()
    → cleanup 为 undefined，跳过
    → cb(newVal, oldVal, onCleanup)
      → 用户调用 onCleanup(() => controller.abort())
        → cleanup = () => controller.abort()   // 存入闭包

prop 第 2 次变化
  → job()
    → cleanup() → controller.abort()           // 取消上一次未完成的请求
    → cb(newVal, oldVal, onCleanup)
      → 用户再次调用 onCleanup(...)
        → cleanup = 新的清理函数               // 覆盖闭包引用
```

`cleanup` 本质上是一个**单槽位存储**：每次 job 执行时先消费上一次的，再让这次的 cb 写入新的。

### 典型场景

```ts
watch(() => state.keyword, (keyword, _, onCleanup) => {
  const controller = new AbortController()

  onCleanup(() => {
    controller.abort() // 下次触发前取消本次未完成的请求
  })

  fetch(`/api/search?q=${keyword}`, { signal: controller.signal })
    .then(res => res.json())
    .then(data => { result.value = data })
})
```

---

## 五、`watch` vs `watchEffect` 对比

| | `watch` | `watchEffect` |
|--|---------|---------------|
| cb | 有，数据变化后调用 | 无，getter 本身就是副作用 |
| oldValue / newValue | ✅ | ❌ |
| 首次是否触发 cb | 默认否，`immediate: true` 才触发 | 立即执行 |
| 依赖收集方式 | 显式指定 source | 自动收集 getter 内访问的依赖 |
| deep | 手动配置 | 不适用 |

---

## 六、关键结论

| 问题 | 答案 |
|------|------|
| `watch` 怎么收集依赖？ | `effect.run()` 执行 getter，访问响应式数据触发 `track` |
| 构造 `ReactiveEffect` 时会执行 getter 吗？ | 不会，只初始化实例，依赖收集在之后显式调用 `effect.run()` 时发生 |
| `deep: true` 怎么实现？ | `traverse` 递归访问所有属性，触发每一层 `get` trap，`if (deep)` 块本身不执行 getter |
| 为什么默认是异步的？ | scheduler 走 `queueJob`，在 nextTick 微任务中批量执行，避免同一 tick 多次触发 |
| cleanup 为什么能跨次调用共享？ | `job` 和 `onCleanup` 共同闭包捕获了 `doWatch` 词法作用域中的同一个 `cleanup` 变量 |
