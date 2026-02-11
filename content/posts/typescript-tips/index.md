---
title: "TypeScript 实用技巧与最佳实践"
date: 2026-02-05
draft: false
description: "分享一些日常开发中常用的 TypeScript 技巧，提升代码质量和开发效率。"
tags: ["TypeScript", "JavaScript", "前端"]
categories: ["前端开发"]
---

## 类型工具

TypeScript 内置了很多实用的类型工具，善用它们可以减少重复代码。

### Partial 和 Required

```typescript
interface User {
  name: string;
  email: string;
  avatar?: string;
}

// 所有属性变为可选
type UpdateUser = Partial<User>;

// 所有属性变为必填
type CompleteUser = Required<User>;
```

### Pick 和 Omit

```typescript
// 只选取部分属性
type UserBasic = Pick<User, "name" | "email">;

// 排除部分属性
type UserWithoutAvatar = Omit<User, "avatar">;
```

## 类型守卫

```typescript
interface Cat {
  meow: () => void;
}

interface Dog {
  bark: () => void;
}

function isCat(animal: Cat | Dog): animal is Cat {
  return (animal as Cat).meow !== undefined;
}

function makeSound(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow(); // TypeScript 知道这里是 Cat
  } else {
    animal.bark(); // TypeScript 知道这里是 Dog
  }
}
```

## 模板字面量类型

```typescript
type Color = "red" | "blue" | "green";
type Size = "sm" | "md" | "lg";

// 自动生成 "red-sm" | "red-md" | ... | "green-lg"
type ClassName = `${Color}-${Size}`;
```

## const 断言

```typescript
// as const 让对象变为深度只读，类型更精确
const config = {
  api: "https://api.example.com",
  timeout: 5000,
  retries: 3,
} as const;

// typeof config.api 是 "https://api.example.com" 而不是 string
```

掌握这些技巧，可以让你的 TypeScript 代码更加健壮和优雅！
