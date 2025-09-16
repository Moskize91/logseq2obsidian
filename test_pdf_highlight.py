#!/usr/bin/env python3
"""
测试 PDF 高亮转换功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter

def test_pdf_highlight_conversion():
    """测试 PDF 高亮转换"""
    
    # 创建实例
    parser = LogseqParser()
    formatter = ObsidianFormatter()
    
    # 设置目录
    logseq_dir = project_root / "examples" / "logseq_data"
    
    # 第一阶段：收集 PDF 高亮映射
    print("=== 收集 PDF 高亮映射 ===")
    formatter.collect_pdf_highlights(logseq_dir)
    print(f"收集到 {len(formatter.pdf_highlight_map)} 个 PDF 高亮映射")
    
    # 测试文件
    test_file = logseq_dir / "pages" / "The Lacanian Subject - Between Language and Jouissance - One Language and Otherness.md"
    
    if not test_file.exists():
        print(f"测试文件不存在: {test_file}")
        return
    
    # 解析文件
    print(f"\n=== 解析文件 ===")
    print(f"文件: {test_file.name}")
    
    try:
        parsed_data = parser.parse_file(test_file)
        print(f"解析成功，内容长度: {len(parsed_data['content'])} 字符")
        
        # 转换文件
        print(f"\n=== 转换文件 ===")
        output_filename = formatter.generate_filename(test_file.stem)
        print(f"输出文件名: {output_filename}")
        
        # 设置输入资源目录以便资源检查
        formatter.input_assets_dir = logseq_dir / "assets"
        
        converted_content = formatter.format_content(parsed_data, output_filename)
        
        # 显示转换结果
        print(f"\n=== 转换结果 ===")
        lines = converted_content.split('\n')
        for i, line in enumerate(lines[:20], 1):  # 显示前20行
            print(f"{i:2d}: {line}")
        
        if len(lines) > 20:
            print(f"... (省略 {len(lines) - 20} 行)")
            
        # 检查是否有 PDF 链接
        pdf_links = [line for line in lines if '.pdf#page=' in line]
        print(f"\n=== PDF 链接检查 ===")
        print(f"找到 {len(pdf_links)} 个 PDF 链接:")
        for link in pdf_links:
            print(f"  {link.strip()}")
        
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_highlight_conversion()