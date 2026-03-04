#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载 nestjs 文章中的外链图片，并上传到腾讯云 COS，替换 md 文件中的图片链接。

使用方式:
  $env:COS_SECRET_ID  = "你的SecretId"
  $env:COS_SECRET_KEY = "你的SecretKey"
  python scripts/download_images.py
"""

import os
import re
import sys
import hashlib
import urllib.request
import tempfile
from pathlib import Path

# =============================================
# 配置（通过环境变量传入密钥）
# =============================================

COS_SECRET_ID  = ""
COS_SECRET_KEY = ""
COS_REGION     = "ap-nanjing"
COS_BUCKET     = "bing-wu-doc-1318477772"
COS_BASE_URL   = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com"
# =============================================

# 通过命令行参数指定处理哪个目录，默认 nestjs
# 用法: python scripts/download_images.py [nestjs|vite]
SECTION = sys.argv[1] if len(sys.argv) > 1 else "nestjs"
COS_PREFIX = f"{SECTION}/"
CONTENT_DIR = Path(f"content/{SECTION}")
TEMP_DIR = Path(tempfile.gettempdir()) / f"{SECTION}_images"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\((https?://[^)\s]+)\)')

# 缓存：原始 URL → COS URL，同一图片只上传一次
url_cache: dict[str, str] = {}


def get_ext(url: str, content_type: str = "") -> str:
    if "png" in content_type:  return "png"
    if "gif" in content_type:  return "gif"
    if "webp" in content_type: return "webp"
    if "svg" in content_type:  return "svg"
    clean = url.split("?")[0].split("~")[0]
    suffix = clean.rsplit(".", 1)[-1].lower()
    return suffix if suffix in ("jpg", "jpeg", "png", "gif", "webp", "svg") else "jpg"


def download_to_temp(url: str) -> Path | None:
    ext = get_ext(url)
    name = hashlib.md5(url.encode()).hexdigest()[:12] + f".{ext}"
    local_path = TEMP_DIR / name

    if local_path.exists():
        return local_path

    try:
        print(f"    ⬇ 下载: {url[:90]}...")
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://juejin.cn/",
        })
        with urllib.request.urlopen(req, timeout=20) as resp:
            content_type = resp.headers.get("Content-Type", "")
            ext = get_ext(url, content_type)
            name = hashlib.md5(url.encode()).hexdigest()[:12] + f".{ext}"
            local_path = TEMP_DIR / name
            local_path.write_bytes(resp.read())
        return local_path
    except Exception as e:
        print(f"    ❌ 下载失败: {e}")
        return None


def upload_to_cos(local_path: Path) -> str | None:
    from qcloud_cos import CosConfig, CosS3Client
    cos_config = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    cos_client = CosS3Client(cos_config)

    cos_key = f"{COS_PREFIX}{local_path.name}"
    try:
        print(f"    ☁ 上传: {cos_key}...")
        cos_client.upload_file(
            Bucket=COS_BUCKET,
            LocalFilePath=str(local_path),
            Key=cos_key,
            EnableMD5=False,
        )
        oss_url = f"{COS_BASE_URL}/{cos_key}"
        print(f"    ✅ {oss_url}")
        return oss_url
    except Exception as e:
        print(f"    ❌ 上传失败: {e}")
        return None


def process_url(url: str) -> str | None:
    if url in url_cache:
        print(f"    ⏭ 缓存: {url_cache[url]}")
        return url_cache[url]

    local_path = download_to_temp(url)
    if not local_path:
        return None

    oss_url = upload_to_cos(local_path)
    if oss_url:
        url_cache[url] = oss_url
    return oss_url


def is_own_image(url: str) -> bool:
    """已经是自己 COS 的图片，跳过"""
    return COS_BUCKET in url


def process_file(md_file: Path):
    content = md_file.read_text(encoding="utf-8")
    matches = IMG_PATTERN.findall(content)
    if not matches:
        return

    external = [(alt, url) for alt, url in matches if not is_own_image(url)]
    if not external:
        return

    print(f"\n📄 {md_file.name}  ({len(external)}/{len(matches)} 张需处理)")
    new_content = content
    changed = False

    for alt, url in external:
        oss_url = process_url(url)
        if oss_url:
            new_content = new_content.replace(f"![{alt}]({url})", f"![{alt}]({oss_url})")
            changed = True

    if changed:
        md_file.write_text(new_content, encoding="utf-8")
        print(f"  ✅ 文件已更新")


def main():
    # 检查密钥
    if not COS_SECRET_ID or not COS_SECRET_KEY:
        print("❌ 未检测到 COS 密钥，请先在终端执行：")
        print('   $env:COS_SECRET_ID  = "你的SecretId"')
        print('   $env:COS_SECRET_KEY = "你的SecretKey"')
        return

    # 检查依赖
    try:
        import qcloud_cos
    except ImportError:
        print("❌ 缺少 COS SDK，请先执行：pip install cos-python-sdk-v5")
        return

    md_files = sorted(CONTENT_DIR.glob("*.md"))
    print(f"共找到 {len(md_files)} 个 md 文件，开始处理...\n")

    for f in md_files:
        process_file(f)

    print(f"\n🎉 全部完成，共处理 {len(url_cache)} 张唯一图片")
    print(f"   临时文件: {TEMP_DIR}")
    print(f"   清理命令: Remove-Item -Recurse \"{TEMP_DIR}\"")


if __name__ == "__main__":
    main()
