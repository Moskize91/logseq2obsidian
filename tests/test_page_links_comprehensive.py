#!/usr/bin/env python3
"""
全面测试页面链接处理逻辑
合并了页面链接相关的测试文件
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter


class TestPageLinksProcessing(unittest.TestCase):
    """测试页面链接处理功能"""

    def setUp(self):
        self.formatter = ObsidianFormatter()

    def test_basic_page_links(self):
        """测试基本页面链接转换"""

        test_cases = [
            ("[[方济各会]]", "[[方济各会]]", "中文页面链接"),
            ("[[佛教]]", "[[佛教]]", "中文单字页面链接"),
            ("[[Buddhism]]", "[[Buddhism]]", "英文页面链接"),
            (
                "[[Traditional Chinese Medicine]]",
                "[[Traditional Chinese Medicine]]",
                "英文词组页面链接",
            ),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_special_characters_in_page_links(self):
        """测试包含特殊字符的页面链接"""

        test_cases = [
            ("[[React.js]]", "[[React.js]]", "带点号的页面链接"),
            ("[[C++]]", "[[C++]]", "带加号的页面链接"),
            ("[[Web3.0]]", "[[Web3.0]]", "带数字的页面链接"),
            ("[[Test-Case]]", "[[Test-Case]]", "带连字符的页面链接"),
            ("[[Test_Case]]", "[[Test_Case]]", "带下划线的页面链接"),
            ("[[Test Space]]", "[[Test Space]]", "带空格的页面链接"),
            ("[[50%]]", "[[50%]]", "带百分号的页面链接"),
            ("[[2023年]]", "[[2023年]]", "带年份的页面链接"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_mixed_language_page_links(self):
        """测试中英混合的页面链接"""

        test_cases = [
            ("[[计算机科学Computer Science]]", "[[计算机科学Computer Science]]", "中英混合页面链接"),
            ("[[AI人工智能]]", "[[AI人工智能]]", "英文缩写+中文"),
            (
                "在 [[React.js]] 中使用 [[TypeScript]] 开发",
                "在 [[React.js]] 中使用 [[TypeScript]] 开发",
                "技术名词页面链接",
            ),
            ("学习 [[Python]] 和 [[机器学习]] 的基础", "学习 [[Python]] 和 [[机器学习]] 的基础", "技术+概念混合"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_page_links_in_context(self):
        """测试文本中的页面链接"""

        test_cases = [
            ("这里有个链接 [[测试页面]] 在文本中", "这里有个链接 [[测试页面]] 在文本中", "文本中的页面链接"),
            ("多个链接：[[页面1]] 和 [[页面2]]", "多个链接：[[页面1]] 和 [[页面2]]", "一行中的多个页面链接"),
            ("- [[任务1]] 这是一个任务", "- [[任务1]] 这是一个任务", "列表项中的页面链接"),
            ("前面文字[[页面]]后面文字", "前面文字[[页面]]后面文字", "紧贴文字的页面链接"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_technical_terms_page_links(self):
        """测试技术术语页面链接"""

        test_cases = [
            ("[[IPv4]]", "[[IPv4]]", "技术术语带数字"),
            ("[[HTTP/2]]", "[[HTTP/2]]", "带斜杠的技术术语"),
            ("[[REST API]]", "[[REST API]]", "技术缩写"),
            ("[[编程语言]]", "[[编程语言]]", "概念词汇页面链接"),
            ("[[机器学习]]", "[[机器学习]]", "技术概念页面链接"),
            ("[[算法]]", "[[算法]]", "学术概念页面链接"),
            ("[[数据结构]]", "[[数据结构]]", "计算机科学概念"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_special_symbols_page_links(self):
        """测试带有特殊符号的页面链接"""

        test_cases = [
            ("[[#标签页面]]", "[[#标签页面]]", "带井号的页面链接"),
            ("[[@提及页面]]", "[[@提及页面]]", "带@符号的页面链接"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_edge_cases_page_links(self):
        """测试边缘情况的页面链接"""

        test_cases = [
            ("[[]]", "[[]]", "空页面链接"),
            ("[[  ]]", "[[  ]]", "只有空格的页面链接"),
            ("[[这是一个非常长的页面名称用于测试边缘情况]]", "[[这是一个非常长的页面名称用于测试边缘情况]]", "长页面名称"),
        ]

        for input_text, expected_output, description in test_cases:
            with self.subTest(description=description):
                result = self.formatter._convert_page_links(input_text)
                self.assertEqual(result, expected_output, f"失败: {description}")

    def test_nested_page_links(self):
        """测试嵌套页面链接情况"""

        # 注意：嵌套链接是一个特殊情况，可能需要特别处理
        test_case = "参考 [[关于[[嵌套]]的讨论]]"
        expected = "参考 [[关于[[嵌套]]的讨论]]"

        result = self.formatter._convert_page_links(test_case)
        self.assertEqual(result, expected, "嵌套链接处理失败")

    def test_page_links_with_method_existence(self):
        """测试页面链接方法存在性"""

        # 确认 _convert_page_links 方法存在
        self.assertTrue(
            hasattr(self.formatter, "_convert_page_links"),
            "ObsidianFormatter 应该有 _convert_page_links 方法",
        )

        # 确认方法可调用
        self.assertTrue(
            callable(getattr(self.formatter, "_convert_page_links")),
            "_convert_page_links 应该是可调用的方法",
        )


if __name__ == "__main__":
    unittest.main()
