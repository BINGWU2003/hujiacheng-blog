#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/vue3/ 下的 22 篇 Vue 3 文章文件：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
3. 处理第 1 篇的特殊子目录结构
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "vue3"
START_DATE = date(2025, 9, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "Vue3 渲染器": list(range(1, 6)),           # 1-5
    "Vue3 响应式原理": list(range(6, 12)),       # 6-11
    "Vue3 编译器": list(range(12, 16)),          # 12-15
    "Vue3 内置组件": list(range(16, 20)),        # 16-19
    "Vue3 特殊元素与指令": list(range(20, 23)),  # 20-22
}

NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "渲染器": "renderer",
    "dom": "dom",
    "diff": "diff",
    "proxy": "proxy",
    "响应式": "reactivity",
    "computed": "computed",
    "watch": "watch",
    "nexttick": "nexttick",
    "副作用": "effect",
    "依赖注入": "provide-inject",
    "编译器": "compiler",
    "ast": "ast",
    "渲染函数": "render-function",
    "transition": "transition",
    "keepalive": "keepalive",
    "teleport": "teleport",
    "suspense": "suspense",
    "双向绑定": "v-model",
    "slot": "slot",
    "插槽": "slot",
}

# ========== 22 条文件名映射 ==========
FILE_MAP = {
    1:  ("opening", "开篇词：Vue 3 与 Vue 2"),
    2:  ("renderer-component-to-dom", "组件是如何被渲染成 DOM 的？"),
    3:  ("renderer-data-proxy", "数据访问是如何被代理的？"),
    4:  ("renderer-component-update", "组件是如何完成更新的？"),
    5:  ("renderer-diff-algorithm", "数组子节点的 diff 算法"),
    6:  ("reactivity-proxy", "基于 Proxy 的响应式是什么样的？"),
    7:  ("reactivity-effect", "副作用函数探秘"),
    8:  ("reactivity-nexttick", "Vue 3 的 nextTick"),
    9:  ("reactivity-watch", "watch 函数的实现原理"),
    10: ("reactivity-computed", "computed 函数和普通函数有什么不同？"),
    11: ("reactivity-provide-inject", "依赖注入实现跨级组件数据共享"),
    12: ("compiler-template-to-ast", "模板是如何被编译成 AST 的？"),
    13: ("compiler-ast-to-jsast", "AST 是如何被转换成 JS AST 的？"),
    14: ("compiler-jsast-to-render", "JS AST 是如何生成渲染函数的？"),
    15: ("compiler-optimization", "编译过程中的优化细节"),
    16: ("builtin-transition", "Transition 是如何实现的？"),
    17: ("builtin-keepalive", "KeepAlive 保活的原理"),
    18: ("builtin-teleport", "Teleport 是如何实现选择性挂载的？"),
    19: ("builtin-suspense", "Suspense 原理与异步"),
    20: ("directive-v-model", "双向绑定是如何实现的？"),
    21: ("directive-slot", "slot 插槽元素是如何实现的？"),
    22: ("conclusion", "再回首，纵观 Vue 3 实现"),
}


def get_tags(num: int, title: str) -> list:
    tags = ["vue3"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def find_file_for_num(num: int) -> Path | None:
    """根据序号查找对应的原始文件"""
    # 特殊处理第 1 篇（在子目录中）
    if num == 1:
        for d in CONTENT_DIR.iterdir():
            if d.is_dir() and d.name.startswith("1."):
                for f in d.iterdir():
                    if f.suffix == '.md':
                        return f
        # 也尝试直接匹配
        for f in CONTENT_DIR.iterdir():
            if f.is_file() and f.suffix == '.md' and f.name != '_index.md':
                m = re.match(r'^1\.', f.name)
                if m:
                    return f
        return None

    for f in CONTENT_DIR.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        m = re.match(r'^(\d+)\.', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None


def generate_front_matter(num: int, slug: str, title: str, tags: list, series: str) -> str:
    d = START_DATE + timedelta(days=num - 1)
    date_str = d.strftime('%Y-%m-%d')

    series_nums = SERIES_MAP.get(series, [])
    if num in series_nums:
        series_order = series_nums.index(num) + 1
    else:
        series_order = num

    safe_title = title.replace('"', '\\"')
    safe_series = series.replace('"', '\\"')
    tags_str = ', '.join(f'"{t}"' for t in tags)

    front_matter = f'''---
title: "{safe_title}"
date: {date_str}
draft: false
description: ""
tags: [{tags_str}]
categories: ["Vue3"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''
    return front_matter


def process_file(num: int, dry_run: bool = True) -> tuple:
    if num not in FILE_MAP:
        return (False, f"#{num}: 映射表中未找到")

    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, "Vue3 渲染器")
    tags = get_tags(num, clean_title)

    src_file = find_file_for_num(num)
    if src_file is None:
        new_name = f"{num:02d}-{slug}.md"
        dst_file = CONTENT_DIR / new_name
        if dst_file.exists():
            return (True, f"#{num:02d}: 已处理过 ({new_name})")
        return (False, f"#{num}: 源文件未找到")

    new_name = f"{num:02d}-{slug}.md"
    dst_file = CONTENT_DIR / new_name

    if dry_run:
        has_fm = False
        try:
            content = src_file.read_text(encoding='utf-8')
            has_fm = content.strip().startswith('---')
        except Exception:
            pass
        rel = src_file.relative_to(CONTENT_DIR)
        msg = f"#{num:02d}: {rel}\n"
        msg += f"  -> {new_name}\n"
        msg += f"  title: \"{clean_title}\"\n"
        msg += f"  series: \"{series}\" (order: {SERIES_MAP.get(series, []).index(num) + 1 if num in SERIES_MAP.get(series, []) else '?'})\n"
        msg += f"  tags: {tags}\n"
        msg += f"  has_frontmatter: {has_fm}"
        return (True, msg)

    try:
        content = src_file.read_text(encoding='utf-8')

        if content.strip().startswith('---'):
            print(f"  #{num:02d}: 已有 front matter，跳过添加")
        else:
            fm = generate_front_matter(num, slug, clean_title, tags, series)
            content = fm + content

        # 写入目标文件
        dst_file.write_text(content, encoding='utf-8', newline='\n')

        # 如果源文件不是目标文件，删除源文件
        if src_file.resolve() != dst_file.resolve():
            src_file.unlink()
            # 如果第 1 篇来自子目录，清理空目录
            if num == 1 and src_file.parent != CONTENT_DIR:
                try:
                    src_file.parent.rmdir()
                except OSError:
                    pass

        return (True, f"#{num:02d}: {src_file.name} -> {new_name} ✓")

    except Exception as e:
        return (False, f"#{num:02d}: 错误 - {e}")


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    if dry_run:
        print("=" * 60)
        print("DRY RUN 模式 - 仅预览，不实际修改文件")
        print("=" * 60)
    else:
        print("=" * 60)
        print("正在执行批量处理...")
        print("=" * 60)

    if not CONTENT_DIR.exists():
        print(f"错误: 目录不存在 {CONTENT_DIR}")
        sys.exit(1)

    success_count = 0
    fail_count = 0
    errors = []

    for num in range(1, 23):
        ok, msg = process_file(num, dry_run=dry_run)
        if ok:
            success_count += 1
            if dry_run:
                print(msg)
                print()
        else:
            fail_count += 1
            errors.append(msg)

        if not dry_run and ok:
            print(msg)

    print("=" * 60)
    print(f"完成: 成功 {success_count}, 失败 {fail_count}")
    if errors:
        print("\n失败的文件:")
        for e in errors:
            print(f"  {e}")


if __name__ == '__main__':
    main()
