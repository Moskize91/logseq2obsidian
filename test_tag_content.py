#!/usr/bin/env python3
"""
测试分类标签清理功能 - 简化版本
"""

# 创建测试内容
test_content_1 = """- #wiki
- ## 读书笔记
- 内容"""

test_content_2 = """- #wiki 法国马克思主义者
- alias:: [[GAN]]
- 其他内容"""

test_content_3 = """- ## 普通文章
- 这是普通内容
- 没有分类标签"""

test_content_4 = """- #wiki #test
- 内容"""

print("=== 标签清理测试内容 ===")
print()
print("测试 1 - 整行只有标签:")
print(test_content_1)
print()
print("测试 2 - 标签与其他内容混合:")
print(test_content_2)
print()
print("测试 3 - 没有标签的文件:")
print(test_content_3)
print()
print("测试 4 - 多个标签:")
print(test_content_4)
print()
print("现在运行实际转换测试...")