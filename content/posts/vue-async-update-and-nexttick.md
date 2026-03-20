---
title: "Vue 核心原理解析笔记：异步更新队列 `queueJob` 与 `nextTick`"
date: 2026-03-20
draft: false
description: ""
tags: ["Vue"]
categories: ["笔记"]
---

## 💡 核心认知：Vue 的 DOM 更新是异步的！
在 Vue 中，当我们修改了响应式数据（例如 `msg.value = 'Hello'`），DOM 并不会立刻发生改变。
为了避免频繁修改数据导致无意义的重复渲染，Vue 引入了**异步更新队列**机制。它会把同一个事件循环（Event Loop）中所有的状态改变缓冲起来，然后在一个**微任务（MicroTask）**中统一执行真实的 DOM 更新。

这个机制背后的核心引擎就是 `queueJob`，而留给开发者对接这个机制的桥梁就是 `nextTick`。



---

## ⚙️ 第一部分：幕后引擎 —— `queueJob` (主任务队列)

`queueJob` 是 Vue 源码中调度器（Scheduler）的核心函数之一，专门用来**管理组件的渲染更新任务（Render Effects）**。

### `queueJob` 的三大核心机制：

1. **去重（Deduplication）：避免重复渲染**
   当你写下 `a=1; a=2; a=3;` 时，触发了三次更新请求。`queueJob` 内部会通过任务的唯一标识（通常是组件实例）进行比对。如果队列中已经存在相同的任务，直接丢弃。最终组件只会因为 `a=3` 重新渲染一次。
2. **微任务缓冲（Microtask Batching）：等待同步代码结束**
   把收集到的更新任务放入一个数组（主队列）中，并开启一个 `Promise.resolve().then(flushJobs)` 的微任务。这意味着：**所有的 DOM 更新动作，都会被迫推迟到当前所有的同步代码执行完毕之后才发生。**
3. **排序壁垒（Sorting）：保证父子渲染顺序**
   在微任务开始真正执行（`flushJobs`）之前，Vue 必须对队列按照组件 ID 进行**升序排序**。
   * **原因：** Vue 规定组件的更新必须由外向内（父组件 -> 子组件）。防止子组件先更新了，随后父组件又把它销毁了，造成无用功甚至报错。

---

## 🌉 第二部分：开发者利器 —— `nextTick`

由于 DOM 更新被 `queueJob` 塞进了微任务里排队，这就导致我们在同步代码中修改数据后，立刻去获取 DOM 元素，拿到的永远是**旧的 DOM**。
**`nextTick` 就是用来把你的代码，精准地排在 DOM 更新微任务之后执行的工具。**

### `nextTick` 的底层逻辑（极简模拟）：
```javascript
const resolvedPromise = Promise.resolve()
let currentFlushPromise = null // 指向当前正在更新 DOM 的那个微任务

export function nextTick(fn) {
  // 核心：优先搭 Vue DOM 更新的“顺风车”，没有就自己开一个新微任务
  const p = currentFlushPromise || resolvedPromise
  return fn ? p.then(fn) : p
}
```

### 运行流程图解：
1. `msg.value = '新值'` $\rightarrow$ 触发 `queueJob` $\rightarrow$ 产生微任务 A（负责更新 DOM）。
2. `await nextTick()` $\rightarrow$ 产生微任务 B，紧紧排在微任务 A 的后面。
3. 同步代码结束 $\rightarrow$ 执行微任务 A（DOM 变成新值） $\rightarrow$ 执行微任务 B（你安全地拿到了新 DOM）。

---

## 🛠️ 第三部分：`nextTick` 的三大经典业务场景

凡是符合 **“改数据 $\rightarrow$ 触发 DOM 结构或尺寸变化 $\rightarrow$ 立刻操作新 DOM”** 这个模式的，都必须使用 `nextTick`。

### 场景 1：`v-if` 元素显示后立刻获取焦点
* **问题：** 点击“编辑”，输入框通过 `v-if` 渲染，此时同步执行 `input.focus()` 会报错 `Cannot read property 'focus' of null`，因为此时真实 DOM 树里还没有这个 input。
* **解法：** `isEditing.value = true; await nextTick(); input.value.focus();`

### 场景 2：聊天室/列表动态添加数据后自动滚动到最底部
* **问题：** 数组 `push` 新消息后，立刻获取容器的 `scrollHeight` 赋值给 `scrollTop`。此时拿到的是**添加新消息前**的高度，导致滚动永远差一行。
* **解法：** `list.push(msg); await nextTick(); box.scrollTop = box.scrollHeight;`

### 场景 3：基于动态挂载的 DOM 初始化第三方库（如 ECharts）
* **问题：** 接口请求完毕，标记 `v-if="true"` 渲染图表容器。立刻执行 `echarts.init(dom)` 时，因为 DOM 还未渲染或尺寸尚未被 CSS 撑开，导致找不到节点或图表变成 $0 \times 0$。
* **解法：** 修改标记后，调用 `await nextTick()`，等待容器在页面上占据了真实的物理空间后，再进行 `init` 初始化。

---

## 📝 总结

| 概念 | 角色定位 | 运行机制 | 核心目的 |
| :--- | :--- | :--- | :--- |
| **`queueJob`** | **幕后引擎** (Vue 框架内部使用) | 利用唯一标识去重、按组件层级排序，并推入 `Promise` 微任务队列执行。 | 批量合并 DOM 更新操作，最大化提升渲染性能，防止页面频繁重绘。 |
| **`nextTick`** | **开发者工具** (暴露给开发者的 API) | 将回调函数挂载到 DOM 更新的微任务 Promise 链之后，或创建一个新的后置微任务。 | 消除异步渲染带来的时间差，让开发者能够安全地获取和操作最新状态的 DOM。 |