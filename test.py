#!/usr/bin/env python3
"""
logseq2obsidian 测试运行器
提供多种测试运行选项
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, cwd=Path(__file__).parent, 
                              capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("🚀 运行所有测试...")
    
    # 收集所有测试文件
    test_files = [
        ("tests/test_basic.py", "基础功能测试"),
        ("tests/test_bug_fixes.py", "Bug修复验证测试"),
        ("tests/test_conversion.py", "完整转换测试"),
        ("tests/test_real_data.py", "真实数据测试"),
        ("tests/test_filename_processing.py", "文件名处理测试"),
        ("tests/test_meta_properties.py", "Meta属性处理测试"),
        ("tests/test_category_tag_feature.py", "分类标签功能测试"),
        ("tests/test_tag_removal.py", "标签移除测试"),
        ("tests/test_block_id_comprehensive.py", "块ID处理综合测试"),
        ("tests/test_category_detection_comprehensive.py", "分类检测综合测试"),
        ("tests/test_formatting_comprehensive.py", "格式优化综合测试"),
        ("tests/test_page_links_comprehensive.py", "页面链接处理综合测试"),
    ]
    
    passed = 0
    total = 0
    
    for test_file, description in test_files:
        if Path(test_file).exists():
            total += 1
            success = run_command(f"python {test_file}", description)
            if success:
                passed += 1
                print(f"✅ {description} - 通过")
            else:
                print(f"❌ {description} - 失败")
        else:
            print(f"⚠️  跳过 {description} (文件不存在)")
    
    print(f"\n{'='*60}")
    print(f"📊 测试汇总: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
        return True
    else:
        print(f"❌ {total - passed} 个测试失败")
        return False

def run_unittest_discovery():
    """使用 unittest 自动发现和运行测试"""
    print("🔍 使用 unittest 自动发现测试...")
    return run_command("python -m unittest discover tests -v", "unittest 自动发现测试")

def run_pytest():
    """使用 pytest 运行测试"""
    print("🧪 使用 pytest 运行测试...")
    return run_command("python -m pytest tests/ -v", "pytest 测试")

def run_specific_test(test_name):
    """运行特定测试"""
    test_file = f"tests/{test_name}"
    if not test_file.endswith('.py'):
        test_file += '.py'
    
    if Path(test_file).exists():
        return run_command(f"python {test_file}", f"运行 {test_name}")
    else:
        print(f"❌ 测试文件不存在: {test_file}")
        return False

def list_available_tests():
    """列出所有可用的测试"""
    print("📋 可用的测试文件:")
    print("-" * 40)
    
    test_dir = Path("tests")
    test_files = sorted(test_dir.glob("test_*.py"))
    
    for i, test_file in enumerate(test_files, 1):
        test_name = test_file.stem
        print(f"{i:2d}. {test_name}")
    
    print(f"\n共找到 {len(test_files)} 个测试文件")

def main():
    parser = argparse.ArgumentParser(description="logseq2obsidian 测试运行器")
    parser.add_argument("--all", action="store_true", help="运行所有测试 (默认)")
    parser.add_argument("--unittest", action="store_true", help="使用 unittest 自动发现")
    parser.add_argument("--pytest", action="store_true", help="使用 pytest 运行")
    parser.add_argument("--test", type=str, help="运行特定测试 (例如: test_basic)")
    parser.add_argument("--list", action="store_true", help="列出所有可用测试")
    
    args = parser.parse_args()
    
    # 如果没有参数，默认运行所有测试
    if not any([args.unittest, args.pytest, args.test, args.list]):
        args.all = True
    
    success = True
    
    if args.list:
        list_available_tests()
    elif args.test:
        success = run_specific_test(args.test)
    elif args.unittest:
        success = run_unittest_discovery()
    elif args.pytest:
        success = run_pytest()
    elif args.all:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()