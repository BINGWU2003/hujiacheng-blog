#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/前端工程体验优化实战/ 下的 20 篇文章文件：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
3. 将目录重命名为 frontend-experience（如仍为中文名）
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent
CN_DIR   = BASE_DIR / "content" / "前端工程体验优化实战"
EN_DIR   = BASE_DIR / "content" / "frontend-experience"
START_DATE = date(2025, 5, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "数据驱动优化":  [1, 2, 3],
    "资源加载优化":  [4, 5, 6],
    "代码优化":      [7, 8, 9, 10],
    "渲染与SSR":     [11, 12],
    "图片与懒加载":  [13, 14, 15, 16],
    "工程化与流程":  [17, 18, 19, 20],
}

# 反转为 序号 -> series 名称
NUM_TO_SERIES: dict[int, str] = {}
for _series_name, _nums in SERIES_MAP.items():
    for _n in _nums:
        NUM_TO_SERIES[_n] = _series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "performance":  "performance-api",
    "cdn":          "cdn",
    "懒加载":       "lazy-load",
    "lazy":         "lazy-load",
    "代码分割":     "code-splitting",
    "code split":   "code-splitting",
    "ssr":          "ssr",
    "服务端渲染":   "ssr",
    "fcp":          "ssr",
    "图片":         "image",
    "gif":          "image",
    "css":          "css",
    "构建":         "build-tools",
    "打包":         "build-tools",
    "自动化":       "automation",
    "webpack":      "webpack",
    "vite":         "vite",
    "资源优先级":   "resource-hints",
}

# ========== 20 条文件名映射 ==========
FILE_MAP = {
    1:  ("data-driven-optimization",  "你做的前端优化都错了：数据驱动、指标先行"),
    2:  ("user-experience-data",      "前端优化数据量化必备神器：用户体验数据收集与可视化"),
    3:  ("performance-api",           "光速入门 Performance API"),
    4:  ("resource-priority-hints",   "2行代码让JS加载耗时减少67%：资源优先级提示"),
    5:  ("cdn-traffic-saving",        "CDN最佳实践：让CDN流量节省10%"),
    6:  ("cdn-verification",          "CDN最佳实践：验证、量化与评估"),
    7:  ("module-lazy-loading",       "超简单的代码模块懒加载：让JS加载体积减少13%"),
    8:  ("lazy-loading-issues",       "超简单的代码模块懒加载：懒加载常见问题解决方案"),
    9:  ("granular-code-split",       "代码分割最佳实践：细粒度代码分割"),
    10: ("code-split-example",        "代码分割最佳实践：应用改造示例"),
    11: ("ssr-fcp-optimization",      "前端渲染进化史：用SSR让首次内容绘制耗时（FCP）降低72%"),
    12: ("ssr-advanced",              "前端渲染进化史：SSR进阶优化"),
    13: ("adaptive-image-format",     "图片加载体积减少20%：自适应选择最优图片格式"),
    14: ("gif-optimization",          "GIF体积减少80%：GIF图片优化"),
    15: ("resource-lazy-loading",     "万物皆可懒加载：3类通用资源懒加载实现方案"),
    16: ("lazy-loading-library",      "万物皆可懒加载：通用资源懒加载工具库"),
    17: ("modern-build-tools",        "打包耗时减少43%：现代构建工具的魔力"),
    18: ("css-solutions",             "CSS开发体验优化：6种方案解决CSS痛点"),
    19: ("frontend-automation",       "用自动化提高工作效率：3类前端开发自动化场景"),
    20: ("workflow-improvement",      "让好制度优化开发体验：3项长效化制度和流程"),
}


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
    tags = ["前端工程体验优化"]
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
    return EN_DIR


def find_file_for_num(num: int, content_dir: Path) -> Path | None:
    """根据序号在目录中查找对应的原始文件（匹配 第XX章 格式）"""
    for f in content_dir.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        m = re.search(r'第(\d+)章', f.name)
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
categories: ["前端工程体验优化"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''


def process_file(num: int, content_dir: Path, dry_run: bool = True) -> tuple:
    """处理单个文件，返回 (成功, 消息)"""
    if num not in FILE_MAP:
        return (False, f"#{num}: 映射表中未找到")
    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, "数据驱动优化")
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
    """将中文目录重命名为 frontend-experience（如还未重命名）"""
    if EN_DIR.exists():
        return (True, f"目录已存在: {EN_DIR}")
    if CN_DIR.exists():
        CN_DIR.rename(EN_DIR)
        return (True, f"目录重命名: {CN_DIR.name} -> frontend-experience ✓")
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
