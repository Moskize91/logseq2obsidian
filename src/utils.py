"""
工具函数模块
包含项目中使用的各种工具函数
"""

import re
from pathlib import Path
from typing import Dict, List, Set


def clean_filename(filename: str) -> str:
    """清理文件名，确保与文件系统兼容"""
    # 移除或替换不安全的字符
    safe_filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # 移除前后空白
    safe_filename = safe_filename.strip()
    # 确保不为空
    if not safe_filename:
        safe_filename = "untitled"
    return safe_filename


def extract_tags_from_content(content: str) -> Set[str]:
    """从内容中提取标签"""
    tags = set()

    # Logseq 标签格式: #标签
    tag_pattern = re.compile(r"#([^\s#]+)")

    for match in tag_pattern.finditer(content):
        tag = match.group(1)
        # 过滤掉数字标签（可能是标题）
        if not tag.isdigit():
            tags.add(tag)

    return tags


def generate_unique_id(existing_ids: Set[str], prefix: str = "block") -> str:
    """生成唯一的 ID"""
    counter = 1
    while True:
        new_id = f"{prefix}{counter}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id
        counter += 1


def normalize_page_name(page_name: str) -> str:
    """标准化页面名称，确保一致性"""
    # 移除前后空白
    normalized = page_name.strip()

    # 替换空格为下划线或连字符（根据需要调整）
    normalized = re.sub(r"\s+", "_", normalized)

    return normalized


def detect_file_encoding(file_path: Path) -> str:
    """检测文件编码"""
    try:
        # 尝试常见编码
        encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin1"]

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    f.read()
                return encoding
            except UnicodeDecodeError:
                continue

        # 如果都失败，默认使用 utf-8
        return "utf-8"

    except Exception:
        return "utf-8"


def validate_markdown_syntax(content: str) -> List[str]:
    """验证 Markdown 语法，返回可能的问题"""
    issues = []

    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # 检查不匹配的括号
        open_brackets = line.count("[")
        close_brackets = line.count("]")
        if open_brackets != close_brackets:
            issues.append(f"行 {i}: 方括号不匹配")

        open_parens = line.count("(")
        close_parens = line.count(")")
        if open_parens != close_parens:
            issues.append(f"行 {i}: 圆括号不匹配")

    return issues


def calculate_file_stats(content: str) -> Dict[str, int]:
    """计算文件统计信息"""
    lines = content.split("\n")

    stats = {
        "total_lines": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "word_count": len(content.split()),
        "char_count": len(content),
        "heading_count": len([line for line in lines if line.strip().startswith("#")]),
        "list_items": len([line for line in lines if re.match(r"^\s*[-*+]\s", line)]),
    }

    return stats


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """创建进度条字符串"""
    if total == 0:
        return "[" + "█" * width + "] 100%"

    progress = current / total
    filled_width = int(width * progress)
    bar = "█" * filled_width + "░" * (width - filled_width)
    percentage = progress * 100

    return f"[{bar}] {percentage:.1f}% ({current}/{total})"
