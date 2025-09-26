#!/usr/bin/env python3
"""
代码质量检查脚本
运行各种 linting 工具来检查代码质量

Code quality checking script
Runs various linting tools to check code quality
"""

import subprocess
import sys
import argparse
from pathlib import Path


class Colors:
    """终端颜色"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    RESET = "\033[0m"


def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{Colors.BLUE}🔍 {description}{Colors.RESET}")
    print(f"{Colors.GRAY}$ {' '.join(cmd)}{Colors.RESET}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0
    except FileNotFoundError:
        print(f"{Colors.RED}❌ 命令未找到: {cmd[0]}{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ 运行命令时出错: {e}{Colors.RESET}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="代码质量检查工具 / Code quality checking tool"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="自动修复可修复的问题 / Auto-fix fixable issues",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="运行完整检查（包括 mypy）/ Run full checks (including mypy)",
    )
    parser.add_argument(
        "--format-only",
        action="store_true",
        help="只运行格式化检查 / Run only format checks",
    )
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="只运行 lint 检查 / Run only lint checks",
    )
    parser.add_argument(
        "--test-only",
        action="store_true",
        help="只运行测试 / Run only tests",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式（更严格的检查）/ CI mode (stricter checks)",
    )

    args = parser.parse_args()

    # 确定要运行的检查
    if args.format_only:
        checks = ["format"]
    elif args.lint_only:
        checks = ["lint"]
    elif args.test_only:
        checks = ["test"]
    else:
        checks = ["format", "lint", "test"]
        if args.full:
            checks.append("type")

    print(f"\n{Colors.BLUE}🚀 开始代码质量检查 / Starting code quality checks{Colors.RESET}")
    print(f"{Colors.GRAY}模式 / Mode: {', '.join(checks)}{Colors.RESET}")

    all_passed = True

    # 1. 代码格式化检查
    if "format" in checks:
        print(f"\n{Colors.YELLOW}📋 代码格式化检查 / Code Formatting Check{Colors.RESET}")

        # Black 格式化检查
        black_cmd = ["poetry", "run", "black"]
        if args.fix:
            black_cmd.extend(["src", "tests"])
            desc = "运行 Black 格式化 / Running Black formatting"
        else:
            black_cmd.extend(["--check", "src", "tests"])
            desc = "检查 Black 格式化 / Checking Black formatting"

        if not run_command(black_cmd, desc):
            all_passed = False

        # isort 导入排序检查
        isort_cmd = ["poetry", "run", "isort"]
        if args.fix:
            isort_cmd.extend(["src", "tests"])
            desc = "运行 isort 导入排序 / Running isort import sorting"
        else:
            isort_cmd.extend(["--check-only", "src", "tests"])
            desc = "检查 isort 导入排序 / Checking isort import sorting"

        if not run_command(isort_cmd, desc):
            all_passed = False

    # 2. Lint 检查
    if "lint" in checks:
        print(f"\n{Colors.YELLOW}🔍 Lint 检查 / Lint Check{Colors.RESET}")

        # 基础 flake8 检查（错误和严重问题）
        flake8_basic_cmd = [
            "poetry", "run", "flake8", "src", "tests",
            "--count", "--select=E9,F63,F7,F82",
            "--show-source", "--statistics"
        ]

        if not run_command(flake8_basic_cmd, "基础 flake8 检查 / Basic flake8 check"):
            all_passed = False

        # 完整 flake8 检查（可选）
        if args.ci or args.full:
            flake8_full_cmd = [
                "poetry", "run", "flake8", "src", "tests",
                "--count", "--exit-zero",
                "--max-complexity=10", "--max-line-length=88",
                "--statistics"
            ]
            if not run_command(flake8_full_cmd, "完整 flake8 检查 / Full flake8 check"):
                print(f"{Colors.YELLOW}⚠️  完整检查有警告，但不影响通过 / Full check has warnings but doesn't affect passing{Colors.RESET}")

    # 3. 类型检查（可选）
    if "type" in checks:
        print(f"\n{Colors.YELLOW}🔧 类型检查 / Type Check{Colors.RESET}")

        mypy_cmd = ["poetry", "run", "mypy", "src"]
        if not run_command(mypy_cmd, "mypy 类型检查 / mypy type check"):
            if args.ci:
                all_passed = False
            else:
                print(f"{Colors.YELLOW}⚠️  类型检查失败，但不影响通过 / Type check failed but doesn't affect passing{Colors.RESET}")

    # 4. 测试
    if "test" in checks:
        print(f"\n{Colors.YELLOW}🧪 测试 / Tests{Colors.RESET}")

        pytest_cmd = ["poetry", "run", "pytest", "tests/", "-v"]
        if not run_command(pytest_cmd, "运行测试 / Running tests"):
            all_passed = False

    # 5. 构建检查（CI 模式）
    if args.ci:
        print(f"\n{Colors.YELLOW}📦 构建检查 / Build Check{Colors.RESET}")

        build_cmd = ["poetry", "build"]
        if not run_command(build_cmd, "构建包 / Building package"):
            all_passed = False

    # 总结
    print(f"\n{Colors.BLUE}📊 检查总结 / Check Summary{Colors.RESET}")

    if all_passed:
        print(f"{Colors.GREEN}✅ 所有检查通过！/ All checks passed!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}❌ 部分检查失败 / Some checks failed{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()