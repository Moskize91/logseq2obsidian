"""
Logseq 解析器
负责解析 Logseq markdown 文件，提取关键元素
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LogseqBlock:
    """Logseq 块数据结构"""
    content: str
    block_id: Optional[str] = None
    level: int = 0  # 缩进层级
    line_number: int = 0


@dataclass
class LogseqReference:
    """Logseq 引用数据结构"""
    type: str  # 'page_link', 'block_ref', 'asset'
    target: str
    display_text: Optional[str] = None
    position: Tuple[int, int] = (0, 0)  # (start, end)


@dataclass
class LogseqMetaProperty:
    """Logseq meta 属性数据结构"""
    key: str
    value: str
    raw_value: str  # 保留原始值（可能包含链接等）
    line_number: int


class LogseqParser:
    """Logseq 文件解析器"""
    
    def __init__(self):
        # 正则表达式模式
        self.page_link_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        self.block_ref_pattern = re.compile(r'\(\(([^)]+)\)\)')
        self.block_id_pattern = re.compile(r'id:: ([a-f0-9-]+)')
        self.asset_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        # Meta 属性模式（支持前面有列表标记）
        self.meta_pattern = re.compile(r'^(?:[-*]\s+)?(\w+(?:-\w+)*)::\s*(.+)$')
        
    def _read_file_robust(self, file_path: Path) -> Tuple[str, bool]:
        """
        健壮地读取文件，处理UTF-8编码错误
        
        Returns:
            Tuple[str, bool]: (文件内容, 是否有编码错误)
        """
        # 首先尝试正常读取
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, False
        except UnicodeDecodeError:
            pass
        
        # 如果UTF-8失败，尝试使用 'replace' 错误处理
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                print(f"⚠️  文件 {file_path.name} 含有无效UTF-8字符，已使用替换字符处理")
                return content, True
        except OSError:
            pass
        
        # 如果还是失败，尝试 'ignore' 错误处理
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                print(f"⚠️  文件 {file_path.name} 含有无效UTF-8字符，已忽略错误字符")
                return content, True
        except OSError:
            pass
        
        # 最后尝试二进制读取并手动处理
        try:
            with open(file_path, 'rb') as f:
                raw_bytes = f.read()
            
            # 尝试解码，如果遇到错误就替换
            content = raw_bytes.decode('utf-8', errors='replace')
            print(f"⚠️  文件 {file_path.name} 使用二进制读取模式处理编码错误")
            return content, True
            
        except OSError as e:
            # 如果所有方法都失败，返回错误信息
            error_content = f"# 文件读取失败\n\n无法读取文件 {file_path.name}，错误：{e}\n"
            print(f"❌ 无法读取文件 {file_path.name}: {e}")
            return error_content, True
        
    def parse_file(self, file_path: Path) -> Dict:
        """解析单个 Logseq 文件"""
        try:
            content, has_encoding_errors = self._read_file_robust(file_path)
            
            result = self.parse_content(content, file_path.name)
            
            # 在结果中添加编码错误信息
            result['has_encoding_errors'] = has_encoding_errors
            
            return result
            
        except Exception as e:
            raise ValueError(f"解析文件 {file_path} 时出错: {e}") from e
    
    def parse_content(self, content: str, filename: str = "") -> Dict:
        """解析 Logseq 文件内容"""
        lines = content.split('\n')
        
        blocks = []
        references = []
        meta_properties = []
        
        # First pass: extract meta properties from the beginning of the file
        # Meta properties can be interspersed with other lines (like tags) at the beginning
        meta_line_count = 0
        
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                meta_line_count = i + 1
                continue
                
            # Check if this is a meta property
            if self.meta_pattern.match(line):
                meta_prop = self._extract_meta_property(line, i + 1)
                if meta_prop:
                    meta_properties.append(meta_prop)
                meta_line_count = i + 1
                continue
            
            # Check if this looks like a simple tag line or bullet point
            # Allow lines like "- #tag" to continue scanning for meta properties
            if re.match(r'^[-*]\s+#\w+\s*$', line) or stripped_line == '-':
                meta_line_count = i + 1
                continue
                
            # If we get here, we've hit actual content, stop scanning for meta properties
            break
        
        # Second pass: parse blocks and references starting after meta properties
        for line_num in range(meta_line_count + 1, len(lines) + 1):
            if line_num > len(lines):
                break
            line = lines[line_num - 1]
            
            # 解析块
            block = self._parse_line_as_block(line, line_num)
            if block:
                blocks.append(block)
            
            # 解析引用
            line_refs = self._extract_references(line, line_num)
            references.extend(line_refs)
        
        return {
            'filename': filename,
            'content': content,
            'blocks': blocks,
            'references': references,
            'meta_properties': meta_properties,
            'page_links': [ref for ref in references if ref.type == 'page_link'],
            'block_refs': [ref for ref in references if ref.type == 'block_ref'],
            'assets': [ref for ref in references if ref.type == 'asset']
        }
    
    def _parse_line_as_block(self, line: str, line_num: int) -> Optional[LogseqBlock]:
        """解析单行为块"""
        if not line.strip():
            return None
        
        # 计算缩进层级
        level = 0
        for char in line:
            if char in ' \t':
                level += 1
            else:
                break
        
        # 检查是否有块 ID
        block_id_match = self.block_id_pattern.search(line)
        block_id = block_id_match.group(1) if block_id_match else None
        
        return LogseqBlock(
            content=line.strip(),
            block_id=block_id,
            level=level,
            line_number=line_num
        )
    
    def _extract_references(self, line: str, line_num: int) -> List[LogseqReference]:
        """从行中提取所有引用"""
        references = []
        
        # 页面链接 [[]]
        for match in self.page_link_pattern.finditer(line):
            references.append(LogseqReference(
                type='page_link',
                target=match.group(1),
                position=(match.start(), match.end())
            ))
        
        # 块引用 (())
        for match in self.block_ref_pattern.finditer(line):
            references.append(LogseqReference(
                type='block_ref',
                target=match.group(1),
                position=(match.start(), match.end())
            ))
        
        # 资源文件 ![](url)
        for match in self.asset_pattern.finditer(line):
            references.append(LogseqReference(
                type='asset',
                target=match.group(2),
                display_text=match.group(1),
                position=(match.start(), match.end())
            ))
        
        return references
    
    def _extract_meta_property(self, line: str, line_num: int) -> Optional[LogseqMetaProperty]:
        """从行中提取 meta 属性"""
        match = self.meta_pattern.match(line)  # 使用原始行而不是 strip()
        if match:
            key = match.group(1)
            raw_value = match.group(2)
            
            # 清理值：移除多余的空格，但保留原始格式用于引用解析
            value = raw_value.strip()
            
            return LogseqMetaProperty(
                key=key,
                value=value,
                raw_value=raw_value,
                line_number=line_num
            )
        return None
    
    def get_statistics(self, parsed_data: Dict) -> Dict:
        """获取解析统计信息"""
        return {
            'total_blocks': len(parsed_data['blocks']),
            'meta_properties_count': len(parsed_data.get('meta_properties', [])),
            'page_links_count': len(parsed_data['page_links']),
            'block_refs_count': len(parsed_data['block_refs']),
            'assets_count': len(parsed_data['assets']),
            'blocks_with_id': len([b for b in parsed_data['blocks'] if b.block_id])
        }