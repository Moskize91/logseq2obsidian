#!/usr/bin/env python3
"""
全面测试分类标签检测逻辑
合并了多个根目录测试文件的内容
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter


class TestCategoryDetectionComprehensive(unittest.TestCase):
    """全面测试分类标签检测"""
    
    def setUp(self):
        self.formatter = ObsidianFormatter(category_tag='wiki', category_folder='Wiki')
    
    def test_specific_cases_ipfs_crdt(self):
        """测试IPFS和CRDT具体案例（来自debug_specific_cases.py）"""
        
        # 测试 IPFS.md 的情况
        ipfs_content = """- > 星际文件系统 #wiki #区块链
- 使用 [[Kademlia]] 的分布式公开文件系统，存储文件全量。有点类似 [[BitTorrent]]。"""
        
        ipfs_data = {
            'content': ipfs_content,
            'meta_properties': []
        }
        
        category = self.formatter.detect_category_folder(ipfs_data)
        self.assertEqual(category, 'Wiki', "IPFS文件应该被归类到Wiki文件夹")
        
        # 测试 crdt.md 的情况  
        crdt_content = """- #算法 #wiki
- CRDT 首先要解决排序问题：让不同客户端的操作经过无中心的广播后，在所有端能够收敛到相同的顺序，从而保证执行这些操作后能够到达一样的结果."""
        
        crdt_data = {
            'content': crdt_content,
            'meta_properties': []
        }
        
        category = self.formatter.detect_category_folder(crdt_data)
        self.assertEqual(category, 'Wiki', "CRDT文件应该被归类到Wiki文件夹")
    
    def test_various_tag_formats(self):
        """测试各种标签格式（来自test_various_tags.py）"""
        
        test_cases = [
            {
                'name': '引用块中的标签',
                'content': '- > #wiki  齐泽克的短路\n- 其他内容',
                'expected': 'Wiki'
            },
            {
                'name': '直接标签',
                'content': '- #wiki 内容\n- 其他内容',
                'expected': 'Wiki'
            },
            {
                'name': '标签在行首（无列表标记）',
                'content': '#wiki 内容\n- 其他内容',
                'expected': 'Wiki'
            },
            {
                'name': '标签不在第一行',
                'content': '- 其他内容\n- #wiki 内容',
                'expected': ''
            },
            {
                'name': '有空行的情况',
                'content': '\n\n- #wiki 内容\n- 其他内容',
                'expected': 'Wiki'
            },
            {
                'name': '有meta属性的情况',
                'content': 'alias:: 别名\ntitle:: 标题\n\n- #wiki 内容\n- 其他内容',
                'expected': 'Wiki'
            },
            {
                'name': '多个标签',
                'content': '- #算法 #wiki #计算机科学\n- 内容',
                'expected': 'Wiki'
            },
            {
                'name': '非匹配标签',
                'content': '- #算法 #computer-science\n- 内容',
                'expected': ''
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case['name']):
                data = {
                    'content': case['content'],
                    'meta_properties': []
                }
                
                # 解析meta属性
                if 'alias::' in case['content'] or 'title::' in case['content']:
                    lines = case['content'].split('\n')
                    meta_properties = []
                    for line in lines:
                        if '::' in line and not line.strip().startswith('-'):
                            key, value = line.split('::', 1)
                            meta_properties.append({
                                'key': key.strip(),
                                'value': value.strip()
                            })
                    data['meta_properties'] = meta_properties
                
                category = self.formatter.detect_category_folder(data)
                self.assertEqual(category, case['expected'], 
                               f"案例 '{case['name']}' 检测结果错误")
    
    def test_quote_block_tag_detection(self):
        """测试引用块中的标签检测（来自test_category_detection.py）"""
        
        test_data = {
            'content': '''- > #wiki  齐泽克的短路
- ((61ff4d79-6753-42ba-aa80-2f01d99b7a9b))
-
- 齐泽克用短路解释哪些想法会被压抑。''',
            'meta_properties': []
        }
        
        category = self.formatter.detect_category_folder(test_data)
        self.assertEqual(category, 'Wiki', "引用块中的#wiki标签应该被正确检测")
    
    def test_bullet_removal_logic(self):
        """测试列表标记移除逻辑"""
        
        test_cases = [
            ('- > #wiki 内容', '#wiki 内容'),
            ('- #wiki 内容', '#wiki 内容'), 
            ('* > #wiki 内容', '#wiki 内容'),
            ('* #wiki 内容', '#wiki 内容'),
            ('#wiki 内容', '#wiki 内容'),
            ('  - #wiki 内容', '#wiki 内容'),
            ('- ', ''),
            ('-', ''),
        ]
        
        for input_line, expected in test_cases:
            with self.subTest(input_line=input_line):
                result = self.formatter._remove_logseq_bullets(input_line)
                self.assertEqual(result, expected, 
                               f"'{input_line}' 应该转换为 '{expected}'")


if __name__ == '__main__':
    unittest.main()