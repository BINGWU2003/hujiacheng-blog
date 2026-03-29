---
title: "ESM 与 CommonJS 深度对比"
date: 2026-03-29
draft: false
description: "从语法、加载机制、静态分析、循环依赖、Tree Shaking、互操作性等多个维度，深度剖析 ESM 与 CommonJS 的核心区别，并结合实际开发场景给出最佳实践建议。"
tags: ["JavaScript", "Node.js", "模块化"]
categories: ["笔记"]
---

ES Modules（ESM）是 JavaScript 语言规范层面的官方模块系统，而 CommonJS（CJS）是 Node.js 早期设计并沿用至今的事实标准。两者在语法、加载时机、作用域、Tree Shaking 等方面存在根本性的差异。理解这些差异是做好前端工程化的基础。

---

## 目录

- [一、语法层面](#一语法层面)
- [二、加载时机：静态 vs 动态](#二加载时机静态-vs-动态)
- [三、导出值的本质：引用 vs 拷贝](#三导出值的本质引用-vs-拷贝)
- [四、顶层 `this` 的指向](#四顶层-this-的指向)
- [五、严格模式](#五严格模式)
- [六、文件扩展名与 `package.json` 的 `type` 字段](#六文件扩展名与-packagejson-的-type-字段)
- [七、循环依赖的处理方式](#七循环依赖的处理方式)
- [八、Tree Shaking 支持](#八tree-shaking-支持)
- [九、异步加载与顶层 `await`](#九异步加载与顶层-await)
- [十、互操作性（Interop）](#十互操作性interop)
- [十一、综合对比表](#十一综合对比表)
- [十二、最佳实践建议](#十二最佳实践建议)

---

## 一、语法层面

### CommonJS

CommonJS 使用 `require()` 引入模块，使用 `module.exports` 或 `exports` 导出。

```js
// math.js —— 导出
const add = (a, b) => a + b;
const PI = 3.14159;

module.exports = { add, PI };

// 也可以逐个挂载
// exports.add = add;
// exports.PI = PI;
```

```js
// main.js —— 引入
const { add, PI } = require('./math');
const math = require('./math'); // 也可整体引入

console.log(add(1, 2)); // 3
console.log(PI);        // 3.14159
```

`require()` 是一个普通的函数调用，可以出现在任意位置，甚至可以放在条件语句或循环中：

```js
if (process.env.NODE_ENV === 'development') {
  const devTool = require('./devTool');
  devTool.init();
}
```

### ESM

ESM 使用 `import` 引入模块，使用 `export` 导出。

```js
// math.js —— 具名导出
export const add = (a, b) => a + b;
export const PI = 3.14159;

// 也可以统一导出
// export { add, PI };

// 默认导出
export default function multiply(a, b) {
  return a * b;
}
```

```js
// main.js —— 引入
import { add, PI } from './math.js';
import multiply from './math.js';         // 引入默认导出
import * as math from './math.js';        // 全部引入为命名空间
import multiply, { add, PI } from './math.js'; // 同时引入默认和具名

console.log(add(1, 2)); // 3
```

`import` 是静态声明语句，**只能出现在模块的顶层**，不能放入条件语句中：

```js
// ❌ 语法错误
if (condition) {
  import { foo } from './foo.js';
}

// ✅ 动态 import() 可以在任意位置使用（返回 Promise）
if (condition) {
  const { foo } = await import('./foo.js');
}
```

---

## 二、加载时机：静态 vs 动态

这是 ESM 与 CommonJS **最核心**的区别。

### CommonJS：运行时加载

CommonJS 模块是在**运行时**（Runtime）才解析和执行的。`require()` 在代码执行到该行时才去加载对应文件，因此整个依赖关系只有在运行时才能确定。

```js
// 运行时才决定加载哪个模块
const moduleName = getModuleName();
const mod = require(moduleName); // 合法的动态行为
```

**执行流程：**

```
启动 → 逐行执行代码 → 遇到 require() → 立即同步加载并执行模块 → 返回 exports 对象 → 继续执行
```

### ESM：编译时（静态）加载

ESM 的 `import` 语句在**编译阶段**（Parse/Compile）就会被分析处理，引擎在真正执行代码前就已知道所有的依赖关系，并提前建立好模块绑定。

```js
// import 会被提升到模块顶部，在代码执行前就建立好链接
import { add } from './math.js';

console.log(add(1, 2)); // 可以正常访问，因为绑定在执行前已建立
```

**执行流程（三个阶段）：**

```
① 构建（Construction）：递归查找所有 import，下载并解析模块文件，建立模块记录（Module Record）
② 实例化（Instantiation）：为导出值分配内存空间，建立导入/导出之间的内存绑定（linking）
③ 求值（Evaluation）：执行代码，将实际值填入内存地址
```

静态加载的优势：
- 打包工具（Rollup、Vite、webpack）可在编译期进行静态分析
- 支持 Tree Shaking（消除未使用代码）
- 可以做循环依赖检测和提前报错

---

## 三、导出值的本质：引用 vs 拷贝

### CommonJS：值的拷贝（对于原始类型）

CommonJS 导出的是 `module.exports` 对象的**快照拷贝**。对于原始值（number、string、boolean），导入方拿到的是拷贝，模块内部后续的修改不会同步到导入方。

```js
// counter.js
let count = 0;

function increment() {
  count++;
}

module.exports = { count, increment };
```

```js
// main.js
const { count, increment } = require('./counter');

console.log(count); // 0
increment();
console.log(count); // 仍然是 0 ！count 是值的拷贝，不会跟随模块内部更新
```

如果导出的是对象（引用类型），则拷贝的是引用地址，对象内部属性的变更会同步：

```js
// state.js
const state = { count: 0 };
function increment() { state.count++; }
module.exports = { state, increment };
```

```js
// main.js
const { state, increment } = require('./state');
console.log(state.count); // 0
increment();
console.log(state.count); // 1 —— 对象引用，内部变更可见
```

### ESM：动态绑定（Live Binding）

ESM 导出的是**内存地址的实时绑定**。无论是原始值还是引用值，模块内部的任何变更都会实时反映到所有导入方。

```js
// counter.mjs
export let count = 0;

export function increment() {
  count++;
}
```

```js
// main.mjs
import { count, increment } from './counter.mjs';

console.log(count); // 0
increment();
console.log(count); // 1 —— 实时绑定！自动更新
```

> [!IMPORTANT]
> ESM 的导入绑定是**只读**的，不能在导入方直接修改导入的值：
>
> ```js
> import { count } from './counter.mjs';
> count = 10; // ❌ TypeError: Assignment to constant variable
> ```
>
> 要修改值，必须通过导出模块提供的方法（如 `increment()`）来操作。

---

## 四、顶层 `this` 的指向

| 环境          | 顶层 `this` 的值        |
| ------------- | ----------------------- |
| CommonJS 模块 | `module.exports`（即 `exports` 对象） |
| ESM           | `undefined`             |
| 浏览器脚本    | `window`                |
| Node.js REPL  | `global`                |

```js
// CommonJS
console.log(this === module.exports); // true
console.log(this === exports);        // true（初始时）
```

```js
// ESM (.mjs 或 type: "module")
console.log(this); // undefined
```

这一差异在编写跨环境兼容代码时需要特别注意。

---

## 五、严格模式

| 规范      | 严格模式         |
| --------- | ---------------- |
| CommonJS  | 默认非严格模式   |
| ESM       | **始终严格模式** |

ESM 模块会自动启用 `"use strict"`，无需手动声明，并且无法通过任何方式关闭。

```js
// ESM 中以下代码会报错（严格模式不允许）
with (obj) { } // ❌ SyntaxError

// CommonJS 中需手动声明
'use strict';
with (obj) { } // ❌ 同样报错，但不声明则不会报错
```

---

## 六、文件扩展名与 `package.json` 的 `type` 字段

Node.js 通过以下规则判断一个文件是 ESM 还是 CommonJS：

### 专属扩展名

| 扩展名 | 规范      |
| ------ | --------- |
| `.mjs` | 强制 ESM  |
| `.cjs` | 强制 CommonJS |
| `.js`  | 取决于最近的 `package.json` 的 `type` 字段 |

### `package.json` 的 `type` 字段

```json
{
  "type": "module"
}
```

设置 `"type": "module"` 后，该包内所有 `.js` 文件都被视为 ESM。

```json
{
  "type": "commonjs"
}
```

设置 `"type": "commonjs"`（或不设置，默认值）后，`.js` 文件被视为 CommonJS。

### 双格式包（Dual Package）

现代 npm 包通常同时提供 ESM 和 CJS 格式，通过 `package.json` 的 `exports` 字段区分：

```json
{
  "name": "my-lib",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  }
}
```

---

## 七、循环依赖的处理方式

### CommonJS 的循环依赖

CommonJS 借助**模块缓存**处理循环依赖。当检测到循环时，`require()` 会返回当前**已导出的部分**（未完成的 `exports` 对象），而不是等待被依赖模块执行完毕。

```js
// a.js
console.log('a 开始');
const b = require('./b');
console.log('在 a 中，b.done =', b.done);
exports.done = true;
console.log('a 结束');
```

```js
// b.js
console.log('b 开始');
const a = require('./a');
console.log('在 b 中，a.done =', a.done); // undefined！a 还未执行完
exports.done = true;
console.log('b 结束');
```

```js
// main.js
const a = require('./a');
const b = require('./b');
```

输出：
```
a 开始
b 开始
在 b 中，a.done = undefined   ← 拿到的是 a 未完成的 exports
b 结束
在 a 中，b.done = true
a 结束
```

### ESM 的循环依赖

ESM 借助**模块地图（Module Map）**处理循环依赖。已进入处理的模块会被标记为"获取中"，再次遇到 `import` 时不会重复执行，而是直接使用已建立的内存绑定（live binding）。

```js
// a.mjs
import { b } from './b.mjs';
export const a = 'a';
console.log('在 a 中，b =', b);
```

```js
// b.mjs
import { a } from './a.mjs';
export const b = 'b';
console.log('在 b 中，a =', a);
```

ESM 的循环依赖场景中，绑定在实例化阶段已建立，但值要到求值阶段才会填入。如果求值时依赖的值还未初始化，会得到 `undefined`（对 `let`/`var`）或 `ReferenceError`（对 `const`，因为 TDZ）。

> [!TIP]
> 无论 ESM 还是 CJS，**都应尽量避免循环依赖**，这通常意味着模块拆分不够合理。

---

## 八、Tree Shaking 支持

Tree Shaking 是打包工具在编译时移除未使用代码的能力，其前提是**模块的导入导出关系必须是静态可分析的**。

| 规范      | 支持 Tree Shaking | 原因                                   |
| --------- | ----------------- | -------------------------------------- |
| ESM       | ✅ 完整支持       | `import`/`export` 是静态语法，编译期可分析 |
| CommonJS  | ⚠️ 有限支持      | `require()` 是动态函数调用，难以静态分析   |

### ESM Tree Shaking 示例

```js
// utils.js
export function usedFunction() { return 'used'; }
export function unusedFunction() { return 'unused'; }
```

```js
// main.js
import { usedFunction } from './utils.js';
usedFunction();
```

打包后，`unusedFunction` 会被完全移除。

### CommonJS 为何难以 Tree Shake

```js
// utils.js
module.exports = {
  usedFunction() { return 'used'; },
  unusedFunction() { return 'unused'; },
};
```

```js
// main.js
const utils = require('./utils');
utils.usedFunction();
```

由于 `require()` 在运行时执行，打包工具无法确定哪些导出真的被用到（例如可能存在 `utils[dynamicKey]()` 的调用），因此保守地将整个 `module.exports` 打包进去。

---

## 九、异步加载与顶层 `await`

### CommonJS：同步加载

`require()` 是同步的，会阻塞当前代码执行直到模块加载完成。这在 Node.js 服务端环境通常没有问题（模块文件在本地），但在浏览器中会造成阻塞。

```js
// 同步，阻塞式
const fs = require('fs'); // 加载完成才继续
```

### ESM：支持顶层 `await`

ESM 模块支持在模块顶层使用 `await`，无需包裹在 `async` 函数中。这使得模块可以执行异步初始化操作，依赖该模块的其他模块会等待其完成后再继续执行。

```js
// config.mjs —— 顶层 await
const response = await fetch('https://api.example.com/config');
export const config = await response.json();
```

```js
// main.mjs —— 等待 config.mjs 的顶层 await 完成后才执行
import { config } from './config.mjs';
console.log(config); // 已经是加载好的值
```

> [!NOTE]
> 顶层 `await` 仅在 ESM 中支持，需要 Node.js 14.8+ 或现代浏览器。

---

## 十、互操作性（Interop）

### 在 ESM 中使用 CommonJS 模块

Node.js 允许在 ESM 中通过 `import` 引入 CommonJS 模块，CJS 的 `module.exports` 会被视为 ESM 的**默认导出**：

```js
// utils.cjs
module.exports = { add: (a, b) => a + b, PI: 3.14 };
```

```js
// main.mjs
import utils from './utils.cjs';         // ✅ 整体引入（默认导出）
console.log(utils.add(1, 2));

// ❌ 具名导入在某些情况下不被支持（取决于 Node.js 版本和工具）
// import { add } from './utils.cjs';
```

### 在 CommonJS 中使用 ESM 模块

CommonJS **不能直接 `require()` 一个 ESM 模块**（Node.js 22 之前），因为 ESM 是异步加载的，而 `require()` 是同步的。需要使用动态 `import()`：

```js
// main.cjs
async function main() {
  const { add } = await import('./utils.mjs'); // ✅ 通过动态 import() 加载
  console.log(add(1, 2));
}

main();

// require('./utils.mjs'); // ❌ ERR_REQUIRE_ESM
```

> [!TIP]
> Node.js 22+ 支持通过 `require()` 同步加载部分 ESM 模块（不含顶层 `await`），这一限制正在逐步放宽。

### Bundler 的处理

在使用 Vite、webpack、Rollup 等打包工具时，互操作性的处理通常由工具自动完成，开发者无需过多关注。但在编写 **纯 Node.js 工具库** 时，需要手动处理好格式兼容。

---

## 十一、综合对比表

| 对比维度              | CommonJS                         | ESM                              |
| --------------------- | -------------------------------- | -------------------------------- |
| **关键字**            | `require` / `module.exports`     | `import` / `export`              |
| **加载时机**          | 运行时（动态）                   | 编译时（静态）                   |
| **导出值类型**        | 值的拷贝（原始类型）             | 动态绑定（Live Binding）         |
| **顶层 `this`**       | `module.exports`                 | `undefined`                      |
| **严格模式**          | 默认关闭                         | 始终开启                         |
| **异步支持**          | 不支持（同步阻塞）               | 支持顶层 `await`                 |
| **Tree Shaking**      | ⚠️ 有限                         | ✅ 完整支持                      |
| **循环依赖**          | 返回未完成的 exports 拷贝        | 基于内存绑定的实时链接           |
| **动态导入**          | `require()` 本身即动态           | `import()` 函数（返回 Promise）  |
| **文件扩展名**        | `.js`（默认）/ `.cjs`            | `.mjs` / `.js`（需配置）         |
| **浏览器原生支持**    | ❌ 不支持                        | ✅ 现代浏览器原生支持            |
| **Node.js 支持**      | ✅ 完整支持                      | ✅ v12.17+ 稳定支持              |
| **主要使用场景**      | Node.js 服务端（历史遗留）       | 现代前端、Node.js 新项目         |

---

## 十二、最佳实践建议

### 新项目：优先使用 ESM

对于新建项目，无论是前端还是 Node.js 后端，都建议优先采用 ESM：

```json
// package.json
{
  "type": "module"
}
```

### 编写 npm 包：提供双格式

如果你在开发一个 npm 包，为了兼容不同的使用者，建议使用构建工具（如 tsup、Rollup、unbuild）同时输出 ESM 和 CJS 格式：

```json
{
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  },
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs"
}
```

### 区分纯 ESM 包的问题

一些现代包（如 `chalk` v5、`got` v12）已改为纯 ESM，无法在 CommonJS 环境中直接 `require()`。解决方案：

1. 将项目迁移到 ESM（推荐）
2. 锁定到支持 CJS 的旧版本（临时方案）
3. 使用动态 `import()` 在异步函数中加载（兼容方案）

### 避免混用产生的常见问题

```js
// ❌ 在 ESM 文件中无法直接使用 __dirname 和 __filename
console.log(__dirname); // ReferenceError

// ✅ ESM 中的替代方式
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

```js
// ✅ ESM 中获取当前模块 URL
console.log(import.meta.url); // file:///Users/.../main.mjs
```

---

## 参考资料

- [ECMAScript Modules - Node.js 官方文档](https://nodejs.org/api/esm.html)
- [CommonJS Modules - Node.js 官方文档](https://nodejs.org/api/modules.html)
- [ES modules: A cartoon deep-dive - Lin Clark](https://hacks.mozilla.org/2018/03/es-modules-a-cartoon-deep-dive/)
- [探索 JavaScript 模块 - MDN Web Docs](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide/Modules)
