#!/usr/bin/env python3
"""
测试LogSeq视频嵌入语法转换为Obsidian格式

LogSeq 视频语法示例:
- {{youtube dQw4w9WgXcQ}}
- {{bilibili BV1xx411c7mD}}  
- {{youtube-timestamp 8:40}}

需要研究最佳的Obsidian转换方案:
1. HTML iframe 嵌入
2. 插件兼容性 (如youtube插件)
3. 简单的链接格式
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter


class TestVideoEmbeds(unittest.TestCase):
    """测试视频嵌入转换"""

    def setUp(self):
        self.formatter = ObsidianFormatter()

    def test_youtube_embed_basic(self):
        """测试基础YouTube嵌入语法"""
        test_cases = [
            (
                "{{youtube dQw4w9WgXcQ}}",
                "YouTube视频ID",
                "![](https://youtu.be/dQw4w9WgXcQ)",
            ),
            (
                "这里有视频: {{youtube dQw4w9WgXcQ}}",
                "行内YouTube嵌入",
                "这里有视频: ![](https://youtu.be/dQw4w9WgXcQ)",
            ),
            (
                "- {{youtube dQw4w9WgXcQ}}",
                "列表中的YouTube嵌入",
                "- ![](https://youtu.be/dQw4w9WgXcQ)",
            ),
        ]

        for input_text, description, expected_output in test_cases:
            with self.subTest(description=description):
                result = self.formatter._process_line(input_text, {})
                print(f"\n{description}:")
                print(f"输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(
                    result, expected_output, f"转换结果应该匹配期望输出: {description}"
                )

    def test_bilibili_embed_basic(self):
        """测试Bilibili嵌入语法"""
        test_cases = [
            (
                "{{bilibili BV1xx411c7mD}}",
                "Bilibili BV号",
                "[Bilibili视频: BV1xx411c7mD](BV1xx411c7mD)",
            ),
            (
                "观看视频: {{bilibili BV1xx411c7mD}}",
                "行内Bilibili嵌入",
                "观看视频: [Bilibili视频: BV1xx411c7mD](BV1xx411c7mD)",
            ),
        ]

        for input_text, description, expected_output in test_cases:
            with self.subTest(description=description):
                result = self.formatter._process_line(input_text, {})
                print(f"\n{description}:")
                print(f"输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(
                    result, expected_output, f"转换结果应该匹配期望输出: {description}"
                )

    def test_youtube_url_extraction(self):
        """测试YouTube URL处理和通用video标签"""
        test_cases = [
            (
                "{{youtube https://youtu.be/rEOoItpzlVw}}",
                "youtu.be完整URL",
                "![](https://youtu.be/rEOoItpzlVw)",
            ),
            (
                "{{youtube https://www.youtube.com/watch?v=dQw4w9WgXcQ}}",
                "完整YouTube URL",
                "![](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
            ),
            (
                "{{video https://youtu.be/Urid8hF54_k}}",
                "通用video标签",
                "![](https://youtu.be/Urid8hF54_k)",
            ),
            ("{{youtube abc123}}", "纯视频ID转为youtu.be格式", "![](https://youtu.be/abc123)"),
        ]

        for input_text, description, expected_output in test_cases:
            with self.subTest(description=description):
                result = self.formatter._process_line(input_text, {})
                print(f"\n{description}:")
                print(f"输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(
                    result, expected_output, f"URL处理转换结果应该匹配期望输出: {description}"
                )

    def test_youtube_timestamp_embed(self):
        """测试YouTube时间戳嵌入语法 - 应该保持原样"""
        test_cases = [
            ("{{youtube-timestamp 8:40}}", "时间戳格式", "{{youtube-timestamp 8:40}}"),
            (
                "{{youtube-timestamp 1:23:45}}",
                "长时间戳格式",
                "{{youtube-timestamp 1:23:45}}",
            ),
            (
                "从这里开始: {{youtube-timestamp 8:40}}",
                "行内时间戳",
                "从这里开始: {{youtube-timestamp 8:40}}",
            ),
        ]

        for input_text, description, expected_output in test_cases:
            with self.subTest(description=description):
                result = self.formatter._process_line(input_text, {})
                print(f"\n{description}:")
                print(f"输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(result, expected_output, f"时间戳语法应该保持原样: {description}")

    def test_video_embed_edge_cases(self):
        """测试视频嵌入的边缘情况"""
        test_cases = [
            # 空格处理
            (
                "{{youtube  dQw4w9WgXcQ  }}",
                "带额外空格的YouTube",
                "![](https://youtu.be/dQw4w9WgXcQ)",
            ),
            (
                "{{bilibili  BV1xx411c7mD  }}",
                "带额外空格的Bilibili",
                "[Bilibili视频: BV1xx411c7mD](BV1xx411c7mD)",
            ),
            (
                "{{youtube-timestamp  8:40  }}",
                "带额外空格的时间戳",
                "{{youtube-timestamp  8:40  }}",
            ),
            # 多个视频在一行
            (
                "{{youtube abc123}} 和 {{bilibili BV456}}",
                "一行多个视频",
                "![](https://youtu.be/abc123) 和 [Bilibili视频: BV456](BV456)",
            ),
            # 混合其他语法
            (
                "[[页面链接]] {{youtube abc123}} ((block-ref))",
                "混合语法",
                "[[页面链接]] ![](https://youtu.be/abc123) <!-- Block Reference (未找到): block-ref -->",
            ),
        ]

        for input_text, description, expected_output in test_cases:
            with self.subTest(description=description):
                result = self.formatter._process_line(input_text, {})
                print(f"\n{description}:")
                print(f"输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(
                    result, expected_output, f"转换结果应该匹配期望输出: {description}"
                )

    def test_no_video_content(self):
        """测试不包含视频语法的内容应保持不变"""
        test_cases = [
            ("这是普通文本", "这是普通文本"),
            ("[[页面链接]] 和 ((块引用))", "[[页面链接]] 和 <!-- Block Reference (未找到): 块引用 -->"),
            ("{ 单个花括号", "{ 单个花括号"),
            ("{{ 两个花括号但不是视频语法", "{{ 两个花括号但不是视频语法"),
        ]

        for input_text, expected_output in test_cases:
            with self.subTest(input_text=input_text):
                result = self.formatter._process_line(input_text, {})
                print(f"无视频内容测试 - 输入: {input_text}")
                print(f"输出: {result}")
                print(f"期望: {expected_output}")
                self.assertEqual(result, expected_output, f"非视频语法应该按预期转换: {input_text}")

    def test_mixed_video_content(self):
        """测试混合视频内容"""
        content = """这是一个包含多种视频的页面:

- YouTube视频: {{youtube dQw4w9WgXcQ}}
- Bilibili视频: {{bilibili BV1xx411c7mD}}
- 时间戳引用: {{youtube-timestamp 8:40}}

其他内容..."""

        expected_content = """这是一个包含多种视频的页面:

- YouTube视频: ![](https://youtu.be/dQw4w9WgXcQ)
- Bilibili视频: [Bilibili视频: BV1xx411c7mD](BV1xx411c7mD)
- 时间戳引用: {{youtube-timestamp 8:40}}

其他内容..."""

        lines = content.split("\n")
        result_lines = []
        for line in lines:
            processed = self.formatter._process_line(line, {})
            result_lines.append(processed)

        result = "\n".join(result_lines)
        print("\n混合内容测试:")
        print(f"输入:\n{content}")
        print(f"输出:\n{result}")
        print(f"期望:\n{expected_content}")
        self.assertEqual(result, expected_content, "混合视频内容应该正确转换")


if __name__ == "__main__":
    unittest.main(verbosity=2)
