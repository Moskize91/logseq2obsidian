#!/usr/bin/env python3
"""
测试块 ID 处理逻辑的修复
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from obsidian_formatter import ObsidianFormatter


def test_unreferenced_block_id_removal():
    """测试无引用的块 ID 会被删除"""
    
    # 创建测试数据：有块ID但没有引用
    test_data_1 = {
        'content': '''这是一段文字
id:: abc123-def456
另一段文字
id:: xyz789-uvw012'''
    }
    
    # 创建测试数据：有块ID且有引用
    test_data_2 = {
        'content': '''这里引用了 ((abc123-def456)) 
id:: abc123-def456
这里没有引用
id:: xyz789-uvw012'''
    }
    
    formatter = ObsidianFormatter()
    
    print("=== 测试 1: 没有引用的块 ID ===")
    
    # 第一阶段：收集被引用的 UUID
    formatter.collect_referenced_uuids(test_data_1)
    print(f"被引用的UUID: {formatter.referenced_uuids}")
    
    # 第二阶段：只为被引用的块分配 ID
    formatter.collect_block_mappings("test1.md", test_data_1)
    print(f"块映射: {formatter.block_uuid_map}")
    
    # 格式化内容
    result = formatter.format_content(test_data_1, "test1.md")
    print(f"转换结果:\n{result}")
    
    # 验证：应该没有块 ID
    assert "^block" not in result, "无引用的块 ID 应该被删除"
    
    print("\n=== 测试 2: 有引用的块 ID ===")
    
    # 重置状态
    formatter = ObsidianFormatter()
    
    # 第一阶段：收集被引用的 UUID
    formatter.collect_referenced_uuids(test_data_2)
    print(f"被引用的UUID: {formatter.referenced_uuids}")
    
    # 第二阶段：只为被引用的块分配 ID
    formatter.collect_block_mappings("test2.md", test_data_2)
    print(f"块映射: {formatter.block_uuid_map}")
    
    # 格式化内容
    result = formatter.format_content(test_data_2, "test2.md")
    print(f"转换结果:\n{result}")
    
    # 验证：应该有一个块 ID（被引用的那个）
    # 统计实际的块 ID 行（以 ^block 开头的行）
    block_lines = [line for line in result.split('\n') if line.strip().startswith('^block')]
    print(f"块 ID 行: {block_lines}")
    
    # 应该只有被引用的那个有块 ID
    assert "^block" in result, "有引用的块 ID 应该被保留"
    assert len(block_lines) == 1, f"只有被引用的块 ID 应该被保留，实际有: {len(block_lines)}"
    
    print("\n🎉 所有测试通过！块 ID 处理逻辑正确")


if __name__ == "__main__":
    test_unreferenced_block_id_removal()