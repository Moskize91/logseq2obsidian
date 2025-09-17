# 测试说明

本项目包含完整的测试套件，确保代码质量和功能正确性。

## 测试结构

```
tests/
├── __init__.py                              # 测试包初始化
├── README.md                                # 测试说明文档
├── test_basic.py                           # 基础功能测试
├── test_bug_fixes.py                       # Bug 修复验证测试
├── test_conversion.py                      # 完整转换测试
├── test_real_data.py                       # 真实数据测试
├── test_filename_processing.py             # 文件名处理测试
├── test_meta_properties.py                 # Meta 属性处理测试
├── test_category_tag_feature.py           # 分类标签功能测试
├── test_tag_removal.py                    # 标签移除测试
│
# 综合测试文件（整合了多个零散测试）
├── test_block_id_comprehensive.py         # 块ID处理综合测试
├── test_category_detection_comprehensive.py # 分类检测综合测试
├── test_formatting_comprehensive.py       # 格式优化综合测试
└── test_page_links_comprehensive.py       # 页面链接处理综合测试
```

## 运行测试

### 运行所有测试（推荐）
```bash
# 从项目根目录运行
python -m pytest tests/ -v
```

### 运行单个测试文件
```bash
# 基础功能测试
python tests/test_basic.py

# Bug 修复测试
python tests/test_bug_fixes.py

# 综合测试
python tests/test_block_id_comprehensive.py
python tests/test_formatting_comprehensive.py
```

## 测试内容分类

### 1. 核心功能测试

#### 基础功能测试 (`test_basic.py`)
- 测试 LogseqParser 解析器的基本功能
- 验证 ObsidianFormatter 格式转换
- 使用真实样本文件进行测试

#### 完整转换测试 (`test_conversion.py`)
- 测试完整的 Logseq 到 Obsidian 转换流程
- 包括文件管理、frontmatter 处理等
- 生成转换报告

### 2. 专项功能测试

#### 块ID处理综合测试 (`test_block_id_comprehensive.py`)
- 无引用块ID删除逻辑
- 有引用块ID保留逻辑
- 多次引用处理
- 混合引用/非引用场景
- 不同格式块ID支持
- 边缘情况处理

#### 页面链接处理综合测试 (`test_page_links_comprehensive.py`)
- 基本页面链接转换
- 特殊字符页面链接
- 中英混合页面链接
- 技术术语页面链接
- 文本中的页面链接
- 嵌套和边缘情况

#### 分类检测综合测试 (`test_category_detection_comprehensive.py`)
- IPFS 文件分类检测
- CRDT 文件分类检测
- 多标签文件处理
- 混合内容文件处理
- 边缘情况处理

#### 格式优化综合测试 (`test_formatting_comprehensive.py`)
- 连续空行合并
- 标题前空行添加
- 空行清理（移除空白字符）
- 复杂文档格式优化
- 与其他功能的集成

### 3. Bug 修复验证测试

#### Bug 修复测试 (`test_bug_fixes.py`)
专门测试已修复的问题，确保这些问题不会再次出现：

- **Bug Fix #1**: 引用块格式转换 (`- >` → `>`)
- **Bug Fix #2**: 空列表项处理
- **Bug Fix #3**: 列表缩进规范化
- **Bug Fix #4**: 双破折号和空行处理
- **Bug Fix #5**: 移除顶级子弹点时的缩进提升
- **集成测试**: 验证所有修复在完整转换中正常工作

### 4. 专门功能测试

#### 文件名处理测试 (`test_filename_processing.py`)
- URL 编码/解码处理
- 特殊字符文件名
- 中文文件名支持

#### Meta 属性处理测试 (`test_meta_properties.py`)
- Frontmatter 生成
- 各种 meta 属性类型
- Alias 属性特殊处理

#### 分类标签功能测试 (`test_category_tag_feature.py`)
- 分类标签检测
- 文件夹分类逻辑

#### 标签移除测试 (`test_tag_removal.py`)
- 标签清理逻辑
- 保留重要标签

### 5. 真实数据测试 (`test_real_data.py`)
- 使用真实的 Logseq 数据进行测试
- 验证大规模数据转换的稳定性

## 测试环境

测试使用项目的 Python 虚拟环境：
```bash
# 激活环境（如果使用 venv）
source .venv/bin/activate

# 或使用 Poetry
poetry shell
```

## 代码质量保证

### 测试覆盖范围
- ✅ 核心解析逻辑
- ✅ 格式转换算法  
- ✅ 文件处理流程
- ✅ 边缘情况处理
- ✅ Bug 修复验证
- ✅ 集成测试

### 测试类型
- **单元测试**: 测试单个函数/方法
- **集成测试**: 测试组件间协作
- **回归测试**: 防止已修复的 bug 重现
- **真实数据测试**: 验证实际使用场景

## 持续集成

所有测试应该在代码提交前运行，确保：
1. 所有测试都通过
2. 新功能有对应的测试用例
3. Bug 修复有防止回归的测试

## 添加新测试

在添加新功能或修复 bug 时，请：

1. **选择合适的测试文件**:
   - 新功能 → 对应的功能测试文件
   - Bug 修复 → `test_bug_fixes.py`
   - 综合特性 → 相应的综合测试文件

2. **编写测试用例**:
   - 确保测试覆盖边界情况
   - 使用描述性的测试方法名
   - 添加详细的测试文档字符串

3. **验证测试**:
   - 运行新测试确保通过
   - 运行所有测试确保没有回归
   - 检查测试覆盖率

## 测试最佳实践

1. **测试独立性**: 每个测试应该能独立运行
2. **可读性**: 测试代码应该清晰表达测试意图
3. **完整性**: 覆盖正常情况、边界情况和错误情况
4. **维护性**: 测试代码也需要维护，保持简洁和结构化