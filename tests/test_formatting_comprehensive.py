#!/usr/bin/env python3
"""
全面测试格式优化功能
合并了格式化相关的测试文件
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter


class TestFormattingOptimization(unittest.TestCase):
    """测试格式优化功能"""
    
    def setUp(self):
        self.formatter = ObsidianFormatter()
    
    def test_empty_lines_merging(self):
        """测试连续空行合并"""
        
        test_content = """- 第一行内容
-
-   
-

- 第二行内容
-
-
-
- 第三行内容"""
        
        expected_lines = [
            '- 第一行内容',
            '',
            '- 第二行内容', 
            '',
            '- 第三行内容'
        ]
        
        lines = test_content.split('\n')
        optimized = self.formatter._optimize_formatting(lines)
        
        self.assertEqual(optimized, expected_lines, "连续空行应该被合并为单个空行")
    
    def test_heading_spacing(self):
        """测试标题前空行添加"""
        
        test_content = """- 第一段内容
- 这是第一段的继续
# 这是标题1
- 标题下的内容
- 更多内容
## 这是标题2
- 二级标题下的内容"""
        
        expected_lines = [
            '- 第一段内容',
            '- 这是第一段的继续',
            '',
            '# 这是标题1',
            '- 标题下的内容',
            '- 更多内容',
            '',
            '## 这是标题2',
            '- 二级标题下的内容'
        ]
        
        lines = test_content.split('\n')
        optimized = self.formatter._optimize_formatting(lines)
        
        self.assertEqual(optimized, expected_lines, "标题前应该添加空行")
    
    def test_clean_empty_lines(self):
        """测试清理带空格的空行"""
        
        test_content = """- 第一行
-    
-\t
-  \t  
- 第二行"""
        
        expected_lines = [
            '- 第一行',
            '',
            '- 第二行'
        ]
        
        lines = test_content.split('\n')
        optimized = self.formatter._optimize_formatting(lines)
        
        self.assertEqual(optimized, expected_lines, "带空格和制表符的空行应该被清理")
    
    def test_full_conversion_with_formatting(self):
        """测试完整转换过程中的格式优化"""
        
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
        
        result = self.formatter.format_content(test_data)
        
        # 检查结果中的空行和标题间距
        lines = result.split('\n')
        
        # 验证标题前有空行
        title1_index = lines.index('# 标题1')
        self.assertEqual(lines[title1_index - 1], '', "标题1前应该有空行")
        
        title2_index = lines.index('## 标题2')
        self.assertEqual(lines[title2_index - 1], '', "标题2前应该有空行")
        
        title3_index = lines.index('### 标题3')
        self.assertEqual(lines[title3_index - 1], '', "标题3前应该有空行")
        
        # 验证没有连续空行
        consecutive_empty = 0
        for line in lines:
            if line == '':
                consecutive_empty += 1
                self.assertLessEqual(consecutive_empty, 1, "不应该有连续的空行")
            else:
                consecutive_empty = 0
    
    def test_edge_cases(self):
        """测试边缘情况"""
        
        # 测试空内容
        self.assertEqual(self.formatter._optimize_formatting([]), [])
        
        # 测试只有空行
        empty_lines = ['', '-', '-   ', '-\t']
        result = self.formatter._optimize_formatting(empty_lines)
        self.assertEqual(result, [''], "只有空行时应该保留一个空行")
        
        # 测试文档开头的标题（不应该添加前置空行）
        content_with_leading_title = ['# 开头标题', '- 内容']
        result = self.formatter._optimize_formatting(content_with_leading_title)
        self.assertEqual(result, ['# 开头标题', '- 内容'], 
                        "文档开头的标题前不应该添加空行")
    
    def test_complex_formatting_scenario(self):
        """测试复杂格式化场景"""
        
        test_content = """- 这是第一段内容
-   
-
-\t
# 没有前置空行的标题
- 标题后的内容
-
-
-
## 多个空行前的标题
- 内容继续
- 更多内容
### 正常标题
- 内容
-
-  \t 
-
#### 带空格的空行前的标题"""
        
        lines = test_content.split('\n')
        optimized = self.formatter._optimize_formatting(lines)
        
        # 验证结果结构
        expected_structure = [
            '- 这是第一段内容',
            '',
            '',  # 这里会有一个空行
            '# 没有前置空行的标题',
            '- 标题后的内容',
            '',
            '## 多个空行前的标题', 
            '- 内容继续',
            '- 更多内容',
            '',
            '### 正常标题',
            '- 内容',
            '',
            '#### 带空格的空行前的标题'
        ]
        
        # 验证关键结构特征
        self.assertIn('# 没有前置空行的标题', optimized)
        self.assertIn('## 多个空行前的标题', optimized)
        self.assertIn('### 正常标题', optimized)
        self.assertIn('#### 带空格的空行前的标题', optimized)
        
        # 验证没有连续空行
        consecutive_empty = 0
        for line in optimized:
            if line == '':
                consecutive_empty += 1
                self.assertLessEqual(consecutive_empty, 1, "不应该有连续的空行")
            else:
                consecutive_empty = 0


if __name__ == '__main__':
    unittest.main()