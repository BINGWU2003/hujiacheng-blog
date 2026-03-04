#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/typescript/ 下的 33 篇 TypeScript 全面进阶指南文章：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "typescript"
START_DATE = date(2025, 3, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "TS 基础类型": list(range(1, 7)),         # 1-6
    "TS 类型编程": list(range(7, 18)),        # 7-17
    "TS 进阶特性": list(range(18, 21)),       # 18-20
    "TS 工程实践": list(range(21, 29)),       # 21-28
    "TS 项目实战": list(range(29, 34)),       # 29-33
}

NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "泛型": "generics",
    "generic": "generics",
    "enum": "enum",
    "枚举": "enum",
    "class": "class",
    "函数重载": "function-overload",
    "any": "any-unknown-never",
    "unknown": "any-unknown-never",
    "never": "any-unknown-never",
    "类型断言": "type-assertion",
    "条件类型": "conditional-type",
    "infer": "infer",
    "工具类型": "utility-types",
    "协变": "covariance",
    "逆变": "contravariance",
    "模板字符串": "template-literal",
    "装饰器": "decorator",
    "反射": "reflect-metadata",
    "依赖注入": "dependency-injection",
    "控制反转": "ioc",
    "tsconfig": "tsconfig",
    "eslint": "eslint",
    "react": "react",
    "prisma": "prisma",
    "nestjs": "nestjs",
    "ast": "ast",
    "ecmascript": "ecmascript",
    "类型兼容": "type-compatibility",
}

# ========== 33 条文件名映射 ==========
FILE_MAP = {
    1:  ("opening", "用正确的方式学习 TypeScript"),
    2:  ("dev-environment", "打造最舒适的 TypeScript 开发环境"),
    3:  ("primitive-and-object-types", "理解原始类型与对象类型"),
    4:  ("literal-types-and-enums", "掌握字面量类型与枚举"),
    5:  ("function-and-class", "函数与 Class 中的类型：函数重载与面向对象"),
    6:  ("any-unknown-never", "探秘内置类型：any、unknown、never 与类型断言"),
    7:  ("type-tools-part1", "TypeScript 类型工具（上）"),
    8:  ("type-tools-part2", "TypeScript 类型工具（下）"),
    9:  ("generics", "TypeScript 中无处不在的泛型"),
    10: ("structural-type-system", "结构化类型系统：类型兼容性判断的幕后"),
    11: ("type-hierarchy", "类型系统层级：从 Top Type 到 Bottom Type"),
    12: ("conditional-types-and-infer", "类型里的逻辑运算：条件类型与 infer"),
    13: ("builtin-utility-types", "内置工具类型基础"),
    14: ("contextual-types", "反方向类型推导：上下文相关类型"),
    15: ("covariance-and-contravariance", "函数类型：协变与逆变的比较"),
    16: ("type-programming-meaning", "了解类型编程与类型体操的意义"),
    17: ("advanced-utility-types", "内置工具类型进阶：类型编程进阶"),
    18: ("template-literal-types", "模板字符串类型入门"),
    19: ("template-string-tool-types", "模板字符串工具类型进阶"),
    20: ("type-declarations-and-directives", "工程层面的类型能力：类型声明、类型指令与命名空间"),
    21: ("react-with-typescript", "在 React 中愉快地使用 TypeScript"),
    22: ("eslint-for-typescript", "让 ESLint 来约束你的 TypeScript 代码"),
    23: ("typescript-toolchain", "全链路 TypeScript 工具库"),
    24: ("typescript-and-ecmascript", "TypeScript 和 ECMAScript 之间那些事儿"),
    25: ("decorators-and-reflect-metadata", "装饰器与反射元数据"),
    26: ("ioc-and-dependency-injection", "控制反转与依赖注入"),
    27: ("tsconfig-part1", "TSConfig 全解（上）：构建相关配置"),
    28: ("tsconfig-part2", "TSConfig 全解（下）：检查相关、工程相关配置"),
    29: ("prisma-nestjs-prerequisites", "基于 Prisma + NestJs 的 Node API：前置知识储备"),
    30: ("prisma-nestjs-project", "基于 Prisma + NestJs 的 Node API：项目开发与部署"),
    31: ("typescript-ast", "玩转 TypeScript AST"),
    32: ("conclusion", "感谢相伴：是结束，也是开始"),
    33: ("interview-typescript", "漫谈篇：面试中的 TypeScript"),
}


def get_tags(num: int, title: str) -> list:
    tags = ["typescript"]
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
    series = NUM_TO_SERIES.get(num, "TS 基础类型")
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

    for num in range(1, 34):
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
