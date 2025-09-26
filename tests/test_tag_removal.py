#!/usr/bin/env python3
"""
测试分类标签清理功能
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

# 直接导入模块而不是类
import obsidian_formatter


def test_tag_removal():
    """测试标签清理功能"""
    formatter = obsidian_formatter.ObsidianFormatter(
        category_tag="wiki", category_folder="wiki"
    )

    # 测试案例 1: 整行只有标签
    test_content_1 = """- #wiki
- ## 读书笔记
- 内容"""

    parsed_data_1 = {"content": test_content_1, "meta_properties": []}

    result_1 = formatter.format_content(parsed_data_1)
    print("测试 1 - 整行只有标签:")
    print("原始:")
    print(test_content_1)
    print("结果:")
    print(result_1)
    print()

    # 测试案例 2: 标签与其他内容混合
    test_content_2 = """- #wiki 法国马克思主义者
- alias:: [[GAN]]
- 其他内容"""

    parsed_data_2 = {"content": test_content_2, "meta_properties": []}

    result_2 = formatter.format_content(parsed_data_2)
    print("测试 2 - 标签与其他内容混合:")
    print("原始:")
    print(test_content_2)
    print("结果:")
    print(result_2)
    print()

    # 测试案例 3: 没有标签的文件
    test_content_3 = """- ## 普通文章
- 这是普通内容
- 没有分类标签"""

    parsed_data_3 = {"content": test_content_3, "meta_properties": []}

    result_3 = formatter.format_content(parsed_data_3)
    print("测试 3 - 没有标签的文件:")
    print("原始:")
    print(test_content_3)
    print("结果:")
    print(result_3)
    print()

    # 测试案例 4: 多个标签
    test_content_4 = """- #wiki #test
- 内容"""

    parsed_data_4 = {"content": test_content_4, "meta_properties": []}

    result_4 = formatter.format_content(parsed_data_4)
    print("测试 4 - 多个标签:")
    print("原始:")
    print(test_content_4)
    print("结果:")
    print(result_4)
    print()


if __name__ == "__main__":
    test_tag_removal()
