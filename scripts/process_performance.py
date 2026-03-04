#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/前端性能优化原理与实践/ 下的 15 篇文章文件：
1. 清理第 1 篇顶部的广告水印
2. 为每个文件添加 Hugo front matter
3. 重命名为英文短横线格式
4. 将目录重命名为 performance（如仍为中文名）
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent
CN_DIR   = BASE_DIR / "content" / "前端性能优化原理与实践"
EN_DIR   = BASE_DIR / "content" / "performance"
START_DATE = date(2025, 2, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "开篇与结语":     [1, 15],
    "网络与存储优化": list(range(2, 7)),   # 2-6
    "浏览器渲染优化": list(range(7, 12)),  # 7-11
    "应用层优化":     [12, 13],
    "性能监测":       [14],
}

# 反转为 序号 -> series 名称
NUM_TO_SERIES: dict[int, str] = {}
for _series_name, _nums in SERIES_MAP.items():
    for _n in _nums:
        NUM_TO_SERIES[_n] = _series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "webpack":    "webpack",
    "gzip":       "gzip",
    "图片":       "image",
    "缓存":       "cache",
    "cdn":        "cdn",
    "cookie":     "cookie",
    "indexeddb":  "storage",
    "web storage": "storage",
    "ssr":        "ssr",
    "服务端渲染": "ssr",
    "dom":        "dom",
    "event loop": "event-loop",
    "reflow":     "reflow",
    "repaint":    "reflow",
    "回流":       "reflow",
    "重绘":       "reflow",
    "lazy":       "lazy-load",
    "懒加载":     "lazy-load",
    "throttle":   "throttle",
    "debounce":   "debounce",
    "节流":       "throttle",
    "防抖":       "debounce",
    "performance": "performance",
    "lighthouse":  "performance",
    "性能监测":   "performance",
}

# ========== 15 条文件名映射 ==========
# 格式: 序号 -> (英文 slug, 清洗后的中文标题)
FILE_MAP = {
    1:  ("opening",              "开篇：知识体系与小册格局"),
    2:  ("webpack-gzip",         "网络篇 1：webpack 性能调优与 Gzip 原理"),
    3:  ("image-optimization",   "网络篇 2：图片优化——质量与性能的博弈"),
    4:  ("browser-cache",        "存储篇 1：浏览器缓存机制介绍与缓存策略剖析"),
    5:  ("local-storage",        "存储篇 2：本地存储——从 Cookie 到 Web Storage、IndexedDB"),
    6:  ("cdn-cache",            "彩蛋篇：CDN 的缓存与回源机制解析"),
    7:  ("server-side-rendering","渲染篇 1：服务端渲染的探索与实践"),
    8:  ("browser-mechanism",    "渲染篇 2：解锁浏览器背后的运行机制"),
    9:  ("dom-optimization",     "渲染篇 3：DOM 优化原理与基本实践"),
    10: ("event-loop-async",     "渲染篇 4：Event Loop 与异步更新策略"),
    11: ("reflow-repaint",       "渲染篇 5：回流（Reflow）与重绘（Repaint）"),
    12: ("lazy-load",            "应用篇 1：优化首屏体验——Lazy-Load 初探"),
    13: ("throttle-debounce",    "应用篇 2：事件的节流（throttle）与防抖（debounce）"),
    14: ("performance-monitoring","性能监测篇：Performance、LightHouse 与性能 API"),
    15: ("summary",              "前方的路：希望以此为你的起点"),
}

# 水印匹配正则（第 1 篇顶部）
_WATERMARK_PATTERN = re.compile(
    r'^.*?(?:号外|xyalinode|耗时整理|cunlove).*?\n?',
    re.MULTILINE
)


def strip_watermark(content: str) -> str:
    """去除文章顶部广告/水印段落（逐行检查前若干行）"""
    lines = content.split('\n')
    clean_lines = []
    skipping = True
    for line in lines:
        if skipping:
            if re.search(r'号外|xyalinode|耗时整理|cunlove', line):
                continue  # 跳过水印行
            else:
                skipping = False
                clean_lines.append(line)
        else:
            clean_lines.append(line)
    return '\n'.join(clean_lines)


def get_tags(num: int, title: str) -> list:
    """根据标题关键词自动生成 tags"""
    tags = ["性能优化"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def get_content_dir() -> Path:
    """返回当前实际存在的内容目录（中文或英文）"""
    if EN_DIR.exists():
        return EN_DIR
    if CN_DIR.exists():
        return CN_DIR
    return EN_DIR  # 不存在时返回目标目录


def find_file_for_num(num: int, content_dir: Path) -> Path | None:
    """根据序号在目录中查找对应的原始文件"""
    for f in content_dir.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        m = re.match(r'^(\d+)\.', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None


def generate_front_matter(num: int, slug: str, title: str, tags: list, series: str) -> str:
    """生成 YAML front matter 字符串"""
    d = START_DATE + timedelta(days=num - 1)
    date_str = d.strftime('%Y-%m-%d')

    series_nums = SERIES_MAP.get(series, [])
    series_order = series_nums.index(num) + 1 if num in series_nums else num

    safe_title  = title.replace('"', '\\"')
    safe_series = series.replace('"', '\\"')
    tags_str    = ', '.join(f'"{t}"' for t in tags)

    return f'''---
title: "{safe_title}"
date: {date_str}
draft: false
description: ""
tags: [{tags_str}]
categories: ["性能优化"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''


def process_file(num: int, content_dir: Path, dry_run: bool = True) -> tuple:
    """处理单个文件，返回 (成功, 消息)"""
    if num not in FILE_MAP:
        return (False, f"#{num}: 映射表中未找到")

    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, "开篇与结语")
    tags   = get_tags(num, clean_title)

    src_file = find_file_for_num(num, content_dir)
    new_name = f"{num:02d}-{slug}.md"
    dst_file = content_dir / new_name

    if src_file is None:
        if dst_file.exists():
            return (True, f"#{num:02d}: 已处理过 ({new_name})")
        return (False, f"#{num}: 源文件未找到")

    if dry_run:
        try:
            content = src_file.read_text(encoding='utf-8')
            has_fm  = content.strip().startswith('---')
        except Exception:
            has_fm = False
        series_nums   = SERIES_MAP.get(series, [])
        series_order  = series_nums.index(num) + 1 if num in series_nums else '?'
        msg  = f"#{num:02d}: {src_file.name}\n"
        msg += f"  -> {new_name}\n"
        msg += f"  title: \"{clean_title}\"\n"
        msg += f"  series: \"{series}\" (order: {series_order})\n"
        msg += f"  tags: {tags}\n"
        msg += f"  has_frontmatter: {has_fm}"
        return (True, msg)

    # 实际执行
    try:
        content = src_file.read_text(encoding='utf-8')

        # 仅对第 1 篇清理水印
        if num == 1:
            content = strip_watermark(content)

        if content.strip().startswith('---'):
            print(f"  #{num:02d}: 已有 front matter，跳过添加")
        else:
            fm      = generate_front_matter(num, slug, clean_title, tags, series)
            content = fm + content

        src_file.write_text(content, encoding='utf-8', newline='\n')

        if src_file.name != new_name:
            if dst_file.exists() and dst_file != src_file:
                return (False, f"#{num:02d}: 目标文件 {new_name} 已存在，跳过重命名")
            src_file.rename(dst_file)

        return (True, f"#{num:02d}: {src_file.name} -> {new_name} ✓")

    except Exception as e:
        return (False, f"#{num:02d}: 错误 - {e}")


def rename_directory() -> tuple[bool, str]:
    """将中文目录重命名为 performance（如还未重命名）"""
    if EN_DIR.exists():
        return (True, f"目录已存在: {EN_DIR}")
    if CN_DIR.exists():
        CN_DIR.rename(EN_DIR)
        return (True, f"目录重命名: {CN_DIR.name} -> performance ✓")
    return (False, f"源目录不存在: {CN_DIR}")


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    print("=" * 60)
    print("DRY RUN 模式 - 仅预览，不实际修改文件" if dry_run else "正在执行批量处理...")
    print("=" * 60)

    content_dir = get_content_dir()

    if not content_dir.exists():
        print(f"错误: 目录不存在 {content_dir}")
        sys.exit(1)

    # 目录重命名（仅在非 dry-run 时执行）
    if not dry_run:
        ok, msg = rename_directory()
        print(msg)
        if not ok:
            sys.exit(1)
        content_dir = EN_DIR

    success_count = fail_count = 0
    errors = []

    for num in range(1, len(FILE_MAP) + 1):
        ok, msg = process_file(num, content_dir, dry_run=dry_run)
        if ok:
            success_count += 1
            print(msg)
            if dry_run:
                print()
        else:
            fail_count += 1
            errors.append(msg)
            print(msg)

    print("=" * 60)
    print(f"完成: 成功 {success_count}, 失败 {fail_count}")
    if errors:
        print("\n失败的文件:")
        for e in errors:
            print(f"  {e}")


if __name__ == '__main__':
    main()
