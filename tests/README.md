# 测试说明

本项目包含完整的测试套件，确保代码质量和功能正确性。

## 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── test_basic.py           # 基础功能测试
├── test_bug_fixes.py       # Bug 修复测试
├── test_conversion.py      # 完整转换测试
├── test_real_data.py       # 真实数据测试
└── README.md               # 测试说明文档

# 项目根目录
test.py                     # 运行所有测试的主脚本
```

## 运行测试

### 运行所有测试（推荐）
```bash
# 从项目根目录运行
python test.py
```

### 运行单个测试文件
```bash
# 基础功能测试
python tests/test_basic.py

# Bug 修复测试
python tests/test_bug_fixes.py

# 完整转换测试
python tests/test_conversion.py
```

## 测试内容

### 1. 基础功能测试 (`test_basic.py`)
- 测试 LogseqParser 解析器的基本功能
- 验证 ObsidianFormatter 格式转换
- 使用真实样本文件进行测试

### 2. Bug 修复测试 (`test_bug_fixes.py`)
专门测试已修复的问题，确保这些问题不会再次出现：

#### Bug Fix #1: 引用块格式转换
- **问题**: Logseq 中的 `- > 内容` 格式在 Obsidian 中被错误解析
- **修复**: 将 `- > 内容` 转换为 `> 内容` 标准 Markdown 引用格式
- **测试用例**:
  - 基本引用块转换
  - 缩进引用块处理（制表符和空格）
  - 普通列表项不受影响
  - 已有引用格式保持不变

#### Bug Fix #2: 空列表项处理
- **问题**: 出现了只有 `-` 的空行，影响文档美观
- **修复**: 跳过空的列表项，不在转换后的文档中留下无意义的空行
- **测试用例**:
  - 空列表项被正确跳过
  - 子列表中的空项也被处理
  - 不影响有内容的列表项

#### Bug Fix #3: 列表缩进规范化
- **问题**: Obsidian 要求同级列表项必须有相同的缩进级别
- **修复**: 规范化列表缩进，将制表符转换为标准的 2 个空格
- **测试用例**:
  - 制表符转换为空格
  - 同级列表项缩进一致
  - 多级缩进保持正确的层级关系

#### 集成测试
- 验证所有 bug 修复在完整转换中正常工作
- 使用包含所有问题类型的复杂测试用例

### 3. 完整转换测试 (`test_conversion.py`)
- 测试完整的 Logseq 到 Obsidian 转换流程
- 包括文件管理、frontmatter 处理等
- 生成转换报告

### 4. 真实数据测试 (`test_real_data.py`)
- 使用真实的 Logseq 数据进行测试
- 验证大规模数据转换的稳定性

## 测试环境

测试使用项目的 venv 环境：
```bash
# 激活环境
source .venv/bin/activate

# 环境路径
/Users/taozeyu/codes/github.com/moskize91/logseq2obsidian/.venv/bin/python
```

## 持续集成

所有测试应该在代码提交前运行，确保：
1. 所有测试都通过
2. 新功能有对应的测试用例
3. Bug 修复有防止回归的测试

## 添加新测试

在添加新功能或修复 bug 时，请：
1. 在相应的测试文件中添加测试用例
2. 确保测试覆盖边界情况
3. 为复杂的修复添加集成测试
4. 运行所有测试确保没有回归