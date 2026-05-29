---
title: "React 样式穿透实践笔记：从 Vue scoped + :deep 到 CSS Modules + :global"
date: 2026-05-29
draft: false
description: ""
tags: ["React"]
categories: ["笔记"]
---

## 背景

在 Vue 项目里，如果使用了 `scoped`，我们经常会通过 `:deep()` 去覆盖第三方组件库的内部样式。

例如：

```vue
<template>
  <div class="page">
    <a-select />
  </div>
</template>

<style scoped>
.page :deep(.ant-select-selector) {
  border-radius: 12px;
}
</style>
```

这类写法的目标通常是：

1. 当前组件内可以覆盖第三方组件内部 DOM 的样式。
2. 样式不能污染全局。
3. 多个组件里写了相同选择器时，互不影响。
4. 有时还需要根据 props 动态改变颜色、圆角、尺寸等样式。

到了 React 项目里，React 本身没有内置类似 Vue `scoped` 的样式隔离机制，也没有官方的 `:deep()` 语法。React 中常见的替代方案是 CSS Modules。

如果你之前主要使用的是 Vue `scoped + :deep`，那么在 React 中最接近的心智模型是：

```txt
Vue:
.page :deep(.third-party-inner) {}

React CSS Modules:
.page :global(.third-party-inner) {}
```

## Vue scoped 是怎么做到不污染全局的

Vue 的 `scoped` 通常会把模板和 CSS 都编译成带属性选择器的形式。

你写的代码：

```vue
<template>
  <div class="page">
    <button class="btn">Button</button>
  </div>
</template>

<style scoped>
.page .btn {
  color: red;
}
</style>
```

编译后大概会变成：

```html
<div class="page" data-v-abc123>
  <button class="btn" data-v-abc123>Button</button>
</div>
```

```css
.page[data-v-abc123] .btn[data-v-abc123] {
  color: red;
}
```

所以 Vue 的隔离方式主要靠 `data-v-xxxx` 属性。

当使用 `:deep()` 时，内部选择器不会再被加上当前组件的 scoped 属性，但外层父级仍然会被 scoped 限定。

例如：

```css
.page :deep(.ant-select-selector) {
  border-radius: 12px;
}
```

大致会变成：

```css
.page[data-v-abc123] .ant-select-selector {
  border-radius: 12px;
}
```

也就是说，真正起隔离作用的是外层 `.page[data-v-abc123]`。

## React CSS Modules 是怎么做到不污染全局的

CSS Modules 不会像 Vue scoped 那样加 `data-v-xxxx` 属性。它的隔离方式是：编译时把局部 className 改成唯一哈希类名。

例如 React 里写：

```tsx
import styles from "./Demo.module.css";

export const Demo = () => {
  return (
    <div className={styles.page}>
      <button className={styles.button}>Button</button>
    </div>
  );
};
```

```css
/* Demo.module.css */
.page {
  padding: 16px;
}

.button {
  color: red;
}
```

编译后大概会变成：

```html
<div class="_page_abc12_1">
  <button class="_button_abc12_5">Button</button>
</div>
```

```css
._page_abc12_1 {
  padding: 16px;
}

._button_abc12_5 {
  color: red;
}
```

所以你在 React 项目里看不到 `data-xxxx` 是正常的。CSS Modules 靠的是 className 哈希，而不是属性选择器。

## :global是什么

`:global` 不是 React 的语法，而是 **CSS Modules 的语法**。

它的意思是：

```txt
这一段选择器不要被 CSS Modules 哈希化，按全局 class 原样输出。
```

比如在 `Demo.module.css` 里写：

```css
.title {
  color: red;
}
```

CSS Modules 会把它编译成类似：

```css
.Demo_title__abc12 {
  color: red;
}
```

React 里使用时：

```tsx
<div className={styles.title}>Hello</div>
```

最终 DOM：

```html
<div class="Demo_title__abc12">Hello</div>
```

但如果你写：

```css
:global(.ant-btn) {
  border-radius: 12px;
}
```

CSS Modules 会认为 `.ant-btn` 是全局类，不要改名。

编译后就是：

```css
.ant-btn {
  border-radius: 12px;
}
```

这会影响全局所有 `.ant-btn`。

所以更推荐这样写：

```css
.page :global(.ant-btn) {
  border-radius: 12px;
}
```

这里分两部分看：

```css
.page
```

这是 CSS Modules 的局部类，会被哈希化：

```css
._page_abc12_1
```

```css
:global(.ant-btn);
```

这是第三方组件库的全局类，不会被改名：

```css
.ant-btn
```

最终变成：

```css
._page_abc12_1 .ant-btn {
  border-radius: 12px;
}
```

意思就是：

```txt
只修改当前组件 .page 里面的 .ant-btn
```

不影响其他地方的 `.ant-btn`。

所以一句话：

```txt
:global 的作用是告诉 CSS Modules：这个选择器是全局的，不要给它加哈希。
```

## React 中推荐的样式穿透写法

如果要在 CSS Modules 里覆盖第三方组件内部样式，推荐写法是：

```css
.page :global(.third-party-inner) {
  /* overrides */
}
```

例如：

```tsx
import { Select } from "antd";
import styles from "./UserFilter.module.css";

export const UserFilter = () => {
  return (
    <section className={styles.page}>
      <Select
        defaultValue="active"
        options={[
          { value: "active", label: "Active" },
          { value: "disabled", label: "Disabled" },
        ]}
      />
    </section>
  );
};
```

```css
/* UserFilter.module.css */
.page {
  padding: 24px;
  background: #f6f8ff;
}

.page :global(.ant-select-content) {
  border-radius: 12px !important;
  background: #e6f4ff !important;
}
```

编译后大致会变成：

```css
._page_abc12_1 .ant-select-content {
  border-radius: 12px !important;
  background: #e6f4ff !important;
}
```

真正起隔离作用的是前面的 `._page_abc12_1`。

## 为什么不推荐裸写 :global

不推荐这样写：

```css
:global(.ant-select-content) {
  border-radius: 12px;
}
```

因为它会编译成真正的全局 CSS：

```css
.ant-select-content {
  border-radius: 12px;
}
```

这意味着项目里所有匹配 `.ant-select-content` 的节点都会被影响。

风险包括：

1. 只想改某个页面，结果全站 Select 都变了。
2. 多个页面写了同一个全局覆盖，最后谁生效取决于 CSS 加载顺序。
3. 组件库升级后内部类名变化，影响范围更大。
4. 维护时很难定位到底是哪一个模块文件影响了全局样式。

推荐始终加一个局部父级：

```css
.page :global(.ant-select-content) {
  border-radius: 12px;
}
```

不要直接写：

```css
:global(.ant-select-content) {
  border-radius: 12px;
}
```

除非你的目标就是全局统一覆盖所有同类组件。

## A/B 组件同名 .page 是否会互相影响

假设 A 组件这样写：

```tsx
import { Select } from "antd";
import styles from "./ComponentA.module.css";

export const ComponentA = () => (
  <section className={styles.page}>
    <Select defaultValue="apple" />
  </section>
);
```

```css
/* ComponentA.module.css */
.page :global(.ant-select-content) {
  border-radius: 18px !important;
  background: #e6f4ff !important;
}
```

B 组件也这样写：

```tsx
import { Select } from "antd";
import styles from "./ComponentB.module.css";

export const ComponentB = () => (
  <section className={styles.page}>
    <Select defaultValue="react" />
  </section>
);
```

```css
/* ComponentB.module.css */
.page :global(.ant-select-content) {
  border-radius: 4px !important;
  background: #fff1d6 !important;
}
```

虽然两个文件里都叫 `.page`，但它们来自不同的 CSS Module 文件，会被编译成不同类名。

实际 DOM 可能是：

```html
<section class="_page_101g6_1">
  <div class="ant-select-content">Apple</div>
</section>

<section class="_page_195hz_1">
  <div class="ant-select-content">React</div>
</section>
```

最终 CSS 类似：

```css
._page_101g6_1 .ant-select-content {
  border-radius: 18px;
  background: #e6f4ff;
}

._page_195hz_1 .ant-select-content {
  border-radius: 4px;
  background: #fff1d6;
}
```

所以 B 组件改样式不会影响 A 组件。

## 会互相影响的几种情况

### 1. 使用普通 CSS，而不是 CSS Modules

如果你写的是普通 CSS：

```css
.page .ant-select-content {
  border-radius: 12px;
}
```

那么 `.page` 就是全局类名。A 和 B 都叫 `.page` 时，就可能互相影响。

### 2. 把父级也写成 global

不推荐：

```css
:global(.page) :global(.ant-select-content) {
  border-radius: 12px;
}
```

这会变成：

```css
.page .ant-select-content {
  border-radius: 12px;
}
```

父级 `.page` 已经不再是 CSS Modules 的局部类名，也就失去了隔离能力。

### 3. 多个组件共用同一个 CSS Module 文件

如果 A 和 B 都引入同一个样式文件：

```tsx
import styles from "./common.module.css";
```

并且都使用：

```tsx
<section className={styles.page}>
```

那么它们拿到的是同一个哈希类名。此时你改 `common.module.css`，当然会同时影响 A 和 B。

### 4. 组件嵌套导致父级作用域包含子组件

例如：

```tsx
<section className={aStyles.page}>
  <ASelect />
  <ComponentB />
</section>
```

如果 A 的 CSS 是：

```css
.page :global(.ant-select-content) {
  background: #e6f4ff;
}
```

那么 A 的规则会匹配 A 容器下面所有 `.ant-select-content`，包括 B 内部的 Select。

如果希望只影响某一个 Select，应该给目标组件更精确的局部类名：

```tsx
<Select className={styles.userSelect} />
```

```css
.userSelect :global(.ant-select-content) {
  background: #e6f4ff;
}
```

## 动态 props 场景：推荐使用 CSS 变量

固定样式覆盖可以直接写 CSS。但如果样式要通过 props 动态改变，例如颜色、圆角、边框、尺寸来自父组件，就推荐使用 CSS 变量。

核心思路是：

```txt
props -> CSS variables -> CSS Modules :global selector
```

例如定义一个动态 Select 卡片：

```tsx
import type { CSSProperties } from "react";
import { Select } from "antd";
import styles from "./DynamicSelectCard.module.css";

type DynamicSelectCardProps = {
  title: string;
  accentColor: string;
  borderColor: string;
  selectBg: string;
  radius: number;
};

type DynamicStyle = CSSProperties & {
  "--card-accent": string;
  "--select-border": string;
  "--select-bg": string;
  "--select-radius": string;
};

export const DynamicSelectCard = ({
  title,
  accentColor,
  borderColor,
  selectBg,
  radius,
}: DynamicSelectCardProps) => {
  const dynamicStyle: DynamicStyle = {
    "--card-accent": accentColor,
    "--select-border": borderColor,
    "--select-bg": selectBg,
    "--select-radius": `${radius}px`,
  };

  return (
    <section className={styles.page} style={dynamicStyle}>
      <h2>{title}</h2>
      <Select defaultValue="react" />
    </section>
  );
};
```

CSS 中使用这些变量：

```css
.page {
  border: 1px solid var(--select-border);
}

.page h2 {
  color: var(--card-accent);
}

.page :global(.ant-select-content) {
  border-color: var(--select-border) !important;
  border-radius: var(--select-radius) !important;
  background: var(--select-bg) !important;
}
```

使用组件时传入不同 props：

```tsx
<DynamicSelectCard
  title="动态组件 A"
  accentColor="#0958d9"
  borderColor="#1677ff"
  selectBg="#d6eaff"
  radius={24}
/>

<DynamicSelectCard
  title="动态组件 B"
  accentColor="#531dab"
  borderColor="#9254de"
  selectBg="#f3e8ff"
  radius={8}
/>
```

这样同一个组件可以复用同一份 CSS，但每个实例都能拥有自己的动态样式。

## 为什么动态样式推荐 CSS 变量，而不是拼 className

如果只有少量固定状态，例如 `primary`、`warning`、`danger`，用 className 切换是可以的：

```tsx
<section className={`${styles.page} ${styles.warning}`}>
```

```css
.warning :global(.ant-select-content) {
  background: #fff7e6;
}
```

这种适合有限枚举：

```ts
variant: "primary" | "warning" | "danger";
```

但如果样式值是连续变化的，例如：

1. 颜色由接口返回。
2. 圆角由配置项决定。
3. 宽度、高度、间距可自定义。
4. 主题色由用户选择。

这时用 CSS 变量更自然：

```tsx
style={{
  "--select-bg": selectBg,
  "--select-radius": `${radius}px`,
} as React.CSSProperties}
```

```css
.page :global(.ant-select-content) {
  background: var(--select-bg);
  border-radius: var(--select-radius);
}
```

CSS 变量的优势是：

1. 仍然保留 CSS 的伪类、媒体查询、层叠能力。
2. 不需要生成大量 className。
3. 每个组件实例可以拥有自己的变量值。
4. 和 CSS Modules 的局部父级天然配合。

## React 中的推荐选择顺序

实际开发时，不建议一上来就穿透第三方组件内部类名。推荐按下面顺序判断。

### 1. 优先使用组件库官方 API

如果组件库提供了官方样式入口，优先使用它。

常见形式包括：

```tsx
className
style
classNames
styles
theme token
CSS variable
ConfigProvider
```

例如 Ant Design 的主题能力通常比直接穿透内部 DOM 更稳定：

```tsx
<ConfigProvider
  theme={{
    components: {
      Button: {
        borderRadius: 12,
      },
    },
  }}
>
  <App />
</ConfigProvider>
```

### 2. 固定局部覆盖用 .page :global(...)

当组件库没有提供合适 API，或者只想在当前页面局部覆盖时：

```css
.page :global(.third-party-inner) {
  /* overrides */
}
```

### 3. 动态局部覆盖用 props + CSS variables + :global

当样式值来自 props：

```tsx
<section
  className={styles.page}
  style={{
    "--select-radius": `${radius}px`,
  } as React.CSSProperties}
>
```

```css
.page :global(.third-party-inner) {
  border-radius: var(--select-radius);
}
```

### 4. 全局统一风格用主题或全局 CSS

如果目标是统一全站组件风格，不要每个组件都局部穿透。应该考虑：

```tsx
ConfigProvider
theme token
全局 CSS
设计系统封装
```

## 弹层挂载到 body 的特殊情况

有一类问题需要特别注意：弹层类组件的 DOM 不一定在当前组件下面。

例如：

1. Select 下拉框
2. Tooltip
3. Popover
4. Dropdown
5. Modal
6. DatePicker 面板

它们的弹层可能默认被挂载到 `body` 下。

这时你写：

```css
.page :global(.ant-select-dropdown) {
  background: red;
}
```

可能不会生效，因为真实 DOM 是：

```html
<body>
  <div id="root">
    <section class="_page_abc12_1">
      <div class="ant-select">...</div>
    </section>
  </div>

  <div class="ant-select-dropdown">...</div>
</body>
```

`.ant-select-dropdown` 并不是 `._page_abc12_1` 的子元素，所以选择器匹配不到。

解决方式通常有两种。

第一种：使用组件库提供的 popup className / classNames API。

例如：

```tsx
<Select
  classNames={{
    popup: {
      root: styles.popup,
    },
  }}
/>
```

```css
.popup {
  border-radius: 12px;
}
```

第二种：改变弹层挂载容器。

有些组件支持类似 `getPopupContainer` 的 API：

```tsx
<Select getPopupContainer={(triggerNode) => triggerNode.parentElement!} />
```

这样弹层会挂到当前组件附近，局部选择器才更容易命中。

具体 API 要以组件库版本文档为准。

## 组件库版本差异

样式穿透依赖第三方组件内部类名，因此要以浏览器真实 DOM 为准。

例如一些 Ant Design 版本中 Select 内部可能是：

```css
.ant-select-selector
```

但当前示例项目使用的是 `antd@6.4.3`，Select 内部实际类名是：

```css
.ant-select-content
```

所以示例里使用的是：

```css
.page :global(.ant-select-content) {
  ...
}
```

如果你在自己的项目里没有生效，第一步应该打开浏览器 DevTools，确认目标元素真实类名是什么。

## 关于 !important

示例里出现了 `!important`：

```css
.page :global(.ant-select-content) {
  border-radius: 12px !important;
}
```

这是因为组件库自身样式可能有较高优先级，或者由 CSS-in-JS 运行时注入。实际项目中不应该无脑使用 `!important`。

推荐顺序是：

1. 优先使用组件库官方 API。
2. 提高选择器精确度。
3. 必要时局部使用 `!important`。
4. 不要写全局 `!important` 覆盖。

可以接受：

```css
.page :global(.ant-select-content) {
  border-radius: 12px !important;
}
```

不推荐：

```css
:global(.ant-select-content) {
  border-radius: 12px !important;
}
```

## 对比总结

| 场景               | Vue 写法                   | React CSS Modules 写法       |
| ------------------ | -------------------------- | ---------------------------- |
| 局部样式隔离       | `<style scoped>`           | `*.module.css`               |
| 穿透第三方内部样式 | `.page :deep(.inner)`      | `.page :global(.inner)`      |
| 隔离原理           | `data-v-xxxx` 属性         | className 哈希               |
| 固定局部覆盖       | `scoped + :deep`           | CSS Modules + `:global`      |
| 动态样式覆盖       | props + CSS 变量 + `:deep` | props + CSS 变量 + `:global` |
| 全局覆盖           | 非 scoped 或全局样式       | 普通 CSS 或裸 `:global`      |

## 最推荐的两种实践

### 固定样式覆盖

```css
.page :global(.third-party-inner) {
  border-radius: 12px;
  background: #f6f8ff;
}
```

适合：

1. 当前页面固定风格。
2. 当前业务组件固定覆盖第三方内部样式。
3. 不需要由 props 动态变化。

### 动态 props 样式覆盖

```tsx
<section
  className={styles.page}
  style={{
    "--select-bg": selectBg,
    "--select-radius": `${radius}px`,
  } as React.CSSProperties}
>
```

```css
.page :global(.third-party-inner) {
  background: var(--select-bg);
  border-radius: var(--select-radius);
}
```

适合：

1. 同一个组件多处复用。
2. 颜色、圆角、尺寸来自 props。
3. 样式值来自接口、配置、主题或用户选择。

## 一句话结论

如果你从 Vue `scoped + :deep` 迁移到 React，可以把它理解为：

```txt
Vue scoped + :deep
≈
React CSS Modules + 局部父级 + :global
```

固定覆盖用：

```css
.page :global(.third-party-inner) {
}
```

动态覆盖用：

```tsx
props -> CSS variables -> .page :global(.third-party-inner)
```

只要记住不要裸写 `:global(.xxx)`，并且注意弹层挂载到 `body` 的特殊情况，这套写法就能覆盖大多数 React 业务项目里的样式穿透需求。
