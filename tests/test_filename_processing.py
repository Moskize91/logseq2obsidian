#!/usr/bin/env python
"""
文件名编码处理测试
测试 Logseq 文件名编码到 Obsidian 兼容文件名的转换功能
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.file_manager import FileManager
from src.filename_processor import FilenameProcessor
from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


class TestFilenameProcessing(unittest.TestCase):
    """文件名编码处理测试"""

    def setUp(self):
        self.processor = FilenameProcessor()
        self.parser = LogseqParser()
        self.formatter = ObsidianFormatter()

    def test_url_decode_processing(self):
        """测试 URL 编码解码"""
        test_cases = [
            ('"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制.md', '"天机不可泄漏"_古代中国对天学的官方垄断和法律控制.md'),
            (
                "From Local to Global%3A A Graph RAG Approach.md",
                "From Local to Global_ A Graph RAG Approach.md",
            ),
            ("Object(a)%3A Cause of Desire.md", "Object(a)_ Cause of Desire.md"),
            ("How the Other Half %22Thinks%22.md", 'How the Other Half "Thinks".md'),
        ]

        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                result = self.processor.process_filename(input_name)
                self.assertEqual(result, expected_output)

    def test_date_format_conversion(self):
        """测试LogSeq日期格式转换为Obsidian格式"""
        formatter = ObsidianFormatter()

        # 测试标准日期格式转换
        test_cases = [
            # LogSeq格式 -> Obsidian格式
            ("2025_01_02", "2025-01-02.md"),
            ("2024_12_31", "2024-12-31.md"),
            ("2023_03_15", "2023-03-15.md"),
            ("2022_09_07", "2022-09-07.md"),
            ("2024_01_06 2", "2024-01-06 2.md"),  # 带后缀
        ]

        for input_name, expected in test_cases:
            result = formatter.generate_filename(input_name)
            self.assertEqual(
                result, expected, f"日期格式转换失败: {input_name} -> {result}, 期望: {expected}"
            )

        # 测试非日期文件不受影响
        non_date_cases = [
            ("normal_file", "normal_file.md"),
            ("not_a_date_2025_format", "not_a_date_2025_format.md"),
            ("2025_1_2", "2025_1_2.md"),  # 不标准格式
            ("2025_13_01", "2025_13_01.md"),  # 无效月份
            ("2025_01_32", "2025_01_32.md"),  # 无效日期
        ]

        for input_name, expected in non_date_cases:
            result = formatter.generate_filename(input_name)
            self.assertEqual(
                result, expected, f"非日期文件处理失败: {input_name} -> {result}, 期望: {expected}"
            )

    def test_obsidian_forbidden_chars(self):
        """测试 Obsidian 不支持字符的替换"""
        test_cases = [
            ("file:name.md", "file_name.md"),
            ("file\\name.md", "file_name.md"),
            ("file/name.md", "file_name.md"),
            ("file:name\\with/all.md", "file_name_with_all.md"),
        ]

        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                result = self.processor.process_filename(input_name)
                self.assertEqual(result, expected_output)

    def test_page_link_processing(self):
        """测试页面链接处理"""
        test_cases = [
            ("normal_page", "normal_page"),
            ('"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制', '"天机不可泄漏"_古代中国对天学的官方垄断和法律控制'),
            (
                "From Local to Global%3A A Graph RAG Approach",
                "From Local to Global_ A Graph RAG Approach",
            ),
        ]

        for input_link, expected_output in test_cases:
            with self.subTest(input_link=input_link):
                result = self.processor.process_page_link(input_link)
                self.assertEqual(result, expected_output)

    def test_conversion_mapping(self):
        """测试转换映射生成"""
        filenames = [
            "normal_file.md",
            '"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制.md',
            "Object(a)%3A Cause of Desire.md",
        ]

        mapping = self.processor.get_conversion_mapping(filenames)

        # 正常文件不应在映射中
        self.assertNotIn("normal_file.md", mapping)

        # 编码文件应在映射中
        self.assertIn('"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制.md', mapping)
        self.assertIn("Object(a)%3A Cause of Desire.md", mapping)

    def test_real_encoded_files_from_logseq_data(self):
        """测试真实的 Logseq 编码文件"""
        pages_dir = Path(__file__).parent.parent / "examples" / "logseq_data" / "pages"

        if not pages_dir.exists():
            self.skipTest("Logseq 数据目录不存在")

        # 查找所有编码文件
        encoded_files = []
        for filepath in pages_dir.glob("*.md"):
            if "%" in filepath.name:
                encoded_files.append(filepath.name)

        self.assertGreater(len(encoded_files), 0, "应该有编码文件用于测试")

        print(f"\n找到 {len(encoded_files)} 个编码文件:")
        for filename in encoded_files:
            processed = self.processor.process_filename(filename)
            print(f"  {filename}")
            print(f"  -> {processed}")

            # 验证处理后的文件名不包含 Obsidian 禁用字符
            for forbidden_char in self.processor.OBSIDIAN_FORBIDDEN_CHARS:
                self.assertNotIn(
                    forbidden_char,
                    processed,
                    f"处理后的文件名不应包含 '{forbidden_char}': {processed}",
                )

    def test_file_manager_integration(self):
        """测试文件管理器集成"""
        # 创建临时输出目录
        output_dir = Path(__file__).parent.parent / "examples" / "test_output_filename"

        file_manager = FileManager(output_dir, dry_run=True)

        # 测试编码文件名写入
        test_filename = '"天机不可泄漏"%3A古代中国对天学的官方垄断和法律控制.md'
        test_content = "# 测试内容\n这是一个测试文件。"

        # Dry run 模式测试
        result_path = file_manager.write_file(test_filename, test_content, "pages")

        # 验证路径中的文件名已被处理
        expected_processed_name = '"天机不可泄漏"_古代中国对天学的官方垄断和法律控制.md'
        self.assertEqual(result_path.name, expected_processed_name)


if __name__ == "__main__":
    print("开始文件名编码处理测试")
    print("=" * 50)

    unittest.main(verbosity=2)
