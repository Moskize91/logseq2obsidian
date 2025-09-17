#!/usr/bin/env python3
"""
测试缩进的块 ID 处理
"""

import re

def test_indented_block_id():
    """测试缩进的块ID是否能正确处理"""
    
    # 模拟实际的文件内容
    test_content = """- [[crdt]]
  id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632
- [[文明是一种错觉]]"""
    
    lines = test_content.split('\n')
    
    # 当前的正则表达式 (行首)
    current_pattern = r'^id:: ([a-zA-Z0-9-]+)\s*$'
    
    # 改进的正则表达式 (允许缩进)
    improved_pattern = r'^\s*id:: ([a-zA-Z0-9-]+)\s*$'
    
    print("原始内容:")
    for i, line in enumerate(lines):
        print(f"{i+1}: '{line}'")
    
    print(f"\n使用当前正则表达式: {current_pattern}")
    for i, line in enumerate(lines):
        match = re.match(current_pattern, line)
        if match:
            print(f"行 {i+1}: ✅ 匹配到 {match.group(1)}")
        elif 'id::' in line:
            print(f"行 {i+1}: ❌ 包含id::但未匹配")
    
    print(f"\n使用改进的正则表达式: {improved_pattern}")
    for i, line in enumerate(lines):
        match = re.match(improved_pattern, line)
        if match:
            print(f"行 {i+1}: ✅ 匹配到 {match.group(1)}")
        elif 'id::' in line:
            print(f"行 {i+1}: ❌ 包含id::但未匹配")

if __name__ == "__main__":
    test_indented_block_id()