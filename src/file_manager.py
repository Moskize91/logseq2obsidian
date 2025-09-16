"""
文件管理器
负责文件的读取、写入和目录管理
"""

import shutil
from pathlib import Path
from typing import List, Dict, Optional
from .filename_processor import FilenameProcessor


class FileManager:
    """文件管理器"""
    
    def __init__(self, output_dir: Path, dry_run: bool = False):
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        
        if not dry_run:
            # 确保输出目录存在
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_file(self, filename: str, content: str, subfolder: str = "") -> Path:
        """写入文件"""
        # 处理文件名：解码 URL 编码并替换 Obsidian 不支持的字符
        processed_filename = FilenameProcessor.process_filename(filename)
        
        # 构造完整路径
        if subfolder:
            target_dir = self.output_dir / subfolder
            if not self.dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self.output_dir
        
        file_path = target_dir / processed_filename
        
        if self.dry_run:
            print(f"[DRY RUN] 会写入文件: {file_path}")
            if processed_filename != filename:
                print(f"[DRY RUN] 文件名转换: {filename} -> {processed_filename}")
            print(f"[DRY RUN] 内容长度: {len(content)} 字符")
            return file_path
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            if processed_filename != filename:
                print(f"文件名转换: {filename} -> {processed_filename}")
            print(f"已写入文件: {file_path}")
            return file_path
            
        except Exception as e:
            raise ValueError(f"写入文件 {file_path} 时出错: {e}") from e
    
    def copy_assets(self, source_paths: List[Path], target_subdir: str = "attachments") -> List[Path]:
        """复制资源文件"""
        target_dir = self.output_dir / target_subdir
        copied_files = []
        
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
        
        for source_path in source_paths:
            if not source_path.exists():
                print(f"警告：源文件不存在: {source_path}")
                continue
            
            target_path = target_dir / source_path.name
            
            if self.dry_run:
                print(f"[DRY RUN] 会复制文件: {source_path} -> {target_path}")
                copied_files.append(target_path)
                continue
            
            try:
                shutil.copy2(source_path, target_path)
                print(f"已复制资源文件: {source_path} -> {target_path}")
                copied_files.append(target_path)
                
            except Exception as e:
                print(f"复制文件失败 {source_path}: {e}")
        
        return copied_files
    
    def create_conversion_report(self, conversions: List[Dict]) -> Path:
        """创建转换报告"""
        report_lines = [
            "# Logseq to Obsidian 转换报告",
            f"生成时间: {self._get_timestamp()}",
            "",
            "## 转换摘要",
            f"- 总文件数: {len(conversions)}",
            f"- 成功转换: {len([c for c in conversions if c.get('success', False)])}",
            f"- 转换失败: {len([c for c in conversions if not c.get('success', False)])}",
            "",
            "## 详细信息",
            ""
        ]
        
        for i, conversion in enumerate(conversions, 1):
            report_lines.extend([
                f"### {i}. {conversion.get('source_file', 'Unknown')}",
                f"- 状态: {'✅ 成功' if conversion.get('success', False) else '❌ 失败'}",
                f"- 目标文件: {conversion.get('target_file', 'N/A')}",
                ""
            ])
            
            if 'summary' in conversion:
                summary = conversion['summary']
                report_lines.extend([
                    "**转换统计:**",
                    f"- 页面链接: {summary.get('original', {}).get('page_links', 0)} -> {summary.get('converted', {}).get('page_links', 0)}",
                    f"- 块引用: {summary.get('original', {}).get('block_refs', 0)} -> {summary.get('converted', {}).get('block_refs', 0)} (转为注释)",
                    f"- 块ID: {summary.get('original', {}).get('block_ids', 0)} -> {summary.get('converted', {}).get('block_ids', 0)}",
                    f"- 资源文件: {summary.get('original', {}).get('assets', 0)} -> {summary.get('converted', {}).get('assets', 0)}",
                    ""
                ])
            
            if 'error' in conversion:
                report_lines.extend([
                    f"**错误信息:** {conversion['error']}",
                    ""
                ])
        
        report_content = '\n'.join(report_lines)
        return self.write_file("conversion_report.md", report_content)
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def list_logseq_files(self, logseq_dir: Path) -> List[Path]:
        """列出 Logseq 目录中的所有 .md 文件"""
        logseq_path = Path(logseq_dir)
        
        if not logseq_path.exists():
            raise Exception(f"Logseq 目录不存在: {logseq_path}")
        
        md_files = []
        
        # 查找 pages 目录
        pages_dir = logseq_path / "pages"
        if pages_dir.exists():
            md_files.extend(pages_dir.glob("*.md"))
        
        # 查找 journals 目录  
        journals_dir = logseq_path / "journals"
        if journals_dir.exists():
            md_files.extend(journals_dir.glob("*.md"))
        
        # 查找根目录的 .md 文件
        md_files.extend(logseq_path.glob("*.md"))
        
        return sorted(md_files)
    
    def get_asset_paths(self, logseq_dir: Path, content: str) -> List[Path]:
        """从内容中提取资源文件路径"""
        import re
        
        logseq_path = Path(logseq_dir)
        asset_paths = []
        
        # 提取图片等资源文件引用
        asset_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        
        for match in asset_pattern.finditer(content):
            asset_url = match.group(2)
            
            # 处理相对路径
            if asset_url.startswith('../assets/'):
                asset_path = logseq_path / asset_url[3:]  # 去掉 '../'
                if asset_path.exists():
                    asset_paths.append(asset_path)
        
        return asset_paths