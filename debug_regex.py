#!/usr/bin/env python3
"""
调试块 ID 处理逻辑
"""

import re

def test_regex():
    """测试正则表达式"""
    block_id_pattern = r'^id:: ([a-f0-9-]+)\s*$'
    
    test_lines = [
        "id:: abc123-def456",
        "id:: xyz789-uvw012",
        "id:: abc123-def456  ",  # 带空格
        " id:: abc123-def456",   # 前面有空格
        "这是文字 id:: abc123-def456",  # 混合内容
    ]
    
    for line in test_lines:
        match = re.match(block_id_pattern, line)
        print(f"Line: '{line}' -> Match: {match.group(1) if match else 'None'}")

if __name__ == "__main__":
    test_regex()