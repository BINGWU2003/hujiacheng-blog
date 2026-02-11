---
title: "Vue 3 Composition API 实战指南"
date: 2026-02-08
draft: false
description: "深入理解 Vue 3 Composition API 的核心概念，包括 ref、reactive、computed 和 watch 的使用。"
tags: ["Vue", "JavaScript", "前端"]
categories: ["前端开发"]
---

## 为什么需要 Composition API？

Vue 2 的 Options API 在组件逻辑复杂时会导致相关代码分散在 `data`、`methods`、`computed` 等不同选项中。Composition API 让我们可以按功能组织代码。

## 核心 API

### ref 和 reactive

```typescript
import { ref, reactive } from "vue";

// ref 用于基本类型
const count = ref(0);

// reactive 用于对象
const state = reactive({
  name: "hujiacheng",
  age: 25,
});
```

### computed

```typescript
import { ref, computed } from "vue";

const price = ref(100);
const quantity = ref(3);

const total = computed(() => price.value * quantity.value);
```

### watch 和 watchEffect

```typescript
import { ref, watch, watchEffect } from "vue";

const keyword = ref("");

// 监听特定值
watch(keyword, (newVal, oldVal) => {
  console.log(`搜索关键词从 "${oldVal}" 变为 "${newVal}"`);
});

// 自动追踪依赖
watchEffect(() => {
  console.log(`当前关键词: ${keyword.value}`);
});
```

## 自定义 Hook

Composition API 最大的优势是可以轻松提取和复用逻辑：

```typescript
// useCounter.ts
export function useCounter(initial = 0) {
  const count = ref(initial);
  const increment = () => count.value++;
  const decrement = () => count.value--;
  const reset = () => (count.value = initial);

  return { count, increment, decrement, reset };
}
```

Composition API 让 Vue 3 的代码组织更加灵活和可维护。
