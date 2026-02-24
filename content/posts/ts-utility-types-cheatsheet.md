---
title: "TypeScript 内置工具类型速查手册"
date: 2026-02-24
draft: false
description: "涵盖 TypeScript 全部官方内置工具类型，结合前端真实场景（组件库、后台管理、接口处理等）提供详细代码示例，对齐官方文档（含 TS 5.4 新增的 NoInfer）。"
tags: ["TypeScript"]
categories: ["笔记"]
---

TypeScript 提供了一批全局可用的内置工具类型（Utility Types），用于在类型层面完成常见的结构转换。本文结合前端日常开发（组件库开发、多租户后台、接口处理等）为**每一个**官方内置工具类型提供详细说明和实战示例。

> 参考：[TypeScript 官方文档 - Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)

---

## 目录

- [一、对象属性操作类](#一对象属性操作类)
  - [`Partial<Type>`](#1-partialtype--全部可选--ts-21)
  - [`Required<Type>`](#2-requiredtype--全部必填--ts-28)
  - [`Readonly<Type>`](#3-readonlytype--全部只读--ts-21)
  - [`Record<Keys, Type>`](#4-recordkeys-type--构造字典--ts-21)
  - [`Pick<Type, Keys>`](#5-picktype-keys--精准提取--ts-21)
  - [`Omit<Type, Keys>`](#6-omittype-keys--精准剔除--ts-35)
- [二、联合类型操作类](#二联合类型操作类)
  - [`Exclude<UnionType, ExcludedMembers>`](#7-excludeuniontype-excludedmembers--排除--ts-28)
  - [`Extract<Type, Union>`](#8-extracttype-union--提取交集--ts-28)
  - [`NonNullable<Type>`](#9-nonnullabletype--剔除空值--ts-28)
- [三、函数与实例推导类](#三函数与实例推导类)
  - [`Parameters<Type>`](#10-parameterstype--提取函数参数元组--ts-31)
  - [`ConstructorParameters<Type>`](#11-constructorparameterstype--提取构造函数参数--ts-31)
  - [`ReturnType<Type>`](#12-returntypetype--提取函数返回值类型--ts-28)
  - [`InstanceType<Type>`](#13-instancetypetype--提取实例类型--ts-28)
- [四、类型推断控制](#四类型推断控制)
  - [`NoInfer<Type>`](#14-noinfertype--阻止类型推断--ts-54)
- [五、this 相关](#五-this-相关)
  - [`ThisParameterType<Type>`](#15-thisparametertypetype--提取-this-类型--ts-33)
  - [`OmitThisParameter<Type>`](#16-omitthisparametertype--剥离-this-参数--ts-33)
  - [`ThisType<Type>`](#17-thistypetype--标记-this-类型--ts-23)
- [六、异步类型解包](#六异步类型解包)
  - [`Awaited<Type>`](#18-awaitedtype--递归解包-promise--ts-45)
- [七、字符串字面量操作](#七字符串字面量操作ts-41)
  - [`Uppercase<StringType>`](#19-uppercasestringtype--全大写)
  - [`Lowercase<StringType>`](#20-lowercasestringtype--全小写)
  - [`Capitalize<StringType>`](#21-capitalizestringtype--首字母大写)
  - [`Uncapitalize<StringType>`](#22-uncapitalizestringtype--首字母小写)

---

## 一、对象属性操作类

### 1. `Partial<Type>` — 全部可选 (TS 2.1)

将 `Type` 的所有属性变为**可选**，常用于组件库配置项——用户只需传入关心的部分，未传的由组件提供默认值。

> **底层实现**：`type Partial<T> = { [P in keyof T]?: T[P] }`，即对 `T` 的每个键加 `?`。

```typescript
interface TableConfig {
  border: boolean;
  stripe: boolean;
  size: "large" | "default" | "small";
  showHeader: boolean;
}

const customConfig: Partial<TableConfig> = {
  size: "small",
  stripe: true,
};
```

**场景：PATCH 接口请求体** — 编辑时只传需要修改的字段，`id` 单独保留为必填：

```typescript
type UpdateUserPayload = { id: string } & Partial<Omit<UserEntity, "id">>;

async function patchUser(payload: UpdateUserPayload) {
  // 只传 { id, avatar } 也合法
  await fetch(`/api/users/${payload.id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

patchUser({ id: "u-001", avatar: "https://cdn.example.com/new.png" }); // ✅
```

---

### 2. `Required<Type>` — 全部必填 (TS 2.8)

将 `Type` 的所有属性变为**必填**，是 `Partial` 的反向操作。

> **底层实现**：`type Required<T> = { [P in keyof T]-?: T[P] }`，`-?` 表示去掉 `?` 修饰符。

```typescript
type UserInputConfig = Partial<TableConfig>;

function mergeConfig(options: UserInputConfig): Required<TableConfig> {
  return {
    border: options.border ?? false,
    stripe: options.stripe ?? false,
    size: options.size ?? "default",
    showHeader: options.showHeader ?? true,
  };
}
```

**场景：表单提交前校验完整性** — 接口需要全部字段，防止遗漏：

```typescript
interface ProfileForm {
  nickname?: string;
  phone?: string;
  email?: string;
  departmentId?: string;
}

// 提交时断言所有字段已填写
function submitProfile(form: Required<ProfileForm>) {
  console.log("提交:", form.nickname, form.email);
}

// 调用时 TS 会强制要求所有字段
submitProfile({
  nickname: "Alice",
  phone: "138-0000-0000",
  email: "alice@example.com",
  departmentId: "D-02",
});
```

---

### 3. `Readonly<Type>` — 全部只读 (TS 2.1)

> **底层实现**：`type Readonly<T> = { readonly [P in keyof T]: T[P] }`，为每个属性加 `readonly`。  
> 注意：仅类型层面约束，运行时不等价于 `Object.freeze()`，深层属性仍可修改。

```typescript
interface TenantContext {
  tenantId: string;
  tenantName: string;
  isVip: boolean;
}

const currentTenant: Readonly<TenantContext> = {
  tenantId: "T-8848",
  tenantName: "华东区代理",
  isVip: true,
};
// currentTenant.tenantId = "T-1001"; // ❌ 只读属性
```

**场景：函数参数防篡改** — 明确声明函数不会修改传入的配置对象：

```typescript
function applyTheme(theme: Readonly<{ primary: string; fontSize: number }>) {
  // theme.primary = "red"; // ❌ 编译报错，阻止意外修改
  document.documentElement.style.setProperty("--primary", theme.primary);
}
```

**`Readonly` vs `as const`**

|          | `Readonly<T>`      | `as const`       |
| -------- | ------------------ | ---------------- |
| 作用范围 | 浅层（第一级属性） | 深层递归         |
| 使用场景 | 类型声明           | 字面量常量       |
| 类型推断 | 保留宽泛类型       | 推断为字面量类型 |

```typescript
const a = { x: 1, y: [2, 3] } as const;
// a.x = 10;     // ❌ 深层只读
// a.y.push(4);  // ❌ 数组也只读

const b: Readonly<{ x: number; y: number[] }> = { x: 1, y: [2, 3] };
// b.x = 10;     // ❌
b.y.push(4); // ✅ 浅层只读，数组内容仍可变
```

---

### 4. `Record<Keys, Type>` — 构造字典 (TS 2.1)

> **底层实现**：`type Record<K extends keyof any, T> = { [P in K]: T }`。  
> 与 `{ [key: string]: T }` 的区别：`Record` 的 `Keys` 是**受约束的联合类型**，所有 key 必须显式赋值，不会遗漏。

```typescript
type AppRole = "super_admin" | "tenant_admin" | "editor";

const rolePermissions: Record<AppRole, string[]> = {
  super_admin: ["all"],
  tenant_admin: ["user_manage", "content_manage"],
  editor: ["content_edit"],
  // 若漏写 editor，TS 会报错 ✅ 穷举检查
};

const cache: Record<string, unknown> = {};
cache["user_123"] = { name: "Alice" };
```

**场景：HTTP 状态码映射表** — Key 有限枚举时比 `Map` 更安全：

```typescript
type HttpStatus = 200 | 201 | 400 | 401 | 403 | 404 | 500;

const statusMessages: Record<HttpStatus, string> = {
  200: "OK",
  201: "Created",
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  500: "Internal Server Error",
};

function getStatusMessage(code: HttpStatus): string {
  return statusMessages[code];
}
```

**场景：以枚举为 Key 构建配置** — 搭配 `enum` 或常量联合类型防止遗漏分支：

```typescript
type Locale = "zh-CN" | "en-US" | "ja-JP";

const dateFormats: Record<Locale, Intl.DateTimeFormatOptions> = {
  "zh-CN": { year: "numeric", month: "2-digit", day: "2-digit" },
  "en-US": { month: "short", day: "numeric", year: "numeric" },
  "ja-JP": { year: "numeric", month: "long", day: "numeric" },
};
```

---

### 5. `Pick<Type, Keys>` — 精准提取 (TS 2.1)

> **底层实现**：`type Pick<T, K extends keyof T> = { [P in K]: T[P] }`。

```typescript
interface UserEntity {
  id: string;
  username: string;
  passwordHash: string;
  avatar: string;
  departmentId: string;
  createdAt: string;
}

type NavbarUserInfo = Pick<UserEntity, "username" | "avatar">;

const navUser: NavbarUserInfo = {
  username: "Admin",
  avatar: "https://cdn.example.com/avatar.png",
};
```

**场景：列表页只暴露展示字段** — 防止渲染层拿到敏感字段：

```typescript
// 列表卡片只需要这几个字段，不暴露 passwordHash / departmentId
type UserCardProps = Pick<UserEntity, "id" | "username" | "avatar">;

function UserCard({ id, username, avatar }: UserCardProps) {
  return `<div data-id="${id}">${username}</div>`;
}
```

---

### 6. `Omit<Type, Keys>` — 精准剔除 (TS 3.5)

> **底层实现**：`type Omit<T, K extends keyof any> = Pick<T, Exclude<keyof T, K>>`，本质是先 `Exclude` 再 `Pick`。

```typescript
type CreateUserPayload = Omit<UserEntity, "id" | "createdAt" | "passwordHash">;

const newUser: CreateUserPayload = {
  username: "new_employee",
  avatar: "",
  departmentId: "D-01",
};
```

**`Pick` vs `Omit` 使用原则**

- 保留字段**少**时用 `Pick`（枚举想要的）
- 去除字段**少**时用 `Omit`（枚举不想要的）
- 字段数量多、只剔除少数几个敏感字段 → 优先 `Omit`

**场景：DTO 分层** — 创建/更新接口各有不同的约束：

```typescript
// 创建：去掉服务端自动生成的字段
type CreateArticleDto = Omit<
  ArticleEntity,
  "id" | "createdAt" | "updatedAt" | "viewCount"
>;

// 更新：创建基础上再套 Partial，所有字段可选
type UpdateArticleDto = Partial<CreateArticleDto>;

// 查询响应：完整实体
type ArticleResponse = ArticleEntity;
```

---

## 二、联合类型操作类

### 7. `Exclude<UnionType, ExcludedMembers>` — 排除 (TS 2.8)

> **底层实现**：`type Exclude<T, U> = T extends U ? never : T`，分发条件类型——联合类型中每个成员逐一判断，命中则换成 `never`（被消除）。

```typescript
type ComponentSizes = "large" | "default" | "small" | "mini";

type ValidSizes = Exclude<ComponentSizes, "mini">;
// 结果: "large" | "default" | "small"

type NonFunction<T> = Exclude<T, Function>;
type T = NonFunction<string | number | (() => void)>;
// 结果: string | number
```

**场景：权限控制 — 删除管理员专属操作**

```typescript
type AllActions =
  | "view"
  | "create"
  | "edit"
  | "delete"
  | "export"
  | "manage_users";
type AdminOnlyActions = "delete" | "manage_users";

// 普通用户可用的操作
type RegularUserActions = Exclude<AllActions, AdminOnlyActions>;
// 结果: "view" | "create" | "edit" | "export"

function checkPermission(action: RegularUserActions) {
  console.log("普通用户执行:", action);
}
```

---

### 8. `Extract<Type, Union>` — 提取交集 (TS 2.8)

> **底层实现**：`type Extract<T, U> = T extends U ? T : never`，与 `Exclude` 逻辑正好相反——命中则保留。

```typescript
type LegacyFeatures = "login" | "log_view" | "sentry_monitor" | "export_excel";
type NewFeatures = "login" | "export_excel" | "pdf_preview";

type CommonFeatures = Extract<LegacyFeatures, NewFeatures>;
// 结果: "login" | "export_excel"
```

**`Exclude` vs `Extract` 记忆口诀**

|                 | 语义                        | 保留条件               |
| --------------- | --------------------------- | ---------------------- |
| `Exclude<T, U>` | T 中**排除** U 的部分       | `T extends U` 为 false |
| `Extract<T, U>` | T 中**提取**与 U 重叠的部分 | `T extends U` 为 true  |

**场景：事件系统 — 只处理 DOM 鼠标事件**

```typescript
type DOMEvents = keyof HTMLElementEventMap;
type MouseEventNames = Extract<DOMEvents, `mouse${string}`>;
// 结果: "mousedown" | "mouseenter" | "mouseleave" | "mousemove" | ...

function onMouseEvent(
  event: MouseEventNames,
  handler: (e: MouseEvent) => void,
) {
  document.addEventListener(event, handler as EventListener);
}
```

---

### 9. `NonNullable<Type>` — 剔除空值 (TS 2.8)

> **底层实现**：`type NonNullable<T> = T & {}`（TS 4.8 之前是 `T extends null | undefined ? never : T`）。  
> 通常配合**类型收窄**（`if (x != null)`）或**非空断言**（`x!`）一起使用。

```typescript
type SentryIssueId = string | number | null | undefined;

function resolveIssue(id: SentryIssueId) {
  if (id == null) return;
  const validId: NonNullable<SentryIssueId> = id;
  console.log("处理 issue:", validId);
}

type T0 = NonNullable<string | number | undefined>; // string | number
type T1 = NonNullable<string[] | null | undefined>; // string[]
```

**场景：封装非空断言工具函数**，配合泛型给断言结果精确类型：

```typescript
function assertDefined<T>(val: T, name: string): NonNullable<T> {
  if (val == null) {
    throw new Error(`[断言失败] ${name} 不能为空`);
  }
  return val as NonNullable<T>;
}

const userId = assertDefined(localStorage.getItem("userId"), "userId");
// userId 类型为 string（去掉了 null）
```

---

## 三、函数与实例推导类

### 10. `Parameters<Type>` — 提取函数参数元组 (TS 3.1)

> **底层实现**：`type Parameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never`，使用 `infer` 在条件类型中推断参数元组。

```typescript
function legacySubmit(data: { id: number; code: string }, force: boolean) {
  // ...
}

type LegacyParams = Parameters<typeof legacySubmit>;
// 结果: [data: { id: number; code: string }, force: boolean]

function myWrapper(...args: LegacyParams) {
  console.log("拦截记录:", args[0].code);
  return legacySubmit(...args);
}
```

**场景：函数防抖/节流包装器** — 保留原函数类型，不丢失参数签名：

```typescript
function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number,
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

function handleSearch(keyword: string, page: number) {
  console.log("搜索:", keyword, page);
}

// debouncedSearch 保留了 (keyword: string, page: number) 的类型
const debouncedSearch = debounce(handleSearch, 300);
debouncedSearch("typescript", 1); // ✅ 类型安全
```

---

### 11. `ConstructorParameters<Type>` — 提取构造函数参数 (TS 3.1)

> **底层实现**：`type ConstructorParameters<T extends abstract new (...args: any) => any> = T extends abstract new (...args: infer P) => any ? P : never`。

```typescript
class MonitorService {
  constructor(
    public dsn: string,
    public maxBreadcrumbs: number,
  ) {}
}

type MonitorConfig = ConstructorParameters<typeof MonitorService>;
// 结果: [dsn: string, maxBreadcrumbs: number]

const config: MonitorConfig = ["https://sentry.io/dsn/xxx", 50];
const service = new MonitorService(...config);
```

**场景：工厂函数 / 依赖注入容器** — 动态创建类实例，参数类型与构造函数同步：

```typescript
function createInstance<T extends new (...args: any[]) => any>(
  Cls: T,
  ...args: ConstructorParameters<T>
): InstanceType<T> {
  return new Cls(...args);
}

class HttpClient {
  constructor(
    public baseUrl: string,
    public timeout: number,
    public withCredentials: boolean,
  ) {}
}

// 参数类型由 HttpClient 的构造函数自动推导
const client = createInstance(
  HttpClient,
  "https://api.example.com",
  5000,
  true,
);
client.baseUrl; // string ✅
```

---

### 12. `ReturnType<Type>` — 提取函数返回值类型 (TS 2.8)

> **底层实现**：`type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any`。

```typescript
function useDeviceState() {
  return {
    isMobile: false,
    screenWidth: 1920,
    orientation: "landscape" as "landscape" | "portrait",
  };
}

type DeviceState = ReturnType<typeof useDeviceState>;
// 结果: { isMobile: boolean; screenWidth: number; orientation: "landscape" | "portrait" }

function applyState(state: DeviceState) {
  if (!state.isMobile) {
    console.log("桌面端宽度:", state.screenWidth);
  }
}
```

**场景：Redux / Pinia 中推导 Store 的 State 类型** — 避免手动维护重复的类型定义：

```typescript
function createUserStore() {
  return {
    list: [] as UserEntity[],
    loading: false,
    pagination: { page: 1, pageSize: 20, total: 0 },
  };
}

// 直接从 Store 工厂函数推导，无需再手写 UserStoreState 接口
type UserStoreState = ReturnType<typeof createUserStore>;
// { list: UserEntity[]; loading: boolean; pagination: { page: number; pageSize: number; total: number } }
```

**场景：组合 `Parameters` + `ReturnType` 实现通用缓存装饰器**

```typescript
function memoize<T extends (...args: any[]) => any>(
  fn: T,
): (...args: Parameters<T>) => ReturnType<T> {
  const cache = new Map<string, ReturnType<T>>();
  return (...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key)!;
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}

const expensiveCalc = memoize((a: number, b: number) => a * b + Math.random());
expensiveCalc(2, 3); // 计算并缓存
expensiveCalc(2, 3); // 直接返回缓存，类型为 number ✅
```

---

### 13. `InstanceType<Type>` — 提取实例类型 (TS 2.8)

```vue
<!-- IipForm.vue（子组件）-->
<script setup lang="ts">
const validate = async (): Promise<boolean> => {
  return true;
};
const reset = (): void => {
  /* 重置 */
};
defineExpose({ validate, reset });
</script>
```

```vue
<!-- 父组件 -->
<script setup lang="ts">
import { ref } from "vue";
import IipForm from "./IipForm.vue";

const formRef = ref<InstanceType<typeof IipForm> | null>(null);

const onSubmit = async () => {
  if (!formRef.value) return;
  const isValid = await formRef.value.validate();
  if (isValid) formRef.value.reset();
};
</script>
```

---

## 四、类型推断控制

### 14. `NoInfer<Type>` — 阻止类型推断 (TS 5.4)

> **作用**：`NoInfer<T>` 包裹某个位置后，TypeScript 不再从该位置**推断**泛型变量，但仍然会在该位置**校验**泛型变量是否匹配。这使得泛型推断完全由其他「参与推断的位置」决定。

```typescript
// 不使用 NoInfer：defaultColor 污染推断，"blue" 不报错
function createStreetLightBad<C extends string>(
  colors: C[],
  defaultColor?: C,
) {}
createStreetLightBad(["red", "yellow", "green"], "blue");
// ❌ 不报错！TS 把 C 推断为 "red" | "yellow" | "green" | "blue"

// 使用 NoInfer：defaultColor 不参与推断，强制只能传 colors 中的值
function createStreetLight<C extends string>(
  colors: C[],
  defaultColor?: NoInfer<C>,
) {}
createStreetLight(["red", "yellow", "green"], "red"); // ✅ OK
createStreetLight(["red", "yellow", "green"], "blue"); // ❌ 报错
```

**场景：i18n 翻译函数** — 确保 `fallback` 只能是已知的 key：

```typescript
const messages = {
  welcome: "欢迎",
  goodbye: "再见",
  error: "出错了",
} as const;

type MessageKey = keyof typeof messages;

function t<K extends MessageKey>(key: K, fallback?: NoInfer<K>): string {
  return messages[key] ?? (fallback ? messages[fallback] : "");
}

t("welcome"); // ✅
t("welcome", "goodbye"); // ✅ fallback 也是合法的 key
t("welcome", "unknown"); // ❌ 报错，"unknown" 不是 MessageKey
```

---

## 五、`this` 相关

### 15. `ThisParameterType<Type>` — 提取 `this` 类型 (TS 3.3)

> **说明**：TypeScript 允许在函数第一个参数位置写 `this: SomeType` 来标注调用时 `this` 的类型（编译后该参数会被擦除）。`ThisParameterType` 用于从函数类型中提取这个隐式的 `this` 类型。

```typescript
function toHex(this: Number) {
  return this.toString(16);
}

type HexThis = ThisParameterType<typeof toHex>;
// 结果: Number

function numberToString(n: HexThis) {
  return toHex.apply(n);
}
```

**场景：Vue 2 Options API 工具函数** — 提取 `this` 类型后复用：

```typescript
const mixin = {
  data() {
    return { count: 0 };
  },
  methods: {
    increment(this: { count: number }) {
      this.count++;
    },
  },
};

type IncrementThis = ThisParameterType<typeof mixin.methods.increment>;
// 结果: { count: number }
```

---

### 16. `OmitThisParameter<Type>` — 剥离 `this` 参数 (TS 3.3)

> **说明**：将带有 `this` 参数的函数类型转为不含 `this` 的普通函数类型，适用于将方法作为回调传递时消除 `this` 的约束。

```typescript
function toHex(this: Number) {
  return this.toString(16);
}

const fiveToHex: OmitThisParameter<typeof toHex> = toHex.bind(5);
console.log(fiveToHex()); // "5"
```

**场景：将实例方法安全地作为回调传递**

```typescript
class Formatter {
  prefix = "[LOG]";

  format(this: Formatter, msg: string) {
    return `${this.prefix} ${msg}`;
  }
}

const formatter = new Formatter();

// 绑定 this 后，类型中的 this 约束消除，可以安全地传递给第三方 API
const boundFormat: OmitThisParameter<typeof formatter.format> =
  formatter.format.bind(formatter);

["err", "warn", "info"].map(boundFormat); // ✅
```

---

### 17. `ThisType<Type>` — 标记 `this` 类型 (TS 2.3)

> **说明**：`ThisType<T>` 本身不产生任何类型，只是一个**标记接口**，告诉 TypeScript 某个对象字面量内部的 `this` 应该是 `T` 类型。通常与 `&` 交叉类型一起用在 `methods` 声明上。
>
> 注意：需要在 `tsconfig.json` 中开启 `"noImplicitThis": true`。

```typescript
type ObjectDescriptor<D, M> = {
  data?: D;
  methods?: M & ThisType<D & M>;
};

function makeObject<D, M>(desc: ObjectDescriptor<D, M>): D & M {
  const data: object = desc.data || {};
  const methods: object = desc.methods || {};
  return { ...data, ...methods } as D & M;
}

const obj = makeObject({
  data: { x: 0, y: 0 },
  methods: {
    moveBy(dx: number, dy: number) {
      this.x += dx; // ✅ 强类型 this
      this.y += dy;
    },
  },
});

obj.x = 10;
obj.moveBy(5, 5);
```

---

## 六、异步类型解包

### 18. `Awaited<Type>` — 递归解包 Promise (TS 4.5)

> **底层实现**：TS 4.5 引入，递归地解包 `.then()` 方法的结果类型，直到不再是 thenable 为止。与之前的 `UnpackedPromise` 手写方案相比，能正确处理任意深度嵌套的 Promise。

```typescript
type A = Awaited<Promise<string>>; // string
type B = Awaited<Promise<Promise<number>>>; // number（递归解包）
type C = Awaited<boolean | Promise<number>>; // boolean | number
```

**场景：从异步函数推导返回值类型**，用于跨层传递数据类型：

```typescript
interface PageResult<T> {
  records: T[];
  total: number;
}
interface TenantData {
  id: string;
  name: string;
}

async function fetchTenants(): Promise<PageResult<TenantData>> {
  return { records: [{ id: "1", name: "华东区" }], total: 1 };
}

type FetchResult = Awaited<ReturnType<typeof fetchTenants>>;
// 结果: PageResult<TenantData>（Promise 被解包）

function renderList(data: FetchResult) {
  console.log(`共 ${data.total} 条`, data.records);
}
```

**场景：`Promise.all` 类型推导** — TS 内部 `Promise.all` 签名就使用了 `Awaited`：

```typescript
async function getUserAndOrders(userId: string) {
  const [user, orders] = await Promise.all([
    fetchUser(userId), // Promise<UserEntity>
    fetchOrders(userId), // Promise<OrderEntity[]>
  ]);
  // user: UserEntity，orders: OrderEntity[] — 自动解包 ✅
  return { user, orders };
}

// 推导并联结两个异步结果的类型
type DashboardData = Awaited<ReturnType<typeof getUserAndOrders>>;
// { user: UserEntity; orders: OrderEntity[] }
```

---

## 七、字符串字面量操作（TS 4.1+）

> 这四个工具类型均为**内置编译器魔法**（intrinsic），无法通过普通 TypeScript 代码实现，直接作用于字符串字面量类型。它们常与**模板字面量类型**（Template Literal Types）配合，批量生成派生类型。

### 19. `Uppercase<StringType>` — 全大写

```typescript
type Environment = "dev" | "test" | "prod";
type EnvConst = `VITE_APP_ENV_${Uppercase<Environment>}`;
// 结果: "VITE_APP_ENV_DEV" | "VITE_APP_ENV_TEST" | "VITE_APP_ENV_PROD"
```

---

### 20. `Lowercase<StringType>` — 全小写

```typescript
type BuildEnv = "Dev" | "Test" | "Prod";
type OutDir = `dist/${Lowercase<BuildEnv>}`;
// 结果: "dist/dev" | "dist/test" | "dist/prod"
```

---

### 21. `Capitalize<StringType>` — 首字母大写

```typescript
type ModelKeys = "visible" | "title" | "content";
type EmitEvents = `onUpdate${Capitalize<ModelKeys>}`;
// 结果: "onUpdateVisible" | "onUpdateTitle" | "onUpdateContent"
```

---

### 22. `Uncapitalize<StringType>` — 首字母小写

```typescript
type ComponentName = "Button" | "Input" | "Select";
type CssClass = `iip-${Uncapitalize<ComponentName>}`;
// 结果: "iip-button" | "iip-input" | "iip-select"
```

---

### 综合示例：批量生成 getter / setter 类型

利用上面四个工具类型 + 模板字面量类型，可以从一个基础类型自动派生出完整的访问器类型，无需手动逐一声明：

```typescript
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type Setters<T> = {
  [K in keyof T as `set${Capitalize<string & K>}`]: (value: T[K]) => void;
};

interface UserStore {
  name: string;
  age: number;
  isAdmin: boolean;
}

type UserGetters = Getters<UserStore>;
// {
//   getName: () => string;
//   getAge: () => number;
//   getIsAdmin: () => boolean;
// }

type UserSetters = Setters<UserStore>;
// {
//   setName: (value: string) => void;
//   setAge: (value: number) => void;
//   setIsAdmin: (value: boolean) => void;
// }

type UserStoreInterface = UserStore & UserGetters & UserSetters;
```

**场景：生成 CSS 变量工具类型** — 统一管控设计 Token：

```typescript
type DesignToken = "primary" | "secondary" | "danger" | "warning";

// CSS 变量名：--color-primary, --color-secondary ...
type CssVarName = `--color-${DesignToken}`;

// 对应的 JS 变量名（驼峰）：colorPrimary, colorSecondary ...
type JsVarName = `color${Capitalize<DesignToken>}`;

const tokenMap: Record<JsVarName, CssVarName> = {
  colorPrimary: "--color-primary",
  colorSecondary: "--color-secondary",
  colorDanger: "--color-danger",
  colorWarning: "--color-warning",
};
```

---

## 速查表

| 工具类型                   | 作用                    | 引入版本 |
| -------------------------- | ----------------------- | :------: |
| `Partial<T>`               | 所有属性变可选          |   2.1    |
| `Required<T>`              | 所有属性变必填          |   2.8    |
| `Readonly<T>`              | 所有属性变只读          |   2.1    |
| `Record<K, T>`             | 构造 key-value 映射类型 |   2.1    |
| `Pick<T, K>`               | 提取指定属性            |   2.1    |
| `Omit<T, K>`               | 剔除指定属性            |   3.5    |
| `Exclude<T, U>`            | 联合类型排除            |   2.8    |
| `Extract<T, U>`            | 联合类型取交集          |   2.8    |
| `NonNullable<T>`           | 剔除 null / undefined   |   2.8    |
| `Parameters<T>`            | 提取函数参数元组        |   3.1    |
| `ConstructorParameters<T>` | 提取构造函数参数元组    |   3.1    |
| `ReturnType<T>`            | 提取函数返回值类型      |   2.8    |
| `InstanceType<T>`          | 提取类实例类型          |   2.8    |
| `NoInfer<T>`               | 阻止泛型推断            | **5.4**  |
| `ThisParameterType<T>`     | 提取函数 this 类型      |   3.3    |
| `OmitThisParameter<T>`     | 移除函数 this 参数      |   3.3    |
| `ThisType<T>`              | 标记上下文 this 类型    |   2.3    |
| `Awaited<T>`               | 递归解包 Promise        |   4.5    |
| `Uppercase<S>`             | 字符串字面量全大写      |   4.1    |
| `Lowercase<S>`             | 字符串字面量全小写      |   4.1    |
| `Capitalize<S>`            | 字符串字面量首字母大写  |   4.1    |
| `Uncapitalize<S>`          | 字符串字面量首字母小写  |   4.1    |
