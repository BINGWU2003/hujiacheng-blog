#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/vite-component-library/ 下的 22 篇文章：
1. 为每个文件添加 Hugo front matter
2. 重命名为英文短横线格式
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "vite-component-library"
START_DATE = date(2025, 10, 1)

# ========== Series 分组 ==========
SERIES_MAP = {
    "组件库基础搭建": list(range(1, 5)),      # 1-4
    "工程化配置": list(range(5, 10)),          # 5-9
    "发布与生态建设": list(range(10, 15)),     # 10-14
    "社区运营与质量": list(range(15, 20)),     # 15-19
    "进阶与开源扩展": list(range(20, 23)),     # 20-22
}

# 反转为 序号 -> series名称
NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# ========== 标签关键词 ==========
TAG_KEYWORDS = {
    "unocss": "unocss",
    "css": "css",
    "原子化": "unocss",
    "jest": "jest",
    "vitest": "vitest",
    "单元测试": "testing",
    "测试": "testing",
    "覆盖率": "testing",
    "eslint": "eslint",
    "prettier": "prettier",
    "husky": "husky",
    "规范": "lint",
    "esm": "esm",
    "commonjs": "esm",
    "模块": "esm",
    "软件包": "npm",
    "发布": "npm",
    "npm": "npm",
    "semver": "semver",
    "语义化版本": "semver",
    "monorepo": "monorepo",
    "按需引入": "tree-shaking",
    "tree-shaking": "tree-shaking",
    "treeshaking": "tree-shaking",
    "vercel": "vercel",
    "部署": "deployment",
    "readme": "documentation",
    "文档": "documentation",
    "ci": "ci-cd",
    "github action": "ci-cd",
    "持续集成": "ci-cd",
    "pullrequest": "open-source",
    "pull request": "open-source",
    "社区": "open-source",
    "许可证": "open-source",
    "license": "open-source",
    "cli": "cli",
    "开源": "open-source",
    "typescript": "typescript",
    "类型": "typescript",
}

# ========== 22 条文件名映射 ==========
# 格式: 序号 -> (英文slug, 清洗后的中文标题)
FILE_MAP = {
    1:  ("opening", "开篇词：学习前端工程化就从搭建组件库开始"),
    2:  ("mvp-component-library", "MVP 原型系统：将组件封装为组件库"),
    3:  ("unocss-atomic-css", "CSS 样式：用 UnoCSS 实现原子化 CSS"),
    4:  ("docs-with-demo", "文档建设：创建具备 Demo 示例功能的文档网站"),
    5:  ("unit-test-jest", "单元测试（一）：使用 Jest 进行前端单元测试"),
    6:  ("unit-test-vitest", "单元测试（二）：搭建 Vitest 的单元测试环境"),
    7:  ("lint-and-format", "规范化：Eslint + Prettier + Husky"),
    8:  ("package-module-compat", "软件包封装：如何发布兼容多种 JS 模块标准的软件包？"),
    9:  ("ci-github-actions", "持续集成 CI：基于 GitHub Action 的回归验证"),
    10: ("open-source-license", "开发许可证：维护自己的版权、拒绝拿来党"),
    11: ("semver-npm-publish", "组件发布：建立语义化版本与提交软件包仓库 Npm"),
    12: ("monorepo-ecosystem", "建立组件库生态：利用 Monorepo 方式管理组件库生态"),
    13: ("tree-shaking-on-demand", "按需引入：实现组件库的按需引入功能"),
    14: ("deploy-docs-vercel", "文档部署：用 Vercel 部署你的线上文档"),
    15: ("write-readme", "README：编写标准的 README"),
    16: ("coverage-report", "品质保证：覆盖率测试报告"),
    17: ("manage-pull-requests", "社区参与：如何管理社区的 PullRequest？"),
    18: ("github-project-management", "敏捷开发：用 Github 看板和 issue 管理需求"),
    19: ("cli-tool-devx", "架构复用：创建 CLI 工具提高研发体验"),
    20: ("npm-init-template", "融入开源生态：编写 npm init 项目让用户更方便"),
    21: ("typescript-types-export", "加餐：类型系统——导出组件库的类型定义"),
    22: ("conclusion", "结语：当好项目的开路先锋"),
}


def get_tags(num: int, title: str) -> list:
    """根据标题关键词自动生成 tags"""
    tags = ["Vite", "组件库"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def find_file_for_num(num: int):
    """根据序号在目录中查找对应的原始文件"""
    for f in CONTENT_DIR.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        m = re.match(r'^(\d+)[\.\s_]', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None


def generate_front_matter(num: int, slug: str, title: str, tags: list, series: str) -> str:
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
categories: ["Vite"]
series: ["{safe_series}"]
series_order: {series_order}
---

'''


def process_file(num: int, dry_run: bool = True):
    if num not in FILE_MAP:
        return False, f"#{num}: 未找到映射"
    slug, clean_title = FILE_MAP[num]
    series = NUM_TO_SERIES.get(num, list(SERIES_MAP.keys())[0])
    tags = get_tags(num, clean_title)
    src_file = find_file_for_num(num)
    new_name = f"{num:02d}-{slug}.md"
    dst_file = CONTENT_DIR / new_name

    if src_file is None:
        if dst_file.exists():
            return True, f"#{num:02d}: 已处理过 -> {new_name}"
        return False, f"#{num:02d}: 未找到源文件"

    if dry_run:
        content = src_file.read_text(encoding='utf-8')
        has_fm = content.strip().startswith('---')
        series_list = SERIES_MAP.get(series, [])
        order = series_list.index(num) + 1 if num in series_list else '?'
        return True, (
            f"#{num:02d}: {src_file.name}\n"
            f"  -> {new_name}\n"
            f"  title:  \"{clean_title}\"\n"
            f"  series: \"{series}\" (order {order})\n"
            f"  tags:   {tags}\n"
            f"  has_frontmatter: {has_fm}"
        )

    try:
        content = src_file.read_text(encoding='utf-8')
        if not content.strip().startswith('---'):
            content = generate_front_matter(num, slug, clean_title, tags, series) + content
        src_file.write_text(content, encoding='utf-8', newline='\n')
        if src_file.name != new_name:
            if dst_file.exists():
                return False, f"#{num:02d}: 目标文件已存在 {new_name}"
            src_file.rename(dst_file)
        return True, f"#{num:02d}: {src_file.name} -> {new_name} ✓"
    except Exception as e:
        return False, f"#{num:02d}: 错误 - {e}"


def main():
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    mode = "DRY RUN 模式 - 仅预览，不修改文件" if dry_run else "正在执行批量处理..."
    print("=" * 65)
    print(mode)
    print("=" * 65)

    if not CONTENT_DIR.exists():
        print(f"错误: 目录不存在 {CONTENT_DIR}")
        sys.exit(1)

    ok_count = fail_count = 0
    errors = []

    for num in range(1, len(FILE_MAP) + 1):
        ok, msg = process_file(num, dry_run=dry_run)
        if ok:
            ok_count += 1
            print(msg)
            if dry_run:
                print()
        else:
            fail_count += 1
            errors.append(msg)
            print(f"[FAIL] {msg}")

    print("=" * 65)
    print(f"完成: 成功 {ok_count}, 失败 {fail_count}")
    if errors:
        print("\n失败详情:")
        for e in errors:
            print(f"  {e}")


if __name__ == '__main__':
    main()
