#!/usr/bin/env python
"""
验证 alias meta 属性页面链接修复测试
专门测试修复后的 alias:: [[想法]] [[观点]] 格式
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


class TestAliasPageLinksFix(unittest.TestCase):
    """验证 alias meta 属性页面链接修复"""
    
    def setUp(self):
        self.parser = LogseqParser()
        self.formatter = ObsidianFormatter()
        
    def test_original_problem_case(self):
        """测试原始问题案例：alias:: [[想法]] [[观点]]"""
        content = "alias:: [[想法]] [[观点]]"
        
        # 解析
        parsed = self.parser.parse_content(content)
        
        # 转换
        formatted = self.formatter.format_content(parsed)
        
        # 验证结果
        self.assertIn('---', formatted)
        self.assertIn('aliases:', formatted)
        self.assertIn('- 想法', formatted)
        self.assertIn('- 观点', formatted)
        
        # 验证不包含非法格式 [[]]
        self.assertNotIn('[[想法]]', formatted)
        self.assertNotIn('[[观点]]', formatted)
        
        print("✅ 原始问题修复验证:")
        print(f"输入: {content}")
        print(f"输出:\n{formatted}")
        
    def test_yaml_frontmatter_validity(self):
        """测试生成的 YAML frontmatter 有效性"""
        content = "alias:: [[想法]] [[观点]]"
        parsed = self.parser.parse_content(content)
        formatted = self.formatter.format_content(parsed)
        
        # 验证基本格式正确
        lines = formatted.split('\n')
        self.assertEqual(lines[0], '---')
        self.assertEqual(lines[1], 'aliases:')
        self.assertTrue(lines[2].startswith('  - '))
        self.assertTrue(lines[3].startswith('  - '))
        
        # 验证包含正确的别名
        self.assertIn('想法', formatted)
        self.assertIn('观点', formatted)
        
        print("✅ YAML frontmatter 格式验证通过")
            
    def test_multiple_page_links_with_spaces(self):
        """测试多个页面链接（空格分隔）"""
        content = "alias:: [[想法]] [[观点]] [[评论]]"
        
        parsed = self.parser.parse_content(content)
        formatted = self.formatter.format_content(parsed)
        
        self.assertIn('- 想法', formatted)
        self.assertIn('- 观点', formatted)
        self.assertIn('- 评论', formatted)
        
    def test_mixed_page_links_and_text(self):
        """测试混合页面链接和普通文本"""
        content = "alias:: [[想法]] [[观点]], 其他内容"
        
        parsed = self.parser.parse_content(content)
        formatted = self.formatter.format_content(parsed)
        
        # 应该提取页面链接内容
        self.assertIn('- 想法', formatted)
        self.assertIn('- 观点', formatted)
        
        print("✅ 混合格式处理:")
        print(f"输入: {content}")
        print(f"输出:\n{formatted}")


if __name__ == '__main__':
    print("验证 alias meta 属性页面链接修复")
    print("=" * 60)
    
    unittest.main(verbosity=2)