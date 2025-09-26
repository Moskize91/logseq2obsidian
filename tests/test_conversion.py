#!/usr/bin/env python3
"""
完整转换测试
将真实的 Logseq 文件转换为 Obsidian 格式，并保存到输出目录
"""

import sys
from pathlib import Path

# 添加项目根目录到路径，以便正确导入 src 模块
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.file_manager import FileManager
from src.logseq_parser import LogseqParser
from src.obsidian_formatter import ObsidianFormatter


def test_full_conversion():
    """测试完整的转换流程"""
    print("=== 完整转换测试 ===")

    # 设置路径
    test_dir = Path(__file__).parent
    logseq_dir = test_dir / "samples"
    output_dir = Path(__file__).parent / "output"  # 使用 tests/output 目录

    # 清空输出目录
    if output_dir.exists():
        import shutil

        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"输入目录: {logseq_dir}")
    print(f"输出目录: {output_dir}")

    # 初始化组件
    parser = LogseqParser()
    formatter = ObsidianFormatter()
    file_manager = FileManager(output_dir, dry_run=False)

    conversions = []

    # 转换所有 .md 文件
    md_files = list(logseq_dir.glob("*.md"))
    print(f"找到 {len(md_files)} 个文件")

    for md_file in md_files:
        print(f"\n处理文件: {md_file.name}")

        try:
            # 解析文件
            parsed_data = parser.parse_file(md_file)

            # 转换内容
            converted_content = formatter.format_content(parsed_data, md_file.name)

            # 生成输出文件名
            output_filename = formatter.generate_filename(md_file.stem)

            # 写入文件
            file_manager.write_file(output_filename, converted_content)

            # 获取转换摘要
            conversion_summary = formatter.get_conversion_summary(
                parsed_data, converted_content
            )

            conversions.append(
                {
                    "source_file": md_file.name,
                    "target_file": output_filename,
                    "success": True,
                    "summary": conversion_summary,
                }
            )

            print(f"✅ 转换成功: {md_file.name} -> {output_filename}")
            print(
                f"   原始: 页面链接{conversion_summary['original']['page_links']}个, 块引用{conversion_summary['original']['block_refs']}个"
            )
            print(
                f"   转换: 页面链接{conversion_summary['converted']['page_links']}个, 注释{conversion_summary['converted']['block_refs']}个"
            )

        except Exception as e:
            print(f"❌ 转换失败: {md_file.name} - {e}")
            conversions.append(
                {"source_file": md_file.name, "success": False, "error": str(e)}
            )

    # 生成转换报告
    report_path = file_manager.create_conversion_report(conversions)
    print(f"\n📊 转换报告已生成: {report_path}")

    # 汇总结果
    successful = len([c for c in conversions if c.get("success", False)])
    total = len(conversions)

    print(f"\n=== 转换汇总 ===")
    print(f"成功: {successful}/{total}")
    print(f"输出目录: {output_dir}")

    if successful == total:
        print("🎉 所有文件转换成功！")
        return True
    else:
        print("⚠️  部分文件转换失败")
        return False


def inspect_output():
    """检查输出文件"""
    print("\n=== 检查输出文件 ===")

    output_dir = Path(__file__).parent.parent / "examples" / "obsidian_output"

    if not output_dir.exists():
        print("输出目录不存在")
        return

    output_files = list(output_dir.glob("*.md"))
    print(f"输出文件数: {len(output_files)}")

    for output_file in output_files:
        print(f"\n📄 {output_file.name}")
        print(f"   大小: {output_file.stat().st_size} 字节")

        # 显示前几行
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[:8]
                for i, line in enumerate(lines, 1):
                    print(f"   {i:2d}: {line.rstrip()}")
                if len(lines) >= 8:
                    print("   ...")
        except Exception as e:
            print(f"   读取错误: {e}")


def main():
    """运行完整转换测试"""
    print("开始完整转换测试\n")

    success = test_full_conversion()
    inspect_output()

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
