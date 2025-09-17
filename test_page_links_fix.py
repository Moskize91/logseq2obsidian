#!/usr/bin/env python3
"""
测试页面链接转换是否正确，验证 bug 修复
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from obsidian_formatter import ObsidianFormatter
from filename_processor import FilenameProcessor

def test_page_links():
    """测试页面链接转换功能"""
    formatter = ObsidianFormatter()
    
    test_cases = [
        ("[[方济各会]]", "[[方济各会]]"),
        ("[[佛教]]", "[[佛教]]"),
        ("[[Buddhism]]", "[[Buddhism]]"),
        ("[[Traditional Chinese Medicine]]", "[[Traditional Chinese Medicine]]"),
        ("[[Web3.0]]", "[[Web3.0]]"),
        ("[[React.js]]", "[[React.js]]"),
        ("这里有个链接 [[测试页面]] 在文本中", "这里有个链接 [[测试页面]] 在文本中"),
        ("多个链接：[[页面1]] 和 [[页面2]]", "多个链接：[[页面1]] 和 [[页面2]]"),
    ]
    
    print("测试页面链接转换功能...")
    print("=" * 50)
    
    all_passed = True
    
    for i, (input_text, expected_output) in enumerate(test_cases, 1):
        try:
            # 直接测试页面链接转换
            result = formatter._convert_page_links(input_text)
            
            # 检查结果
            if result == expected_output:
                print(f"✓ 测试 {i}: 通过")
                print(f"  输入: {input_text}")
                print(f"  输出: {result}")
            else:
                print(f"✗ 测试 {i}: 失败")
                print(f"  输入: {input_text}")
                print(f"  期望: {expected_output}")
                print(f"  实际: {result}")
                all_passed = False
            
            print("-" * 30)
            
        except (AttributeError, ValueError, TypeError) as e:
            print(f"✗ 测试 {i}: 异常")
            print(f"  输入: {input_text}")
            print(f"  错误: {e}")
            all_passed = False
            print("-" * 30)
    
    if all_passed:
        print("🎉 所有测试通过！页面链接转换功能正常")
    else:
        print("❌ 有测试失败，需要检查代码")
    
    return all_passed

if __name__ == "__main__":
    test_page_links()