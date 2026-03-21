---
title: "Vue 3 响应式原理与 Proxy/Reflect 核心机制学习笔记"
date: 2026-03-21
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 一、 Vue 3 响应式核心基础

Vue 3 的响应式系统放弃了 Vue 2 的 `Object.defineProperty`，全面拥抱了 ES6 的 **Proxy** 和 **Reflect** API。

### 1. 核心流程：拦截 -> 收集 -> 派发
* **拦截 (Proxy)**：使用 `Proxy` 包装原始对象，拦截对对象属性的读取（`get`）、设置（`set`）、删除等操作。
* **依赖收集 (Track)**：在 `get` 拦截器中，记录当前正在执行的副作用函数（如组件渲染函数、`computed`、`watch`），将其与当前读取的属性建立联系。
* **派发更新 (Trigger)**：在 `set` 拦截器中，当属性值发生改变时，找到并重新执行依赖于该属性的所有副作用函数。

### 2. 依赖存储的数据结构
Vue 3 使用了三重数据结构来精细管理依赖，并防止内存泄漏：
`WeakMap { target (原始对象) -> Map { key (属性名) -> Set [ effect1, effect2... ] (副作用函数) } }`
* **WeakMap**：键为原始对象。当对象不再被引用时，可被垃圾回收，避免内存泄漏。
* **Map**：管理对象下的每一个具体属性。
* **Set**：存储依赖于该属性的副作用函数，自动去重。

---

## 二、 核心探究：为什么要使用 Reflect？

在仅仅使用 `Proxy` 的情况下，确实可以拦截大部分对象操作。但是，当遇到**对象内部包含基于 `this` 的 Getter 属性**或**涉及原型链继承**时，如果不使用 `Reflect`，会导致严重的**“`this` 指向错误”**，进而引发**“依赖收集丢失”**的致命问题。

### 1. 场景重现：带有 Getter 的普通对象
假设我们有以下对象：
```javascript
const rawUser = {
  firstName: '张',
  lastName: '三',
  // 注意：这里用到了 this 来依赖同对象内的其他属性
  get fullName() {
    return this.firstName + this.lastName;
  }
};
```

### 2. 错误做法：只用 Proxy (导致响应式失效)
```javascript
const proxyWithoutReflect = new Proxy(rawUser, {
  get(target, key, receiver) {
    // 错误写法：直接返回目标对象上的属性
    return target[key]; 
  }
});
```
**运行机制与问题**：
当访问 `proxyWithoutReflect.fullName` 时，触发 `get` 拦截。引擎执行 `return target['fullName']`。
此时，去执行原始对象 `rawUser` 上的 getter。**在这个 getter 内部，`this` 指向的是 `rawUser`（原始对象），而不是代理对象！**
因此，后续读取 `this.firstName` 时，直接访问了原始对象，**完全绕过了 Proxy 的拦截**。Vue 无法知道 `fullName` 依赖了 `firstName`，数据修改时视图将不会更新。

### 3. 正确做法：Proxy + Reflect (完美追踪)
```javascript
const proxyWithReflect = new Proxy(rawUser, {
  get(target, key, receiver) {
    // 正确写法：使用 Reflect 透传 receiver
    return Reflect.get(target, key, receiver); 
  }
});
```
**原理解析：`receiver` 的上下文劫持**
* `Reflect.get(target, key, receiver)` 的核心作用是：**如果 `target[key]` 是一个 getter，它会强制将该 getter 调用时的 `this` 指向 `receiver`。**
* `receiver` 在这里代表**最初触发这次读取操作的对象**（也就是我们的代理对象 Proxy 实例）。
* 因此，当 getter 内部执行 `this.firstName` 时，等同于访问 `代理对象.firstName`。
* 这会**再次触发 Proxy 的 `get` 拦截器**，让 Vue 能够完美收集到 `firstName` 和 `lastName` 的依赖，不留死角。

---

## 三、 与 Vue 3 实际用法的对应关系

在上述 `rawUser` 例子中，`get fullName()` 这种原生 JavaScript 的 Getter 机制，在 Vue 3 中主要对应以下两种情况：

### 1. 传递给 `reactive` 的原生 Getter
你可以直接把这个对象传给 `reactive`。由于 Vue 底层使用了 `Reflect` 保证了正确的 `this` 指向，这种写法可以完美实现响应式。
```javascript
import { reactive } from 'vue';

const user = reactive({
  firstName: '张',
  lastName: '三',
  get fullName() { 
    return this.firstName + this.lastName;
  }
});
// 视图中使用 user.fullName，当修改 user.firstName 时会自动更新
```

### 2. 概念层面的对应：计算属性 (`computed`)
从框架功能设计的角度来看，对象里的 Getter 对应的就是 Vue 中的 **`computed`（计算属性）**，即“基于已有的状态，派生出新的状态”。

```javascript
import { reactive, computed } from 'vue';

const user = reactive({ firstName: '张', lastName: '三' });
// 对应的功能实现
const fullName = computed(() => user.firstName + user.lastName);
```

**两者区别：**
* **每次触发计算 vs 缓存：** 原生对象的 Getter 每次被读取时都会重新执行里面的逻辑。而 Vue 的 `computed` 具有**缓存机制**，只要依赖的数据（如 `firstName`）没有改变，多次访问 `fullName` 只会返回上一次计算好的缓存结果，性能更优。

---
**💡 核心总结：** Vue 3 响应式的强大之处在于细节的严谨。`Proxy` 负责建立拦截的围墙，而 `Reflect` 负责传递正确的 `this` 钥匙，两者结合，才保证了任意深度的属性访问和内部依赖都能被框架精准捕捉。