#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from obsidian_formatter import ObsidianFormatter

def test_specific_cases():
    formatter = ObsidianFormatter(category_tag='wiki', category_folder='Wiki')
    
    # 测试 IPFS.md 的情况
    print("=== 测试 IPFS.md ===")
    ipfs_content = """- > 星际文件系统 #wiki #区块链
- 使用 [[Kademlia]] 的分布式公开文件系统，存储文件全量。有点类似 [[BitTorrent]]。"""
    
    ipfs_data = {
        'content': ipfs_content,
        'meta_properties': []
    }
    
    lines = ipfs_content.split('\n')
    actual_lines = formatter._get_actual_content_lines(lines, {})
    print(f"实际内容行: {actual_lines}")
    
    for i, line in enumerate(actual_lines):
        cleaned = formatter._remove_logseq_bullets(line)
        print(f"第{i+1}行: '{line}' -> '{cleaned}'")
        
    category = formatter.detect_category_folder(ipfs_data)
    print(f"检测结果: {category}")
    print()
    
    # 测试 crdt.md 的情况  
    print("=== 测试 crdt.md ===")
    crdt_content = """- #算法 #wiki
- CRDT 首先要解决排序问题：让不同客户端的操作经过无中心的广播后，在所有端能够收敛到相同的顺序，从而保证执行这些操作后能够到达一样的结果."""
    
    crdt_data = {
        'content': crdt_content,
        'meta_properties': []
    }
    
    lines = crdt_content.split('\n')
    actual_lines = formatter._get_actual_content_lines(lines, {})
    print(f"实际内容行: {actual_lines}")
    
    for i, line in enumerate(actual_lines):
        cleaned = formatter._remove_logseq_bullets(line)
        print(f"第{i+1}行: '{line}' -> '{cleaned}'")
        
    category = formatter.detect_category_folder(crdt_data)
    print(f"检测结果: {category}")

if __name__ == "__main__":
    test_specific_cases()