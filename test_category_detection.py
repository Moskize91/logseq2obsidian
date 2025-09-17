#!/usr/bin/env python3
"""
测试分类标签检测逻辑
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from logseq_parser import LogseqParser
from obsidian_formatter import ObsidianFormatter


def test_category_detection():
    """测试分类标签检测逻辑"""
    
    # 模拟原始的 Logseq 文件内容
    test_data = {
        'content': '''- > #wiki  齐泽克的短路
- ((61ff4d79-6753-42ba-aa80-2f01d99b7a9b))
-
- 齐泽克用短路解释哪些想法会被压抑。''',
        'meta_properties': []
    }
    
    # 配置分类标签
    formatter = ObsidianFormatter()
    formatter.category_tag = "wiki"
    formatter.category_folder = "wiki"
    
    print("=== 原始内容 ===")
    print(test_data['content'])
    
    print("\n=== 检测分类标签 ===")
    detected_folder = formatter.detect_category_folder(test_data)
    print(f"检测到的文件夹: '{detected_folder}'")
    
    # 详细分析第一行
    lines = test_data['content'].split('\n')
    first_line = lines[0]
    print(f"\n第一行: '{first_line}'")
    
    # 模拟 _get_actual_content_lines 的逻辑
    content_lines = formatter._get_actual_content_lines(lines, [])
    print(f"实际内容行: {content_lines}")
    
    if content_lines:
        first_content = content_lines[0]
        print(f"第一个实际内容行: '{first_content}'")
        
        # 模拟 _remove_logseq_bullets 的逻辑
        cleaned = formatter._remove_logseq_bullets(first_content)
        print(f"移除列表标记后: '{cleaned}'")
        
        # 检查是否以 #wiki 开头
        starts_with_wiki = cleaned.startswith("#wiki")
        print(f"是否以 #wiki 开头: {starts_with_wiki}")


if __name__ == "__main__":
    test_category_detection()