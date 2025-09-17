#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from obsidian_formatter import ObsidianFormatter

def test_formatting_optimization():
    formatter = ObsidianFormatter()
    
    # 测试案例1：连续多个空行
    print("=== 测试案例1：连续多个空行 ===")
    test_content1 = """- 第一行内容
-
-   
-

- 第二行内容
-
-
-
- 第三行内容"""
    
    lines1 = test_content1.split('\n')
    optimized1 = formatter._optimize_formatting(lines1)
    print("原始:")
    for i, line in enumerate(lines1):
        print(f"{i+1:2}: '{line}'")
    print("\n优化后:")
    for i, line in enumerate(optimized1):
        print(f"{i+1:2}: '{line}'")
    print()
    
    # 测试案例2：标题前缺少空行
    print("=== 测试案例2：标题前缺少空行 ===")
    test_content2 = """- 第一段内容
- 这是第一段的继续
# 这是标题1
- 标题下的内容
- 更多内容
## 这是标题2
- 二级标题下的内容"""
    
    lines2 = test_content2.split('\n')
    optimized2 = formatter._optimize_formatting(lines2)
    print("原始:")
    for i, line in enumerate(lines2):
        print(f"{i+1:2}: '{line}'")
    print("\n优化后:")
    for i, line in enumerate(optimized2):
        print(f"{i+1:2}: '{line}'")
    print()
    
    # 测试案例3：带空格的空行
    print("=== 测试案例3：带空格和缩进的空行 ===")
    test_content3 = """- 第一行
-    
-	
-  	  
- 第二行"""
    
    lines3 = test_content3.split('\n')
    optimized3 = formatter._optimize_formatting(lines3)
    print("原始:")
    for i, line in enumerate(lines3):
        print(f"{i+1:2}: '{line}' (长度: {len(line)})")
    print("\n优化后:")
    for i, line in enumerate(optimized3):
        print(f"{i+1:2}: '{line}' (长度: {len(line)})")
    print()
    
    # 测试案例4：完整转换测试
    print("=== 测试案例4：完整转换测试 ===")
    test_data = {
        'content': """- 开头内容
-
-
# 标题1
- 标题下内容
-   
## 标题2
- 二级标题内容
-
-
### 标题3
- 三级标题内容""",
        'meta_properties': []
    }
    
    result = formatter.format_content(test_data)
    print("完整转换结果:")
    print(repr(result))
    print("\n渲染效果:")
    print(result)

if __name__ == "__main__":
    test_formatting_optimization()