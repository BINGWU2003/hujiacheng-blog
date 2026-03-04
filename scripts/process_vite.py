#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/vite/ 下的 28 篇 Vite 文章文件：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "vite"
START_DATE = date(2025, 6, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "Vite 基础入门": list(range(1, 8)),      # 1-7
    "Vite 双引擎": list(range(8, 12)),        # 8-11
    "Vite 高级应用": list(range(12, 20)),     # 12-19
    "Vite 源码解析": list(range(20, 24)),     # 20-23
    "Vite 手写实现": list(range(24, 29)),     # 24-28
}

# 反转为 序号 -> series名称
NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "esbuild": "esbuild",
    "rollup": "rollup",
    "hmr": "hmr",
    "热更新": "hmr",
    "ssr": "ssr",
    "预渲染": "ssr",
    "css": "css",
    "sass": "css",
    "scss": "css",
    "postcss": "css",
    "less": "css",
    "tailwind": "css",
    "lint": "lint",
    "eslint": "lint",
    "prettier": "lint",
    "stylelint": "lint",
    "polyfill": "polyfill",
    "语法降级": "polyfill",
    "tree shaking": "tree-shaking",
    "tree-shaking": "tree-shaking",
    "module federation": "module-federation",
    "模块联邦": "module-federation",
    "esm": "esm",
    "模块标准": "esm",
    "代码分割": "code-splitting",
    "拆包": "code-splitting",
    "ast": "ast",
    "词法分析": "ast",
    "语义分析": "ast",
    "bundler": "bundler",
    "打包": "bundler",
    "性能优化": "performance",
    "插件": "plugin",
    "静态资源": "static-assets",
    "预构建": "pre-bundling",
}

# ========== 28 条文件名映射 ==========
# 格式: 序号 -> (英文slug, 清洗后的中文标题)
FILE_MAP = {
    1:  ("opening", "让 Vite 助力你的前端工程化之路"),
    2:  ("esm-module-standard", "为什么 ESM 是前端模块化的未来？"),
    3:  ("quick-start", "如何用 Vite 从零搭建前端项目？"),
    4:  ("css-engineering", "在 Vite 中接入现代化的 CSS 工程化方案"),
    5:  ("lint-toolchain", "如何利用 Lint 工具链来保证代码风格和质量？"),
    6:  ("static-assets", "在 Vite 中处理各种静态资源"),
    7:  ("dependency-pre-bundling", "玩转秒级依赖预构建的能力"),
    8:  ("dual-engine-architecture", "Vite 是如何站在巨人的肩膀上实现的？"),
    9:  ("esbuild-in-practice", "Esbuild 功能使用与插件开发实战"),
    10: ("rollup-basics", "Rollup 打包基本概念及使用"),
    11: ("rollup-plugin-mechanism", "深入理解 Rollup 的插件机制"),
    12: ("vite-plugin-development", "如何开发一个完整的 Vite 插件？"),
    13: ("hmr-api-and-principle", "代码改动后如何进行毫秒级别的局部更新？"),
    14: ("code-splitting", "打包完产物体积太大，怎么拆包？"),
    15: ("syntax-polyfill", "联合前端编译工具链，消灭低版本浏览器兼容问题"),
    16: ("ssr-prerender", "如何借助 Vite 搭建高可用的服务端渲染工程？"),
    17: ("module-federation", "如何实现优雅的跨应用代码共享？"),
    18: ("esm-advanced", "ESM 高阶特性与 Pure ESM 时代"),
    19: ("performance-optimization", "如何体系化地对 Vite 项目进行性能优化？"),
    20: ("config-resolution", "配置文件在 Vite 内部被转换成什么样子了？"),
    21: ("esbuild-pre-bundling", "Esbuild 打包功能如何被 Vite 玩出花来？"),
    22: ("plugin-pipeline", "从整体到局部，理解 Vite 的核心编译能力"),
    23: ("hmr-implementation", "基于 ESM 的毫秒级 HMR 的实现揭秘"),
    24: ("handwrite-vite-part1", "实现 no-bundle 开发服务（上）"),
    25: ("handwrite-vite-part2", "实现 no-bundle 开发服务（下）"),
    26: ("handwrite-bundler-ast", "实现 JavaScript AST 解析器——词法分析、语义分析"),
    27: ("handwrite-bundler-treeshaking", "实现代码打包、Tree Shaking"),
    28: ("vite3-updates", "Vite 3.0 核心更新盘点与分析"),
}


def get_tags(num: int, title: str) -> list:
    """根据标题关键词自动生成 tags"""
    tags = ["vite"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def find_file_for_num(num: int) -> Path | None:
    """根据序号在目录中查找对应的原始文件"""
    for f in CONTENT_DIR.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        # 匹配 "序号." 格式（如 "1." "10." "28."）
        m = re.match(r'^(\d+)\.', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None


def generate_front_matter(num: int, slug: str, title: str, tags: list, series: str) -> str:
    """生成 YAML front matter 字符串"""
    d = START_DATE + timedelta(days=num - 1)
    date_str = d.strftime('%Y-%m-%d')

    # 计算 series_order
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
categories: ["Vite"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''
    return front_matter


def process_file(num: int, dry_run: bool = True) -> tuple:
    """处理单个文件，返回 (成功, 消息)"""
    if num not in FILE_MAP:
        return (False, f"#{num}: 映射表中未找到")

    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, "Vite 基础入门")
    tags = get_tags(num, clean_title)

    # 查找原始文件
    src_file = find_file_for_num(num)
    if src_file is None:
        # 检查是否已经是处理过的文件名
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

    # 实际执行
    try:
        content = src_file.read_text(encoding='utf-8')

        # 检查是否已有 front matter
        if content.strip().startswith('---'):
            print(f"  #{num:02d}: 已有 front matter，跳过添加")
        else:
            fm = generate_front_matter(num, slug, clean_title, tags, series)
            content = fm + content

        # 写回文件
        src_file.write_text(content, encoding='utf-8', newline='\n')

        # 重命名
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

    for num in range(1, 29):
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
