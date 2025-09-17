# 智能标签检测功能使用说明

## 🎯 功能概述

智能标签检测是 Logseq2Obsidian 工具的一个重要新功能，解决了 Logseq 和 Obsidian 在标签与页面引用处理上的根本差异：

- **Logseq**: `[[标签]]` = 页面引用 = 可以包含完整内容的页面
- **Obsidian**: `#标签` = 纯标签 = 只是分类标记，没有内容

智能标签检测能够自动分析 Logseq 页面引用，判断哪些应该转换为 Obsidian 标签，哪些应该保持为页面链接。

## 🧠 智能检测逻辑

### 转换为标签的条件（满足任一即可）：

1. **页面不存在**：引用的页面文件不存在
2. **内容过少**：页面内容少于配置的阈值（默认3行）
3. **符合标签特征**：
   - 全小写单词（如 `tech`, `work`）
   - 常见标签词汇（如 `工作`, `学习`, `技术`）
   - 日期格式（如 `2024`, `12月`）
   - 状态词汇（如 `进行中`, `已完成`）
   - 简短词汇（少于6个字符且不含特殊符号）

### 保持为页面链接的条件：

1. **有实质内容**：页面包含丰富的内容
2. **强制配置**：在 `force_pages` 列表中指定
3. **复杂命名**：不符合标签命名特征的复杂页面名

## 🔧 配置选项

### 基本配置

```python
from src.tag_analyzer import TagAnalysisConfig

config = TagAnalysisConfig(
    # 是否启用智能检测（默认：True）
    smart_tag_detection=True,
    
    # 内容长度阈值：少于此行数转为标签（默认：3）
    content_threshold=3,
    
    # 强制转换为标签的页面名称
    force_tags=["工作", "学习", "想法"],
    
    # 强制保持为页面的名称
    force_pages=["重要项目", "深度学习笔记"],
    
    # 是否检测标签命名模式（默认：True）
    detect_tag_patterns=True
)
```

### 在转换脚本中使用

```bash
# 启用智能标签检测（默认）
python scripts/convert_examples.py

# 禁用智能标签检测
python scripts/convert_examples.py --disable-smart-tag-detection
```

## 📊 转换示例

### 智能检测启用时：

| Logseq 格式 | Obsidian 格式 | 原因 |
|------------|---------------|------|
| `[[技术]]` | `#技术` | 简短词汇，符合标签特征 |
| `[[2024]]` | `#2024` | 日期格式 |
| `[[工作]]` | `#工作` | 常见标签词汇 |
| `[[深度学习笔记]]` | `[[深度学习笔记]]` | 有实质内容的页面 |
| `[[项目管理方法论]]` | `[[项目管理方法论]]` | 复杂主题，保持页面链接 |
| `[[不存在的页面]]` | `#不存在的页面` | 页面文件不存在 |

### 智能检测禁用时：

所有 `[[页面引用]]` 都保持为 `[[页面引用]]` 格式。

## 🎨 标签名称规范化

转换为标签时，会自动处理特殊字符：

- 空格 → 下划线：`前端 开发` → `#前端_开发`
- 连字符 → 下划线：`Vue-js` → `#Vue_js`
- 特殊字符 → 下划线：`C++编程` → `#C__编程`

## 📈 转换统计

智能标签检测会在转换过程中显示详细统计：

```
📊 智能标签分析：
   - 总页面数: 773
   - 将转为标签: 324
   - 保持为页面: 449
   - 标签示例: 技术, 工作, 学习, 2024, 想法
   - 页面示例: 深度学习笔记, 项目管理方法论, 精神分析引论
```

同时在每个文件的转换统计中也能看到页面链接数量的变化：

```
📊 页面链接: 17 → 4  # 说明13个页面引用被转换为了标签
```

## 🔍 调试和验证

### 查看分析结果

```python
from src.tag_analyzer import TagAnalyzer, TagAnalysisConfig
from pathlib import Path

# 创建分析器
analyzer = TagAnalyzer(Path("examples/logseq_data/pages"))

# 获取分析摘要
summary = analyzer.get_analysis_summary()
print(summary)

# 获取将转换为标签的页面列表
tag_candidates = analyzer.get_tag_candidates()
print(f"将转为标签: {tag_candidates[:10]}")

# 获取将保持为页面的列表
page_candidates = analyzer.get_page_candidates()
print(f"保持为页面: {page_candidates[:10]}")

# 检查特定页面
print(f"'技术' 转为标签: {analyzer.should_convert_to_tag('技术')}")
print(f"'深度学习笔记' 转为标签: {analyzer.should_convert_to_tag('深度学习笔记')}")
```

### 测试不同配置

```python
# 测试严格模式（提高阈值）
strict_config = TagAnalysisConfig(content_threshold=10)
strict_analyzer = TagAnalyzer(pages_dir, strict_config)

# 测试宽松模式（降低阈值）
loose_config = TagAnalysisConfig(content_threshold=1)
loose_analyzer = TagAnalyzer(pages_dir, loose_config)
```

## ⚙️ 高级用法

### 自定义标签检测模式

如果需要自定义检测逻辑，可以继承 `TagAnalyzer` 类：

```python
from src.tag_analyzer import TagAnalyzer

class CustomTagAnalyzer(TagAnalyzer):
    def _is_tag_like_name(self, page_name: str) -> bool:
        # 自定义标签特征检测
        custom_patterns = [
            r'^我的.*',  # 以"我的"开头
            r'.*笔记$',  # 以"笔记"结尾
        ]
        
        for pattern in custom_patterns:
            if re.match(pattern, page_name):
                return True
        
        return super()._is_tag_like_name(page_name)
```

## 💡 最佳实践

1. **首次使用**：建议先用默认配置转换，观察效果后再调整
2. **内容审查**：转换后在 Obsidian 中检查标签和页面链接是否合理
3. **逐步调优**：根据实际需求调整 `content_threshold` 和强制列表
4. **备份原始数据**：转换前务必备份原始 Logseq 数据

## 🚀 升级指南

如果您之前使用过 Logseq2Obsidian 工具：

1. **自动升级**：新版本默认启用智能标签检测
2. **保持兼容**：可以使用 `--disable-smart-tag-detection` 参数恢复旧行为
3. **重新转换**：建议用新功能重新转换以获得更好的效果

智能标签检测让您的 Logseq 到 Obsidian 迁移更加智能和准确！