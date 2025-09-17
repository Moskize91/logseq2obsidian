#!/usr/bin/env python3
"""
调试特定 UUID 匹配问题
"""

import re

def debug_uuid_matching():
    """调试为什么这个UUID没有被正确处理"""
    
    test_uuid = "61a8ad30-0b98-43fb-9d05-77b7f77be632"
    test_line = f"id:: {test_uuid}"
    
    # 测试我们的正则表达式
    block_id_pattern = r'^id:: ([a-zA-Z0-9-]+)\s*$'
    
    print(f"测试行: '{test_line}'")
    print(f"正则表达式: {block_id_pattern}")
    
    match = re.match(block_id_pattern, test_line)
    if match:
        print(f"✅ 匹配成功: {match.group(1)}")
    else:
        print("❌ 匹配失败")
        
    # 测试各种可能的情况
    test_cases = [
        "id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632",
        "id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632 ",
        " id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632",
        "id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632\n",
    ]
    
    for i, case in enumerate(test_cases):
        match = re.match(block_id_pattern, case)
        print(f"测试 {i+1}: '{repr(case)}' -> {'✅' if match else '❌'}")

if __name__ == "__main__":
    debug_uuid_matching()