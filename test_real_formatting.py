#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from obsidian_formatter import ObsidianFormatter

def test_real_case():
    formatter = ObsidianFormatter()
    
    # 读取测试文件
    with open('test_formatting_sample.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    test_data = {
        'content': content,
        'meta_properties': []
    }
    
    result = formatter.format_content(test_data)
    
    print("=== 原始内容 ===")
    print(repr(content))
    print("\n=== 转换结果 ===")
    print(repr(result))
    print("\n=== 渲染效果 ===")
    print(result)

if __name__ == "__main__":
    test_real_case()