#!/usr/bin/env python3
"""
测试各种分类标签情况
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from obsidian_formatter import ObsidianFormatter


def test_various_tag_formats():
    """测试各种标签格式"""
    
    test_cases = [
        {
            'name': '引用块中的标签',
            'content': '- > #wiki  齐泽克的短路\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '直接标签',
            'content': '- #wiki 内容\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '标签在行首（无列表标记）',
            'content': '#wiki 内容\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '标签不在第一行',
            'content': '- 其他内容\n- #wiki 内容',
            'expected': ''
        },
        {
            'name': '有空行的情况',
            'content': '\n\n- #wiki 内容\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '有meta信息的情况',
            'content': 'title:: 测试\n- #wiki 内容\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '标签后有其他标签',
            'content': '- #wiki #tag2 内容\n- 其他内容',
            'expected': 'wiki'
        },
        {
            'name': '不匹配的标签',
            'content': '- #other 内容\n- 其他内容',
            'expected': ''
        }
    ]
    
    formatter = ObsidianFormatter()
    formatter.category_tag = "wiki"
    formatter.category_folder = "wiki"
    
    print("=== 测试各种标签格式 ===")
    
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"内容: {repr(case['content'])}")
        
        test_data = {
            'content': case['content'],
            'meta_properties': []
        }
        
        # 如果有meta信息，模拟meta_properties
        if 'title::' in case['content']:
            test_data['meta_properties'] = [type('', (), {'line_number': 1})()]
        
        detected = formatter.detect_category_folder(test_data)
        expected = case['expected']
        
        print(f"检测到: '{detected}' | 期望: '{expected}'")
        
        if detected == expected:
            print("✅ 通过")
        else:
            print("❌ 失败")


if __name__ == "__main__":
    test_various_tag_formats()