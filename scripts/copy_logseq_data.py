#!/usr/bin/env python3
"""
Logseq 数据复制脚本
全量复制真实 Logseq 数据到 examples/logseq_data/ 用于转换测试
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# 源 Logseq 目录
LOGSEQ_SOURCE_DIR = Path("/Users/taozeyu/Library/Mobile Documents/iCloud~com~logseq~logseq/Documents")

# 目标目录
PROJECT_ROOT = Path(__file__).parent.parent
TARGET_DIR = PROJECT_ROOT / "examples" / "logseq_data"


def check_source_directory():
    """检查源目录是否存在和可访问"""
    print(f"检查源目录: {LOGSEQ_SOURCE_DIR}")
    
    if not LOGSEQ_SOURCE_DIR.exists():
        print(f"❌ 源目录不存在: {LOGSEQ_SOURCE_DIR}")
        return False
    
    # 检查主要子目录
    pages_dir = LOGSEQ_SOURCE_DIR / "pages"
    journals_dir = LOGSEQ_SOURCE_DIR / "journals"
    assets_dir = LOGSEQ_SOURCE_DIR / "assets"
    
    print(f"📁 pages: {pages_dir.exists()}")
    print(f"📁 journals: {journals_dir.exists()}")
    print(f"📁 assets: {assets_dir.exists()}")
    
    # 统计文件数量
    if pages_dir.exists():
        page_files = list(pages_dir.glob("*.md"))
        print(f"   - pages 中有 {len(page_files)} 个 .md 文件")
    
    if journals_dir.exists():
        journal_files = list(journals_dir.glob("*.md"))
        print(f"   - journals 中有 {len(journal_files)} 个 .md 文件")
    
    if assets_dir.exists():
        asset_files = list(assets_dir.rglob("*"))
        asset_files = [f for f in asset_files if f.is_file()]
        print(f"   - assets 中有 {len(asset_files)} 个文件")
        
        # 计算总大小
        total_size = sum(f.stat().st_size for f in asset_files)
        size_mb = total_size / (1024 * 1024)
        print(f"   - assets 总大小: {size_mb:.1f} MB")
    
    return True


def clear_target_directory():
    """清空目标目录"""
    if TARGET_DIR.exists():
        print(f"清空目标目录: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR)
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"创建目标目录: {TARGET_DIR}")


def copy_logseq_data():
    """复制 Logseq 数据"""
    print(f"\n开始复制数据...")
    print(f"从: {LOGSEQ_SOURCE_DIR}")
    print(f"到: {TARGET_DIR}")
    
    copied_items = []
    
    # 复制主要目录
    directories_to_copy = ["pages", "journals", "assets", "logseq"]
    
    for dir_name in directories_to_copy:
        source_path = LOGSEQ_SOURCE_DIR / dir_name
        target_path = TARGET_DIR / dir_name
        
        if source_path.exists():
            print(f"\n📁 复制目录: {dir_name}")
            try:
                shutil.copytree(source_path, target_path)
                
                # 统计复制的文件
                files = list(target_path.rglob("*"))
                files = [f for f in files if f.is_file()]
                print(f"   ✅ 复制了 {len(files)} 个文件")
                
                copied_items.append({
                    'directory': dir_name,
                    'files': len(files),
                    'success': True
                })
                
            except Exception as e:
                print(f"   ❌ 复制失败: {e}")
                copied_items.append({
                    'directory': dir_name,
                    'files': 0,
                    'success': False,
                    'error': str(e)
                })
        else:
            print(f"📁 跳过不存在的目录: {dir_name}")
    
    # 复制根目录的重要文件
    important_files = ["config.edn", "custom.css", "export.css"]
    
    print(f"\n📄 复制根目录重要文件:")
    for file_name in important_files:
        source_file = LOGSEQ_SOURCE_DIR / file_name
        target_file = TARGET_DIR / file_name
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                print(f"   ✅ {file_name}")
            except Exception as e:
                print(f"   ❌ {file_name}: {e}")
        else:
            print(f"   ⚪ {file_name} (不存在)")
    
    return copied_items


def create_copy_report(copied_items):
    """创建复制报告"""
    report_path = TARGET_DIR / "copy_report.md"
    
    lines = [
        "# Logseq 数据复制报告",
        f"复制时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"源目录: {LOGSEQ_SOURCE_DIR}",
        f"目标目录: {TARGET_DIR}",
        "",
        "## 复制摘要",
    ]
    
    total_files = sum(item['files'] for item in copied_items if item['success'])
    successful_dirs = len([item for item in copied_items if item['success']])
    total_dirs = len(copied_items)
    
    lines.extend([
        f"- 成功复制目录: {successful_dirs}/{total_dirs}",
        f"- 总文件数: {total_files}",
        "",
        "## 详细信息",
        ""
    ])
    
    for item in copied_items:
        status = "✅ 成功" if item['success'] else "❌ 失败"
        lines.append(f"### {item['directory']} - {status}")
        lines.append(f"- 文件数: {item['files']}")
        
        if not item['success'] and 'error' in item:
            lines.append(f"- 错误: {item['error']}")
        
        lines.append("")
    
    report_content = '\n'.join(lines)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📊 复制报告已生成: {report_path}")
    return report_path


def main():
    """主函数"""
    print("🚀 开始 Logseq 数据复制")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查源目录
    if not check_source_directory():
        print("❌ 源目录检查失败，退出")
        return False
    
    # 2. 清空目标目录
    clear_target_directory()
    
    # 3. 复制数据
    copied_items = copy_logseq_data()
    
    # 4. 生成报告
    create_copy_report(copied_items)
    
    # 5. 汇总结果
    successful = len([item for item in copied_items if item['success']])
    total = len(copied_items)
    
    print(f"\n=== 复制汇总 ===")
    print(f"成功: {successful}/{total}")
    print(f"目标目录: {TARGET_DIR}")
    
    if successful == total:
        print("🎉 数据复制完成！")
        print(f"现在可以运行转换脚本: python scripts/convert_examples.py")
        return True
    else:
        print("⚠️  部分目录复制失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)