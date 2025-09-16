#!/usr/bin/env python3
"""
真实数据转换测试
使用用户的真实 Logseq 数据进行转换测试
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径，以便正确导入 src 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter
from src.file_manager import FileManager


# 真实的 Logseq 目录路径
LOGSEQ_SOURCE_DIR = Path("/Users/taozeyu/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents")
# 测试输出目录（会被清空）
TEST_OUTPUT_DIR = Path(__file__).parent / "output"


def clear_output_directory():
    """清空输出目录"""
    if TEST_OUTPUT_DIR.exists():
        print(f"清空输出目录: {TEST_OUTPUT_DIR}")
        shutil.rmtree(TEST_OUTPUT_DIR)
    
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"创建新的输出目录: {TEST_OUTPUT_DIR}")


def check_logseq_access():
    """检查是否能访问 Logseq 目录"""
    print(f"检查 Logseq 目录访问: {LOGSEQ_SOURCE_DIR}")
    
    if not LOGSEQ_SOURCE_DIR.exists():
        print(f"❌ Logseq 目录不存在: {LOGSEQ_SOURCE_DIR}")
        return False
    
    # 检查主要子目录
    pages_dir = LOGSEQ_SOURCE_DIR / "pages"
    journals_dir = LOGSEQ_SOURCE_DIR / "journals"
    
    print(f"📁 pages 目录存在: {pages_dir.exists()}")
    print(f"📁 journals 目录存在: {journals_dir.exists()}")
    
    if pages_dir.exists():
        page_files = list(pages_dir.glob("*.md"))
        print(f"   - pages 中找到 {len(page_files)} 个 .md 文件")
    
    if journals_dir.exists():
        journal_files = list(journals_dir.glob("*.md"))
        print(f"   - journals 中找到 {len(journal_files)} 个 .md 文件")
    
    return True


def test_sample_files(max_files=5):
    """测试部分样本文件"""
    print(f"\n=== 测试样本文件转换 (最多 {max_files} 个) ===")
    
    # 初始化组件
    parser = LogseqParser()
    formatter = ObsidianFormatter()
    file_manager = FileManager(TEST_OUTPUT_DIR, dry_run=False)
    
    conversions = []
    
    # 获取 .md 文件
    md_files = file_manager.list_logseq_files(LOGSEQ_SOURCE_DIR)
    print(f"总共找到 {len(md_files)} 个 markdown 文件")
    
    if not md_files:
        print("❌ 没有找到 markdown 文件")
        return False
    
    # 限制测试文件数量
    test_files = md_files[:max_files]
    print(f"选择测试前 {len(test_files)} 个文件")
    
    for i, md_file in enumerate(test_files, 1):
        print(f"\n📄 [{i}/{len(test_files)}] 处理文件: {md_file.name}")
        
        try:
            # 解析文件
            parsed_data = parser.parse_file(md_file)
            
            # 格式转换
            converted_content = formatter.format_content(parsed_data)
            
            # 添加 frontmatter
            metadata = {
                'logseq_source': md_file.name,
                'source_path': str(md_file.relative_to(LOGSEQ_SOURCE_DIR)),
                'created': file_manager._get_timestamp()
            }
            final_content = formatter.add_frontmatter(converted_content, metadata)
            
            # 生成输出文件名
            output_filename = formatter.generate_filename(md_file.stem)
            
            # 写入文件
            file_manager.write_file(output_filename, final_content)
            
            # 获取转换摘要
            conversion_summary = formatter.get_conversion_summary(parsed_data, converted_content)
            
            conversions.append({
                'source_file': str(md_file.relative_to(LOGSEQ_SOURCE_DIR)),
                'target_file': output_filename,
                'success': True,
                'summary': conversion_summary
            })
            
            print(f"   ✅ 转换成功")
            print(f"   📊 页面链接: {conversion_summary['original']['page_links']} → {conversion_summary['converted']['page_links']}")
            print(f"   📊 块引用: {conversion_summary['original']['block_refs']} → {conversion_summary['converted']['block_refs']} (注释)")
            print(f"   📊 块ID: {conversion_summary['original']['block_ids']} → {conversion_summary['converted']['block_ids']}")
            
        except Exception as e:
            print(f"   ❌ 转换失败: {e}")
            conversions.append({
                'source_file': str(md_file.relative_to(LOGSEQ_SOURCE_DIR)),
                'success': False,
                'error': str(e)
            })
    
    # 生成转换报告
    report_path = file_manager.create_conversion_report(conversions)
    print(f"\n📊 转换报告已生成: {report_path}")
    
    # 汇总结果
    successful = len([c for c in conversions if c.get('success', False)])
    total = len(conversions)
    
    print(f"\n=== 转换汇总 ===")
    print(f"成功: {successful}/{total}")
    print(f"成功率: {successful/total*100:.1f}%")
    print(f"输出目录: {TEST_OUTPUT_DIR}")
    
    return successful == total


def inspect_output():
    """检查输出文件"""
    print(f"\n=== 检查输出文件 ===")
    
    if not TEST_OUTPUT_DIR.exists():
        print("输出目录不存在")
        return
    
    output_files = list(TEST_OUTPUT_DIR.glob("*.md"))
    report_files = list(TEST_OUTPUT_DIR.glob("conversion_report.md"))
    
    print(f"📄 输出文件数: {len(output_files)}")
    print(f"📊 报告文件数: {len(report_files)}")
    
    if output_files:
        print(f"\n前3个输出文件预览：")
        for output_file in output_files[:3]:
            print(f"\n📄 {output_file.name} ({output_file.stat().st_size} 字节)")
            
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:8]
                    for i, line in enumerate(lines, 1):
                        print(f"   {i:2d}: {line.rstrip()}")
                    if len(lines) >= 8:
                        print("   ...")
            except Exception as e:
                print(f"   读取错误: {e}")


def main():
    """运行真实数据转换测试"""
    print("🚀 开始真实数据转换测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 清空输出目录
    clear_output_directory()
    
    # 2. 检查 Logseq 目录访问
    if not check_logseq_access():
        print("❌ 无法访问 Logseq 目录，测试终止")
        return False
    
    # 3. 运行转换测试
    success = test_sample_files(max_files=3)  # 先测试3个文件
    
    # 4. 检查输出结果
    inspect_output()
    
    if success:
        print("\n🎉 真实数据转换测试成功！")
    else:
        print("\n⚠️  转换测试有部分失败")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)