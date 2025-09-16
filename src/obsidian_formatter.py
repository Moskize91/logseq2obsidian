"""
Obsidian 格式化器
负责将解析的 Logseq 数据转换为 Obsidian 兼容格式
"""

import re
from typing import Dict
from pathlib import Path
from .filename_processor import FilenameProcessor


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
        
        # 生成 YAML frontmatter（如果有 meta 属性）
        frontmatter = self._generate_frontmatter(parsed_data.get('meta_properties', []))
        
        # 移除原始内容中的 meta 属性行
        filtered_lines = self._filter_meta_lines(lines, parsed_data.get('meta_properties', []))
        
        # 处理每一行
        formatted_lines = []
        for line in filtered_lines:
            formatted_line = self._process_line(line, parsed_data)
            formatted_lines.append(formatted_line)
        
        # 如果启用了删除第一级列表符号，进行后处理
        if self.remove_top_level_bullets:
            formatted_lines = self._remove_top_level_bullets(formatted_lines)
        
        # 组合 frontmatter 和内容
        if frontmatter:
            return frontmatter + '\n' + '\n'.join(formatted_lines)
        else:
            return '\n'.join(formatted_lines)
    
    def _process_line(self, line: str, parsed_data: Dict) -> str:
        """处理单行内容"""
        processed_line = line
        
        # 1. 处理 Logseq 引用块格式 "- >" -> ">"
        processed_line = self._convert_quote_blocks(processed_line)
        
        # 2. 处理页面链接 [[]]  
        processed_line = self._convert_page_links(processed_line)
        
        # 3. 处理块引用 (()) - 转换为注释或删除
        processed_line = self._convert_block_refs(processed_line)
        
        # 4. 处理块 ID - 转换为 Obsidian 块引用格式
        processed_line = self._convert_block_ids(processed_line)
        
        # 5. 处理资源文件路径
        processed_line = self._convert_asset_paths(processed_line)
        
        return processed_line
    
    def _convert_quote_blocks(self, line: str) -> str:
        """转换 Logseq 引用块格式 '- >' 为 Obsidian 引用格式 '>'"""
        # 匹配以任意数量的空格/制表符开头，然后是 "- >" 的行
        pattern = r'^(\s*)-\s*>\s*(.*)$'
        match = re.match(pattern, line)
        
        if match:
            indent = match.group(1)  # 保留原有的缩进
            content = match.group(2)  # 引用的内容
            return f"{indent}> {content}"
        
        return line
    
    def _convert_page_links(self, line: str) -> str:
        """转换页面链接格式"""
        def replace_link(match):
            link_text = match.group(1)
            # 处理文件名：解码 URL 编码并替换 Obsidian 不支持的字符
            processed_link = FilenameProcessor.process_page_link(link_text)
            # Obsidian 双链基本兼容，但需要确保文件扩展名
            return f"[[{processed_link}]]"

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
        """删除第一级列表符号，转换为段落格式，并规范化列表缩进"""
        result = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # 跳过只有 '-' 的空行
            if line.strip() == '-':
                i += 1
                continue
            
            # 检查是否是第一级列表项（没有前导空格的 "- "）
            if line.startswith('- ') and not line.startswith('  '):
                # 删除 "- " 前缀
                content = line[2:]
                
                # 如果内容不为空，添加到结果
                if content.strip():
                    result.append(content)
                else:
                    # 如果是空的列表项，跳过
                    i += 1
                    continue
                
                # 处理后续的子项，规范化缩进
                j = i + 1
                has_sub_items = False
                
                while j < len(lines):
                    next_line = lines[j]
                    
                    # 空行保持原样
                    if next_line.strip() == '':
                        result.append(next_line)
                        j += 1
                        continue
                    
                    # 检查是否是子项（以制表符或多个空格开头）
                    if next_line.startswith('\t') or next_line.startswith('  '):
                        has_sub_items = True
                        # 规范化缩进并提升一个层级（减少缩进）
                        normalized_line = self._normalize_list_indent(next_line)
                        
                        # 处理空的子列表项
                        if normalized_line.strip() in ['-', '- ']:
                            # 跳过空的子列表项
                            j += 1
                            continue
                        
                        # 提升一个层级：移除一级缩进（2个空格）
                        if normalized_line.startswith('  '):
                            promoted_line = normalized_line[2:]  # 移除前面的2个空格
                        else:
                            promoted_line = normalized_line  # 如果没有足够的缩进，保持原样
                        
                        result.append(promoted_line)
                        j += 1
                    else:
                        # 不是子项，停止处理
                        break
                
                i = j - 1
                
                # 只有在没有子项且下一行不是空行或另一个第一级列表项时才添加空行
                if not has_sub_items and i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip() != '' and not next_line.startswith('- '):
                        result.append('')
                    
            else:
                # 不是第一级列表项
                if line.startswith('\t') or line.startswith('  '):
                    # 规范化子项缩进
                    normalized_line = self._normalize_list_indent(line)
                    
                    # 处理空的子列表项
                    if normalized_line.strip() in ['-', '- ']:
                        # 跳过空的子列表项
                        i += 1
                        continue
                        
                    result.append(normalized_line)
                else:
                    # 普通行保持原样
                    result.append(line)
            
            i += 1
        
        return result
    
    def _normalize_list_indent(self, line: str) -> str:
        """规范化列表项的缩进"""
        # 计算前导空白的数量
        stripped = line.lstrip()
        leading_whitespace = line[:len(line) - len(stripped)]
        
        # 计算缩进级别：制表符按1级计算，每2个空格按1级计算
        indent_level = 0
        i = 0
        while i < len(leading_whitespace):
            char = leading_whitespace[i]
            if char == '\t':
                indent_level += 1
                i += 1
            elif char == ' ':
                # 连续的空格按2个为一级缩进
                space_count = 0
                while i < len(leading_whitespace) and leading_whitespace[i] == ' ':
                    space_count += 1
                    i += 1
                indent_level += space_count // 2  # 每2个空格算1级
            else:
                i += 1
        
        # 生成规范化的缩进（每级2个空格）
        normalized_indent = '  ' * indent_level
        
        return normalized_indent + stripped
    
    def _generate_frontmatter(self, meta_properties) -> str:
        """生成 YAML frontmatter"""
        if not meta_properties:
            return ""
        
        frontmatter_lines = ["---"]
        
        for prop in meta_properties:
            key = prop.key
            value = prop.value
            
            # 处理不同类型的属性
            if key == "alias":
                # 别名转换为 aliases 数组
                # 首先提取所有 [[]] 格式的页面链接
                page_link_matches = re.findall(r'\[\[([^\]]+)\]\]', value)
                if page_link_matches:
                    # 如果有页面链接，使用页面链接内容作为别名
                    aliases = page_link_matches
                else:
                    # 否则按逗号分割
                    aliases = [alias.strip() for alias in value.split(',')]
                
                frontmatter_lines.append("aliases:")
                for alias in aliases:
                    # 确保别名不为空
                    if alias.strip():
                        frontmatter_lines.append(f"  - {alias.strip()}")
            elif key == "tags":
                # 标签处理：提取 [[]] 内的内容
                tag_matches = re.findall(r'\[\[([^\]]+)\]\]', value)
                if tag_matches:
                    frontmatter_lines.append("tags:")
                    for tag in tag_matches:
                        frontmatter_lines.append(f"  - {tag}")
                else:
                    # 如果没有 [[]] 格式，按逗号分割
                    tags = [tag.strip() for tag in value.split(',')]
                    frontmatter_lines.append("tags:")
                    for tag in tags:
                        frontmatter_lines.append(f"  - {tag}")
            elif key == "created-at":
                # 日期属性
                frontmatter_lines.append(f"created: {value}")
            elif key == "type":
                # 类型属性
                frontmatter_lines.append(f"type: {value}")
            elif key == "author":
                # 作者属性
                frontmatter_lines.append(f"author: {value}")
            elif key == "status":
                # 状态属性
                frontmatter_lines.append(f"status: {value}")
            elif key == "priority":
                # 优先级属性
                frontmatter_lines.append(f"priority: {value}")
            elif key == "description":
                # 描述属性（可能包含换行，用引号包围）
                frontmatter_lines.append(f"description: \"{value}\"")
            else:
                # 其他属性直接添加
                frontmatter_lines.append(f"{key}: {value}")
        
        frontmatter_lines.append("---")
        return '\n'.join(frontmatter_lines)
    
    def _filter_meta_lines(self, lines, meta_properties):
        """过滤掉原始内容中的 meta 属性行"""
        if not meta_properties:
            return lines
        
        # 获取所有 meta 属性的行号
        meta_line_numbers = {prop.line_number for prop in meta_properties}
        
        # 过滤掉这些行，同时跳过文件开头的空行
        filtered_lines = []
        content_started = False
        
        for i, line in enumerate(lines, 1):
            if i in meta_line_numbers:
                continue  # 跳过 meta 属性行
            
            # 跳过文件开头的空行（在 meta 属性之后）
            if not content_started and not line.strip():
                continue
            
            content_started = True
            filtered_lines.append(line)
        
        return filtered_lines