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
SITE_ASSET_DIR = ASSETS_DIR / "site"
SITE_IMAGE_SOURCE = SOURCE / "微信图片_20260528231942_115_26.jpg"

SITE = {
    "title": "潮汐日志",
    "subtitle": "Tide Logs · 一名学习者的潮汐记录",
    "author": "墨玉",
    "github": "https://github.com/swilderyude",
    "repo": "https://github.com/swilderyude/swilderyude.github.io",
    "base_url": "https://swilderyude.github.io",
    "cover": "assets/site/moyu-cover.webp",
    "avatar": "assets/site/moyu-avatar.webp",
}

TIDE_SECTIONS = {
    "拾贝": {
        "en": "Shells",
        "motto": "学习记录，零散捡到的都算。",
        "desc": "AI 基础、计算机视觉、工具与日常学习笔记，都先收进这一篮贝壳里。",
    },
    "造船": {
        "en": "Shipyard",
        "motto": "项目记录，从龙骨到下水。",
        "desc": "把项目推进中的数据、标注、训练、封装、复盘按时间留下来。",
    },
    "潜渊": {
        "en": "Deep Dive",
        "motto": "科研记录，往深处去。",
        "desc": "论文精读、科研方法和模型机制理解，放在更深的水域里慢慢看。",
    },
    "漂流瓶": {
        "en": "Drift Bottle",
        "motto": "思想感悟，写给海，不一定有人捡。",
        "desc": "暂时还没有投出的瓶子，等某天潮水把它带来。",
    },
}

SECTION_ORDER = ("拾贝", "造船", "潜渊", "漂流瓶")


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


def display_folder_parts_from_source(source: str) -> list[str]:
    parts = list(Path(source).parts[:-1])
    if parts and parts[0] == "CS自学":
        parts = parts[1:]
    return parts or ["根目录笔记"]


def folder_label(parts: Iterable[str], include_root: bool = True) -> str:
    pieces = list(parts)
    if include_root:
        pieces = ["CS自学", *pieces]
    return " / ".join(pieces)


def top_folder_names_from_configs() -> set[str]:
    return {display_folder_parts_from_source(cfg.source)[0] for cfg in ARTICLES}


def tide_section_for(source: str, category: str) -> str:
    top = display_folder_parts_from_source(source)[0]
    if category == "项目实践" or top == "人脸色斑检测":
        return "造船"
    if category in {"科研方法", "文献精读"} or top in {"科研", "精读论文"}:
        return "潜渊"
    return "拾贝"


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


def copy_site_assets() -> None:
    SITE_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    cover = SITE_ASSET_DIR / "moyu-cover.webp"
    avatar = SITE_ASSET_DIR / "moyu-avatar.webp"

    if not SITE_IMAGE_SOURCE.exists():
        return

    try:
        from PIL import Image, ImageOps

        img = Image.open(SITE_IMAGE_SOURCE).convert("RGB")
        cover_img = img.copy()
        cover_img.thumbnail((1400, 1400))
        cover_img.save(cover, "WEBP", quality=82, method=6)

        resample = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        avatar_img = ImageOps.fit(img, (360, 360), method=resample, centering=(0.5, 0.45))
        avatar_img.save(avatar, "WEBP", quality=84, method=6)
    except Exception:
        shutil.copy2(SITE_IMAGE_SOURCE, SITE_ASSET_DIR / SITE_IMAGE_SOURCE.name)


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
    html_text = wrap_code_blocks(html_text)
    return html_text


def wrap_code_blocks(html_text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        block = match.group(0)
        attrs = f"{match.group(1) or ''} {match.group(2) or ''}"
        lang = "代码"
        class_match = re.search(r'class="([^"]+)"', attrs)
        if class_match:
            classes = [c for c in class_match.group(1).split() if c not in {"sourceCode", "numberSource"}]
            if classes:
                lang = classes[0].replace("language-", "").upper()
        return (
            '<details class="codeFold">'
            f'<summary><span>展开代码</span><em>{html_escape(lang)}</em></summary>'
            f"{block}</details>"
        )

    return re.sub(r'<pre([^>]*)><code([^>]*)>[\s\S]*?</code></pre>', repl, html_text)


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
    display_parts = display_folder_parts_from_source(article.source)
    return {
        "slug": slug,
        "source": article.source,
        "file_name": Path(article.source).name,
        "folder_parts": list(Path(article.source).parts[:-1]),
        "display_folder_parts": display_parts,
        "folder_label": folder_label(display_parts),
        "section": tide_section_for(article.source, article.category),
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


def layout(title: str, active: str, main: str, sidebar: str, description: str = "", prefix: str = "") -> str:
    desc = html_escape(description or SITE["subtitle"])
    nav = [
        ("首页", f"{prefix}index.html", "home"),
        ("目录", f"{prefix}categories.html", "categories"),
        ("归档", f"{prefix}archive.html", "archive"),
        ("关于", f"{prefix}about.html", "about"),
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
  <title>{html_escape(title)} - {html_escape(SITE["title"])}</title>
  <link rel="stylesheet" href="{prefix}assets/css/style.css">
  <script defer src="{prefix}assets/js/site.js"></script>
</head>
<body class="page-{active or "article"}">
  <a id="top"></a>
  <div id="home">
    <header id="header">
      <div id="blogTitle">
        <a id="lnkBlogLogo" href="{prefix}index.html" aria-label="返回主页"><img id="blogLogo" src="{prefix}{SITE["avatar"]}" alt=""></a>
        <div class="brandText">
          <h1><a id="Header1_HeaderTitle" class="headermaintitle" href="{prefix}index.html">{html_escape(SITE["title"])}</a></h1>
          <h2>{html_escape(SITE["subtitle"])}</h2>
        </div>
      </div>
      <nav id="navigator" aria-label="主导航">
        <ul id="navList">
          {nav_html}
        </ul>
        <div class="blogStats">日志 {len(ARTICLES)} · 分区 {len(SECTION_ORDER)} · 今日潮汐</div>
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


def folder_sort_key(name: str) -> tuple[int, str]:
    return (FOLDER_ORDER.get(name, 99), name)


def make_folder_node(name: str, path: list[str]) -> dict:
    return {"name": name, "path": path, "children": {}, "articles": []}


def build_folder_tree(articles: list[dict]) -> dict:
    root = make_folder_node("CS自学", [])
    for article in articles:
        node = root
        for part in article["display_folder_parts"]:
            if part not in node["children"]:
                node["children"][part] = make_folder_node(part, [*node["path"], part])
            node = node["children"][part]
        node["articles"].append(article)
    return root


def folder_article_count(node: dict) -> int:
    return len(node["articles"]) + sum(folder_article_count(child) for child in node["children"].values())


def folder_child_count(node: dict) -> int:
    return len(node["children"])


def folder_anchor(parts: Iterable[str]) -> str:
    return f"folder-{slugify('/'.join(parts))}"


def folder_article_item(article: dict, prefix: str = "") -> str:
    tags = "".join(f"<span>{html_escape(tag)}</span>" for tag in article["tags"][:3])
    return f"""
<li class="folder-article">
  <a href="{prefix}{article["url"]}">{html_escape(article["title"])}</a>
  <time>{article["date"]}</time>
  <div class="miniTags">{tags}</div>
</li>
"""


def render_folder_node(node: dict, prefix: str = "", top: bool = False, index: str = "") -> str:
    children = sorted(node["children"].values(), key=lambda child: folder_sort_key(child["name"]))
    direct_articles = sorted(node["articles"], key=lambda a: a["date"], reverse=True)
    count = folder_article_count(node)
    child_count = folder_child_count(node)
    article_word = f"{count} 篇笔记"
    child_word = f"{child_count} 个子目录" if child_count else "无子目录"
    path_label = folder_label(node["path"])
    description = FOLDER_DESCRIPTIONS.get(node["name"], "按原始文件夹保留的一组研究笔记。")

    direct_html = ""
    if direct_articles:
        direct_html = f"""
<div class="folder-section">
  <div class="folder-section-title">当前目录</div>
  <ul class="folder-article-list">
    {"".join(folder_article_item(article, prefix) for article in direct_articles)}
  </ul>
</div>
"""

    children_html = ""
    if children:
        child_nodes = "".join(
            render_folder_node(child, prefix, top=False, index=f"{index}.{i}" if index else str(i))
            for i, child in enumerate(children, 1)
        )
        children_html = f"""
<div class="subfolder-stack">
  {child_nodes}
</div>
"""

    classes = "folder-card" if top else "folder-node"
    anchor = folder_anchor(node["path"])
    index_html = html_escape(index or "00")
    return f"""
<details id="{anchor}" class="{classes}">
  <summary>
    <span class="folderIndex" aria-hidden="true">{index_html}</span>
    <span class="folderSummaryText">
      <strong>{html_escape(node["name"])}</strong>
      <small>{html_escape(description)}</small>
    </span>
    <span class="folderMeta">{article_word} · {child_word}</span>
  </summary>
  <div class="folderBody">
    <div class="folderPath">路径：{html_escape(path_label)}</div>
    {direct_html}
    {children_html}
  </div>
</details>
"""


def folder_overview_html(articles: list[dict], prefix: str = "", title: str = "研究生阶段笔记目录", intro: str = "") -> str:
    tree = build_folder_tree(articles)
    top_nodes = sorted(tree["children"].values(), key=lambda node: folder_sort_key(node["name"]))
    newest = max((a["date"] for a in articles), default="")
    intro_text = intro or "首页按原始文件夹组织，只展示目录入口；展开文件夹后再进入具体笔记。"
    folder_cards = "\n".join(render_folder_node(node, prefix=prefix, top=True, index=f"{i:02d}") for i, node in enumerate(top_nodes, 1))
    return f"""
<section class="directoryIntro">
  <div>
    <p class="directoryEyebrow">文件夹视图</p>
    <h2>{html_escape(title)}</h2>
    <p>{html_escape(intro_text)}</p>
  </div>
  <dl class="directoryStats">
    <div><dt>{len(top_nodes)}</dt><dd>一级文件夹</dd></div>
    <div><dt>{len(articles)}</dt><dd>公开笔记</dd></div>
    <div><dt>{html_escape(newest)}</dt><dd>最近更新</dd></div>
  </dl>
</section>
<section class="folderExplorer" aria-label="文件夹目录">
  {folder_cards}
</section>
"""


def home_hero_html(articles: list[dict]) -> str:
    newest = max((a["date"] for a in articles), default="")
    return f"""
<section class="homeHero">
  <div class="heroContent">
    <p class="heroKicker">Tide Logs</p>
    <h2>潮汐日志</h2>
    <p class="heroLead">一名学习者的潮汐记录。把学习、项目、科研与偶然漂来的念头，按潮水的节律慢慢写下。</p>
    <blockquote class="dailyQuote">
      <span data-daily-quote>潮平两岸阔，风正一帆悬。</span>
    </blockquote>
    <dl class="heroStats">
      <div><dt>{len(articles)}</dt><dd>公开笔记</dd></div>
      <div><dt>{len(SECTION_ORDER)}</dt><dd>潮汐分区</dd></div>
      <div><dt>{html_escape(newest)}</dt><dd>最近更新</dd></div>
    </dl>
  </div>
  <figure class="heroPortrait">
    <img src="{SITE["cover"]}" alt="潮汐日志主视觉">
  </figure>
</section>
"""


def group_by_tide_section(articles: list[dict]) -> dict[str, list[dict]]:
    grouped = {name: [] for name in SECTION_ORDER}
    for article in articles:
        grouped.setdefault(article["section"], []).append(article)
    for items in grouped.values():
        items.sort(key=lambda item: item["date"], reverse=True)
    return grouped


def tide_article_link(article: dict, prefix: str = "", index: int = 1) -> str:
    tags = "".join(f"<span>{html_escape(tag)}</span>" for tag in article["tags"][:2])
    return f"""
<li class="tideArticle">
  <a href="{prefix}{article["url"]}">
    <span class="tideArticleNo">{index:02d}</span>
    <span class="tideArticleMain">
      <strong>{html_escape(article["title"])}</strong>
      <small>{html_escape(article["summary"])}</small>
    </span>
    <time>{article["date"]}</time>
  </a>
  <div class="miniTags">{tags}</div>
</li>
"""


def tide_sections_html(articles: list[dict], prefix: str = "", title: str = "潮汐目录", intro: str = "") -> str:
    grouped = group_by_tide_section(articles)
    intro_text = intro or "每一段学习都像潮水留下的纹理，按它靠岸的方式归入不同海域。"
    cards = []
    for section_index, section in enumerate(SECTION_ORDER, 1):
        meta = TIDE_SECTIONS[section]
        items = grouped.get(section, [])
        if items:
            article_list = "\n".join(tide_article_link(article, prefix, i) for i, article in enumerate(items, 1))
        else:
            article_list = '<li class="emptyBottle">潮水还没有送来新的瓶子。</li>'
        cards.append(
            f"""
<section id="{slugify(section)}" class="tideSection">
  <div class="sectionHeader">
    <span class="sectionIndex">{section_index:02d}</span>
    <div>
      <p>{html_escape(meta["en"])}</p>
      <h3>{html_escape(section)}</h3>
      <small>{html_escape(meta["motto"])}</small>
    </div>
  </div>
  <p class="sectionDesc">{html_escape(meta["desc"])}</p>
  <ul class="sectionArticles">{article_list}</ul>
</section>
"""
        )
    return f"""
<section class="tideIntro">
  <p class="sectionEyebrow">Current Index</p>
  <h2>{html_escape(title)}</h2>
  <p>{html_escape(intro_text)}</p>
</section>
<div class="tideBoard">
  {"".join(cards)}
</div>
"""


def sidebar_section_links(articles: list[dict], prefix: str = "") -> str:
    grouped = group_by_tide_section(articles)
    return "\n".join(
        f'<li><a href="{prefix}categories.html#{slugify(section)}">{html_escape(section)}<span>{len(grouped.get(section, []))}</span></a></li>'
        for section in SECTION_ORDER
    )


def sidebar_html(articles: list[dict], current_category: str | None = None, prefix: str = "") -> str:
    latest = "\n".join(
        f'<li><span>{i:02d}</span><a href="{prefix}{a["url"]}">{html_escape(a["title"])}</a></li>'
        for i, a in enumerate(sorted(articles, key=lambda x: x["date"], reverse=True)[:6], 1)
    )
    recommended = "\n".join(
        f'<li><span>{i:02d}</span><a href="{prefix}{a["url"]}">{html_escape(a["title"])}</a></li>'
        for i, a in enumerate([a for a in articles if a["pinned"]], 1)
    )
    tags = Counter(tag for a in articles for tag in a["tags"])
    tag_cloud = "\n".join(
        f'<a href="{prefix}archive.html?tag={html_escape(tag)}">{html_escape(tag)}</a>'
        for tag, _ in tags.most_common(18)
    )
    return f"""
<section class="profileCard">
  <img src="{prefix}{SITE["avatar"]}" alt="墨玉头像">
  <h3>潮汐日志</h3>
  <p>学习者的潮汐记录，写下每一次靠岸和远航。</p>
  <a href="{SITE["github"]}">GitHub / swilderyude</a>
</section>
<section class="catList">
  <h3 class="catListTitle">潮汐分区</h3>
  <ul class="sectionSideList">{sidebar_section_links(articles, prefix)}</ul>
</section>
<section class="catList">
  <h3 class="catListTitle">主线笔记</h3>
  <ul class="rankList">{recommended}</ul>
</section>
<section class="catList">
  <h3 class="catListTitle">最近更新</h3>
  <ul class="rankList">{latest}</ul>
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
    main = home_hero_html(articles) + tide_sections_html(
        articles,
        title="潮汐目录",
        intro="不摊开成冷冰冰的清单，而按学习时的潮汐归港：拾贝、造船、潜渊，以及尚未投出的漂流瓶。",
    )
    (DIST / "index.html").write_text(layout("首页", "home", main, sidebar_html(articles), "潮汐日志，一名学习者的潮汐记录"), encoding="utf-8")


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
    section_href = f'../categories.html#{slugify(article["section"])}'
    return f"""
<article class="post">
  <div class="breadcrumbs"><a href="../index.html">首页</a><span>/</span><a href="{section_href}">{html_escape(article["section"])}</a><span>/</span><strong>{html_escape(article["title"])}</strong></div>
  <h1 class="postTitle single"><span>{html_escape(article["title"])}</span></h1>
  <div class="postDesc">posted @ {article["date"]} {html_escape(SITE["author"])} 分区: <a href="../categories.html#{slugify(article["section"])}">{html_escape(article["section"])}</a></div>
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
        page = layout(article["title"], "", body, article_sidebar, article["summary"], prefix="../")
        (ARTICLES_DIR / f"{article['slug']}.html").write_text(page, encoding="utf-8")


def build_categories(articles: list[dict]) -> None:
    main = tide_sections_html(
        articles,
        title="潮汐目录",
        intro="拾贝、造船、潜渊、漂流瓶：让笔记按它们的气质靠岸。",
    )
    (DIST / "categories.html").write_text(layout("目录", "categories", main, sidebar_html(articles), "潮汐目录"), encoding="utf-8")


def build_archive(articles: list[dict]) -> None:
    rows = "\n".join(
        f'<li id="{a["date"]}"><time>{a["date"]}</time><a href="{a["url"]}">{html_escape(a["title"])}</a><span>{html_escape(a["section"])}</span></li>'
        for a in sorted(articles, key=lambda x: x["date"], reverse=True)
    )
    tags = Counter(tag for a in articles for tag in a["tags"])
    tag_list = "\n".join(f'<button class="tag-filter" data-tag="{html_escape(tag)}">{html_escape(tag)} <span>{count}</span></button>' for tag, count in tags.most_common())
    data = html_escape(
        json.dumps(
            [
                {
                    "title": a["title"],
                    "url": a["url"],
                    "date": a["date"],
                    "folder": a["section"],
                    "tags": a["tags"],
                }
                for a in articles
            ],
            ensure_ascii=False,
        )
    )
    main = f"""
<section class="archive">
  <h2>归档</h2>
  <div class="archive-tags">{tag_list}</div>
  <ul class="archive-list" data-articles="{data}">{rows}</ul>
</section>
"""
    (DIST / "archive.html").write_text(layout("归档", "archive", main, sidebar_html(articles), "文章归档"), encoding="utf-8")


def build_about(articles: list[dict]) -> None:
    counts = Counter(a["section"] for a in articles)
    rows = "\n".join(f"<tr><td>{html_escape(section)}</td><td>{counts.get(section, 0)}</td></tr>" for section in SECTION_ORDER)
    main = f"""
<section class="about">
  <h2>关于这个博客</h2>
  <p>这是《潮汐日志》，一名学习者的潮汐记录。内容来自本地 Markdown 笔记，经过筛选、分区和静态化生成，托管在 GitHub Pages。</p>
  <p>主页按拾贝、造船、潜渊、漂流瓶四个海域组织；文章页保留目录、正文、推荐阅读和侧栏索引。</p>
  <div class="table-wrap"><table><thead><tr><th>分区</th><th>文章数</th></tr></thead><tbody>{rows}</tbody></table></div>
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
            "folder": a["folder_label"],
            "section": a["section"],
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
    copy_site_assets()
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
        "# 潮汐日志\n\nTide Logs · 一名学习者的潮汐记录。\n",
        encoding="utf-8",
    )
    print(f"Built {len(articles)} articles into {DIST}")


if __name__ == "__main__":
    main()
