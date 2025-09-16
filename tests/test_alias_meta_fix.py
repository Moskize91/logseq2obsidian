#!/usr/bin/env python
"""
测试 alias meta 属性的多页面链接处理
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


class TestAliasMetaProperty(unittest.TestCase):
    """测试 alias meta 属性处理"""
    
    def setUp(self):
        self.parser = LogseqParser()
        self.formatter = ObsidianFormatter()
        
    def test_alias_with_page_links(self):
        """测试包含页面链接的 alias 属性"""
        content = "alias:: [[想法]] [[观点]]\n\n这是一些内容。"
        
        # 解析
        parsed = self.parser.parse_content(content)
        
        # 验证解析出的 meta 属性
        self.assertEqual(len(parsed['meta_properties']), 1)
        meta_prop = parsed['meta_properties'][0]
        self.assertEqual(meta_prop.key, 'alias')
        self.assertEqual(meta_prop.value, '[[想法]] [[观点]]')
        
        # 转换
        formatted = self.formatter.format_content(parsed)
        
        # 验证生成的 frontmatter
        expected_frontmatter = """---
aliases:
  - 想法
  - 观点
---

这是一些内容。"""
        
        self.assertEqual(formatted.strip(), expected_frontmatter.strip())
        
    def test_alias_with_comma_separated(self):
        """测试逗号分隔的 alias 属性"""
        content = "alias:: 想法, 观点\n\n这是一些内容。"
        
        # 解析
        parsed = self.parser.parse_content(content)
        
        # 转换
        formatted = self.formatter.format_content(parsed)
        
        # 验证生成的 frontmatter
        expected_frontmatter = """---
aliases:
  - 想法
  - 观点
---

这是一些内容。"""
        
        self.assertEqual(formatted.strip(), expected_frontmatter.strip())
        
    def test_alias_mixed_format(self):
        """测试混合格式的 alias 属性"""
        content = "alias:: [[想法]], 观点, [[评论]]\n\n这是一些内容。"
        
        # 解析
        parsed = self.parser.parse_content(content)
        
        # 转换
        formatted = self.formatter.format_content(parsed)
        
        # 验证生成的 frontmatter 
        lines = formatted.strip().split('\n')
        
        # 检查是否有正确的 frontmatter 结构
        self.assertEqual(lines[0], '---')
        self.assertEqual(lines[1], 'aliases:')
        self.assertTrue(any('想法' in line for line in lines[2:5]))
        self.assertTrue(any('观点' in line for line in lines[2:5]) or any('评论' in line for line in lines[2:5]))
        
    def test_empty_alias(self):
        """测试空的 alias 属性"""
        content = "alias:: \n\n这是一些内容。"
        
        # 解析
        parsed = self.parser.parse_content(content)
        
        # 转换
        formatted = self.formatter.format_content(parsed)
        
        # 应该没有 frontmatter（因为 alias 为空）
        self.assertNotIn('aliases:', formatted)
        self.assertIn('这是一些内容。', formatted)


if __name__ == '__main__':
    print("开始 alias meta 属性测试")
    print("=" * 50)
    
    unittest.main(verbosity=2)