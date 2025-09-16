#!/usr/bin/env python
"""
Meta 属性功能测试
测试 Logseq meta 属性转换为 Obsidian YAML frontmatter 的功能
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


class TestMetaProperties(unittest.TestCase):
    """Meta 属性转换测试"""
    
    def setUp(self):
        self.parser = LogseqParser()
        self.formatter = ObsidianFormatter()
        
    def test_meta_property_parsing(self):
        """测试 meta 属性解析"""
        sample_path = Path(__file__).parent.parent / "examples" / "logseq_samples" / "meta_sample.md"
        
        # 解析文件
        result = self.parser.parse_file(sample_path)
        
        # 验证解析结果
        self.assertIn('meta_properties', result)
        meta_props = result['meta_properties']
        
        # 验证找到了正确数量的 meta 属性
        self.assertEqual(len(meta_props), 9)
        
        # 验证特定的 meta 属性
        prop_dict = {prop.key: prop.value for prop in meta_props}
        
        self.assertEqual(prop_dict['title'], '人工智能研究笔记')
        self.assertEqual(prop_dict['alias'], 'AI研究, 机器学习笔记')
        self.assertEqual(prop_dict['type'], '研究笔记')
        self.assertEqual(prop_dict['author'], '研究员')
        self.assertEqual(prop_dict['status'], '进行中')
        self.assertEqual(prop_dict['priority'], '高')
        
        # 验证标签解析（包含页面链接）
        self.assertIn('[[人工智能]]', prop_dict['tags'])
        self.assertIn('[[机器学习]]', prop_dict['tags'])
        self.assertIn('[[深度学习]]', prop_dict['tags'])
        
    def test_meta_property_conversion(self):
        """测试 meta 属性转换为 YAML frontmatter"""
        sample_path = Path(__file__).parent.parent / "examples" / "logseq_samples" / "meta_sample.md"
        
        # 解析并转换
        result = self.parser.parse_file(sample_path)
        obsidian_content = self.formatter.format_content(result)
        
        # 验证生成了 YAML frontmatter
        self.assertTrue(obsidian_content.startswith('---'))
        
        lines = obsidian_content.split('\n')
        
        # 找到 frontmatter 结束位置
        frontmatter_end = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                frontmatter_end = i
                break
        
        self.assertGreater(frontmatter_end, 0, "应该找到 frontmatter 结束标记")
        
        # 验证 frontmatter 内容
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter_content = '\n'.join(frontmatter_lines)
        
        # 验证关键字段
        self.assertIn('title: 人工智能研究笔记', frontmatter_content)
        self.assertIn('aliases:', frontmatter_content)
        self.assertIn('- AI研究', frontmatter_content)
        self.assertIn('- 机器学习笔记', frontmatter_content)
        self.assertIn('tags:', frontmatter_content)
        self.assertIn('- 人工智能', frontmatter_content)
        self.assertIn('- 机器学习', frontmatter_content)
        self.assertIn('- 深度学习', frontmatter_content)
        self.assertIn('type: 研究笔记', frontmatter_content)
        self.assertIn('author: 研究员', frontmatter_content)
        self.assertIn('created: 2024-01-15', frontmatter_content)
        self.assertIn('status: 进行中', frontmatter_content)
        self.assertIn('priority: 高', frontmatter_content)
        self.assertIn('description:', frontmatter_content)
        
    def test_meta_property_filtering(self):
        """测试 meta 属性行从内容中被正确过滤"""
        sample_path = Path(__file__).parent.parent / "examples" / "logseq_samples" / "meta_sample.md"
        
        # 解析并转换
        result = self.parser.parse_file(sample_path)
        obsidian_content = self.formatter.format_content(result)
        
        # 确保原始的 meta 属性行不出现在转换后的内容中
        lines = obsidian_content.split('\n')
        content_lines = []
        in_frontmatter = False
        frontmatter_closed = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    frontmatter_closed = True
                continue
            if frontmatter_closed:
                content_lines.append(line)
        
        content = '\n'.join(content_lines)
        
        # 验证原始 meta 属性格式不存在于内容中
        self.assertNotIn('title::', content)
        self.assertNotIn('alias::', content)
        self.assertNotIn('tags::', content)
        self.assertNotIn('type::', content)
        self.assertNotIn('author::', content)
        self.assertNotIn('created-at::', content)
        self.assertNotIn('status::', content)
        self.assertNotIn('priority::', content)
        self.assertNotIn('description::', content)
        
    def test_statistics_include_meta_properties(self):
        """测试统计信息包含 meta 属性计数"""
        sample_path = Path(__file__).parent.parent / "examples" / "logseq_samples" / "meta_sample.md"
        
        result = self.parser.parse_file(sample_path)
        stats = self.parser.get_statistics(result)
        
        self.assertIn('meta_properties_count', stats)
        self.assertEqual(stats['meta_properties_count'], 9)
        
    def test_files_without_meta_properties(self):
        """测试没有 meta 属性的文件不受影响"""
        sample_path = Path(__file__).parent.parent / "examples" / "logseq_samples" / "sample1.md"
        
        result = self.parser.parse_file(sample_path)
        stats = self.parser.get_statistics(result)
        
        # 没有 meta 属性
        self.assertEqual(stats['meta_properties_count'], 0)
        
        # 转换后不应有 frontmatter
        obsidian_content = self.formatter.format_content(result)
        self.assertFalse(obsidian_content.startswith('---'))


if __name__ == '__main__':
    print("开始 Meta 属性功能测试")
    print("=" * 50)
    
    unittest.main(verbosity=2)