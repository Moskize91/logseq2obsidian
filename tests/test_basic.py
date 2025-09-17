"""
测试 Logseq 解析器的基本功能
使用真实的样本文件
"""

import sys
from pathlib import Path

# 添加项目根目录到路径，以便正确导入 src 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


def test_sample1():
    """测试 sample1.md 文件的解析"""
    print("=== 测试 sample1.md ===")
    
    # 文件路径
    sample_file = Path(__file__).parent / "samples" / "sample1.md"
    
    if not sample_file.exists():
        print(f"错误：测试文件不存在: {sample_file}")
        return False
    
    try:
        # 解析文件
        parser = LogseqParser()
        parsed_data = parser.parse_file(sample_file)
        
        # 显示解析结果
        print(f"文件名: {parsed_data['filename']}")
        print(f"总块数: {len(parsed_data['blocks'])}")
        print(f"页面链接数: {len(parsed_data['page_links'])}")
        print(f"块引用数: {len(parsed_data['block_refs'])}")
        print(f"资源文件数: {len(parsed_data['assets'])}")
        
        # 显示统计
        stats = parser.get_statistics(parsed_data)
        print(f"统计信息: {stats}")
        
        # 测试格式转换
        formatter = ObsidianFormatter()
        converted_content = formatter.format_content(parsed_data)
        
        # 显示转换摘要
        conversion_summary = formatter.get_conversion_summary(parsed_data, converted_content)
        print(f"转换摘要: {conversion_summary}")
        
        # 显示转换后的前几行（预览）
        preview_lines = converted_content.split('\n')[:10]
        print("\n转换预览（前10行）:")
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:2d}: {line}")
        
        print("✅ sample1.md 测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_journal_sample():
    """测试 journal_sample.md 文件的解析"""
    print("\n=== 测试 journal_sample.md ===")
    
    # 文件路径
    sample_file = Path(__file__).parent / "samples" / "journal_sample.md"
    
    if not sample_file.exists():
        print(f"错误：测试文件不存在: {sample_file}")
        return False
    
    try:
        # 解析文件
        parser = LogseqParser()
        parsed_data = parser.parse_file(sample_file)
        
        # 显示解析结果
        print(f"文件名: {parsed_data['filename']}")
        print(f"总块数: {len(parsed_data['blocks'])}")
        print(f"页面链接数: {len(parsed_data['page_links'])}")
        print(f"块引用数: {len(parsed_data['block_refs'])}")
        print(f"资源文件数: {len(parsed_data['assets'])}")
        
        # 测试格式转换
        formatter = ObsidianFormatter()
        converted_content = formatter.format_content(parsed_data)
        
        # 显示转换摘要
        conversion_summary = formatter.get_conversion_summary(parsed_data, converted_content)
        print(f"转换摘要: {conversion_summary}")
        
        print("✅ journal_sample.md 测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("开始运行 Logseq2Obsidian 基础测试\n")
    
    results = []
    
    # 运行测试
    results.append(test_sample1())
    results.append(test_journal_sample())
    
    # 汇总结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n=== 测试汇总 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 有测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)