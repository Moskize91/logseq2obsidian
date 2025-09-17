#!/usr/bin/env python3
"""
页面链接转换的边缘情况测试套件
确保各种格式的页面链接都能正确处理
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from obsidian_formatter import ObsidianFormatter


def test_page_link_edge_cases():
    """测试页面链接转换的各种边缘情况"""
    formatter = ObsidianFormatter()
    
    # 边缘情况测试集
    edge_cases = [
        # 基本页面链接
        ("[[方济各会]]", "[[方济各会]]", "中文页面链接"),
        ("[[佛教]]", "[[佛教]]", "中文单字页面链接"),
        ("[[Buddhism]]", "[[Buddhism]]", "英文页面链接"),
        
        # 包含特殊字符的页面链接
        ("[[React.js]]", "[[React.js]]", "带点号的页面链接"),
        ("[[C++]]", "[[C++]]", "带加号的页面链接"),
        ("[[Web3.0]]", "[[Web3.0]]", "带数字的页面链接"),
        ("[[Test-Case]]", "[[Test-Case]]", "带连字符的页面链接"),
        ("[[Test_Case]]", "[[Test_Case]]", "带下划线的页面链接"),
        ("[[Test Space]]", "[[Test Space]]", "带空格的页面链接"),
        
        # 包含中英混合的页面链接
        ("[[Traditional Chinese Medicine]]", "[[Traditional Chinese Medicine]]", "英文词组页面链接"),
        ("[[计算机科学Computer Science]]", "[[计算机科学Computer Science]]", "中英混合页面链接"),
        ("[[AI人工智能]]", "[[AI人工智能]]", "英文缩写+中文"),
        
        # 文本中的页面链接
        ("这里有个链接 [[测试页面]] 在文本中", "这里有个链接 [[测试页面]] 在文本中", "文本中的页面链接"),
        ("多个链接：[[页面1]] 和 [[页面2]]", "多个链接：[[页面1]] 和 [[页面2]]", "一行中的多个页面链接"),
        ("- [[任务1]] 这是一个任务", "- [[任务1]] 这是一个任务", "列表项中的页面链接"),
        
        # 带有特殊符号的边缘情况
        ("[[#标签页面]]", "[[#标签页面]]", "带井号的页面链接"),
        ("[[@提及页面]]", "[[@提及页面]]", "带@符号的页面链接"),
        ("[[50%]]", "[[50%]]", "带百分号的页面链接"),
        ("[[2023年]]", "[[2023年]]", "带年份的页面链接"),
        
        # 可能与标签混淆的情况
        ("[[编程语言]]", "[[编程语言]]", "概念词汇页面链接"),
        ("[[机器学习]]", "[[机器学习]]", "技术概念页面链接"),
        ("[[算法]]", "[[算法]]", "学术概念页面链接"),
        ("[[数据结构]]", "[[数据结构]]", "计算机科学概念"),
        
        # 混合格式的复杂情况  
        ("在 [[React.js]] 中使用 [[TypeScript]] 开发", "在 [[React.js]] 中使用 [[TypeScript]] 开发", "技术名词页面链接"),
        ("学习 [[Python]] 和 [[机器学习]] 的基础", "学习 [[Python]] 和 [[机器学习]] 的基础", "技术+概念混合"),
        
        # 空白和格式边缘情况
        ("[[]]", "[[]]", "空页面链接"),
        ("[[  ]]", "[[  ]]", "只有空格的页面链接"),
        ("前面文字[[页面]]后面文字", "前面文字[[页面]]后面文字", "紧贴文字的页面链接"),
        
        # 嵌套情况
        ("参考 [[关于[[嵌套]]的讨论]]", "参考 [[关于[[嵌套]]的讨论]]", "嵌套链接情况"),
        
        # 长页面名称
        ("[[这是一个非常长的页面名称用于测试边缘情况]]", "[[这是一个非常长的页面名称用于测试边缘情况]]", "长页面名称"),
        
        # 数字和符号组合
        ("[[IPv4]]", "[[IPv4]]", "技术术语带数字"),
        ("[[HTTP/2]]", "[[HTTP/2]]", "带斜杠的技术术语"),
        ("[[REST API]]", "[[REST API]]", "技术缩写"),
    ]
    
    print("测试页面链接转换的边缘情况...")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected_output, description) in enumerate(edge_cases, 1):
        try:
            result = formatter._convert_page_links(input_text)
            
            if result == expected_output:
                print(f"✓ 测试 {i:2d}: {description}")
                passed += 1
            else:
                print(f"✗ 测试 {i:2d}: {description}")
                print(f"     输入: {input_text}")
                print(f"     期望: {expected_output}")
                print(f"     实际: {result}")
                failed += 1
                
        except (AttributeError, ValueError, TypeError) as e:
            print(f"✗ 测试 {i:2d}: {description} - 异常: {e}")
            failed += 1
    
    print("=" * 70)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有边缘情况测试通过！页面链接转换功能完全正常")
        return True
    else:
        print(f"❌ {failed} 个测试失败，需要检查代码")
        return False


if __name__ == "__main__":
    test_page_link_edge_cases()