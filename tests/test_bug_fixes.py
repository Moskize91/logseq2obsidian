#!/usr/bin/env python3
"""
测试已修复的 Bug 案例
这个测试文件专门测试所有已修复的问题，确保这些问题不会再次出现
"""

import os
import sys
import unittest

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.obsidian_formatter import ObsidianFormatter


class TestBugFixes(unittest.TestCase):
    """测试已修复的 bug"""

    def setUp(self):
        """设置测试环境"""
        self.formatter_with_bullets = ObsidianFormatter(remove_top_level_bullets=False)
        self.formatter_without_bullets = ObsidianFormatter(
            remove_top_level_bullets=True
        )

    def test_quote_block_conversion(self):
        """Bug Fix #1: 修复 `- >` 引用块格式问题"""
        print("\n=== 测试引用块转换 ===")

        test_cases = [
            ("- > 看起来并非传统科学那样来让人置信。", "> 看起来并非传统科学那样来让人置信。"),
            ("\t- > 荣格也有类似观点。", "\t> 荣格也有类似观点。"),
            ("  - > 这是有缩进的引用。", "  > 这是有缩进的引用。"),
            ("- 这不是引用块", "- 这不是引用块"),  # 普通列表项应该保持不变
            ("> 这已经是标准引用", "> 这已经是标准引用"),  # 标准引用应该保持不变
        ]

        formatter = ObsidianFormatter()

        for input_line, expected in test_cases:
            result = formatter._convert_quote_blocks(input_line)
            self.assertEqual(result, expected, f"引用块转换失败: {input_line}")
            print(f"✅ 基本引用块: '{input_line}' -> '{result}'")

        print("✅ 引用块转换测试通过")

    def test_empty_list_item_handling(self):
        """Bug Fix #2: 处理空的列表项问题"""
        print("\n=== 测试空列表项处理 ===")

        # 测试用例：包含空列表项的内容
        test_content = """释梦的难点：
- 总是在挑选念头，但在联想时又没有耐心究其本源。
\t- 被人释梦时，有所顾忌，不愿意将特定念头说出来。
\t-
- 另一个问题""".split(
            "\n"
        )

        # 使用 remove_top_level_bullets=True 模式测试
        result_lines = self.formatter_without_bullets._remove_top_level_bullets(
            test_content
        )
        result_text = "\n".join(result_lines)

        # 验证结果中不包含只有 `-` 的行
        for line in result_lines:
            self.assertNotIn(line.strip(), ["-", "- "], f"结果中不应包含空的列表项: '{line}'")

        # 验证空的子列表项被正确跳过
        self.assertNotIn("\t-", result_text)

        print("✅ 空列表项被正确跳过")
        print("转换结果:")
        print(result_text)

    def test_list_indent_normalization(self):
        """Bug Fix #3: 列表缩进规范化"""
        print("\n=== 测试列表缩进规范化 ===")

        # 测试用例：混合使用制表符和空格的缩进
        test_content = """给他人释梦时：
\t- 做梦者会对联想结果批判。
\t\t- 拼命驳斥的念头，往往是关键因素。
\t\t- 释梦时遇到的困难可视为阻力。
\t- 阻力越大，替代物离潜意识本意越远。"""

        # 使用完整的格式化流程测试缩进规范化
        result = self.formatter_without_bullets.format_content(
            {"content": test_content}
        )
        result_lines = result.split("\n")

        # 验证所有制表符都被转换为空格
        for line in result_lines:
            self.assertNotIn("\t", line, f"结果中不应包含制表符: '{line}'")

        # 验证一级子列表使用 2 个空格缩进
        for line in result_lines:
            if (
                line.strip().startswith("- ")
                and line.startswith("  ")
                and not line.startswith("    ")
            ):
                indent = len(line) - len(line.lstrip())
                expected_indent = 2  # 一级缩进
                self.assertEqual(
                    indent,
                    expected_indent,
                    f"一级子列表缩进应该是 {expected_indent} 个空格，实际是 {indent}",
                )

        # 验证二级子列表使用 4 个空格缩进
        for line in result_lines:
            if line.strip().startswith("- ") and line.startswith("    "):
                indent = len(line) - len(line.lstrip())
                expected_indent = 4  # 二级缩进
                self.assertEqual(
                    indent,
                    expected_indent,
                    f"二级子列表缩进应该是 {expected_indent} 个空格，实际是 {indent}",
                )

        print("✅ 列表缩进规范化正确")
        print("转换结果:")
        for i, line in enumerate(result_lines, 1):
            print(f"  {i:2d}: {repr(line)}")

    def test_double_dash_and_empty_line_handling(self):
        """Bug Fix #4: 处理双破折号和空行问题"""
        print("\n=== 测试双破折号和空行处理 ===")

        # 测试内容，包含双破折号和空行问题
        test_content = """- 待补充：
\t- - 叠加数必须是污染的
\t- 表达式 = 坍缩数的方程，必须至少有一个坍缩数的解
-
- # 2022-01-14 补充"""

        formatter = ObsidianFormatter(remove_top_level_bullets=True)
        result = formatter.format_content({"content": test_content})

        # 验证结果
        lines = result.split("\n")

        # 验证双破折号被保留但现在已经被提升到顶级
        self.assertIn("- - 叠加数必须是污染的", lines)
        print("✅ 双破折号被保留且正确提升为顶级内容")

        # 验证tab被转换为空格
        for line in lines:
            self.assertNotIn("\t", line)
        print("✅ Tab缩进被正确转换为空格")

        # 验证空的列表项被移除
        self.assertNotIn("-", [line.strip() for line in lines if line.strip()])
        print("✅ 空的列表项被正确移除")

        # 验证顶级子弹被移除
        self.assertTrue(result.startswith("待补充："))
        print("✅ 顶级子弹被正确移除")

        print("最终转换结果:")
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {repr(line)}")

        print("✅ 双破折号和空行处理测试通过")

    def test_complete_bug_fix_integration(self):
        """集成测试：验证所有 bug 修复在完整转换中正常工作"""
        print("\n=== 集成测试 ===")

        # 复杂测试用例，包含所有问题类型
        test_content = """对于释梦， <!-- Block Reference: 6211a9d9-f200-4348-a308-23381ba25cb9 -->
- 梦的内容不是我们的目标。

- > 看起来并非传统科学那样来让人置信。
- 仅唤起元素的替代联想，不做多余的事。


释梦的难点：
- 总是在挑选念头，但在联想时又没有耐心究其本源。
\t- 被人释梦时，有所顾忌，不愿意将特定念头说出来。
\t- > 荣格也有类似观点。
- 另一个问题"""

        # 完整转换流程
        result = self.formatter_without_bullets.format_content(
            {"content": test_content}
        )

        # 验证引用块转换正确
        self.assertIn("> 看起来并非传统科学那样来让人置信。", result)
        self.assertIn("> 荣格也有类似观点。", result)  # 现在也被提升为顶级

        # 验证缩进规范化
        self.assertNotIn("\t", result)

        # 验证块引用被注释
        self.assertIn(
            "<!-- Block Reference: 6211a9d9-f200-4348-a308-23381ba25cb9 -->", result
        )

        print("✅ 集成测试通过")
        print("最终转换结果:")
        for i, line in enumerate(result.split("\n"), 1):
            print(f"  {i:2d}: {line}")

    def test_indentation_promotion_when_removing_top_bullets(self):
        """Bug Fix #5: 移除顶级子弹点时的缩进提升"""
        print("\n=== 测试缩进提升逻辑 ===")

        # 测试实际的 oomol 文件内容
        test_content = """- #oomol
- [[oomol 电路图设计]]
- 待补充：
\t- - 叠加数必须是污染的
\t- 表达式 = 坍缩数的方程，必须至少有一个坍缩数的解
- 满足这两条，可以推测出将方程带入另一个方程后，得出的新方程的解空间是原来两个方程解空间的叠加
-
- # 2022-01-14 补充
- 这个想法我推翻了，我有更新做法"""

        formatter = ObsidianFormatter(remove_top_level_bullets=True)
        result = formatter.format_content({"content": test_content})

        # 验证所有内容都被提升为顶级内容（没有缩进）
        lines = result.split("\n")
        expected_lines = [
            "#oomol",
            "[[oomol 电路图设计]]",
            "待补充：",
            "- - 叠加数必须是污染的",
            "- 表达式 = 坍缩数的方程，必须至少有一个坍缩数的解",
            "满足这两条，可以推测出将方程带入另一个方程后，得出的新方程的解空间是原来两个方程解空间的叠加",
            "",
            "# 2022-01-14 补充",
            "这个想法我推翻了，我有更新做法",
        ]

        # 验证结果行数正确
        self.assertEqual(len(lines), len(expected_lines))

        # 验证每一行都没有前导空格（都是顶级内容）
        for i, (actual_line, expected_line) in enumerate(zip(lines, expected_lines)):
            self.assertEqual(
                actual_line,
                expected_line,
                f"第{i+1}行不匹配: 期望 {repr(expected_line)}, 实际 {repr(actual_line)}",
            )

        print("✅ 所有内容正确提升为顶级，无缩进")
        print("✅ 缩进提升逻辑正确")

        print("最终转换结果:")
        for i, line in enumerate(lines, 1):
            print(f"  {i:2d}: {repr(line)}")


def run_bug_fix_tests():
    """运行所有 bug 修复测试"""
    print("开始 Bug 修复测试")
    print("=" * 50)

    # 创建测试套件
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBugFixes)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 返回是否全部通过
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_bug_fix_tests()
    sys.exit(0 if success else 1)
