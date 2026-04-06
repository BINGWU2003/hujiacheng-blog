---
title: "Git 代理配置指南（Windows）"
date: 2026-04-06
draft: false
description: ""
tags: ["Git", "代理", "Windows"]
categories: ["博客"]
---

## 查看当前代理配置

```cmd
git config --global --list | findstr proxy
```

> ⚠️ Windows CMD 没有 `grep`，需用 `findstr` 替代。PowerShell 用 `Select-String proxy`。

---

## 配置代理

### 全局代理（所有域名生效）

```cmd
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### 域名级代理（推荐，精准控制）

只给指定域名配代理，其他域名不受影响：

```cmd
rem 只给 GitHub 配代理
git config --global http.https://github.com.proxy http://127.0.0.1:7890

rem 给不同域名配不同代理
git config --global http.https://github.com.proxy http://127.0.0.1:7890
git config --global http.https://gitlab.com.proxy http://127.0.0.1:10808
```

> 域名级代理优先级高于全局代理。

### SOCKS5 代理

v2ray 默认 10808 端口为 socks5 协议，需使用以下格式：

```cmd
git config --global http.https://github.com.proxy socks5://127.0.0.1:10808
```

> 常见端口说明：
> - **Clash**：7890（HTTP）
> - **v2ray/v2rayN**：10808（SOCKS5）、10809（HTTP）

---

## 取消代理

```cmd
rem 取消全局代理
git config --global --unset http.proxy
git config --global --unset https.proxy

rem 取消指定域名代理
git config --global --unset http.https://github.com.proxy
```

---

## 多代理工具切换（Clash / v2ray）

Git 对同一域名只能配一个代理，不同工具需手动切换。

推荐创建两个批处理脚本，放在顺手的目录下：

**`use-clash.bat`**
```bat
git config --global http.https://github.com.proxy http://127.0.0.1:7890
echo 已切换到 Clash (7890)
```

**`use-v2ray.bat`**
```bat
git config --global http.https://github.com.proxy http://127.0.0.1:10808
echo 已切换到 v2ray (10808)
```

双击或在命令行运行即可切换。

---

## 验证代理是否生效

**1. 确认配置写入：**

```cmd
git config --global --list | findstr proxy
```

**2. 确认端口正在监听（代理工具是否在运行）：**

```cmd
netstat -ano | findstr 7890
```

有输出说明代理工具正常运行，无输出则需启动 Clash / v2ray。

---

## 推荐配置（仅 GitHub 走代理）

```cmd
rem 删除全局代理（避免影响其他域名）
git config --global --unset http.proxy
git config --global --unset https.proxy

rem 只给 GitHub 配域名级代理
git config --global http.https://github.com.proxy http://127.0.0.1:7890
```

最终 `--list` 中只会有这一条代理配置：

```
http.https://github.com.proxy=http://127.0.0.1:7890
```

---

## SSH 推送代理配置

如果远端地址格式为 `git@github.com:...`（SSH），HTTP 代理不生效，需编辑 `~/.ssh/config`：

```
Host github.com
  HostName github.com
  User git
  ProxyCommand connect -S 127.0.0.1:7890 %h %p
```

> `connect.exe` 通常随 Git for Windows 一起安装，位于 Git 安装目录的 `mingw64/bin/` 下。

---

## 判断使用哪种代理

```cmd
git remote -v
```

| 远端地址格式 | 代理类型 |
|---|---|
| `https://github.com/...` | HTTP 代理 |
| `git@github.com:...` | SSH 代理 |
