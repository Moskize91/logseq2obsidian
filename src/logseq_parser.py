"""
Logseq 解析器
负责解析 Logseq markdown 文件，提取关键元素
"""

import re
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


class LogseqParser:
    """Logseq 文件解析器"""
    
    def __init__(self):
        # 正则表达式模式
        self.page_link_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        self.block_ref_pattern = re.compile(r'\(\(([^)]+)\)\)')
        self.block_id_pattern = re.compile(r'id:: ([a-f0-9-]+)')
        self.asset_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        
    def parse_file(self, file_path: Path) -> Dict:
        """解析单个 Logseq 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_content(content, file_path.name)
            
        except Exception as e:
            raise Exception(f"解析文件 {file_path} 时出错: {e}")
    
    def parse_content(self, content: str, filename: str = "") -> Dict:
        """解析 Logseq 文件内容"""
        lines = content.split('\n')
        
        blocks = []
        references = []
        
        for line_num, line in enumerate(lines, 1):
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
    
    def get_statistics(self, parsed_data: Dict) -> Dict:
        """获取解析统计信息"""
        return {
            'total_blocks': len(parsed_data['blocks']),
            'page_links_count': len(parsed_data['page_links']),
            'block_refs_count': len(parsed_data['block_refs']),
            'assets_count': len(parsed_data['assets']),
            'blocks_with_id': len([b for b in parsed_data['blocks'] if b.block_id])
        }