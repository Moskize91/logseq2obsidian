# Logseq2Obsidian

一个将 Logseq 笔记迁移到 Obsidian 格式的 Python 工具。

## 🚀 快速开始

### 环境搭建

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

### 运行转换

#### 命令行转换 (开发中)
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

**测试类型：**
- `test_basic` - 基础功能测试
- `test_bug_fixes` - Bug 修复验证测试
- `test_formatting_comprehensive` - 格式优化综合测试
- `test_block_id_comprehensive` - 块ID处理综合测试
- `test_page_links_comprehensive` - 页面链接处理综合测试
- `test_category_detection_comprehensive` - 分类检测综合测试

## 🎯 主要功能

- ✅ **Logseq 格式解析**: 解析 Logseq markdown 文件
- ✅ **页面链接转换**: 保持 `[[页面]]` 格式兼容
- ✅ **块引用处理**: 将 `((uuid))` 转换为 Obsidian 块引用
- ✅ **Meta 属性转换**: 将 `property:: value` 转换为 YAML frontmatter
- ✅ **格式优化**: 空行处理、标题间距、内容清理
- ✅ **文件名处理**: URL 编码和特殊字符处理
- ✅ **分类功能**: 基于标签自动分类文件到文件夹

## 📁 项目结构

```
logseq2obsidian/
├── src/                    # 源代码
│   ├── main.py            # 主程序入口
│   ├── logseq_parser.py   # Logseq 解析器
│   ├── obsidian_formatter.py # Obsidian 格式转换器
│   ├── file_manager.py    # 文件管理器
│   └── ...
├── tests/                 # 测试代码
├── scripts/               # 工具脚本
│   ├── setup.sh          # 环境搭建脚本
│   └── convert_examples.py # 示例转换脚本
├── examples/              # 示例数据
├── docs/                  # 文档
└── test.py               # 测试运行器
```

## 🛠️ 开发

测试驱动开发，确保代码质量：

```bash
# 开发时持续运行测试
python test.py

# 修改代码后验证
python test.py --test test_specific_feature
```

详细的开发文档和 API 说明请参考 `docs/` 目录。