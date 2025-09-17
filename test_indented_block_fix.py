#!/usr/bin/env python3
"""
测试缩进块ID的修复
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from obsidian_formatter import ObsidianFormatter


def test_indented_block_id_fix():
    """测试缩进块ID的修复"""
    
    # 创建测试数据：模拟实际的日志文件
    test_data = {
        'content': '''- [[crdt]]
  id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632
- [[文明是一种错觉]]
- [[卡片式笔记]]'''
    }
    
    formatter = ObsidianFormatter()
    
    print("=== 测试缩进的无引用块 ID ===")
    print(f"原始内容:\n{test_data['content']}\n")
    
    # 第一阶段：收集被引用的 UUID
    formatter.collect_referenced_uuids(test_data)
    print(f"被引用的UUID: {formatter.referenced_uuids}")
    
    # 第二阶段：只为被引用的块分配 ID
    formatter.collect_block_mappings("test.md", test_data)
    print(f"块映射: {formatter.block_uuid_map}")
    
    # 格式化内容
    result = formatter.format_content(test_data, "test.md")
    print(f"转换结果:\n{result}")
    
    # 验证：应该没有包含原始的id::行
    assert "id:: 61a8ad30-0b98-43fb-9d05-77b7f77be632" not in result, "无引用的缩进块 ID 应该被删除"
    assert "^block" not in result, "无引用的块不应该有块ID"
    
    print("\n🎉 缩进块 ID 删除测试通过！")


if __name__ == "__main__":
    test_indented_block_id_fix()