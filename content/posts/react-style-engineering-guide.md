---
title: "React 样式工程化实战笔记"
date: 2026-02-25
draft: false
description: ""
tags: ["React"]
categories: ["笔记"]
---

在 React 开发中，为了获得类似 Vue 的样式开发体验（局部作用域、动态绑定、强类型补全），我们将 **SCSS Modules**、**classnames** 和 **TypeScript** 结合使用。

## 1. 核心技术栈说明

- **SCSS Modules**: 解决 CSS 类名全局污染问题，自动将类名哈希化。
- **classnames/bind**: 类似 Vue 的 `:class`，用于优雅地拼接多个类名并映射哈希值。
- **sass-dts (Vite Plugin)**: 自动为 SCSS 生成 `.d.ts` 类型文件，提供类名补全基础。
- **Typed cx Wrapper**: 手写工具函数，让 `cx()` 具备完美的 Key 提示和类型检查。

## 2. 环境配置 (Vite)

### 安装依赖

```bash
npm install classnames
npm install vite-plugin-sass-dts -D

```

### Vite 配置 (`vite.config.ts`)

```typescript
export default defineConfig({
  css: {
    modules: {
      localsConvention: "camelCaseOnly", // 开启驼峰转换：.base-btn -> styles.baseBtn
    },
  },
  plugins: [
    sassDts(), // 自动生成 .scss.d.ts
  ],
});
```

## 3. 核心工具：强类型 `cx` 构造器

由于 `classnames/bind` 默认不带具体的 Key 提示，我们在项目中建立 `src/utils/cx.ts`：

```typescript
import classNames from "classnames/bind";

/**
 * 强类型 cx 构造器
 * @param styles 导入的 CSS Modules 对象 (typeof import('*.module.scss'))
 */
export function createCx<T extends Record<string, string>>(styles: T) {
  const cx = classNames.bind(styles);

  // 定义参数类型：可以是 styles 的 key，或者是以 key 为键的布尔对象
  type ClassNameArg =
    | keyof T
    | { [K in keyof T]?: boolean | undefined | null }
    | undefined
    | null
    | false
    | string; // 允许传入普通字符串用于合并外部类名

  return (...args: ClassNameArg[]) => cx(...(args as any));
}
```

## 4. 组件实战用法

### 步骤 A：编写 SCSS

```scss
/* button.module.scss */
.baseBtn {
  padding: 10px;
  &.primary {
    background: blue;
  }
}
```

### 步骤 B：在组件中使用

```tsx
import React from "react";
import rawStyles from "./button.module.scss";
import type ButtonStyles from "./button.module.scss"; // 导入生成的类型
import { createCx } from "@/utils/cx";

// 1. 强类型转换并创建 cx
const styles = rawStyles as unknown as typeof ButtonStyles;
const cx = createCx(styles);

interface Props {
  type?: "primary" | "default";
  className?: string;
}

const Button: React.FC<Props> = ({ type, className }) => {
  // 2. 此时输入 'ba' 会自动提示 'baseBtn'，输入 'pr' 提示 'primary'
  const internalClass = cx("baseBtn", {
    primary: type === "primary",
  });

  return (
    <button className={`${internalClass} ${className || ""}`}>提交</button>
  );
};
```

## 5. 关键避坑与技巧总结

### Q: 为什么点击 styles 跳转到了 `client.d.ts`？

- **原因**: Vite 的全局声明优先级过高。
- **对策**: 使用 `as unknown as typeof Styles` 显式指定类型。这样 TS 就能越过全局定义，精准匹配到你生成的 `.scss.d.ts`。

### Q: 嵌套类名支持 `styles.root.btn` 吗？

- **不支持**。CSS Modules 的 `styles` 对象永远是**扁平**的键值对。即使 SCSS 嵌套，在 JS 里也只需通过 `cx('btn')` 直接访问。

### Q: 什么时候用 `styles.xxx`，什么时候用 `cx('xxx')`？

- **`styles.xxx`**: 静态、单一类名，性能最高，提示最稳。
- **`cx(...)`**: 动态切换、多类名组合，逻辑最优雅。

---

## 6. 开发者心法：Vue 开发者转 React 的样式映射

| 功能           | Vue 2/3                   | React (Modules + Typed cx)       |
| -------------- | ------------------------- | -------------------------------- |
| **局部作用域** | `<style scoped>`          | `*.module.scss`                  |
| **动态绑定**   | `:class="{ active: ok }"` | `cx({ active: ok })`             |
| **外部类名**   | 自动合并                  | 手动合并或在 `cx` 参数中加入变量 |
| **智能补全**   | Volar                     | `sass-dts` + `createCx`          |

## 7. vscode css modules插件

也可以使用vscode的css modules插件，来实现css modules的智能补全和动态绑定。

但是cx函数的类型提示会失效,只能手动输入。

插件地址：[vscode-css-modules](https://marketplace.visualstudio.com/items?itemName=clinyong.vscode-css-modules)

```tsx
import { createCx } from "../../utils/typedCx";
import rawStyles from "./button.module.scss";

interface ButtonProps {
  isPrimary: boolean;
  isDisabled: boolean;
}

const cx = createCx(rawStyles);

const Button = ({ isPrimary, isDisabled }: ButtonProps) => {
  return (
    <div className={rawStyles.container}>
      <button
        className={cx("btn-primary", {
          "btn-disabled": isDisabled,
          "btn-primary": isPrimary,
        })}
      >
        提交
      </button>
    </div>
  );
};

export default Button;
```
