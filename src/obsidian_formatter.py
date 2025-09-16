"""
Obsidian 格式化器
负责将解析的 Logseq 数据转换为 Obsidian 兼容格式
"""

import re
from typing import Dict, List, Optional
from pathlib import Path


class ObsidianFormatter:
    """Obsidian 格式转换器"""
    
    def __init__(self):
        # Obsidian 块引用计数器（用于生成唯一的块引用）
        self.block_ref_counter = 0
    
    def format_content(self, parsed_data: Dict) -> str:
        """将解析的 Logseq 数据转换为 Obsidian 格式"""
        lines = parsed_data['content'].split('\n')
        
        # 处理每一行
        formatted_lines = []
        for line in lines:
            formatted_line = self._process_line(line, parsed_data)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def _process_line(self, line: str, parsed_data: Dict) -> str:
        """处理单行内容"""
        processed_line = line
        
        # 1. 处理页面链接 [[]]  
        processed_line = self._convert_page_links(processed_line)
        
        # 2. 处理块引用 (()) - 转换为注释或删除
        processed_line = self._convert_block_refs(processed_line)
        
        # 3. 处理块 ID - 转换为 Obsidian 块引用格式
        processed_line = self._convert_block_ids(processed_line)
        
        # 4. 处理资源文件路径
        processed_line = self._convert_asset_paths(processed_line)
        
        return processed_line
    
    def _convert_page_links(self, line: str) -> str:
        """转换页面链接格式"""
        def replace_link(match):
            link_text = match.group(1)
            # Obsidian 双链基本兼容，但需要确保文件扩展名
            return f"[[{link_text}]]"
        
        return re.sub(r'\[\[([^\]]+)\]\]', replace_link, line)
    
    def _convert_block_refs(self, line: str) -> str:
        """处理块引用 - Obsidian 没有对应语法，转换为注释"""
        def replace_block_ref(match):
            block_uuid = match.group(1)
            # 转换为注释形式
            return f"<!-- Block Reference: {block_uuid} -->"
        
        return re.sub(r'\(\(([^)]+)\)\)', replace_block_ref, line)
    
    def _convert_block_ids(self, line: str) -> str:
        """转换块 ID 为 Obsidian 块引用格式"""
        def replace_block_id(match):
            uuid = match.group(1)
            # 生成简短的块引用 ID
            self.block_ref_counter += 1
            block_id = f"block{self.block_ref_counter}"
            return f"^{block_id}"
        
        return re.sub(r'id:: ([a-f0-9-]+)', replace_block_id, line)
    
    def _convert_asset_paths(self, line: str) -> str:
        """转换资源文件路径"""
        def replace_asset(match):
            alt_text = match.group(1)
            file_path = match.group(2)
            
            # 处理相对路径
            if file_path.startswith('../assets/'):
                # 转换为 Obsidian 附件路径
                filename = Path(file_path).name
                new_path = f"attachments/{filename}"
            else:
                new_path = file_path
            
            return f"![{alt_text}]({new_path})"
        
        return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_asset, line)
    
    def add_frontmatter(self, content: str, metadata: Dict = None) -> str:
        """添加 YAML frontmatter"""
        if metadata is None:
            metadata = {}
        
        frontmatter_lines = ["---"]
        
        # 添加基本元数据
        if 'tags' in metadata:
            frontmatter_lines.append(f"tags: {metadata['tags']}")
        
        if 'created' in metadata:
            frontmatter_lines.append(f"created: {metadata['created']}")
        
        if 'logseq_source' in metadata:
            frontmatter_lines.append(f"logseq_source: {metadata['logseq_source']}")
        
        frontmatter_lines.append("---")
        frontmatter_lines.append("")  # 空行分隔
        
        return '\n'.join(frontmatter_lines) + content
    
    def generate_filename(self, original_name: str) -> str:
        """生成 Obsidian 兼容的文件名"""
        # 移除或替换 Obsidian 不支持的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
        
        # 确保 .md 扩展名
        if not safe_name.endswith('.md'):
            safe_name += '.md'
        
        return safe_name
    
    def get_conversion_summary(self, original_data: Dict, converted_content: str) -> Dict:
        """生成转换摘要"""
        original_stats = {
            'page_links': len(re.findall(r'\[\[([^\]]+)\]\]', original_data['content'])),
            'block_refs': len(re.findall(r'\(\(([^)]+)\)\)', original_data['content'])),
            'block_ids': len(re.findall(r'id:: ([a-f0-9-]+)', original_data['content'])),
            'assets': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', original_data['content']))
        }
        
        converted_stats = {
            'page_links': len(re.findall(r'\[\[([^\]]+)\]\]', converted_content)),
            'block_refs': len(re.findall(r'<!-- Block Reference:', converted_content)),
            'block_ids': len(re.findall(r'\^block\d+', converted_content)),
            'assets': len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', converted_content))
        }
        
        return {
            'original': original_stats,
            'converted': converted_stats,
            'changes': {
                'block_refs_to_comments': original_stats['block_refs'],
                'block_ids_converted': original_stats['block_ids']
            }
        }