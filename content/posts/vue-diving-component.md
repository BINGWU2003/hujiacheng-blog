---
title: "Vue 深入组件"
date: 2024-03-18
draft: false
description: ""
tags: []
categories: ["博客"]
---



# 深入组件

## Props

### 传递 prop 的细节

**使用一个对象绑定多个 prop**

如果你想要将一个对象的所有属性都当作 props 传入，你可以使用没有参数的 `v-bind`，即只使用 `v-bind` 而非 `:prop-name`。

```vue


<BlogPost v-bind="post" />

<!-- 等价于 -->
<BlogPost :id="post.id" :title="post.title" />
```

### 单向数据流

**_所有的 props 都遵循着单向绑定原则，props 因父组件的更新而变化，自然地将新的状态向下流往子组件，而不会逆向传递。这避免了子组件意外修改父组件的状态的情况，不然应用的数据流将很容易变得混乱而难以理解。_**

如果要更改一个 prop 通常是下面两种场景：

1. prop 被用于传入初始值；而子组件想在之后将其作为一个局部数据属性。

```ts
const props = defineProps(['initialCounter'])

// 计数器只是将 props.initialCounter 作为初始值
// 像下面这样做就使 prop 和后续更新无关了
const counter = ref(props.initialCounter)
```

2. 需要对传入的 prop 值做进一步的转换。

```ts
const props = defineProps(['size'])

// 该 prop 变更时计算属性也会自动更新
const normalizedSize = computed(() => props.size.trim().toLowerCase())
```

**更改对象 / 数组类型的 props**

当对象或数组作为 props 被传入时，虽然子组件无法更改 props 绑定，但仍然可以更改对象或数组内部的值。这是因为 JavaScript 的对象和数组是按引用传递，而对 Vue 来说，禁止这样的改动，虽然可能生效，但有很大的性能损耗，比较得不偿失。

这种更改的主要缺陷是它允许了子组件以某种不明显的方式影响父组件的状态，可能会使数据流在将来变得更难以理解。在最佳实践中，你应该尽可能避免这样的更改，除非父子组件在设计上本来就需要紧密耦合。_在大多数场景下，子组件应该抛出一个事件来通知父组件做出改变。_

### Prop 校验

常用的几种校验应该不用我多说了，下面介绍几种不常见的:

```vue

```

::: tip
`defineProps()` 宏中的参数不可以访问 `
```

::: tip
尽管事件声明是可选的，官方文档更推荐完整声明所有触发的事件，以此在代码中作为文档记录组件的用法。同时，事件声明能让 Vue 更好地将事件和透传 attribute 作出区分，从而避免一些由第三方代码触发的自定义 DOM 事件所导致的边界情况。

如果定义的事件名和原生事件名冲突(比如`click`)，那么监听器只会监听组件触发的而不是原生事件
:::

### 事件校验

要为事件添加校验，那么事件可以被赋值为一个函数，接受的参数就是抛出事件时传入 emit 的内容，返回一个布尔值来表明事件是否合法。

```vue

```

## 组件 v-model

### 基本使用

先来实现一下自定义组件 v-model：

1. 通过子组件的 prop 的`modelValue`和 emit 的`update:modelValue`实现（两个名称必须是这个）

::: code-group

```vue [Parent.vue]


<template>
  <Child v-model="username" />
</template>
```

```vue [Child.vue]


<template>
  <input
    type="text"
    :value="modelValue"
    @input="emit('update:modelValue', $event.target.value)"
  >
</template>
```

:::

2. vue3.4+新增的 API: `defineModel()`, 更推荐这种方式

::: code-group

```vue [Parent.vue]
<Child v-model="count" />
```

```vue [Child.vue]


<template>
  <div>parent bound v-model is: {{ model }}</div>
</template>
```

:::

`defineModel()`返回的是 ref，所以：

- 它的 `.value` 和父组件的 `v-model` 的值同步
- 当它被子组件变更了，会触发父组件绑定的值一起更新

这意味的你可以用 v-model 将这个 ref 绑定到原生 input 上

```vue


<template>
  <input v-model="model">
</template>
```

`defineModel()`是声明了一个 prop，所以你可以传递选项来约束 prop。

::: warning
如果`defineModel`prop 设置了一个 default 值，但是父组件并没有为该 prop 提供任何值，那将会导致父子组件不同步

```js
// 子组件：
const model = defineModel({ default: 1 })

// 父组件
const myRef = ref()
```

<br/>

```vue
<Child v-model="myRef"></Child>
```

:::

### v-model 的参数

如果想要 v-model 有不一样的名称可以在`defineModel`第一个参数定义:

```vue
<MyComponent v-model:title="title" />
```

```vue


<template>
  <input v-model="title" type="text">
</template>
```

::: details 3.4 之前的写法

```vue


<template>
  <input
    type="text"
    :value="title"
    @input="$emit('update:title', $event.target.value)"
  >
</template>
```

:::

如果需要多个 v-model，只需要使用上面的方式创建多个 prop 即可。

### v-model 修饰符

除了系统自带了`.trim`, `.number`, `.lazy`等。还有可能需要自定义修饰符。

比如现在自定义一个修饰符用于将输入的字符串首位字母转换成大写:

::: code-group

```vue [Parent.vue]
<MyComponent v-model.capitalize="text" />
```

```vue [MyComponent.vue]


<template>
  <input v-model="model" type="text">
</template>
```

:::

::: details 3.4 之前的写法

```vue


<template>
  <input type="text" :value="modelValue" @input="emitValue">
</template>
```

:::

## 透传 Attributes

### Attributes 继承

“透传 Attributes”指的是传递给一个组件，但是没有被该组件声明为`props`, `emits`的 attribute 或者是`v-on`事件监听器，比如 class，style 和 id。

当一个组件以单个元素作为跟渲染时，那么透传的 attribute 会自动添加到根元素上。

```vue
<LeButton class="btn" />

<!-- 那么他是这样的 -->
<button class="btn">
Click
</button>
```

**对 class 或 style 的合并**

如果根元素上已经存在 class 或者 style attribute，他会和从父元素上继承的值合并。

**`v-on`监听器继承**

如果将监听器添加到组件时会被添加到根元素上，即 button 上会绑定一个监听器，当 button 点击时会触发 LeButton 上的 click 方法。

**深层组件继承**

有些情况下一个组件会在根节点渲染另一个组件，例如`<BaseButton />`，此时`<LeButton />`接受的透传 attribute 会继续传给`<BaseButton />`

::: tip

1. 透传的 `attribute` 不会包含 `<LeButton>` 上声明过的 props 或是针对 `emits` 声明事件的 `v-on` 侦听函数，换句话说，声明过的 props 和侦听函数被 `<LeButton>`“消费”了

2. 透传的 `attribute` 若符合声明，也可以作为 props 传入 `<BaseButton>`
   :::

### 禁用 Attributes 继承

如果你不想要组件自动的继承，你可以在组件选项中配置`inheritAttrs: false`。

在 3.3 中你也可以直接使用`defineOptions({ inheritAttrs: false })`。

最常见的需要禁用 Attribute 继承的场景就是需要应用在根节点以外的其他元素上。通过 inheritAttrs 禁用继承来主动控制透传的 Attributes 如何使用。

在模板中能直接使用`$attrs`，这个对象包含了除组件声明的 props 和 emits 之外的所有 attribute。

- 和 `props` 有所不同，透传 attributes 在 JavaScript 中保留了它们原始的大小写，所以像 `foo-bar` 这样的一个 attribute 需要通过 `$attrs['foo-bar']` 来访问。
- 像 `@click` 这样的一个 `v-on` 事件监听器将在此对象下被暴露为一个函数 `$attrs.onClick`。

### 多根节点的 Attributes 继承

多根节点的情况下，不会自动 attribute 透传行为。如果`$attrs`没有被显式绑定会抛出运行时警告。

### 在 JavaScript 中访问透传 Attributes

如果需要，可以在`
```

如果没使用 setup 语法:

```js
export default {
  setup(props, ctx) {
    // 透传 attribute 被暴露为 ctx.attrs
    console.log(ctx.attrs)
  }
}
```

::: tip
需要注意的是，虽然这里的 attrs 对象总是反映为最新的透传 attribute，但它并不是响应式的 (考虑到性能因素)。你不能通过侦听器去监听它的变化。如果你需要响应性，可以使用 prop。或者你也可以使用 onUpdated() 使得在每次更新时结合最新的 attrs 执行副作用。
:::

## 插槽

用三张图代替:

<!-- <ZoomImg src="https://cn.vuejs.org/assets/slots.inBPF2Hb.png" desc="默认插槽" />

<ZoomImg src="https://cn.vuejs.org/assets/named-slots.giG_TKP2.png" desc="具名插槽" />

<ZoomImg src="https://cn.vuejs.org/assets/scoped-slots.eu7SD3OQ.svg" desc="作用域插槽" /> -->

**无渲染组件**

一些组件可能只包括了逻辑而不需要自己渲染内容，视图输出通过作用域插槽全权交给了消费者组件。我们将这种类型的组件称为无渲染组件

```vue
<MouseTracker v-slot="{ x, y }">
  Mouse is at: {{ x }}, {{ y }}
</MouseTracker>
```

## 依赖注入

### Prop 逐级透传

业务中，我们会碰到这种情况：有一三层级的组件树，c 组件要使用 a 组件的数据，但是需要 a 组件传递给 b 再传递给 c。这就是 prop 逐级透传。如果 b 组件根本不关心传给 c 组件的数据，那这整个过程 a 传给 b 这个过程是完全没必要的。

<!-- <ZoomImg src="https://cn.vuejs.org/assets/prop-drilling.FyV2vFBP.png" /> -->

所以就有了`provide`和`inject`。一个父组件相对所有的后代组件，会作为依赖提供者。任何后代的组件树，都可以注入由父组件提供给整条链路的依赖。

<!-- <ZoomImg src="https://cn.vuejs.org/assets/provide-inject.tIACH1Z-.png" /> -->

### `provide`

为组件后代提供数据要用到`provide()`（必须是与 setup 同步调用）:

```vue

```

还可以直接在最顶层 App 上提供依赖，这样整个应用下都能使用依赖。直接在最顶层`App.vue`使用`provide()`即可。

### `inject`

```vue

```

如果提供的值是 ref，那么注入进来的会是该 ref 对象，而不会自动解包。这使得注入放组件能够通过 ref 对象保持了和供给放的响应式链接

如果在注入一个值不要求必须有提供者，那么可以声明一个默认值

```js
const value = inject('message', '默认值')

// 在一些场景中，默认值可能需要通过调用一个函数或者初始化一个类来取得
// 为了避免在用不到默认值的情况下进行不必要的计算或产生副作用，可以用工厂函数创建
// 第三个参数表示默认值应该被当作一个工厂函数
// const value = inject('message', () => new ExpensiveClass(), true)
```

### 和响应式数据配合使用

**建议尽可能将任何对响应式状态的变更都保持在供给方组件中**，这样可以确保所提供状态的声明和变更操作都内聚在同一个组件内，使其更容易维护

如果需要在注入方组件中更改数据，可以在提供方声明一个更改该数据的函数:

::: code-group

```vue [Provide.vue]

```

```vue [Inject.vue]


<template>
  <button @click="updateLocation">
    {{ location }}
  </button>
</template>
```

:::

如果你想确保注入方不能修改数据你可以这样做:

```js
const count = ref(0)
provide('read-only-count', readonly(count))
```

## 异步组件

### 基本用法

在大型项目中，我们可能需要拆分应用为更小的块，并仅在需要时再从服务器加载相关组件。Vue 提供了 `defineAsyncComponent` 方法来实现此功能：

```js
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() => {
  return new Promise((resolve, reject) => {
    // ...从服务器获取组件
    resolve(/* 获取到的组件 */)
  })
})
// ... 像使用其他一般组件一样使用 `AsyncComp`
```

如你所见，`defineAsyncComponent` 方法接收一个返回 Promise 的加载函数。这个 Promise 的 `resolve` 回调方法应该在从服务器获得组件定义时调用。你也可以调用 `reject(reason)` 表明加载失败。

ES 模块动态导入也会返回一个 Promise。类似 Vite 和 Webpack 这样的构建工具也支持此语法 (并且会将它们作为打包时的代码分割点)，因此我们也可以用它来导入 Vue 单文件组件：

```js
import { defineAsyncComponent } from 'vue'

const AsyncComp = defineAsyncComponent(() =>
  import('./components/MyComponent.vue')
)
```

最后得到的 `AsyncComp` 是一个外层包装过的组件，仅在页面需要它渲染时才会调用加载内部实际组件的函数。它会将接收到的 props 和插槽传给内部组件，所以你可以使用这个异步的包装组件无缝地替换原始组件，同时实现延迟加载。

### 加载与错误状态

异步操作避免不了加载和错误状态，因此该 API 也支持在高级选项中处理这些状态：

```js
const AsyncComp = defineAsyncComponent({
  // 加载函数
  loader: () => import('./Foo.vue'),

  // 加载异步组件时使用的组件
  loadingComponent: LoadingComponent,
  // 展示加载组件前的延迟时间，默认为 200ms
  delay: 200,

  // 加载失败后展示的组件
  errorComponent: ErrorComponent,
  // 如果提供了一个 timeout 时间限制，并超时了
  // 也会显示这里配置的报错组件，默认值是：Infinity
  timeout: 3000
})
```

### 搭配 Suspense 使用

异步组件可以搭配内置的 `<Suspense>` 组件一起使用
