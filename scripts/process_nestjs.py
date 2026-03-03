#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理 content/nestjs/ 下的 200 个 NestJS 文章文件：
1. 清理文件名中的广告水印
2. 为每个文件添加 Hugo front matter
3. 重命名为英文短横线格式
"""

import re
import sys
from pathlib import Path
from datetime import date, timedelta

# ========== 配置 ==========
CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "nestjs"
START_DATE = date(2025, 1, 1)
WATERMARK_REGEX = re.compile(r'【耗时整理[‖|]免费分享\s*cunlove\.cn】')

# ========== 200 条文件名映射 ==========
# 格式: 序号 -> (英文slug, 清洗后的中文标题, series名称, tags列表)

SERIES_MAP = {
    "NestJS 基础": list(range(1, 27)),
    "图书管理系统": list(range(27, 34)),
    "日志与部署": list(range(34, 45)),
    "MySQL 与 TypeORM": list(range(45, 62)),
    "认证与权限": list(range(62, 76)),
    "Docker 进阶": list(range(76, 79)),
    "Nginx": list(range(79, 81)),
    "实战技巧": list(range(81, 109)),
    "会议室预订系统": list(range(109, 140)),
    "微服务": list(range(140, 146)),
    "Prisma": list(range(146, 152)),
    "Redis 高级应用": list(range(152, 155)),
    "考试系统": list(range(155, 172)),
    "WebSocket 与聊天室": list(range(172, 195)),
    "MongoDB 与 GraphQL": list(range(195, 201)),
}

# 反转为 序号 -> series名称
NUM_TO_SERIES = {}
for series_name, nums in SERIES_MAP.items():
    for n in nums:
        NUM_TO_SERIES[n] = series_name

# 根据标题关键词自动打标签
TAG_KEYWORDS = {
    "typeorm": "typeorm",
    "mysql": "mysql",
    "docker": "docker",
    "redis": "redis",
    "prisma": "prisma",
    "websocket": "websocket",
    "socket.io": "websocket",
    "graphql": "graphql",
    "nginx": "nginx",
    "mongodb": "mongodb",
    "mongoose": "mongoose",
    "jwt": "jwt",
    "session": "session",
    "passport": "passport",
    "rbac": "rbac",
    "acl": "acl",
    "swagger": "swagger",
    "winston": "winston",
    "pm2": "pm2",
    "multer": "multer",
    "etcd": "etcd",
    "nacos": "nacos",
    "grpc": "grpc",
    "rabbitmq": "rabbitmq",
    "minio": "minio",
    "puppeteer": "puppeteer",
    "rxjs": "rxjs",
    "middleware": "middleware",
    "interceptor": "interceptor",
    "pipe": "pipe",
    "guard": "guard",
    "decorator": "decorator",
    "microservice": "microservice",
    "微服务": "microservice",
    "monorepo": "monorepo",
    "migration": "migration",
    "oss": "oss",
    "excel": "excel",
    "sharp": "sharp",
    "repl": "repl",
    "sse": "sse",
    "国际化": "i18n",
    "定时任务": "cron",
    "邮件": "email",
    "docker compose": "docker-compose",
}

FILE_MAP = {
    1: ("introduction", "开篇词"),
    2: ("five-reasons-to-learn-nest", "给你 5 个学习 Nest 的理由"),
    3: ("nest-basics", "Nest 基础概念扫盲"),
    4: ("nest-cli", "快速掌握 Nest CLI"),
    5: ("http-data-transfer", "5 种 HTTP 数据传输方式"),
    6: ("ioc-pain-points", "IoC 解决了什么痛点问题？"),
    7: ("debug-nest-project", "如何调试 Nest 项目"),
    8: ("multiple-providers", "使用多种 Provider，灵活注入对象"),
    9: ("global-module-lifecycle", "全局模块和生命周期"),
    10: ("aop-architecture", "AOP 架构有什么好处？"),
    11: ("all-nest-decorators", "一网打尽 Nest 全部装饰器"),
    12: ("custom-decorators", "Nest 如何自定义装饰器"),
    13: ("metadata-and-reflector", "Metadata 和 Reflector"),
    14: ("execution-context", "ExecutionContext：切换不同上下文"),
    15: ("circular-dependency", "Module 和 Provider 的循环依赖怎么处理？"),
    16: ("dynamic-module", "如何创建动态模块"),
    17: ("nest-express-fastify", "Nest 和 Express 的关系，如何切到 fastify"),
    18: ("nest-middleware", "Nest 的 Middleware"),
    19: ("rxjs-and-interceptor", "RxJS 和 Interceptor"),
    20: ("built-in-and-custom-pipe", "内置 Pipe 和自定义 Pipe"),
    21: ("validation-pipe", "如何使用 ValidationPipe 验证 post 请求参数"),
    22: ("custom-exception-filter", "如何自定义 Exception Filter"),
    23: ("nest-core-concepts", "图解串一串 Nest 核心概念"),
    24: ("api-versioning", "接口如何实现多版本共存"),
    25: ("express-multer-upload", "Express 如何使用 multer 实现文件上传"),
    26: ("nest-multer-upload", "Nest 如何使用 multer 实现文件上传"),
    27: ("book-system-requirements", "图书管理系统：需求分析和原型图"),
    28: ("book-system-user-backend", "图书管理系统：用户模块后端开发"),
    29: ("book-system-book-backend", "图书管理系统：图书模块后端开发"),
    30: ("book-system-user-frontend", "图书管理系统：用户模块前端开发"),
    31: ("book-system-book-search", "图书管理系统：图书模块前端开发--图书搜索"),
    32: ("book-system-book-crud", "图书管理系统：图书模块前端开发--图书增删改"),
    33: ("book-system-summary", "图书管理系统：项目总结"),
    34: ("large-file-upload", "大文件分片上传"),
    35: ("oss-upload", "最完美的 OSS 上传方案"),
    36: ("nest-logging", "Nest 里如何打印日志？"),
    37: ("why-winston", "为什么 Node 里要用 Winston 打印日志？"),
    38: ("nest-winston-integration", "Nest 集成日志框架 Winston"),
    39: ("docker-desktop-learning", "通过 Desktop 学 Docker 也太简单了"),
    40: ("first-dockerfile", "你的第一个 Dockerfile"),
    41: ("nest-dockerfile", "Nest 项目如何编写 Dockerfile"),
    42: ("dockerfile-tips", "提升 Dockerfile 水平的 5 个技巧"),
    43: ("how-docker-works", "Docker 是怎么实现的？"),
    44: ("why-pm2", "为什么 Node 应用要用 PM2 来跑？"),
    45: ("mysql-quickstart", "快速入门 MySQL"),
    46: ("sql-syntax-and-functions", "SQL 查询语句的所有语法和函数"),
    47: ("one-to-one-join-cascade", "一对一、join 查询、级联方式"),
    48: ("one-to-many-many-to-many", "一对多、多对多关系的表设计"),
    49: ("subquery-and-exists", "子查询和 EXISTS"),
    50: ("sql-practice", "SQL 综合练习"),
    51: ("mysql-transaction-isolation", "MySQL 的事务和隔离级别"),
    52: ("mysql-view-procedure-function", "MySQL 的视图、存储过程和函数"),
    53: ("node-mysql-two-ways", "使用 Node 操作 MySQL 的两种方式"),
    54: ("typeorm-quickstart", "快速掌握 TypeORM"),
    55: ("typeorm-one-to-one", "TypeORM 一对一的映射和关联 CRUD"),
    56: ("typeorm-one-to-many", "TypeORM 一对多的映射和关联 CRUD"),
    57: ("typeorm-many-to-many", "TypeORM 多对多的映射和关联 CRUD"),
    58: ("nest-typeorm-integration", "在 Nest 里集成 TypeORM"),
    59: ("typeorm-nested-relations", "TypeORM 如何保存任意层级的关系？"),
    60: ("typeorm-migration-why", "为什么生产环境要用 TypeORM 的 migration 迁移功能？"),
    61: ("nest-typeorm-migration", "Nest 项目里如何使用 TypeORM 迁移"),
    62: ("dynamic-config", "如何动态读取不同环境的配置？"),
    63: ("redis-quickstart", "快速入门 Redis"),
    64: ("nest-redis", "在 Nest 里操作 Redis"),
    65: ("why-not-cache-manager", "为什么不用 cache-manager 操作 Redis？"),
    66: ("jwt-vs-session", "两种登录状态保存方式：JWT、Session"),
    67: ("nest-session-jwt", "Nest 里实现 Session 和 JWT"),
    68: ("mysql-typeorm-jwt-login", "MySQL + TypeORM + JWT 实现登录注册"),
    69: ("acl-permission", "基于 ACL 实现权限控制"),
    70: ("rbac-permission", "基于 RBAC 实现权限控制"),
    71: ("access-refresh-token", "基于 access_token 和 refresh_token 实现登录状态无感刷新"),
    72: ("single-token-refresh", "单 token 无限续期，实现登录状态无感刷新"),
    73: ("passport-auth", "使用 passport 做身份认证"),
    74: ("passport-github-login", "passport 实现 GitHub 三方账号登录"),
    75: ("passport-google-login", "passport 实现 Google 三方账号登录"),
    76: ("why-docker-compose", "为什么要使用 Docker Compose？"),
    77: ("docker-bridge-network", "Docker 容器通信的最简单方式：桥接网络"),
    78: ("docker-restart-vs-pm2", "Docker 支持重启策略，是否还需要 PM2"),
    79: ("nginx-core-usage", "快速掌握 Nginx 的 2 大核心用法"),
    80: ("nginx-gray-release", "基于 Nginx 实现灰度系统"),
    81: ("redis-distributed-session", "基于 Redis 实现分布式 session"),
    82: ("redis-nearby-service", "Redis + 高德地图，实现附近的充电宝"),
    83: ("swagger-api-docs", "用 Swagger 自动生成 api 文档"),
    84: ("flexible-dto", "如何灵活创建 DTO"),
    85: ("class-validator-decorators", "class-validator 的内置装饰器，如何自定义装饰器"),
    86: ("serialization-entity", "序列化 Entity，你不需要 VO 对象"),
    87: ("custom-serialization-interceptor", "手写序列化 Entity 的拦截器"),
    88: ("compodoc", "使用 compodoc 生成文档"),
    89: ("node-send-email", "Node 如何发邮件？"),
    90: ("email-code-login", "实现基于邮箱验证码的登录"),
    91: ("cron-redis-view-count", "定时任务 + Redis 实现阅读量计数"),
    92: ("nest-cron-jobs", "Nest 的 3 种定时任务"),
    93: ("nest-event-communication", "Nest 里如何实现事件通信？"),
    94: ("weather-query-service", "HttpModule + pinyin 实现天气预报查询服务"),
    95: ("request-logging", "如何记录请求日志"),
    96: ("short-url-service", "短链服务？自己写一个"),
    97: ("server-sent-event", "Nest 实现 Server Sent Event 数据推送"),
    98: ("minio-oss", "用 minio 自己搭一个 OSS 服务"),
    99: ("direct-upload-minio", "前端如何直传文件到 Minio"),
    100: ("sharp-gif-compress", "基于 sharp 实现 gif 压缩工具"),
    101: ("stream-download", "大文件如何实现流式下载？"),
    102: ("puppeteer-crawler", "Puppeteer 实现爬虫，爬取 BOSS 直聘全部前端岗位"),
    103: ("qr-code-login", "实现扫二维码登录"),
    104: ("nest-repl-mode", "Nest 的 REPL 模式"),
    105: ("excel-import-export", "实现 Excel 导入导出"),
    106: ("generate-ppt", "如何用代码动态生成 PPT"),
    107: ("server-cpu-memory-disk", "如何拿到服务器 CPU、内存、磁盘状态"),
    108: ("nest-i18n", "Nest 如何实现国际化？"),
    109: ("meeting-room-requirements", "会议室预订系统：需求分析和原型图"),
    110: ("meeting-room-tech-design", "会议室预订系统：技术方案和数据库设计"),
    111: ("meeting-room-user-register", "会议室预订系统：用户管理模块--用户注册"),
    112: ("meeting-room-auth", "会议室预订系统：用户管理模块--配置抽离、登录认证鉴权"),
    113: ("meeting-room-user-interceptor", "会议室预订系统：用户管理模块--interceptor、修改信息接口"),
    114: ("meeting-room-user-list", "会议室预订系统：用户管理模块--用户列表和分页查询"),
    115: ("meeting-room-swagger", "会议室预订系统：用户管理模块--swagger 接口文档"),
    116: ("meeting-room-user-login-page", "会议室预订系统：用户管理模块--用户端登录注册页面"),
    117: ("meeting-room-user-info-page", "会议室预订系统：用户管理模块--用户端信息修改页面"),
    118: ("meeting-room-avatar-upload", "会议室预订系统：用户管理模块--头像上传"),
    119: ("meeting-room-admin-user-list", "会议室预订系统：用户管理模块--管理端用户列表页面"),
    120: ("meeting-room-admin-info-page", "会议室预订系统：用户管理模块--管理端信息修改页面"),
    121: ("meeting-room-room-backend", "会议室预订系统：会议室管理模块-后端开发"),
    122: ("meeting-room-room-admin-frontend", "会议室预订系统：会议室管理模块-管理端前端开发"),
    123: ("meeting-room-room-user-frontend", "会议室预订系统：会议室管理模块-用户端前端开发"),
    124: ("meeting-room-booking-backend", "会议室预订系统：预定管理模块-后端开发"),
    125: ("meeting-room-booking-admin-frontend", "会议室预订系统：预定管理模块-管理端前端开发"),
    126: ("meeting-room-booking-user-frontend", "会议室预订系统：预定管理模块-用户端前端开发"),
    127: ("meeting-room-stats-backend", "会议室预订系统：统计管理模块-后端开发"),
    128: ("meeting-room-stats-frontend", "会议室预订系统：统计管理模块-前端开发"),
    129: ("meeting-room-deploy-backend", "会议室预订系统：后端项目部署到阿里云"),
    130: ("meeting-room-deploy-frontend", "会议室预订系统：前端项目部署到阿里云"),
    131: ("meeting-room-migration", "会议室预订系统：用 migration 初始化表和数据"),
    132: ("meeting-room-oss-upload", "会议室预订系统：文件上传 OSS"),
    133: ("meeting-room-google-login-backend", "会议室预订系统：Google 账号登录后端开发"),
    134: ("meeting-room-google-login-frontend", "会议室预订系统：Google 账号登录前端开发"),
    135: ("meeting-room-backend-optimize", "会议室预订系统：后端代码优化"),
    136: ("meeting-room-winston", "会议室预订系统：集成日志框架 winston"),
    137: ("meeting-room-frontend-optimize", "会议室预订系统：前端代码优化"),
    138: ("meeting-room-full-test", "会议室预订系统：全部功能测试"),
    139: ("meeting-room-summary", "会议室预订系统：项目总结"),
    140: ("nest-microservice", "Nest 如何创建微服务？"),
    141: ("nest-monorepo-library", "Nest 的 Monorepo 和 Library"),
    142: ("etcd-config-registry", "用 Etcd 实现微服务配置中心和注册中心"),
    143: ("nest-etcd-integration", "Nest 集成 Etcd 做注册中心、配置中心"),
    144: ("nacos-config-registry", "用 Nacos 实现微服务配置中心和注册中心"),
    145: ("grpc-cross-language", "基于 gRPC 实现跨语言的微服务通信"),
    146: ("prisma-quickstart", "快速入门 ORM 框架 Prisma"),
    147: ("prisma-all-commands", "Prisma 的全部命令"),
    148: ("prisma-schema-syntax", "Prisma 的全部 schema 语法"),
    149: ("prisma-client-single-table", "Prisma Client 单表 CRUD 的全部 api"),
    150: ("prisma-client-multi-table", "Prisma Client 多表 CRUD 的全部 api"),
    151: ("nest-prisma-integration", "在 Nest 里集成 Prisma"),
    152: ("why-rabbitmq", "为什么前端监控系统要用 RabbitMQ？"),
    153: ("redis-follow-system", "基于 Redis 实现关注关系"),
    154: ("redis-leaderboard", "基于 Redis 实现各种排行榜（周榜、月榜、年榜）"),
    155: ("exam-system-requirements", "考试系统：需求分析"),
    156: ("exam-system-tech-design", "考试系统：技术方案和数据库设计"),
    157: ("exam-system-microservice-lib", "考试系统：微服务、Lib 拆分"),
    158: ("exam-system-user-register", "考试系统：用户注册"),
    159: ("exam-system-login-password", "考试系统：用户登录、修改密码"),
    160: ("exam-system-exam-service", "考试系统：考试微服务"),
    161: ("exam-system-login-page", "考试系统：登录、注册页面"),
    162: ("exam-system-paper-list", "考试系统：修改密码、试卷列表页面"),
    163: ("exam-system-paper-recycle", "考试系统：新增试卷、回收站"),
    164: ("exam-system-paper-editor", "考试系统：试卷编辑器"),
    165: ("exam-system-paper-preview", "考试系统：试卷回显、预览、保存"),
    166: ("exam-system-answer-service", "考试系统：答卷微服务"),
    167: ("exam-system-answer-page", "考试系统：答题页面"),
    168: ("exam-system-auto-grading", "考试系统：自动判卷"),
    169: ("exam-system-analysis-ranking", "考试系统：分析微服务、排行榜页面"),
    170: ("exam-system-full-test", "考试系统：整体测试"),
    171: ("exam-system-summary", "考试系统：项目总结"),
    172: ("handwrite-websocket", "用 Node.js 手写 WebSocket 协议"),
    173: ("nest-websocket", "Nest 开发 WebSocket 服务"),
    174: ("socketio-room-chat", "基于 Socket.io 的 room 实现群聊"),
    175: ("chat-room-requirements", "聊天室：需求分析和原型图"),
    176: ("chat-room-tech-design", "聊天室：技术选型和数据库设计"),
    177: ("chat-room-user-register", "聊天室：用户注册"),
    178: ("chat-room-user-login", "聊天室：用户登录"),
    179: ("chat-room-password-info", "聊天室：修改密码、修改信息"),
    180: ("chat-room-friend-list", "聊天室：好友列表、发送好友申请"),
    181: ("chat-room-create-join", "聊天室：创建聊天室、加入群聊"),
    182: ("chat-room-login-register-page", "聊天室：登录、注册页面开发"),
    183: ("chat-room-password-info-page", "聊天室：修改密码、信息页面开发"),
    184: ("chat-room-avatar-upload", "聊天室：头像上传"),
    185: ("chat-room-friend-group-list", "聊天室：好友/群聊列表页面"),
    186: ("chat-room-friend-notification", "聊天室：添加好友弹窗、通知页面"),
    187: ("chat-room-chat-backend", "聊天室：聊天功能后端开发"),
    188: ("chat-room-chat-frontend", "聊天室：聊天功能前端开发"),
    189: ("chat-room-one-to-one", "聊天室：一对一聊天"),
    190: ("chat-room-group-chat", "聊天室：创建群聊、进入群聊"),
    191: ("chat-room-emoji-file", "聊天室：发送表情、图片、文件"),
    192: ("chat-room-favorites", "聊天室：收藏"),
    193: ("chat-room-full-test", "聊天室：全部功能测试"),
    194: ("chat-room-summary", "聊天室：项目总结"),
    195: ("mongodb-quickstart", "MongoDB 快速入门"),
    196: ("mongoose-mongodb", "使用 mongoose 操作 MongoDB 数据库"),
    197: ("graphql-quickstart", "GraphQL 快速入门"),
    198: ("nest-graphql-crud", "Nest 开发 GraphQL 服务：实现 CRUD"),
    199: ("graphql-prisma-react-todolist", "GraphQL + Prisma + React 实现 TodoList"),
    200: ("debug-nest-source", "如何调试 Nest 源码？"),
}


def get_tags(num: int, title: str) -> list:
    """根据标题关键词自动生成 tags"""
    tags = ["nestjs"]
    title_lower = title.lower()
    for keyword, tag in TAG_KEYWORDS.items():
        if keyword.lower() in title_lower and tag not in tags:
            tags.append(tag)
    return tags


def find_file_for_num(num: int) -> Path | None:
    """根据序号在目录中查找对应的原始文件"""
    pattern = f"{num}.*"
    # 需要精确匹配序号开头（避免 1 匹配 10, 100 等）
    for f in CONTENT_DIR.iterdir():
        if not f.is_file() or f.suffix != '.md' or f.name == '_index.md':
            continue
        # 匹配 "序号. " 或 "序号.  " 格式
        m = re.match(r'^(\d+)\.\s+', f.name)
        if m and int(m.group(1)) == num:
            return f
    return None


def generate_front_matter(num: int, slug: str, title: str, tags: list, series: str) -> str:
    """生成 YAML front matter 字符串，手动拼接避免中文转义"""
    d = START_DATE + timedelta(days=num - 1)
    date_str = d.strftime('%Y-%m-%d')

    # 计算 series_order: 在该 series 中的顺序
    series_nums = SERIES_MAP.get(series, [])
    if num in series_nums:
        series_order = series_nums.index(num) + 1
    else:
        series_order = num

    # 转义标题中的双引号
    safe_title = title.replace('"', '\\"')
    safe_series = series.replace('"', '\\"')

    tags_str = ', '.join(f'"{t}"' for t in tags)

    front_matter = f'''---
title: "{safe_title}"
date: {date_str}
draft: false
description: ""
tags: [{tags_str}]
categories: ["NestJS"]
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
    series = NUM_TO_SERIES.get(num, "NestJS 基础")
    tags = get_tags(num, clean_title)

    # 查找原始文件
    src_file = find_file_for_num(num)
    if src_file is None:
        return (False, f"#{num}: 源文件未找到")

    new_name = f"{num:03d}-{slug}.md"
    dst_file = CONTENT_DIR / new_name

    if dry_run:
        has_fm = False
        try:
            content = src_file.read_text(encoding='utf-8')
            has_fm = content.strip().startswith('---')
        except Exception:
            pass
        msg = f"#{num:03d}: {src_file.name}\n"
        msg += f"  -> {new_name}\n"
        msg += f"  title: \"{clean_title}\"\n"
        msg += f"  series: \"{series}\" (order: {SERIES_MAP.get(series, []).index(num) + 1 if num in SERIES_MAP.get(series, []) else '?'})\n"
        msg += f"  tags: {tags}\n"
        msg += f"  has_frontmatter: {has_fm}"
        return (True, msg)

    # 实际执行
    try:
        # 1. 读取原始内容
        content = src_file.read_text(encoding='utf-8')

        # 2. 检查是否已有 front matter，避免重复添加
        if content.strip().startswith('---'):
            print(f"  #{num:03d}: 已有 front matter，跳过添加")
        else:
            # 3. 生成并添加 front matter
            fm = generate_front_matter(num, slug, clean_title, tags, series)
            content = fm + content

        # 4. 写回文件（先写入原文件，确保内容安全）
        src_file.write_text(content, encoding='utf-8', newline='\n')

        # 5. 重命名
        if src_file.name != new_name:
            if dst_file.exists() and dst_file != src_file:
                return (False, f"#{num:03d}: 目标文件 {new_name} 已存在，跳过重命名")
            src_file.rename(dst_file)

        return (True, f"#{num:03d}: {src_file.name} -> {new_name} ✓")

    except Exception as e:
        return (False, f"#{num:03d}: 错误 - {e}")


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

    # 检查目录
    if not CONTENT_DIR.exists():
        print(f"错误: 目录不存在 {CONTENT_DIR}")
        sys.exit(1)

    success_count = 0
    fail_count = 0
    errors = []

    for num in range(1, 201):
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

    # 水印检查
    if not dry_run:
        print("\n正在检查残留水印...")
        watermark_found = False
        for f in CONTENT_DIR.iterdir():
            if f.suffix == '.md' and f.name != '_index.md':
                if WATERMARK_REGEX.search(f.name):
                    print(f"  文件名水印残留: {f.name}")
                    watermark_found = True
                try:
                    text = f.read_text(encoding='utf-8')
                    if 'cunlove' in text or '耗时整理' in text:
                        print(f"  正文水印残留: {f.name}")
                        watermark_found = True
                except Exception:
                    pass
        if not watermark_found:
            print("  无残留水印 ✓")


if __name__ == '__main__':
    main()
