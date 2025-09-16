"""
Obsidian 格式化器
负责将解析的 Logseq 数据转换为 Obsidian 兼容格式
"""

import re
from typing import Dict, List, Optional
from pathlib import Path


class ObsidianFormatter:
    """Obsidian 格式转换器"""
    
    def __init__(self, remove_top_level_bullets=False):
        # Obsidian 块引用计数器（用于生成唯一的块引用）
        self.block_ref_counter = 0
        # 是否删除第一级列表符号
        self.remove_top_level_bullets = remove_top_level_bullets
    
    def format_content(self, parsed_data: Dict) -> str:
        """将解析的 Logseq 数据转换为 Obsidian 格式"""
        lines = parsed_data['content'].split('\n')
        
        # 处理每一行
        formatted_lines = []
        for line in lines:
            formatted_line = self._process_line(line, parsed_data)
            formatted_lines.append(formatted_line)
        
        # 如果启用了删除第一级列表符号，进行后处理
        if self.remove_top_level_bullets:
            formatted_lines = self._remove_top_level_bullets(formatted_lines)
        
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
    
    def _remove_top_level_bullets(self, lines: list) -> list:
        """删除第一级列表符号，转换为段落格式"""
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # 检查是否是第一级列表项（没有前导空格的 "- "）
            if line.startswith('- ') and not line.startswith('  '):
                # 删除 "- " 前缀
                content = line[2:]
                
                # 如果内容不为空，添加到结果
                if content.strip():
                    result.append(content)
                
                # 检查下一行是否是缩进的子项
                has_sub_items = False
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == '':
                        j += 1
                        continue
                    elif next_line.startswith('  ') or next_line.startswith('\t'):
                        # 这是子项，保留原样
                        has_sub_items = True
                        break
                    else:
                        # 这不是子项，停止检查
                        break
                
                # 如果有子项，处理它们
                if has_sub_items:
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip() == '':
                            result.append(next_line)
                        elif next_line.startswith('  ') or next_line.startswith('\t'):
                            result.append(next_line)
                        else:
                            break
                        j += 1
                    i = j - 1
                
                # 在段落后添加空行（如果下一行不是空行）
                if i + 1 < len(lines) and lines[i + 1].strip() != '':
                    result.append('')
                    
            else:
                # 不是第一级列表项，保持原样
                result.append(line)
            
            i += 1
        
        return result