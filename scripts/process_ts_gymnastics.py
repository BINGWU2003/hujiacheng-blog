#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/ts-type-gymnastics/ 下的 29 篇 TypeScript 类型体操文章：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "ts-type-gymnastics"
START_DATE = date(2025, 4, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "类型体操入门": list(range(1, 5)),          # 1-4
    "类型体操六大套路": list(range(5, 12)),      # 5-11
    "类型编程实战": list(range(12, 17)),         # 12-16
    "类型体操原理": list(range(17, 23)),         # 17-22
    "类型体操加餐": list(range(23, 30)),         # 23-29
}

NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "模式匹配": "pattern-matching",
    "递归": "recursion",
    "联合": "union-type",
    "infer": "infer",
    "协变": "covariance",
    "逆变": "contravariance",
    "babel": "babel",
    "tsc": "tsc",
    "satisfies": "satisfies",
    "jsdoc": "jsdoc",
    "project reference": "project-reference",
    "高级类型": "advanced-types",
    "面试": "interview",
}

# ========== 29 条文件名映射 ==========
FILE_MAP = {
    1:  ("how-to-read", "如何阅读本小册"),
    2:  ("why-typescript-is-popular", "为什么说 TypeScript 的火爆是必然？"),
    3:  ("why-called-type-gymnastics", "TypeScript 类型编程为什么被叫做类型体操？"),
    4:  ("type-system-and-operations", "TypeScript 类型系统支持哪些类型和类型运算？"),
    5:  ("pattern-matching", "套路一：模式匹配做提取"),
    6:  ("reconstruct", "套路二：重新构造做变换"),
    7:  ("recursion", "套路三：递归复用做循环"),
    8:  ("array-length-counting", "套路四：数组长度做计数"),
    9:  ("union-distribution", "套路五：联合分散可简化"),
    10: ("special-features", "套路六：特殊特性要记清"),
    11: ("type-gymnastics-rhyme", "类型体操顺口溜"),
    12: ("builtin-advanced-types", "TypeScript 内置的高级类型有哪些？"),
    13: ("real-world-cases", "真实案例说明类型编程的意义"),
    14: ("practice-one", "类型编程综合实战一"),
    15: ("practice-two", "类型编程综合实战二"),
    16: ("infer-extends", "新语法 infer extends 是如何简化类型编程的"),
    17: ("variance", "原理篇：逆变、协变、双向协变、不变"),
    18: ("tsc-vs-babel", "原理篇：编译 ts 代码用 tsc 还是 babel？"),
    19: ("simple-type-checker", "原理篇：实现简易 TypeScript 类型检查"),
    20: ("read-typescript-source", "原理篇：如何阅读 TypeScript 源码"),
    21: ("special-cases", "原理篇：一些特殊情况的说明"),
    22: ("conclusion", "小册总结"),
    23: ("type-sources-and-modules", "加餐：3 种类型来源和 3 种模块语法"),
    24: ("project-reference", "加餐：用 Project Reference 优化 tsc 编译性能"),
    25: ("three-layer-interview", "加餐：一道 3 层的 ts 面试题"),
    26: ("real-type-programming-cases", "加餐：项目中 2 个真实的类型编程案例"),
    27: ("satisfies-keyword", "加餐：TypeScript 新语法 satisfies"),
    28: ("jsdoc-vs-typescript", "加餐：JSDoc 真能取代 TypeScript？"),
    29: ("bytedance-interview", "加餐：一道字节面试真题"),
}


def get_tags(num: int, title: str) -> list:
    tags = ["typescript", "type-gymnastics"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def find_file_for_num(num: int) -> Path | None:
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
categories: ["TypeScript"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''
    return front_matter


def process_file(num: int, dry_run: bool = True) -> tuple:
    if num not in FILE_MAP:
        return (False, f"#{num}: 映射表中未找到")

    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, "类型体操入门")
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
        msg = f"#{num:02d}: {src_file.name}\n"
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

        src_file.write_text(content, encoding='utf-8', newline='\n')

        if src_file.name != new_name:
            if dst_file.exists() and dst_file != src_file:
                return (False, f"#{num:02d}: 目标文件 {new_name} 已存在，跳过重命名")
            src_file.rename(dst_file)

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

    for num in range(1, 30):
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
