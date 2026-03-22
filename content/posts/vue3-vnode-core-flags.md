---
title: "Vue 3 VNode 核心标识解析 - type、shapeFlag 与 patchFlag"
date: 2026-03-22
draft: false
description: ""
tags: ["vue3"]
categories: ["笔记"]
---


在 Vue 3 的 Virtual DOM 架构中，每一个虚拟节点（VNode）身上都带着三个极其重要的标识属性：`type`、`shapeFlag` 和 `patchFlag`。

很多开发者容易将它们混淆，但实际上它们在 Vue 的渲染和更新流程中扮演着完全不同的角色。简而言之：**`type` 是原材料本体，`shapeFlag` 是描述结构的特征码，`patchFlag` 是指导更新的动态靶标。**

---

## 一、 `type`：我是谁？（本体形态 / 原材料）

**1. 这是用来做什么的？**
`type` 决定了当前这个虚拟节点在真实世界中到底是个什么东西。它是渲染器真正去创建真实 DOM 或实例化组件时所依赖的“图纸本体”。

**2. 核心特点：**
它是天生的，是在编写代码或模板编译时就确定的最原始参数。

**3. 形态分类与代码示例：**

* **原生 HTML 元素（String）：**
    ```javascript
    // 模板: <div id="app"></div>
    // 生成的 VNode 核心结构:
    const vnode = {
      type: 'div', // 纯字符串
      props: { id: 'app' }
    }
    ```
* **Vue 自定义组件（Object）：**
    ```javascript
    import MyButton from './MyButton.vue'
    
    // 模板: <MyButton />
    // 生成的 VNode 核心结构:
    const vnode = {
      type: MyButton, // 引入的组件配置对象本体
      props: null
    }
    ```
* **特殊节点（Symbol）：**
    纯文本、Fragment（多根节点碎片）、注释等。
    ```javascript
    import { Text, Fragment } from 'vue'
    
    const textVnode = { type: Text, children: '纯文本内容' }
    const fragmentVnode = { type: Fragment, children: [...] }
    ```

---

## 二、 `shapeFlag`：我长啥样？（结构特征码）

**1. 这是用来做什么的？**
用于**极速判断节点的自身类型和子节点类型**。Vue 在渲染节点时，不需要做低效的 `typeof vnode.type === 'string'` 判断，而是直接通过二进制位运算（`&`）扫描 `shapeFlag` 这个“条形码”，瞬间决定走哪条渲染分支（比如是挂载普通元素还是挂载组件）。

**2. 核心特点：**
它是**算出来**的。在创建 VNode 的瞬间（执行 `createVNode` 时），Vue 内部根据传入的 `type` 和 `children`，通过**按位或（`|`）**运算贴上的结构标签。

**3. 代码示例：**

```javascript
// Vue 内部定义的 ShapeFlags 字典 (基于二进制)
const ShapeFlags = {
  ELEMENT: 1,            // 0000 0001 (普通元素)
  STATEFUL_COMPONENT: 4, // 0000 0100 (有状态组件)
  TEXT_CHILDREN: 8,      // 0000 1000 (子节点是文本)
  ARRAY_CHILDREN: 16     // 0001 0000 (子节点是数组)
}

// 【场景】：创建一个包含纯文本的 div
// createVNode('div', null, 'hello') 内部逻辑演示：
let shapeFlag = 0;

// 1. 判断 type 是字符串 -> 标记为普通元素
shapeFlag = ShapeFlags.ELEMENT; // 二进制 0001

// 2. 判断 children 是字符串 -> 叠加文本子节点标记
shapeFlag = shapeFlag | ShapeFlags.TEXT_CHILDREN; // 0001 | 1000 = 1001 (十进制 9)

const vnode = {
  type: 'div',
  shapeFlag: 9 // 最终生成的特征码
}

// 【使用场景】：渲染器读取特征码
if (vnode.shapeFlag & ShapeFlags.ELEMENT) {
  // 命中！瞬间知道这是个 HTML 元素，去执行 mountElement
}
```

---

## 三、 `patchFlag`：我哪里会变？（动态更新靶标）

**1. 这是用来做什么的？**
这是 Vue 3 **靶向更新（极速 Diff）的绝对核心**。它告诉运行时的 Diff 算法：“这个节点只有哪些属性是动态绑定的”。Diff 算法扫描到这个标记后，会直接跳过所有静态属性，只比对标记指出的动态部分。

**2. 核心特点：**
它是**编译器（Compiler）在编译阶段静态分析出来**的。只有使用了模板编译，或者手写渲染函数时手动传入，VNode 才会带上这个精准的补丁标记。

**3. 代码示例：**

```javascript
// Vue 内部定义的 PatchFlags 字典 (基于二进制)
const PatchFlags = {
  TEXT: 1,   // 0001 (动态文本)
  CLASS: 2,  // 0010 (动态 class)
  STYLE: 4   // 0100 (动态 style)
}

// 【场景】：模板编译 <div :class="dynamicClass">{{ dynamicText }}</div>
// 编译器发现 class 和 文本 是动态的，算出 patchFlag：
// 1 (TEXT) | 2 (CLASS) = 3 (二进制 0011)

const vnode = {
  type: 'div',
  patchFlag: 3 // 编译器塞进来的动态靶标
}

// 【使用场景】：Diff 算法更新时
if (vnode.patchFlag & PatchFlags.CLASS) {
  // 命中！只去比对和更新 class，其他 style、id 之类的静态属性直接无视！
}
if (vnode.patchFlag & PatchFlags.TEXT) {
  // 命中！去更新内部文本
}
```

---

## 终极对比总结表

| 属性 | 核心比喻 | 来源与时机 | 主要作用阶段 | 解决的核心问题 |
| :--- | :--- | :--- | :--- | :--- |
| **`type`** | **原材料图纸** (决定是什么) | 开发者编写 / 模板解析提取 | 全生命周期 | 告诉渲染器要调用什么原生 API 或组件逻辑来创建实体。 |
| **`shapeFlag`** | **体貌特征条形码** (决定怎么建) | 运行时 `createVNode` 阶段动态计算 | **挂载阶段 (Mount)** / 初次渲染 | 替换低效的 `typeof` 类型推断，用极速的位运算决定渲染分支。 |
| **`patchFlag`** | **动态诊断更新单** (决定修哪里) | 编译阶段静态分析生成 | **更新阶段 (Patch / Diff)** | 指导 Diff 算法跳过全量比对，实现按图索骥的“靶向更新”。 |
