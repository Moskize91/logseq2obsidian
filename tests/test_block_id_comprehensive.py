#!/usr/bin/env python3
"""
全面测试块ID处理逻辑
合并了块ID相关的测试文件
"""

import re
import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter


class TestBlockIdProcessing(unittest.TestCase):
    """测试块ID处理功能"""

    def setUp(self):
        self.formatter = ObsidianFormatter()

    def count_block_ids(self, text):
        """计算文本中的块ID数量（只计算行尾的块ID，不包括引用）"""
        lines = text.split("\n")
        return len([line for line in lines if re.search(r"\^block\d+$", line.strip())])

    def test_unreferenced_block_id_removal(self):
        """测试无引用的块ID会被删除"""

        # 创建测试数据：有块ID但没有引用
        test_data = {
            "content": """这是一段文字
id:: abc123-def456
另一段文字
id:: xyz789-uvw012""",
            "meta_properties": [],
        }

        # 第一阶段：收集被引用的 UUID
        self.formatter.collect_referenced_uuids(test_data)

        # 第二阶段：只为被引用的块分配 ID
        self.formatter.collect_block_mappings("test1.md", test_data)

        # 格式化内容
        result = self.formatter.format_content(test_data, "test1.md")

        # 验证：应该没有块 ID
        self.assertNotIn("^block", result, "无引用的块 ID 应该被删除")
        self.assertEqual(len(self.formatter.referenced_uuids), 0, "应该没有被引用的UUID")

    def test_referenced_block_id_preserved(self):
        """测试有引用的块ID会被保留"""

        # 创建测试数据：有块ID且有引用
        test_data = {
            "content": """这里引用了 ((abc123-def456)) 
id:: abc123-def456
这里没有引用
id:: xyz789-uvw012""",
            "meta_properties": [],
        }

        # 第一阶段：收集被引用的 UUID
        self.formatter.collect_referenced_uuids(test_data)

        # 第二阶段：只为被引用的块分配 ID
        self.formatter.collect_block_mappings("test2.md", test_data)

        # 格式化内容
        result = self.formatter.format_content(test_data, "test2.md")

        # 验证：应该有一个块 ID（被引用的那个）
        self.assertIn("^block", result, "有引用的块 ID 应该被保留")

        # 统计实际的块 ID 行（现在块ID附加在内容行末尾）
        # 检查以 ^block 结尾的行，而不是包含 ^block 的行（避免误计算块引用）
        self.assertEqual(self.count_block_ids(result), 1, "只有被引用的块 ID 应该被保留")

        # 验证被引用的UUID被正确识别
        self.assertIn("abc123-def456", self.formatter.referenced_uuids, "被引用的UUID应该被识别")
        self.assertNotIn(
            "xyz789-uvw012", self.formatter.referenced_uuids, "未被引用的UUID不应该被识别"
        )

    def test_multiple_references_same_block(self):
        """测试同一个块被多次引用"""

        test_data = {
            "content": """这里引用了 ((abc123-def456)) 和 ((abc123-def456))
id:: abc123-def456
这里又引用了一次 ((abc123-def456))""",
            "meta_properties": [],
        }

        # 处理流程
        self.formatter.collect_referenced_uuids(test_data)
        self.formatter.collect_block_mappings("test3.md", test_data)
        result = self.formatter.format_content(test_data, "test3.md")

        # 验证：只有一个块ID，但UUID被正确识别
        # 检查以 ^block 结尾的行，而不是包含 ^block 的行
        self.assertEqual(self.count_block_ids(result), 1, "同一个块多次引用只应该有一个块ID")
        self.assertIn(
            "abc123-def456", self.formatter.referenced_uuids, "多次引用的UUID应该被识别"
        )

    def test_mixed_referenced_and_unreferenced(self):
        """测试混合场景：部分块被引用，部分未被引用"""

        test_data = {
            "content": """引用第一个 ((uuid-1)) 但不引用第二个
id:: uuid-1
这是第一个块内容
id:: uuid-2
这是第二个块内容（无引用）
id:: uuid-3
引用第三个 ((uuid-3))""",
            "meta_properties": [],
        }

        # 处理流程
        self.formatter.collect_referenced_uuids(test_data)
        self.formatter.collect_block_mappings("test4.md", test_data)
        result = self.formatter.format_content(test_data, "test4.md")

        # 验证：应该有两个块ID（被引用的那些）
        # 检查以 ^block 结尾的行，而不是包含 ^block 的行
        self.assertEqual(self.count_block_ids(result), 2, "应该有两个被引用的块ID")

        # 验证引用识别正确
        self.assertIn("uuid-1", self.formatter.referenced_uuids)
        self.assertIn("uuid-3", self.formatter.referenced_uuids)
        self.assertNotIn("uuid-2", self.formatter.referenced_uuids)

    def test_block_id_format_variations(self):
        """测试不同格式的块ID"""

        test_data = {
            "content": """引用: ((abc123-def456))
id:: abc123-def456
引用: ((xyz-789))  
id:: xyz-789
引用: ((simple))
id:: simple""",
            "meta_properties": [],
        }

        # 处理流程
        self.formatter.collect_referenced_uuids(test_data)
        self.formatter.collect_block_mappings("test5.md", test_data)
        result = self.formatter.format_content(test_data, "test5.md")

        # 验证：所有不同格式的块ID都被正确处理
        # 检查以 ^block 结尾的行，而不是包含 ^block 的行
        self.assertEqual(self.count_block_ids(result), 3, "所有格式的块ID都应该被保留")

        # 验证所有UUID都被识别
        self.assertEqual(len(self.formatter.referenced_uuids), 3, "所有不同格式的UUID都应该被识别")

    def test_edge_case_empty_content(self):
        """测试边缘情况：空内容"""

        test_data = {"content": "", "meta_properties": []}

        # 处理流程
        self.formatter.collect_referenced_uuids(test_data)
        self.formatter.collect_block_mappings("test6.md", test_data)
        result = self.formatter.format_content(test_data, "test6.md")

        # 验证：空内容不会出错
        self.assertEqual(result, "", "空内容应该返回空字符串")
        self.assertEqual(len(self.formatter.referenced_uuids), 0, "空内容没有引用的UUID")


if __name__ == "__main__":
    unittest.main()
