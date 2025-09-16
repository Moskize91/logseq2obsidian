#!/usr/bin/env python
"""
测试分类标签功能
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


class TestCategoryTagFeature(unittest.TestCase):
    """测试分类标签功能"""
    
    def setUp(self):
        self.parser = LogseqParser()
        
    def test_wiki_tag_detection_simple(self):
        """测试简单的 wiki 标签检测"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "#wiki\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_tag_with_meta_properties(self):
        """测试带有 meta 属性的 wiki 标签检测"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = """title:: Wiki 文章
author:: 测试

#wiki

这是一个 wiki 文章。"""
        
        parsed = self.parser.parse_content(content)
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_tag_not_at_start(self):
        """测试 wiki 标签不在开头的情况"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = """这是一些内容。

#wiki 标签在中间。

更多内容。"""
        
        parsed = self.parser.parse_content(content)
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "")  # 应该返回空，表示不归类
        
    def test_no_category_config(self):
        """测试没有配置分类功能"""
        formatter = ObsidianFormatter()  # 没有分类配置
        
        content = "#wiki\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "")  # 应该返回空
        
    def test_multiple_tags_wiki_first(self):
        """测试多个标签，wiki 在第一位"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "#wiki #知识库 #重要\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_with_spaces_around(self):
        """测试 wiki 标签前后有空格"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "  #wiki  \n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_with_logseq_bullet(self):
        """测试带有 Logseq 列表标记的 wiki 标签"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "- #wiki 法国马克思主义者\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_with_indented_bullet(self):
        """测试带有缩进的 Logseq 列表标记"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "  - #wiki 内容\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_wiki_with_asterisk_bullet(self):
        """测试带有星号列表标记的 wiki 标签"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "* #wiki 内容\n\n这是一个 wiki 文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "wiki")
        
    def test_bullet_without_wiki_tag(self):
        """测试列表标记但没有 wiki 标签在开头"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "- 一些内容 #wiki\n\n这是一个普通文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "")  # 标签不在开头，不应该归类
        
    def test_custom_category_tag(self):
        """测试自定义分类标签"""
        formatter = ObsidianFormatter(category_tag="知识库", category_folder="knowledge")
        
        content = "#知识库\n\n这是一个知识库文章。"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "knowledge")
        
    def test_empty_content(self):
        """测试空内容"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = ""
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "")
        
    def test_only_meta_properties(self):
        """测试只有 meta 属性没有实际内容"""
        formatter = ObsidianFormatter(category_tag="wiki", category_folder="wiki")
        
        content = "title:: 测试\nauthor:: 用户"
        parsed = self.parser.parse_content(content)
        
        folder = formatter.detect_category_folder(parsed)
        self.assertEqual(folder, "")


if __name__ == '__main__':
    print("开始分类标签功能测试")
    print("=" * 50)
    
    unittest.main(verbosity=2)