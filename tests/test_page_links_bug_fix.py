#!/usr/bin/env python3
"""
页面链接转换的单元测试
测试修复后的页面链接处理逻辑，确保不再错误转换为标签
"""

import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from obsidian_formatter import ObsidianFormatter


class TestPageLinksConversion(unittest.TestCase):
    """页面链接转换测试类"""
    
    def setUp(self):
        """设置测试环境"""
        self.formatter = ObsidianFormatter()
    
    def test_basic_page_links(self):
        """测试基本页面链接转换"""
        test_cases = [
            ("[[方济各会]]", "[[方济各会]]"),
            ("[[佛教]]", "[[佛教]]"),
            ("[[Buddhism]]", "[[Buddhism]]"),
            ("[[Traditional Chinese Medicine]]", "[[Traditional Chinese Medicine]]"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected)
    
    def test_special_characters_in_page_links(self):
        """测试包含特殊字符的页面链接"""
        test_cases = [
            ("[[React.js]]", "[[React.js]]"),
            ("[[C++]]", "[[C++]]"),
            ("[[Web3.0]]", "[[Web3.0]]"),
            ("[[Test-Case]]", "[[Test-Case]]"),
            ("[[Test_Case]]", "[[Test_Case]]"),
            ("[[Test Space]]", "[[Test Space]]"),
            ("[[HTTP/2]]", "[[HTTP/2]]"),  # 这个之前失败，现在应该通过
            ("[[50%]]", "[[50%]]"),
            ("[[#标签页面]]", "[[#标签页面]]"),
            ("[[@提及页面]]", "[[@提及页面]]"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected)
    
    def test_multiple_page_links_in_text(self):
        """测试文本中的多个页面链接"""
        test_cases = [
            ("这里有个链接 [[测试页面]] 在文本中", "这里有个链接 [[测试页面]] 在文本中"),
            ("多个链接：[[页面1]] 和 [[页面2]]", "多个链接：[[页面1]] 和 [[页面2]]"),
            ("- [[任务1]] 这是一个任务", "- [[任务1]] 这是一个任务"),
            ("在 [[React.js]] 中使用 [[TypeScript]] 开发", "在 [[React.js]] 中使用 [[TypeScript]] 开发"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected)
    
    def test_concept_words_remain_as_page_links(self):
        """测试概念词汇保持为页面链接格式，不转换为标签"""
        # 这些是之前被错误转换为标签的概念词汇
        concept_words = [
            "[[编程语言]]",
            "[[机器学习]]", 
            "[[算法]]",
            "[[数据结构]]",
            "[[人工智能]]",
            "[[深度学习]]",
            "[[自然语言处理]]",
            "[[计算机视觉]]",
        ]
        
        for concept in concept_words:
            with self.subTest(concept=concept):
                result = self.formatter._convert_page_links(concept)
                # 确保不转换为标签格式
                self.assertNotIn('#', result)
                # 确保保持页面链接格式
                self.assertEqual(result, concept)
    
    def test_edge_cases(self):
        """测试边缘情况"""
        test_cases = [
            ("[[]]", "[[]]"),  # 空链接
            ("[[  ]]", "[[  ]]"),  # 只有空格
            ("前面文字[[页面]]后面文字", "前面文字[[页面]]后面文字"),  # 紧贴文字
            ("[[这是一个非常长的页面名称用于测试边缘情况]]", "[[这是一个非常长的页面名称用于测试边缘情况]]"),
            ("[[IPv4]]", "[[IPv4]]"),
            ("[[REST API]]", "[[REST API]]"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected)
    
    def test_no_conversion_to_tags(self):
        """重点测试：确保页面链接不被转换为标签"""
        # 这些是原始 bug 报告中的具体案例
        original_bug_cases = [
            "[[方济各会]]",
            "[[佛教]]", 
            "[[分裂]]",
            "[[宗教]]",
        ]
        
        for case in original_bug_cases:
            with self.subTest(case=case):
                result = self.formatter._convert_page_links(case)
                # 最重要的断言：确保结果不包含 # 标签格式
                self.assertNotIn('#', result, f"页面链接 {case} 被错误转换为标签格式")
                # 确保保持原有的双链格式
                self.assertTrue(result.startswith('[[') and result.endswith(']]'))
                # 确保内容不变（除了可能的 URL 解码）
                self.assertEqual(result, case)


class TestBugFix(unittest.TestCase):
    """专门测试原始 bug 修复"""
    
    def setUp(self):
        """设置测试环境"""
        self.formatter = ObsidianFormatter()
    
    def test_original_bug_scenario(self):
        """测试原始 bug 场景：方济各会与佛教分裂文件中的页面链接"""
        # 模拟原始文件中的内容
        test_content = """
- 这里讨论了 [[方济各会]] 的历史
- 以及与 [[佛教]] 的关系  
- 涉及到宗教 [[分裂]] 的问题
- 还有 [[宗教改革]] 的影响
        """.strip()
        
        result = self.formatter._convert_page_links(test_content)
        
        # 确保没有任何页面链接被转换为标签
        self.assertNotIn('#方济各会', result)
        self.assertNotIn('#佛教', result)
        self.assertNotIn('#分裂', result)
        self.assertNotIn('#宗教改革', result)
        
        # 确保页面链接格式保持不变
        self.assertIn('[[方济各会]]', result)
        self.assertIn('[[佛教]]', result)
        self.assertIn('[[分裂]]', result)
        self.assertIn('[[宗教改革]]', result)


if __name__ == '__main__':
    unittest.main(verbosity=2)