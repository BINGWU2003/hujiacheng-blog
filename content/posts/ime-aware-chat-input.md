---
title: "IME 输入法感知 —— 聊天输入框 Enter 键冲突问题"
date: 2026-05-17
draft: false
description: ""
tags: []
categories: ["笔记"]
---

## 问题背景

在实现 AI 聊天组件时，需要支持以下交互：
- `Enter` → 发送消息

在考虑中文输入法场景时，发现存在一个经典的前端兼容性问题：**IME 组合输入状态下的 Enter 键会和发送消息的 Enter 键产生冲突。**

---

## 什么是 IME 组合输入状态

IME（Input Method Editor，输入法编辑器）是操作系统提供的输入法框架。当用户使用中文/日文/韩文输入法时，打字过程分两个阶段：

```
用户按字母键 "nihao"
    ↓
浏览器进入 Composition（组合）状态
    ↓
候选框出现，显示 "你好"、"nihao" 等候选词
    ↓
用户按 Enter / 空格 / 数字键 确认选词
    ↓
compositionend 触发，文字上屏，Composition 状态结束
```

在 Composition 状态期间，浏览器会触发三个专属事件：
- `compositionstart` —— 进入组合状态
- `compositionupdate` —— 组合内容更新
- `compositionend` —— 组合结束，文字上屏

---

## 核心 Bug：事件顺序冲突

### 旧版浏览器（Chrome < 53 / 部分移动端 WebView）

```
用户在 IME 状态下按 Enter 确认选词：

keydown(key='Enter', isComposing=true)   ← 先触发！
    ↓ 如果没有 isComposing 判断，sendMessage() 被调用
compositionend                            ← 后触发，文字才上屏
```

**后果：** 用户只是想确认选词，结果把输入框里**上一条消息的内容**意外发送出去了，且用户完全不知情。

### 现代浏览器（Chrome ≥ 53 / 新版 Firefox）

```
用户在 IME 状态下按 Enter 确认选词：

compositionend                            ← 先触发，isComposing → false
keydown(key='Enter', isComposing=false)  ← 后触发，isComposing 已为 false
```

现代浏览器已修复事件顺序，所以在 PC 端现代浏览器上难以复现此问题。

---

## 解决方案

在 `keydown.enter` 处理函数开头加入 IME 状态检测：

```js
handleEnterPress(e) {
  // 检查是否处于 IME 组合输入状态
  if (e.isComposing || e.keyCode === 229) {
    return;
  }

  if (e.shiftKey) {
    // Shift + Enter：插入换行符
    const start = e.target.selectionStart;
    const end = e.target.selectionEnd;
    const value = e.target.value;
    this.newMessage = value.substring(0, start) + '\n' + value.substring(end);
    this.$nextTick(() => {
      e.target.selectionStart = e.target.selectionEnd = start + 1;
    });
  } else {
    // 仅按 Enter：发送消息
    this.sendMessage();
  }
},
```

### 两个判断条件的含义

| 条件 | 说明 |
|------|------|
| `e.isComposing` | 标准属性，`true` 表示当前处于 IME 组合状态 |
| `e.keyCode === 229` | 旧浏览器兼容写法，旧版浏览器在 IME 状态下会将所有按键的 `keyCode` 报告为 229 |

---

## 各环境的影响

| 环境 | isComposing 判断是否必要 |
|------|------------------------|
| 现代 PC 浏览器（Chrome 53+, 新版 Firefox） | 实际上不需要，但保留无害 |
| iOS Safari | ✅ 仍然需要 |
| Android WebView（企业 APP 内嵌 H5） | ✅ 仍然需要 |
| 旧版 Chrome（< 53） | ✅ 需要 |
| 微信/钉钉内置浏览器 | ✅ 需要 |

---

## 验证方法

### 方法一：控制台模拟（验证代码逻辑）

```js
// 在浏览器控制台手动模拟 isComposing=true 的 Enter 事件
const input = document.querySelector('.chat-textarea textarea');
const fakeEvent = new KeyboardEvent('keydown', {
  key: 'Enter',
  keyCode: 13,
  isComposing: true, // 模拟旧浏览器 / 移动端 IME 状态
  bubbles: true
});
input.dispatchEvent(fakeEvent);
```

若控制台打印了 `sendMessage` 被调用的日志，则说明缺少 `isComposing` 判断时存在 bug。

### 方法二：真机测试

在 iOS Safari 或 Android WebView 环境下，使用中文输入法测试 Enter 确认选词时是否意外触发发送。

---

## 补充：发送的内容是什么

当 bug 触发时（`keydown` 早于 `compositionend` 触发），此时：

- IME 缓冲区中正在组合的拼音 **尚未提交** 到 Vue 的数据模型
- `this.newMessage` 里存的是**输入框中已有的旧内容**

```
示例：
  输入框已有内容：  "这是上一条消息"
  正在 IME 输入：  "nihao"（候选框开着）
  用户按 Enter 确认选词
          ↓
  Bug 触发：sendMessage() 发送的是 "这是上一条消息"（旧内容！）
            而不是 "这是上一条消息nihao" 或 "这是上一条消息你好"
```

---

## 相关知识点

- `KeyboardEvent.isComposing` —— [MDN 文档](https://developer.mozilla.org/zh-CN/docs/Web/API/KeyboardEvent/isComposing)
- `CompositionEvent` —— compositionstart / compositionupdate / compositionend
- IME 兼容性处理是处理 CJK（中日韩）输入的标准实践
