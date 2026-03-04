# 批量处理小册文章 —— AI 提示词

## 背景说明

本博客使用 Hugo 静态站点框架，主题为 Blowfish。小册文章统一放在 `content/{section}/` 下，需符合以下规范：

- 文章文件名格式：`{序号:02d}-{英文slug}.md`（如 `01-opening.md`）
- 每篇文章需有 Hugo front matter（YAML 格式，`---` 包裹）
- 每个 section 需有 `_index.md` 索引页
- 菜单配置在 `config/_default/menus.zh-cn.toml`，小册统一挂在 `parent = "小册"` 下

---

## 标准 Front Matter 格式

```yaml
---
title: "文章标题"
date: 2025-01-01
draft: false
description: ""
tags: ["tag1", "tag2"]
categories: ["分类名"]
series: ["系列名"]
series_order: 1
---
```

---

## 已有小册及配置

| 小册名称                | 目录                  | 菜单 weight | date 起点  | categories |
| ----------------------- | --------------------- | ----------- | ---------- | ---------- |
| NestJS 通关秘籍         | `nestjs/`             | 10          | 2025-01-01 | NestJS     |
| 深入浅出 Vite           | `vite/`               | 20          | 2025-06-01 | Vite       |
| Vue 3 源码揭秘          | `vue3/`               | 30          | 2025-09-01 | Vue3       |
| TypeScript 全面进阶指南 | `typescript/`         | 40          | 2025-03-01 | TypeScript |
| TypeScript 类型体操     | `ts-type-gymnastics/` | 50          | 2025-04-01 | TypeScript |

> 新增小册 weight 依次递增 10，date 起点选择未被占用的月份。

---

## 任务说明（给 AI 的指令）

### 目标

将新增小册 `content/{目录名}/` 下的文章按规范处理：

1. **重命名目录**（如果是中文目录名）：`Rename-Item "content\中文目录" "英文目录"`
2. **更新菜单**：在 `config/_default/menus.zh-cn.toml` 的"小册"子菜单中添加新条目
3. **创建 `_index.md`**：为该 section 创建 Hugo 索引页
4. **编写并执行处理脚本**：参照 `scripts/process_vite.py` 的模式，批量添加 front matter 并重命名文件

### 需要 AI 完成的具体步骤

**Step 1：调研阶段**

请先读取以下信息再动手：

- 列出目标目录的所有文件（确认文章数量、文件名格式）
- 读取 2-3 篇文章的前 15 行（确认是否有 front matter、是否有水印）
- 读取当前 `menus.zh-cn.toml`（确认当前 weight 最大值）
- 搜索文章中是否含 `cunlove` 或 `耗时整理` 水印

**Step 2：制定映射表**

根据文章标题，生成 `FILE_MAP`：

```python
FILE_MAP = {
    序号: ("英文-slug", "清洗后的中文标题"),
    ...
}
```

英文 slug 规则：

- 全小写
- 空格用 `-` 连接
- 去掉标点（冒号、问号、括号等）
- 尽量简洁（5 个单词以内）

**Step 3：制定 Series 分组**

根据文章内容，将文章分为 3-6 个 series 组：

```python
SERIES_MAP = {
    "系列名 A": list(range(1, N)),
    "系列名 B": list(range(N, M)),
    ...
}
```

**Step 4：确定标签关键词**

根据文章主题，在 `TAG_KEYWORDS` 字典中添加关键词 → tag 的映射。

**Step 5：执行**

1. 编写 `scripts/process_{section}.py`（参照现有脚本模式）
2. 先运行 `python scripts/process_{section}.py --dry-run` 预览
3. 确认无误后运行 `python scripts/process_{section}.py` 正式处理

---

## 参考脚本模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from pathlib import Path
from datetime import date, timedelta

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "{section}"
START_DATE = date(2025, X, 1)  # 选择未被占用的月份

SERIES_MAP = {
    "系列名": list(range(1, N)),
}

NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

TAG_KEYWORDS = {
    "关键词": "tag",
}

FILE_MAP = {
    1: ("slug", "中文标题"),
}

def get_tags(num, title):
    tags = ["{主标签}"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags

def find_file_for_num(num):
    for f in CONTENT_DIR.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        m = re.match(r'^(\d+)\.', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None

def generate_front_matter(num, slug, title, tags, series):
    d = START_DATE + timedelta(days=num - 1)
    series_nums = SERIES_MAP.get(series, [])
    series_order = series_nums.index(num) + 1 if num in series_nums else num
    safe_title = title.replace('"', '\\"')
    safe_series = series.replace('"', '\\"')
    tags_str = ', '.join(f'"{t}"' for t in tags)
    return f'''---
title: "{safe_title}"
date: {d.strftime('%Y-%m-%d')}
draft: false
description: ""
tags: [{tags_str}]
categories: ["{分类名}"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''

def process_file(num, dry_run=True):
    if num not in FILE_MAP:
        return False, f"#{num}: 未找到"
    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, list(SERIES_MAP.keys())[0])
    tags = get_tags(num, clean_title)
    src_file = find_file_for_num(num)
    new_name = f"{num:02d}-{slug}.md"
    dst_file = CONTENT_DIR / new_name
    if src_file is None:
        return (True, f"已处理过") if dst_file.exists() else (False, f"#{num}: 未找到源文件")
    if dry_run:
        content = src_file.read_text(encoding='utf-8')
        has_fm = content.strip().startswith('---')
        return True, f"#{num:02d}: {src_file.name}\n  -> {new_name}\n  title: \"{clean_title}\"\n  series: \"{series}\"\n  tags: {tags}\n  has_frontmatter: {has_fm}"
    try:
        content = src_file.read_text(encoding='utf-8')
        if not content.strip().startswith('---'):
            content = generate_front_matter(num, slug, clean_title, tags, series) + content
        src_file.write_text(content, encoding='utf-8', newline='\n')
        if src_file.name != new_name:
            if dst_file.exists():
                return False, f"#{num:02d}: 目标已存在"
            src_file.rename(dst_file)
        return True, f"#{num:02d}: {src_file.name} -> {new_name} ✓"
    except Exception as e:
        return False, f"#{num:02d}: 错误 - {e}"

def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    mode = "DRY RUN 模式 - 仅预览" if dry_run else "正在执行批量处理..."
    print("=" * 60); print(mode); print("=" * 60)
    if not CONTENT_DIR.exists():
        print(f"错误: 目录不存在 {CONTENT_DIR}"); sys.exit(1)
    ok_count = fail_count = 0
    errors = []
    for num in range(1, len(FILE_MAP) + 1):
        ok, msg = process_file(num, dry_run=dry_run)
        if ok:
            ok_count += 1
            if dry_run: print(msg); print()
            else: print(msg)
        else:
            fail_count += 1; errors.append(msg)
    print("=" * 60); print(f"完成: 成功 {ok_count}, 失败 {fail_count}")
    if errors: print("\n失败:"); [print(f"  {e}") for e in errors]

if __name__ == '__main__':
    main()
```

---

## 菜单条目模板

在 `menus.zh-cn.toml` 中添加：

```toml
[[main]]
  name = "显示名称"
  parent = "小册"
  pageRef = "目录名"
  weight = {weight}
```

---

## \_index.md 模板

```markdown
---
title: "小册完整标题"
description: "一句话描述小册内容。"
---
```

---

## 特殊情况处理

### 文章在子目录中（如 Vue3 第 1 篇）

文件名含 `/` 时操作系统会创建子目录，需特殊处理：

```python
def find_file_for_num(num):
    if num == 1:
        for d in CONTENT_DIR.iterdir():
            if d.is_dir() and d.name.startswith("1."):
                for f in d.iterdir():
                    if f.suffix == '.md':
                        return f
    # 正常逻辑...
```

处理后清理空目录：

```python
if num == 1 and src_file.parent != CONTENT_DIR:
    try:
        src_file.parent.rmdir()
    except OSError:
        pass
```

### SSH 格式 Git 链接导致 Hugo 报错

Hugo 无法解析 `git@github.com:user/repo.git` 格式的链接，需替换为 HTTPS：

```
git@github.com:user/repo.git
→ https://github.com/user/repo
```

### 含水印的文件

如果文件名或内容含 `cunlove` 或 `耗时整理‖免费分享` 水印，需在脚本中加入清理逻辑（参考 `process_nestjs.py`）。

---

## 图片处理

文章中的外链图片（主要是掘金 CDN：`p*-juejin.byteimg.com`）可使用 `scripts/download_images.py` 批量迁移到腾讯云 COS：

```powershell
python scripts/download_images.py {section}
```

需先设置环境变量 `COS_SECRET_ID` 和 `COS_SECRET_KEY`，并安装 `cos-python-sdk-v5`。
