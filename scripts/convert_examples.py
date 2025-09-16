#!/usr/bin/env python3
"""
Examples 转换脚本
将 examples/logseq_data/ 转换为 Obsidian 格式，输出到 examples/obsidian_output/
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

# 路径配置
LOGSEQ_DATA_DIR = project_root / "examples" / "logseq_data"
OBSIDIAN_OUTPUT_DIR = project_root / "examples" / "obsidian_output"


def check_source_data():
    """检查源数据是否存在"""
    print(f"检查源数据: {LOGSEQ_DATA_DIR}")
    
    if not LOGSEQ_DATA_DIR.exists():
        print(f"❌ 源数据目录不存在: {LOGSEQ_DATA_DIR}")
        print("请先运行: python scripts/copy_logseq_data.py")
        return False
    
    # 检查主要目录
    pages_dir = LOGSEQ_DATA_DIR / "pages"
    journals_dir = LOGSEQ_DATA_DIR / "journals"
    
    pages_files = list(pages_dir.glob("*.md")) if pages_dir.exists() else []
    journals_files = list(journals_dir.glob("*.md")) if journals_dir.exists() else []
    
    print(f"📁 pages: {len(pages_files)} 个 .md 文件")
    print(f"📁 journals: {len(journals_files)} 个 .md 文件")
    
    total_files = len(pages_files) + len(journals_files)
    
    if total_files == 0:
        print("❌ 没有找到 markdown 文件")
        return False
    
    print(f"✅ 总共找到 {total_files} 个 markdown 文件")
    return True


def clear_output_directory():
    """清空输出目录"""
    if OBSIDIAN_OUTPUT_DIR.exists():
        print(f"清空输出目录: {OBSIDIAN_OUTPUT_DIR}")
        shutil.rmtree(OBSIDIAN_OUTPUT_DIR)
    
    OBSIDIAN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"创建输出目录: {OBSIDIAN_OUTPUT_DIR}")


def convert_logseq_to_obsidian():
    """转换 Logseq 数据为 Obsidian 格式"""
    print("\n开始转换...")
    
    # 初始化组件
    parser = LogseqParser()
    formatter = ObsidianFormatter()
    file_manager = FileManager(OBSIDIAN_OUTPUT_DIR, dry_run=False)
    
    conversions = []
    
    # 获取所有 .md 文件
    md_files = file_manager.list_logseq_files(LOGSEQ_DATA_DIR)
    print(f"找到 {len(md_files)} 个 markdown 文件")
    
    if not md_files:
        print("❌ 没有找到 markdown 文件")
        return []
    
    # 转换每个文件
    for i, md_file in enumerate(md_files, 1):
        relative_path = md_file.relative_to(LOGSEQ_DATA_DIR)
        print(f"\n📄 [{i}/{len(md_files)}] {relative_path}")
        
        try:
            # 解析文件
            parsed_data = parser.parse_file(md_file)
            
            # 格式转换
            converted_content = formatter.format_content(parsed_data)
            
            # 添加 frontmatter
            metadata = {
                'logseq_source': str(relative_path),
                'original_file': md_file.name,
                'converted_time': file_manager._get_timestamp(),
                'source_directory': relative_path.parent.name if relative_path.parent.name != '.' else 'root'
            }
            final_content = formatter.add_frontmatter(converted_content, metadata)
            
            # 生成输出文件名（保持目录结构）
            output_filename = formatter.generate_filename(md_file.stem)
            
            # 如果文件在子目录中，保持子目录结构
            if relative_path.parent.name != '.':
                subfolder = relative_path.parent.name
                file_manager.write_file(output_filename, final_content, subfolder)
            else:
                file_manager.write_file(output_filename, final_content)
            
            # 获取转换摘要
            conversion_summary = formatter.get_conversion_summary(parsed_data, converted_content)
            
            conversions.append({
                'source_file': str(relative_path),
                'target_file': output_filename,
                'success': True,
                'summary': conversion_summary
            })
            
            # 显示转换统计
            orig = conversion_summary['original']
            conv = conversion_summary['converted']
            print(f"   ✅ 转换完成")
            print(f"   📊 页面链接: {orig['page_links']} → {conv['page_links']}")
            print(f"   📊 块引用: {orig['block_refs']} → {conv['block_refs']} (注释)")
            print(f"   📊 块ID: {orig['block_ids']} → {conv['block_ids']}")
            print(f"   📊 资源: {orig['assets']} → {conv['assets']}")
            
        except Exception as e:
            print(f"   ❌ 转换失败: {e}")
            conversions.append({
                'source_file': str(relative_path),
                'success': False,
                'error': str(e)
            })
    
    return conversions


def copy_assets():
    """复制资源文件"""
    assets_source = LOGSEQ_DATA_DIR / "assets"
    assets_target = OBSIDIAN_OUTPUT_DIR / "assets"
    
    if not assets_source.exists():
        print("\n📁 没有找到 assets 目录，跳过资源复制")
        return
    
    print(f"\n📁 复制资源文件: {assets_source} → {assets_target}")
    
    try:
        if assets_target.exists():
            shutil.rmtree(assets_target)
        
        shutil.copytree(assets_source, assets_target)
        
        # 统计复制的文件
        asset_files = list(assets_target.rglob("*"))
        asset_files = [f for f in asset_files if f.is_file()]
        
        total_size = sum(f.stat().st_size for f in asset_files)
        size_mb = total_size / (1024 * 1024)
        
        print(f"   ✅ 复制了 {len(asset_files)} 个资源文件")
        print(f"   📊 总大小: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"   ❌ 资源复制失败: {e}")


def create_conversion_summary(conversions):
    """创建转换总结"""
    summary_path = OBSIDIAN_OUTPUT_DIR / "conversion_summary.md"
    
    successful = len([c for c in conversions if c.get('success', False)])
    total = len(conversions)
    
    lines = [
        "# Logseq → Obsidian 转换总结",
        f"转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"源目录: {LOGSEQ_DATA_DIR}",
        f"目标目录: {OBSIDIAN_OUTPUT_DIR}",
        "",
        "## 转换摘要",
        f"- 总文件数: {total}",
        f"- 成功转换: {successful}",
        f"- 转换失败: {total - successful}",
        f"- 成功率: {successful/total*100:.1f}%" if total > 0 else "- 成功率: 0%",
        "",
        "## 使用说明",
        "1. 用 Obsidian 打开这个目录作为新的仓库",
        "2. 检查转换效果，特别注意：",
        "   - 双链是否正确显示",
        "   - 图片和附件是否能正常访问",
        "   - 块引用注释是否合理",
        "3. 如有问题，请反馈给开发者进行修复",
        "",
        "## 转换特点",
        "- 块引用 `((uuid))` → `<!-- Block Reference: uuid -->`",
        "- 块ID `id:: uuid` → `^blockN`",
        "- 资源路径 `../assets/` → `assets/`",
        "- 双链 `[[页面]]` → `[[页面]]` (保持不变)",
        "",
    ]
    
    # 添加失败的文件列表
    failed = [c for c in conversions if not c.get('success', False)]
    if failed:
        lines.extend([
            "## 转换失败的文件",
            ""
        ])
        for failure in failed:
            lines.append(f"- `{failure['source_file']}`: {failure.get('error', '未知错误')}")
        lines.append("")
    
    lines.extend([
        "---",
        f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    ])
    
    summary_content = '\n'.join(lines)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"\n📊 转换总结已生成: {summary_path}")
    return summary_path


def main():
    """主函数"""
    print("🔄 开始 Examples 转换")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查源数据
    if not check_source_data():
        return False
    
    # 2. 清空输出目录
    clear_output_directory()
    
    # 3. 转换 markdown 文件
    conversions = convert_logseq_to_obsidian()
    
    if not conversions:
        print("❌ 没有文件被转换")
        return False
    
    # 4. 复制资源文件
    copy_assets()
    
    # 5. 生成转换总结
    create_conversion_summary(conversions)
    
    # 6. 汇总结果
    successful = len([c for c in conversions if c.get('success', False)])
    total = len(conversions)
    
    print(f"\n=== 转换汇总 ===")
    print(f"成功: {successful}/{total}")
    print(f"成功率: {successful/total*100:.1f}%")
    print(f"输出目录: {OBSIDIAN_OUTPUT_DIR}")
    
    if successful == total:
        print("🎉 转换完成！")
        print("现在可以用 Obsidian 打开输出目录进行测试")
        return True
    else:
        print("⚠️  部分文件转换失败，请查看转换总结")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)