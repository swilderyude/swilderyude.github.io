#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("MOYU_SOURCE", ROOT.parent / "moyu")).expanduser().resolve()
DIST = ROOT
ARTICLES_DIR = DIST / "articles"
ASSETS_DIR = DIST / "assets"
MEDIA_DIR = ASSETS_DIR / "media"

SITE = {
    "title": "【SwilderYude 的研究生笔记】",
    "subtitle": "道阻且长，与君共勉",
    "author": "swilderyude",
    "github": "https://github.com/swilderyude",
    "repo": "https://github.com/swilderyude/swilderyuede.github.io",
    "base_url": "https://swilderyude.github.io",
}


@dataclass(frozen=True)
class ArticleConfig:
    source: str
    title: str
    category: str
    summary: str
    pinned: bool = False
    tags: tuple[str, ...] = ()
    date: str | None = None
    include_images: bool = True


ARTICLES: list[ArticleConfig] = [
    ArticleConfig(
        "CS自学/人脸色斑检测/人脸色斑检测项目.md",
        "人脸色斑检测项目：从数据处理到 SDK 封装",
        "项目实践",
        "围绕人脸色斑检测任务，整理数据匿名化、数据集结构、YOLO 训练、结果融合与 SDK 对接的完整工程记录。",
        pinned=True,
        tags=("YOLO", "小目标检测", "医学图像", "工程化"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/YOLO相关/YOLO理论.md",
        "YOLO 理论笔记：从 YOLOv1 到 YOLOv8",
        "计算机视觉",
        "梳理目标检测基本任务、YOLO 的网格预测、Anchor、NMS、损失函数和多尺度训练等核心概念。",
        pinned=True,
        tags=("YOLO", "目标检测", "计算机视觉"),
    ),
    ArticleConfig(
        "CS自学/科研/科研(大队长）.md",
        "科研入门路线：论文、代码与组合创新",
        "科研方法",
        "从选题、读论文、精读代码、实验设置到论文结构，整理一套面向研究生早期阶段的科研工作流。",
        pinned=True,
        tags=("科研", "论文写作", "读代码"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/调研/人脸皮肤色斑检测算法综合报告.md",
        "人脸皮肤色斑检测算法综合报告",
        "文献精读",
        "对色斑检测与分割领域的两阶段检测、YOLO 小目标、多模态融合、临床诊断逻辑和轻量化部署进行综述。",
        tags=("综述", "色斑检测", "多模态", "轻量化"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/YOLO相关/超市识别项目.md",
        "超市识别项目：视频预处理、标注与 YOLO 训练",
        "项目实践",
        "记录自助收银/人工柜台场景下的视频处理、数据标注、YOLO 训练、目标追踪和状态机理解过程。",
        tags=("项目", "YOLO", "目标追踪", "状态机"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/sdk运行.md",
        "斑点检测 SDK 封装记录",
        "项目实践",
        "将已有 Python 推理流程封装为 C ABI SDK 的设计笔记，包含头文件、runner、Demo 和交付检查思路。",
        tags=("SDK", "C++", "Python", "工程交付"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/数据集/数据集.md",
        "人脸色斑检测数据集整理笔记",
        "项目实践",
        "整理数据集结构、标注格式、训练/验证划分和数据管理中的注意事项。",
        tags=("数据集", "标注", "YOLO"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/标注/标注规范.md",
        "人脸色斑检测标注规范",
        "项目实践",
        "记录色斑、痘痣等类别的标注边界、质量控制和一致性要求。",
        tags=("标注", "规范", "数据质量"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/标注/X-AnyLabeling.md",
        "X-AnyLabeling 标注工具使用记录",
        "工具与环境",
        "记录自动标注工具的安装、模型配置和常见问题处理。",
        tags=("X-AnyLabeling", "标注工具"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/优化/优化计划.md",
        "人脸色斑检测优化计划",
        "项目实践",
        "围绕小目标检测、分割模型、切图推理、损失函数和多任务管线整理后续优化方向。",
        tags=("优化", "小目标", "分割"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/修改.md",
        "检测与分割双模型协同方案",
        "项目实践",
        "把斑点分割和痘痣检测拆成两个模型，并通过统一切图、结果回拼和可视化叠加实现协同。",
        tags=("检测", "分割", "Pipeline"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/结果分析/实验记录.md",
        "人脸色斑检测实验记录",
        "项目实践",
        "记录训练、验证、指标观察和实验复盘，为后续调参与模型改进提供依据。",
        tags=("实验", "结果分析"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人脸色斑检测/结果分析/训练结果.md",
        "人脸色斑检测训练结果",
        "项目实践",
        "汇总模型训练过程中的主要结果、指标变化和阶段性判断。",
        tags=("训练", "指标"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/精读论文/circulant attention/Circulant Attention.md",
        "Circulant Attention 精读笔记",
        "文献精读",
        "围绕 Vision Transformer 中的 Circulant Attention 机制，整理论文结构、核心方法和实现理解。",
        tags=("Transformer", "Attention", "论文精读"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/精读论文/MobileNet/MobileNet.md",
        "MobileNet 精读笔记",
        "文献精读",
        "整理轻量化网络 MobileNet 系列的核心结构、深度可分离卷积和移动端部署思想。",
        tags=("MobileNet", "轻量化网络"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/精读论文/知识蒸馏/知识蒸馏.md",
        "知识蒸馏精读笔记",
        "文献精读",
        "整理教师网络、学生网络、软标签、温度系数和蒸馏损失等知识蒸馏基础概念。",
        tags=("知识蒸馏", "模型压缩"),
    ),
    ArticleConfig(
        "CS自学/人工智能/PyTorch.md",
        "PyTorch 入门笔记：Dataset 与 Dataloader",
        "AI 基础",
        "记录 PyTorch 环境配置、自定义 Dataset、Dataloader 和图像数据读取的基础实践。",
        tags=("PyTorch", "Dataset", "深度学习"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人工智能/python/python学习.md",
        "Python 学习笔记",
        "AI 基础",
        "整理 Python 语法、常用库、文件处理和编程基础，作为后续深度学习实践的底座。",
        tags=("Python", "编程基础"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人工智能/统计学习方法.md",
        "统计学习方法笔记",
        "AI 基础",
        "整理统计学习中的基本概念、模型、损失函数、优化和泛化问题。",
        tags=("机器学习", "统计学习"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/人工智能/动手学深度学习.md",
        "动手学深度学习笔记",
        "AI 基础",
        "记录深度学习基础、模型训练和实验实践中的关键知识点。",
        tags=("深度学习", "动手实践"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/计算机视觉/计算机视觉.md",
        "计算机视觉基础笔记",
        "计算机视觉",
        "整理图像处理、分类、检测、分割等计算机视觉基础概念。",
        tags=("计算机视觉", "图像处理"),
    ),
    ArticleConfig(
        "CS自学/计算机视觉/open CV.md",
        "OpenCV 学习笔记",
        "计算机视觉",
        "记录 OpenCV 的图像读取、处理、显示和常见视觉任务实践。",
        tags=("OpenCV", "图像处理"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/AI基础/远程服务器.md",
        "远程服务器使用笔记",
        "工具与环境",
        "整理 SSH、远程训练、环境管理和服务器使用流程。",
        tags=("服务器", "SSH", "环境配置"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/工具/Git.md",
        "Git 使用笔记",
        "工具与环境",
        "整理 Git 常用命令、分支、提交和协作流程。",
        tags=("Git", "版本控制"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/工具/Linux命令.md",
        "Linux 命令笔记",
        "工具与环境",
        "整理研究和开发中常用的 Linux 命令与终端工作流。",
        tags=("Linux", "命令行"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/工具/LaTeX/LaTeX.md",
        "LaTeX 写作笔记",
        "工具与环境",
        "整理 LaTeX 环境、公式、排版和论文写作常用技巧。",
        tags=("LaTeX", "论文写作"),
        include_images=False,
    ),
    ArticleConfig(
        "CS自学/Loom.md",
        "Obsidian DataLoom 使用笔记",
        "工具与环境",
        "整理 DataLoom 表格、字段类型、过滤排序、Source 自动生成行和导出功能。",
        tags=("Obsidian", "DataLoom", "知识管理"),
        include_images=False,
    ),
]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[\s/\\:：|]+", "-", text.strip().lower())
    text = re.sub(r"[^\w\-\u4e00-\u9fff]+", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or hashlib.sha1(text.encode()).hexdigest()[:10]


def page_slug(article: ArticleConfig) -> str:
    stem = Path(article.source).stem
    return slugify(stem if stem.lower() not in {"readme", "未命名"} else article.title)


def html_escape(text: str) -> str:
    return html.escape(text, quote=True)


def rel_url(from_file: Path, to_file: Path) -> str:
    return os.path.relpath(to_file, start=from_file.parent).replace(os.sep, "/")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def mtime_date(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")


def find_image(article_path: Path, name: str) -> Path | None:
    candidate_names = [name]
    if "|" in name:
        candidate_names.insert(0, name.split("|", 1)[0].strip())
    clean = candidate_names[0].strip()
    direct = (article_path.parent / clean).resolve()
    if direct.exists() and direct.is_file():
        return direct
    for parent in [article_path.parent, *article_path.parents]:
        pic_dir = parent / "图片"
        if pic_dir.exists():
            candidate = pic_dir / clean
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()
    matches = list(SOURCE.glob(f"**/{clean}"))
    matches = [p for p in matches if p.is_file() and not p.name.startswith("._")]
    return matches[0].resolve() if matches else None


def image_is_safe(article: ArticleConfig, image_path: Path) -> bool:
    if not article.include_images:
        return False
    normalized = str(image_path)
    if "人脸色斑检测" in normalized or "医院" in normalized:
        return False
    return image_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def copy_image(src: Path) -> str:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:10]
    suffix = src.suffix.lower()
    out_suffix = ".webp" if suffix in {".png", ".jpg", ".jpeg"} else suffix
    out_name = f"{slugify(src.stem)[:60]}-{digest}{out_suffix}"
    out = MEDIA_DIR / out_name
    if out.exists():
        return f"assets/media/{out_name}"

    if suffix in {".png", ".jpg", ".jpeg"}:
        try:
            from PIL import Image

            img = Image.open(src)
            img.thumbnail((1600, 1600))
            if img.mode not in {"RGB", "RGBA"}:
                img = img.convert("RGB")
            img.save(out, "WEBP", quality=72, method=6)
        except Exception:
            fallback_name = f"{slugify(src.stem)[:60]}-{digest}{suffix}"
            fallback = MEDIA_DIR / fallback_name
            shutil.copy2(src, fallback)
            return f"assets/media/{fallback_name}"
    else:
        shutil.copy2(src, out)
    return f"assets/media/{out_name}"


def convert_obsidian_links(markdown: str, article: ArticleConfig, article_path: Path) -> str:
    def replace_image(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        image_path = find_image(article_path, target)
        label = target.split("|", 1)[0].strip()
        if image_path and image_is_safe(article, image_path):
            copied = copy_image(image_path)
            return f"![{label}](../{copied})"
        return f"> 图片未发布：{label}"

    markdown = re.sub(r"!\[\[([^\]]+)\]\]", replace_image, markdown)

    def replace_wiki(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        label = target.split("|")[-1].strip()
        return f"`{label}`"

    markdown = re.sub(r"(?<!!)\[\[([^\]]+)\]\]", replace_wiki, markdown)
    return markdown


def normalize_markdown(markdown: str, article: ArticleConfig, article_path: Path) -> str:
    markdown = markdown.replace("\r\n", "\n").replace("\r", "\n")
    markdown = redact_sensitive_text(markdown)
    markdown = re.sub(r"^---\n.*?\n---\n", "", markdown, flags=re.S)
    markdown = re.sub(r"^#\s+.*\n+", "", markdown, count=1)
    markdown = convert_obsidian_links(markdown, article, article_path)
    # Obsidian highlights are not standard Markdown; keep the emphasis visually.
    markdown = re.sub(r"==([^=\n][\s\S]*?)==", r"**\1**", markdown)
    markdown = normalize_markdown_blocks(markdown)
    return markdown.strip() + "\n"


def redact_sensitive_text(text: str) -> str:
    replacements = [
        (r"/Users/[^/\s]+", "~"),
        (r"/Volumes/[^/\s]+/[^/\s]+", "~"),
        (r"\bsk-[A-Za-z0-9_\-]{12,}\b", "sk-REDACTED"),
        (r"\brt_[A-Za-z0-9._\-]{12,}\b", "rt_REDACTED"),
        (r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b", "JWT_REDACTED"),
        (r"(?i)(bduss=)[A-Za-z0-9_\-]+", r"\1[REDACTED]"),
        (r"(?i)(stoken=)[A-Za-z0-9_\-]+", r"\1[REDACTED]"),
        (r"(?i)(ANTHROPIC_AUTH_TOKEN\s*=\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(ANTHROPIC_API_KEY\s*=\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(OPENAI_API_KEY\"\s*:\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(api_key\s*=\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(V_API_KEY\s*=\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(id_token\"\s*:\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(access_token\"\s*:\s*)\"[^\"]+\"", r'\1"REDACTED"'),
        (r"(?i)(refresh_token\"\s*:\s*)\"[^\"]+\"", r'\1"REDACTED"'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text


def normalize_markdown_blocks(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if out and out[-1].strip() and not in_fence:
                out.append("")
            out.append(line)
            in_fence = not in_fence
            continue
        if not in_fence:
            is_heading = bool(re.match(r"#{1,6}\s+", stripped))
            is_list = bool(re.match(r"([-*+]\s+|\d+[.)]\s+)", stripped))
            is_table = stripped.startswith("|")
            is_block = stripped.startswith("> ")
            if (is_heading or is_list or is_table or is_block) and out and out[-1].strip():
                out.append("")
            out.append(line)
            if is_heading:
                out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def run_pandoc(markdown: str) -> str:
    process = subprocess.run(
        [
            "pandoc",
            "-f",
            "markdown+pipe_tables+fenced_code_attributes+tex_math_dollars",
            "-t",
            "html5",
            "--no-highlight",
        ],
        input=markdown,
        text=True,
        capture_output=True,
        check=True,
    )
    return process.stdout


def add_heading_ids(html_text: str) -> tuple[str, list[tuple[int, str, str]]]:
    used: Counter[str] = Counter()
    toc: list[tuple[int, str, str]] = []

    def repl(match: re.Match[str]) -> str:
        level = int(match.group(1))
        attrs = match.group(2) or ""
        body = match.group(3)
        plain = re.sub(r"<[^>]+>", "", body)
        plain = html.unescape(plain).strip()
        existing = re.search(r'\sid="([^"]+)"', attrs)
        anchor = existing.group(1) if existing else slugify(plain)
        used[anchor] += 1
        if used[anchor] > 1:
            anchor = f"{anchor}-{used[anchor]}"
        if not existing:
            attrs = f'{attrs} id="{anchor}"'
        if level <= 3:
            toc.append((level, plain, anchor))
        return f"<h{level}{attrs}>{body}</h{level}>"

    return re.sub(r"<h([1-6])([^>]*)>(.*?)</h\1>", repl, html_text), toc


def clean_html(html_text: str) -> str:
    html_text = html_text.replace("<table>", '<div class="table-wrap"><table>')
    html_text = html_text.replace("</table>", "</table></div>")
    html_text = re.sub(r"<blockquote>\s*<p>图片未发布：([^<]+)</p>\s*</blockquote>", r'<div class="image-placeholder">图片未发布：\1</div>', html_text)

    def clean_link(match: re.Match[str]) -> str:
        href, label = match.group(1), match.group(2)
        if href.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        return f"<code>{label}</code>"

    html_text = re.sub(r'<a href="([^"]+)">([^<]+)</a>', clean_link, html_text)
    return html_text


def excerpt(markdown: str, fallback: str, length: int = 160) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", markdown)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", lambda m: m.group(0).split("](")[0][1:], text)
    text = re.sub(r"[\[#>*_`|=-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return (text[: length - 1] + "…") if len(text) > length else (text or fallback)


def article_html(article: ArticleConfig) -> dict:
    src = SOURCE / article.source
    if not src.exists():
        raise FileNotFoundError(src)
    markdown = normalize_markdown(read_text(src), article, src)
    body = run_pandoc(markdown)
    body, toc = add_heading_ids(clean_html(body))
    date = article.date or mtime_date(src)
    slug = page_slug(article)
    return {
        "slug": slug,
        "source": article.source,
        "title": article.title,
        "category": article.category,
        "summary": article.summary,
        "excerpt": excerpt(markdown, article.summary),
        "date": date,
        "tags": list(article.tags),
        "pinned": article.pinned,
        "body": body,
        "toc": toc,
        "url": f"articles/{slug}.html",
    }


def layout(title: str, active: str, main: str, sidebar: str, description: str = "") -> str:
    desc = html_escape(description or SITE["subtitle"])
    nav = [
        ("首页", "index.html", "home"),
        ("分类", "categories.html", "categories"),
        ("归档", "archive.html", "archive"),
        ("关于", "about.html", "about"),
        ("GitHub", SITE["github"], "github"),
    ]
    nav_html = "\n".join(
        f'<li><a class="menu{" active" if key == active else ""}" href="{href}">{label}</a></li>'
        for label, href, key in nav
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{desc}">
  <title>{html_escape(title)} - {html_escape(SITE["author"])}</title>
  <link rel="stylesheet" href="assets/css/style.css">
  <script defer src="assets/js/site.js"></script>
</head>
<body>
  <a id="top"></a>
  <div id="home">
    <header id="header">
      <div id="blogTitle">
        <a id="lnkBlogLogo" href="index.html" aria-label="返回主页"><span id="blogLogo">S</span></a>
        <h1><a id="Header1_HeaderTitle" class="headermaintitle" href="index.html">{html_escape(SITE["title"])}</a></h1>
        <h2>{html_escape(SITE["subtitle"])}</h2>
      </div>
      <nav id="navigator" aria-label="主导航">
        <ul id="navList">
          {nav_html}
        </ul>
        <div class="blogStats">随笔 {len(ARTICLES)} · 分类 6 · 更新 {datetime.now().strftime("%Y-%m-%d")}</div>
      </nav>
    </header>
    <div id="main">
      <main id="mainContent">
        <div class="forFlow">
          {main}
        </div>
      </main>
      <aside id="sideBar">
        <div id="sideBarMain">
          {sidebar}
        </div>
      </aside>
    </div>
    <footer id="footer">
      <span>Powered by GitHub Pages</span>
      <a href="#top">返回顶部</a>
    </footer>
  </div>
</body>
</html>
"""


def sidebar_html(articles: list[dict], current_category: str | None = None, prefix: str = "") -> str:
    categories = Counter(a["category"] for a in articles)
    category_items = "\n".join(
        f'<li><a class="{"current" if cat == current_category else ""}" href="{prefix}categories.html#{slugify(cat)}">{html_escape(cat)} ({count})</a></li>'
        for cat, count in sorted(categories.items())
    )
    latest = "\n".join(
        f'<li><a href="{prefix}{a["url"]}">{html_escape(a["title"])}</a></li>'
        for a in sorted(articles, key=lambda x: x["date"], reverse=True)[:8]
    )
    recommended = "\n".join(
        f'<li><a href="{prefix}{a["url"]}">{html_escape(a["title"])}</a></li>'
        for a in articles
        if a["pinned"]
    )
    tags = Counter(tag for a in articles for tag in a["tags"])
    tag_cloud = "\n".join(
        f'<a href="{prefix}archive.html?tag={html_escape(tag)}">{html_escape(tag)}</a>'
        for tag, _ in tags.most_common(18)
    )
    return f"""
<section class="catList">
  <h3 class="catListTitle">公告</h3>
  <p>这里整理研究生阶段的课程实践、科研方法、论文精读、计算机视觉和工程工具笔记。</p>
  <p><a href="{SITE["github"]}">GitHub: {SITE["author"]}</a></p>
</section>
<section class="catList">
  <h3 class="catListTitle">随笔分类</h3>
  <ul>{category_items}</ul>
</section>
<section class="catList">
  <h3 class="catListTitle">推荐阅读</h3>
  <ul>{recommended}</ul>
</section>
<section class="catList">
  <h3 class="catListTitle">最新随笔</h3>
  <ul>{latest}</ul>
</section>
<section class="catList">
  <h3 class="catListTitle">标签云</h3>
  <div class="tagCloud">{tag_cloud}</div>
</section>
"""


def post_card(article: dict) -> str:
    pinned = '<span class="pinned-post-mark">[置顶]</span> ' if article["pinned"] else ""
    tags = "".join(f'<span>{html_escape(tag)}</span>' for tag in article["tags"][:4])
    return f"""
<article class="day {'pinned' if article['pinned'] else ''}">
  <div class="dayTitle"><a href="archive.html#{article['date']}">{article['date']}</a></div>
  <h2 class="postTitle"><a class="postTitle2" href="{article['url']}">{pinned}{html_escape(article['title'])}</a></h2>
  <div class="postCon">
    <div class="c_b_p_desc">摘要：{html_escape(article['summary'])} <a class="c_b_p_desc_readmore" href="{article['url']}">阅读全文</a></div>
  </div>
  <div class="postDesc">posted @ {article['date']} {html_escape(SITE['author'])} 分类: <a href="categories.html#{slugify(article['category'])}">{html_escape(article['category'])}</a></div>
  <div class="postTags">{tags}</div>
</article>
"""


def build_index(articles: list[dict]) -> None:
    ordered = sorted(articles, key=lambda a: (not a["pinned"], a["date"]), reverse=False)
    pinned = [a for a in articles if a["pinned"]]
    rest = [a for a in sorted(articles, key=lambda x: x["date"], reverse=True) if not a["pinned"]]
    main = """
<section class="introBox">
  <h2>研究生阶段笔记目录</h2>
  <p>按博客园式文章流整理：置顶放主线，下面按时间发布项目、论文、AI 基础和工具笔记。</p>
</section>
""" + "\n".join(post_card(a) for a in [*pinned, *rest])
    (DIST / "index.html").write_text(layout("首页", "home", main, sidebar_html(articles), "研究生阶段学习和科研笔记"), encoding="utf-8")


def article_page(article: dict, articles: list[dict]) -> str:
    toc = ""
    if article["toc"]:
        items = "\n".join(
            f'<li class="toc-level-{level}"><a href="#{anchor}">{html_escape(text)}</a></li>'
            for level, text, anchor in article["toc"]
        )
        toc = f'<div class="toc"><div class="toc-container-header">目录</div><ul>{items}</ul></div>'
    recs = "\n".join(
        f'<div><a href="../{a["url"]}">{html_escape(a["title"])}</a></div>'
        for a in articles
        if a["slug"] != article["slug"] and (a["pinned"] or a["category"] == article["category"])
    )
    tags = " ".join(f'<span>{html_escape(tag)}</span>' for tag in article["tags"])
    return f"""
<article class="post">
  <h1 class="postTitle single"><span>{html_escape(article["title"])}</span></h1>
  <div class="postDesc">posted @ {article["date"]} {html_escape(SITE["author"])} 分类: <a href="../categories.html#{slugify(article["category"])}">{html_escape(article["category"])}</a></div>
  <p class="postSummary">{html_escape(article["summary"])}</p>
  <div class="postTags">{tags}</div>
  {toc}
  <div id="cnblogs_post_body" class="blogpost-body cnblogs-markdown">
    {article["body"]}
  </div>
  <section class="recommend">
    <h2>推荐阅读</h2>
    {recs}
  </section>
</article>
"""


def build_articles(articles: list[dict]) -> None:
    ARTICLES_DIR.mkdir(exist_ok=True)
    article_sidebar = sidebar_html(articles, prefix="../")
    for article in articles:
        body = article_page(article, articles)
        page = layout(article["title"], "", body, article_sidebar, article["summary"])
        page = page.replace('href="assets/css/style.css"', 'href="../assets/css/style.css"')
        page = page.replace('src="assets/js/site.js"', 'src="../assets/js/site.js"')
        page = page.replace('href="index.html"', 'href="../index.html"')
        page = page.replace('href="categories.html"', 'href="../categories.html"')
        page = page.replace('href="archive.html"', 'href="../archive.html"')
        page = page.replace('href="about.html"', 'href="../about.html"')
        page = page.replace('href="categories.html#', 'href="../categories.html#')
        page = page.replace('href="archive.html#', 'href="../archive.html#')
        page = page.replace('href="archive.html?', 'href="../archive.html?')
        page = page.replace(f'href="{SITE["github"]}"', f'href="{SITE["github"]}"')
        (ARTICLES_DIR / f"{article['slug']}.html").write_text(page, encoding="utf-8")


def build_categories(articles: list[dict]) -> None:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for a in articles:
        grouped[a["category"]].append(a)
    sections = []
    for cat, items in sorted(grouped.items()):
        cards = "\n".join(post_card(a) for a in sorted(items, key=lambda x: x["date"], reverse=True))
        sections.append(f'<section id="{slugify(cat)}" class="category-section"><h2>{html_escape(cat)}</h2>{cards}</section>')
    main = "\n".join(sections)
    (DIST / "categories.html").write_text(layout("分类", "categories", main, sidebar_html(articles), "文章分类"), encoding="utf-8")


def build_archive(articles: list[dict]) -> None:
    rows = "\n".join(
        f'<li id="{a["date"]}"><time>{a["date"]}</time><a href="{a["url"]}">{html_escape(a["title"])}</a><span>{html_escape(a["category"])}</span></li>'
        for a in sorted(articles, key=lambda x: x["date"], reverse=True)
    )
    tags = Counter(tag for a in articles for tag in a["tags"])
    tag_list = "\n".join(f'<button class="tag-filter" data-tag="{html_escape(tag)}">{html_escape(tag)} <span>{count}</span></button>' for tag, count in tags.most_common())
    data = html_escape(json.dumps([{k: a[k] for k in ("title", "url", "date", "category", "tags")} for a in articles], ensure_ascii=False))
    main = f"""
<section class="archive">
  <h2>归档</h2>
  <div class="archive-tags">{tag_list}</div>
  <ul class="archive-list" data-articles="{data}">{rows}</ul>
</section>
"""
    (DIST / "archive.html").write_text(layout("归档", "archive", main, sidebar_html(articles), "文章归档"), encoding="utf-8")


def build_about(articles: list[dict]) -> None:
    counts = Counter(a["category"] for a in articles)
    rows = "\n".join(f"<tr><td>{html_escape(cat)}</td><td>{count}</td></tr>" for cat, count in sorted(counts.items()))
    main = f"""
<section class="about">
  <h2>关于这个博客</h2>
  <p>这是 swilderyude 的研究生阶段学习与科研笔记站点，托管在 GitHub Pages。内容来自本地 Markdown 笔记，经过筛选、分类和静态化生成。</p>
  <p>当前主要栏目包括项目实践、文献精读、计算机视觉、AI 基础、科研方法、工具与环境。大体风格参考博客园的文章流和侧栏结构，但站点实现、样式与内容组织都重新制作。</p>
  <div class="table-wrap"><table><thead><tr><th>分类</th><th>文章数</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p>GitHub：<a href="{SITE["github"]}">{SITE["github"]}</a></p>
</section>
"""
    (DIST / "about.html").write_text(layout("关于", "about", main, sidebar_html(articles), "关于博客"), encoding="utf-8")


def build_search_index(articles: list[dict]) -> None:
    data = [
        {
            "title": a["title"],
            "url": a["url"],
            "date": a["date"],
            "category": a["category"],
            "summary": a["summary"],
            "tags": a["tags"],
        }
        for a in articles
    ]
    (ASSETS_DIR / "search-index.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_output() -> None:
    for name in ["index.html", "categories.html", "archive.html", "about.html"]:
        path = DIST / name
        if path.exists():
            path.unlink()
    for path in [ARTICLES_DIR, MEDIA_DIR]:
        if path.exists():
            shutil.rmtree(path)
    search_index = ASSETS_DIR / "search-index.json"
    if search_index.exists():
        search_index.unlink()


def main() -> None:
    clean_output()
    (ASSETS_DIR / "css").mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "js").mkdir(parents=True, exist_ok=True)
    articles = [article_html(cfg) for cfg in ARTICLES]
    # Sort once for stable sidebars and stats.
    articles = sorted(articles, key=lambda a: a["date"], reverse=True)
    build_index(articles)
    build_articles(articles)
    build_categories(articles)
    build_archive(articles)
    build_about(articles)
    build_search_index(articles)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "README.md").write_text(
        "# swilderyuede.github.io\n\nGitHub Pages blog generated from research-stage notes.\n",
        encoding="utf-8",
    )
    print(f"Built {len(articles)} articles into {DIST}")


if __name__ == "__main__":
    main()
