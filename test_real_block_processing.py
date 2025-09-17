#!/usr/bin/env python3
"""
测试真实文件的块 ID 处理
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from logseq_parser import LogseqParser
from obsidian_formatter import ObsidianFormatter


def test_real_block_file():
    """测试真实的块 ID 文件处理"""
    
    test_file = Path("test_block_sample.md")
    
    # 解析文件
    parser = LogseqParser()
    data = parser.parse_file(test_file)
    print(f"原始内容:\n{data['content']}\n")
    
    # 创建formatter并按阶段处理
    formatter = ObsidianFormatter()
    
    print("=== 第一阶段：收集被引用的 UUID ===")
    formatter.collect_referenced_uuids(data)
    print(f"被引用的UUID: {formatter.referenced_uuids}")
    
    print("\n=== 第二阶段：收集块映射 ===")
    formatter.collect_block_mappings("test_block_sample.md", data)
    print(f"块映射: {formatter.block_uuid_map}")
    
    print("\n=== 第三阶段：转换内容 ===")
    result = formatter.format_content(data, "test_block_sample.md")
    print(f"转换结果:\n{result}")
    
    # 验证结果
    lines = result.split('\n')
    block_id_lines = [line for line in lines if line.strip().startswith('^block')]
    reference_lines = [line for line in lines if '![[#^block' in line]
    
    print(f"\n块 ID 行数: {len(block_id_lines)}")
    print(f"引用行数: {len(reference_lines)}")
    print(f"块 ID 行: {block_id_lines}")
    print(f"引用行: {reference_lines}")


if __name__ == "__main__":
    test_real_block_file()