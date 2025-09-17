#!/usr/bin/env python3
"""
Embed语法转换综合测试
测试LogSeq的{{embed ((uuid))}}语法转换为Obsidian的![[filename#^blockId]]格式
"""

import unittest
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.obsidian_formatter import ObsidianFormatter
from src.logseq_parser import LogseqParser


class TestEmbedComprehensive(unittest.TestCase):
    """Embed功能综合测试"""
    
    def setUp(self):
        self.formatter = ObsidianFormatter()
        self.parser = LogseqParser()
    
    def test_embed_with_file_mapping(self):
        """测试embed功能和文件映射集成"""
        print('\n=== 测试embed功能和文件映射集成 ===')
        
        # 设置块UUID映射（模拟logseq页面到obsidian文件的映射）
        self.formatter.block_uuid_map = {
            'abc123-def456': ('test_page.md', 'block1'),
            'xyz789-ghi012': ('another_page.md', 'block2')
        }
        
        # 测试数据：包含embed语法的内容
        test_data = {
            'content': '''这是一个测试页面。

{{embed ((abc123-def456))}}

这里还有另一个embed：
{{embed ((xyz789-ghi012))}}

这里有一个未知的embed（不在映射中）：
{{embed ((unknown-uuid))}}
''',
            'meta_properties': []
        }
        
        # 处理转换
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'main.md')
        
        print('转换结果:')
        print(result)
        print('\n分行结果:')
        for i, line in enumerate(result.split('\n'), 1):
            print(f'{i:2}: {repr(line)}')
        
        # 验证结果
        self.assertIn('![[test_page#^block1]]', result, "有文件映射的embed应该转换为带文件名的格式")
        self.assertIn('![[another_page#^block2]]', result, "第二个embed也应该正确转换")
        self.assertIn('<!-- Block Embed (未找到): unknown-uuid -->', result, "未知UUID的embed应该生成注释")
        
        print('\n✅ Embed功能测试通过！')
        
        # 验证referenced_uuids被正确收集
        expected_uuids = {'abc123-def456', 'xyz789-ghi012', 'unknown-uuid'}
        self.assertEqual(self.formatter.referenced_uuids, expected_uuids, 
                        f"期望的UUID: {expected_uuids}, 实际: {self.formatter.referenced_uuids}")
        
        print('✅ UUID收集功能正常！')
    
    def test_embed_without_file_mapping(self):
        """测试没有文件映射的embed转换"""
        print('\n=== 测试没有文件映射的embed转换 ===')
        
        # 不设置任何文件映射
        test_data = {
            'content': '''这是一个测试页面。

{{embed ((some-uuid))}}

{{embed ((another-uuid))}}
''',
            'meta_properties': []
        }
        
        # 处理转换
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'main.md')
        
        # 验证结果：没有映射的UUID应该生成注释
        self.assertIn('<!-- Block Embed (未找到): some-uuid -->', result)
        self.assertIn('<!-- Block Embed (未找到): another-uuid -->', result)
        
        # 验证UUID被收集
        expected_uuids = {'some-uuid', 'another-uuid'}
        self.assertEqual(self.formatter.referenced_uuids, expected_uuids)
        
        print('✅ 无映射embed测试通过！')
    
    def test_embed_syntax_variations(self):
        """测试embed语法的不同变化形式"""
        print('\n=== 测试embed语法变化形式 ===')
        
        # 设置一些映射
        self.formatter.block_uuid_map = {
            'uuid-1': ('file1.md', 'block1'),
            'uuid-2': ('file2.md', 'block2')
        }
        
        test_data = {
            'content': '''测试不同的embed语法：

- {{embed ((uuid-1))}}
- 文本前 {{embed ((uuid-2))}} 文本后
  - {{embed ((uuid-3))}}
    - {{embed ((uuid-1))}}

{{embed ((uuid-2))}}
''',
            'meta_properties': []
        }
        
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'test.md')
        
        print('转换结果:')
        print(result)
        
        # 验证转换
        self.assertIn('![[file1#^block1]]', result)
        self.assertIn('![[file2#^block2]]', result)
        self.assertIn('<!-- Block Embed (未找到): uuid-3 -->', result)
        
        # 验证UUID收集
        expected_uuids = {'uuid-1', 'uuid-2', 'uuid-3'}
        self.assertEqual(self.formatter.referenced_uuids, expected_uuids)
        
        print('✅ 语法变化测试通过！')
    
    def test_full_embed_workflow(self):
        """测试完整的embed转换工作流"""
        print('\n=== 测试完整的embed转换工作流 ===')
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 创建logseq输入目录结构
            logseq_dir = temp_path / "logseq_data"
            pages_dir = logseq_dir / "pages"
            pages_dir.mkdir(parents=True)
            
            # 创建带有embed语法的测试文件
            main_page = pages_dir / "main_page.md"
            main_page.write_text('''- 这是主页面
- 下面嵌入了另一个页面：
- {{embed ((page-with-blocks))}}
- 这是主页面的一个块
  id:: main-block-id
''', encoding='utf-8')
            
            # 创建被嵌入的页面
            target_page = pages_dir / "target_page.md"
            target_page.write_text('''- 这是被嵌入的页面
  id:: page-with-blocks
- 第一个段落
- 第二个段落
- 这个块会被引用：((main-block-id))
''', encoding='utf-8')
            
            # 创建输出目录
            output_dir = temp_path / "obsidian_output"
            output_dir.mkdir()
            
            # 模拟转换流程
            formatter = ObsidianFormatter()
            
            # 第一阶段：收集所有块映射
            print("第一阶段：收集块映射...")
            for md_file in pages_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                parsed = self.parser.parse_content(content)
                formatter.collect_referenced_uuids(parsed)
                formatter.collect_block_mappings(md_file.stem + ".md", parsed)
            
            # 第二阶段：执行转换
            print("第二阶段：执行转换...")
            for md_file in pages_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                parsed = self.parser.parse_content(content)
                formatted = formatter.format_content(parsed, md_file.stem + ".md")
                
                output_file = output_dir / f"{md_file.stem}.md"
                output_file.write_text(formatted, encoding='utf-8')
            
            # 检查转换结果
            main_result = (output_dir / "main_page.md").read_text(encoding='utf-8')
            target_result = (output_dir / "target_page.md").read_text(encoding='utf-8')
            
            print("主页面转换结果:")
            for i, line in enumerate(main_result.split('\n'), 1):
                print(f'{i:2}: {repr(line)}')
            
            print("\n被嵌入页面转换结果:")
            for i, line in enumerate(target_result.split('\n'), 1):
                print(f'{i:2}: {repr(line)}')
            
            # 验证embed转换
            self.assertIn('![[target_page#^block1]]', main_result, "Embed应该正确转换为Obsidian格式")
            
            # 验证块引用转换（这里应该是注释，因为main-block-id在同一阶段未被处理）
            self.assertIn('<!-- Block Reference (未找到): main-block-id -->', target_result, 
                         "未找到的块引用应该生成注释")
            
            # 验证块ID生成
            self.assertIn('^block1', target_result, "被嵌入页面应该有块ID")
            
            print("\n✅ 完整转换工作流测试通过！")
    
    def test_embed_edge_cases(self):
        """测试embed功能的边缘情况"""
        print('\n=== 测试embed边缘情况 ===')
        
        # 测试空内容
        test_data = {
            'content': '',
            'meta_properties': []
        }
        
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'test.md')
        self.assertEqual(result.strip(), '')
        
        # 测试只有embed的内容
        test_data = {
            'content': '{{embed ((test-uuid))}}',
            'meta_properties': []
        }
        
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'test.md')
        self.assertIn('<!-- Block Embed (未找到): test-uuid -->', result)
        
        # 测试多行embed
        test_data = {
            'content': '''{{embed ((uuid-1))}}
{{embed ((uuid-2))}}
{{embed ((uuid-3))}}''',
            'meta_properties': []
        }
        
        self.formatter.collect_referenced_uuids(test_data)
        result = self.formatter.format_content(test_data, 'test.md')
        
        self.assertIn('<!-- Block Embed (未找到): uuid-1 -->', result)
        self.assertIn('<!-- Block Embed (未找到): uuid-2 -->', result)
        self.assertIn('<!-- Block Embed (未找到): uuid-3 -->', result)
        
        expected_uuids = {'test-uuid', 'uuid-1', 'uuid-2', 'uuid-3'}
        self.assertEqual(self.formatter.referenced_uuids, expected_uuids)
        
        print('✅ 边缘情况测试通过！')


if __name__ == '__main__':
    unittest.main(verbosity=2)