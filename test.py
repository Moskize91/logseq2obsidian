#!/usr/bin/env python3
"""
运行所有测试
"""

import sys
import subprocess
import os
from pathlib import Path


def run_test_file(test_file):
    """运行单个测试文件"""
    print(f"\n{'='*50}")
    print(f"运行测试: {test_file.name}")
    print(f"{'='*50}")
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    try:
        # 使用 venv 环境运行测试
        # 设置环境变量确保使用 .venv 中的 Python
        env = os.environ.copy()
        venv_python = project_root / ".venv" / "bin" / "python"
        
        if not venv_python.exists():
            print(f"❌ 虚拟环境未找到: {venv_python}")
            print("请先运行: bash scripts/setup.sh")
            return False
        
        result = subprocess.run([
            str(venv_python), str(test_file)
        ], 
        capture_output=True, 
        text=True, 
        cwd=test_file.parent.parent,
        env=env)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} 测试通过")
            return True
        else:
            print(f"❌ {test_file.name} 测试失败 (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ 运行 {test_file.name} 时出错: {e}")
        return False


def main():
    """运行所有测试"""
    # 项目根目录
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    # 要运行的测试文件
    test_files = [
        tests_dir / "test_basic.py",
        tests_dir / "test_bug_fixes.py",
    ]
    
    print("Logseq2Obsidian 测试套件")
    print("=" * 50)
    print(f"项目根目录: {project_root}")
    print(f"测试目录: {tests_dir}")
    print(f"计划运行 {len(test_files)} 个测试文件")
    
    # 运行所有测试
    results = []
    for test_file in test_files:
        if test_file.exists():
            success = run_test_file(test_file)
            results.append((test_file.name, success))
        else:
            print(f"⚠️  测试文件不存在: {test_file}")
            results.append((test_file.name, False))
    
    # 汇总结果
    print(f"\n{'='*50}")
    print("测试结果汇总")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
        return True
    else:
        print("⚠️  有测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)