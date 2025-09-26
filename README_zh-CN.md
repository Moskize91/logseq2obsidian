<div align=center>
  <h1>Logseq to Obsidian</h1>
  <p><a href="./README.md">English</a> | 中文</a></p>

  ![CI](https://github.com/moskize91/logseq2obsidian/workflows/CI/badge.svg)
  ![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
  ![License](https://img.shields.io/badge/license-MIT-green)
  ![PyPI](https://img.shields.io/pypi/v/logseq2obsidian)
</div>

一个将 [Logseq](https://logseq.com/) 笔记迁移到 [Obsidian](https://obsidian.md/) 格式的 Python 工具。

[Logseq](https://logseq.com/) 是一款隐私优先、本地优先的开源知识管理工具，采用大纲式编辑器，支持双向链接和块引用，适合构建个人知识网络。

[Obsidian](https://obsidian.md/) 是一款基于 Markdown 的本地知识管理工具，通过双向链接帮助用户建立知识图谱，拥有强大的插件生态系统和可视化功能。

## 🚀 快速开始

### PyPI 安装（推荐）

直接从 PyPI 安装：

```bash
pip install logseq2obsidian
```

### 运行转换

#### PyPI 安装后使用
```bash
# 基本转换
logseq2obsidian <logseq_dir> <obsidian_dir>

# 预览模式（不实际写入文件）
logseq2obsidian <logseq_dir> <obsidian_dir> --dry-run
```

#### 开发环境使用
```bash
# 基本转换
python -m src.main <logseq_dir> <obsidian_dir>

# 预览模式（不实际写入文件）
python -m src.main <logseq_dir> <obsidian_dir> --dry-run
```

#### 示例数据转换
```bash
# 基本转换（保留列表格式）
python scripts/convert_examples.py

# 转换为段落格式（移除顶级列表符号）
python scripts/convert_examples.py --remove-top-level-bullets

# 带分类功能的转换
python scripts/convert_examples.py \
  --remove-top-level-bullets \
  --category-tag wiki \
  --category-folder wiki
```

**参数说明：**
- `--remove-top-level-bullets`: 删除第一级列表符号，将内容转换为段落格式
- `--category-tag <tag>`: 指定分类标签名称（如 "wiki"）
- `--category-folder <folder>`: 指定分类文件夹名称，与 category-tag 配合使用

## 🎯 主要功能

- ✅ **Logseq 格式解析**: 解析 Logseq markdown 文件
- ✅ **页面链接转换**: 保持 `[[页面]]` 格式兼容
- ✅ **块引用处理**: 将 `((uuid))` 转换为 Obsidian 块引用
- ✅ **Meta 属性转换**: 将 `property:: value` 转换为 YAML frontmatter
- ✅ **格式优化**: 空行处理、标题间距、内容清理
- ✅ **文件名处理**: URL 编码和特殊字符处理
- ✅ **分类功能**: 基于标签自动分类文件到文件夹

### 运行测试

提供多种测试运行方式：

```bash
# 运行所有测试（推荐）
python test.py

# 查看所有可用测试
python test.py --list

# 运行特定测试
python test.py --test test_basic
python test.py --test test_bug_fixes
python test.py --test test_formatting_comprehensive

# 使用标准测试框架
python test.py --unittest    # unittest 自动发现
python test.py --pytest     # 使用 pytest（如果安装）

# 直接运行单个测试文件
python tests/test_basic.py
```

## 🛠️ 开发环境搭建

项目使用 Poetry 管理依赖，一键安装：

```bash
# 运行环境搭建脚本
bash scripts/setup.sh
```

脚本会自动：
- 检查 Python 3.10+ 版本
- 检查并配置 Poetry
- 创建虚拟环境 (.venv)
- 安装所有依赖

手动激活环境：
```bash
source .venv/bin/activate
```

测试驱动开发，确保代码质量：

```bash
# 开发时持续运行测试
python test.py

# 修改代码后验证
python test.py --test test_specific_feature
```

**测试类型：**
- `test_basic` - 基础功能测试
- `test_bug_fixes` - Bug 修复验证测试
- `test_formatting_comprehensive` - 格式优化综合测试
- `test_block_id_comprehensive` - 块ID处理综合测试
- `test_page_links_comprehensive` - 页面链接处理综合测试
- `test_category_detection_comprehensive` - 分类检测综合测试