# 日期格式修复总结

## 问题描述
用户反馈：转换后的 Obsidian 日记文件使用 `2025_01_02.md` 格式，但 Obsidian 默认应该使用 `2025-01-02.md` 格式（连字符而非下划线）。

## 根因分析
1. **LogSeq 日期格式**: LogSeq 的 journals 目录中使用下划线格式 `2025_01_02.md`
2. **转换逻辑缺失**: 原代码只是简单复制文件名，没有针对日期格式的特殊处理
3. **Obsidian 标准**: Obsidian 的 Daily Notes 插件默认使用连字符格式 `YYYY-MM-DD`

## 解决方案

### 1. 修改 `generate_filename` 方法
在 `src/obsidian_formatter.py` 中的 `generate_filename` 方法添加日期格式转换逻辑：

```python
def generate_filename(self, original_name: str) -> str:
    """生成 Obsidian 兼容的文件名"""
    # 移除或替换 Obsidian 不支持的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
    
    # 转换 LogSeq 日期格式为 Obsidian 格式
    # LogSeq: 2025_01_02 -> Obsidian: 2025-01-02
    # 只转换合理的日期格式（年份2000-2099，月份01-12，日期01-31）
    date_pattern = r'^(20[0-9]{2})_([0-1][0-9])_([0-3][0-9])(.*)$'
    date_match = re.match(date_pattern, safe_name)
    if date_match:
        year, month, day, suffix = date_match.groups()
        # 基本的日期合理性检查
        month_int = int(month)
        day_int = int(day)
        if 1 <= month_int <= 12 and 1 <= day_int <= 31:
            safe_name = f"{year}-{month}-{day}{suffix}"
    
    # 确保 .md 扩展名
    if not safe_name.endswith('.md'):
        safe_name += '.md'
    
    return safe_name
```

### 2. 转换规则
- **匹配模式**: `(20[0-9]{2})_([0-1][0-9])_([0-3][0-9])(.*)`
- **年份范围**: 2000-2099
- **月份范围**: 01-12（必须是两位数）
- **日期范围**: 01-31（必须是两位数）
- **后缀支持**: 保留任何后缀（如 `2024_01_06 2.md` → `2024-01-06 2.md`）

### 3. 安全性考虑
- **严格验证**: 只转换符合标准日期格式的文件名
- **边缘情况**: 无效的日期（如 `2025_13_01`、`2025_01_32`）保持原格式
- **非日期文件**: 完全不受影响

## 测试验证

### 1. 单元测试
在 `tests/test_filename_processing.py` 中添加了 `test_date_format_conversion` 方法：

```python
def test_date_format_conversion(self):
    """测试LogSeq日期格式转换为Obsidian格式"""
    # 测试标准日期格式转换
    test_cases = [
        ("2025_01_02", "2025-01-02.md"),
        ("2024_12_31", "2024-12-31.md"),
        ("2024_01_06 2", "2024-01-06 2.md"),  # 带后缀
    ]
    
    # 测试非日期文件不受影响
    non_date_cases = [
        ("normal_file", "normal_file.md"),
        ("2025_1_2", "2025_1_2.md"),      # 不标准格式
        ("2025_13_01", "2025_13_01.md"),  # 无效月份
    ]
```

### 2. 实际转换测试
验证了实际转换输出：
- **之前**: `/Daily Notes/2025_01_02.md`
- **之后**: `/Daily Notes/2025-01-02.md`

### 3. 回归测试
- ✅ 所有现有测试继续通过
- ✅ 文件名处理功能正常
- ✅ 非日期文件不受影响

## 转换效果

### 文件名对比
| LogSeq 原格式 | Obsidian 新格式 | 说明 |
|---------------|----------------|------|
| `2025_01_02.md` | `2025-01-02.md` | 标准日期格式转换 |
| `2024_12_31.md` | `2024-12-31.md` | 年底日期 |
| `2024_01_06 2.md` | `2024-01-06 2.md` | 带后缀的重复文件 |
| `normal_file.md` | `normal_file.md` | 非日期文件不变 |
| `2025_13_01.md` | `2025_13_01.md` | 无效月份保持原样 |

### 目录结构
```
obsidian_output/
├── Daily Notes/
│   ├── 2025-01-02.md     ← 使用连字符
│   ├── 2025-01-03.md     ← 使用连字符
│   └── 2025-01-04.md     ← 使用连字符
├── Wiki/
└── 其他文件.md
```

## 兼容性

### Obsidian 兼容性
- ✅ **Daily Notes 插件**: 完全兼容默认的 `YYYY-MM-DD` 格式
- ✅ **Calendar 插件**: 可以正确识别和导航日期文件
- ✅ **文件链接**: `[[2025-01-02]]` 格式的内部链接正常工作

### 向后兼容性
- ✅ 不影响现有的非日期文件处理
- ✅ 保持所有其他文件名转换规则
- ✅ 不改变文件内容转换逻辑

## 总结

### ✅ 已完成
1. **日期格式转换**: LogSeq `2025_01_02` → Obsidian `2025-01-02`
2. **智能识别**: 只转换符合标准格式的日期文件
3. **安全处理**: 无效日期和非日期文件保持不变
4. **测试覆盖**: 添加了完整的单元测试和集成测试
5. **向后兼容**: 保持所有现有功能不变

### 🎯 效果
- **用户体验**: 转换后的文件完全符合 Obsidian 标准
- **日期导航**: Obsidian 的日期相关插件可以正常工作
- **文件组织**: Daily Notes 按标准格式整齐排列

现在用户可以无缝地将 LogSeq 日记迁移到 Obsidian，享受原生的日期导航和管理体验！