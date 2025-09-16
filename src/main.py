#!/usr/bin/env python3
"""
Logseq2Obsidian - 将 Logseq 笔记迁移到 Obsidian 格式的工具

主程序入口
"""

import argparse
import sys
from pathlib import Path

from .logseq_parser import LogseqParser
from .obsidian_formatter import ObsidianFormatter
from .file_manager import FileManager


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='将 Logseq 笔记迁移到 Obsidian 格式')
    parser.add_argument('input_dir', help='Logseq 笔记目录路径')
    parser.add_argument('output_dir', help='Obsidian 输出目录路径')
    parser.add_argument('--dry-run', action='store_true', help='只预览转换结果，不实际写入文件')
    
    args = parser.parse_args()
    
    # 验证输入路径
    input_path = Path(args.input_dir)
    if not input_path.exists():
        print(f"错误：输入目录不存在: {input_path}")
        sys.exit(1)
    
    output_path = Path(args.output_dir)
    
    print(f"开始转换 Logseq 笔记...")
    print(f"输入目录: {input_path}")
    print(f"输出目录: {output_path}")
    print(f"预览模式: {'是' if args.dry_run else '否'}")
    
    try:
        # 初始化组件
        parser = LogseqParser()
        formatter = ObsidianFormatter()
        file_manager = FileManager(output_path, dry_run=args.dry_run)
        
        # TODO: 实现完整的转换流程
        print("转换功能正在开发中...")
        
    except Exception as e:
        print(f"转换过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()